#!/usr/bin/env python3
import re
import sys

# Put the raw JSON response here (as you pasted it). Keep the triple-quotes.
RAW = r'''{\n \"Code\" : \"Success\",\n \"LastUpdated\" : \"20 25-09-27T13:22:36Z\",\n \"Type\" : \"AWSHMAC\",\n \"AccessKeyId\" : \"ASIAXYK JQ7ESDV6PY4ZU\",\n \"SecretAccessKey\" :
\"Onm+fgjVfCusok1w2V7j/xsYyFRL0KvfWkmr pnl0\",\n \"Token\" :
\"IQoJb3JpZ2luX2VjEB4aDmFwLXNvdXRoZWFzdC0xIkYwRAIgNgaD2i2
+cP/scbSSJrI0do2JbqMajFTqgBikfPDGczgCIG7i6+HiCnlmzrNGMRMCyMksiwHRxmuOZcK/DgUjvKw
5KtQFCKf//////////wEQABoMNTMzMjY3MDIwMDY4IgyVGoj3u7MtCjlIC2AqqAVqCpdmO0NG9F7azfQ
yMiQSrLFe/cRzOr1q2A071x9/2ZVW4ZBhos5oK8rMMRGIRqmE4x4MfWkAmELoBjtfwWMGONbK+cKBfWM
Y6uJRYbwsPMyfWUsgUXmlb6voz97+pxnEQpLoCUvKMRfgENpSHVJxTKZKWU/C68cuMpEYvtseK8Mj9D5
Lz6f6y0nWrUSl0aSPKQ+1X3/TxIOr4A1Dq6cfgxxcNs1+abaxesIsBs04YKmJIyrWNTSYHP3vruXTLyV
ScLjt2W5lxwXsvH/IOTNDRJL5kSMPQ2rKuSCmucun0KOgeiqAX8WdlSnQR4pj8YLqkInl2RCDMUySAfi
LNHbz7u4Le/c+PI1LeXADt334OpuT7EfH7BVyeK+wDayEQrj2S3BhPpBC4GukHtdQtHD8zv0Cf1MbHAd
3gDxrM2VM6bdsGBT9N8N30ZAR1UjUYmazFpxPWfNb3piIxWBm4aTfyU/NnF0j7VXWkT80meoTi6VWim2
oXTLQ5App9qsCifuZ4ATqTvPBOxmrxCkhN/b11Ut05kKhgsJYTKuusdFuiDQC3ChC2dDqR6daBfaxET7
0LNyK7wFQbEWdI72qbqUKvW2FQHXYQN57zOXE59rwVYTMdgccFDma5qttJYPvIT0TdPkFJmVXjsfAPCb
IzIxr4fnt+KSKWJtP4osH1eycM377hDbYO/Sr/u4n7Vrm5SBNjLdeNKBAboj2f+ikzJkaMRlmitIhVr6
3Co1rroc47DyyITcP1SHiERDyjD5G0XlpAtwM7HlXpn7UMDE9WyRRi02aS2rvx5+oa65CsAG+pZ2ul9M
Nbsz54x9cBEJZe7sDFtVUueTds/LR6xODvKHmez4T18D+IWoX4NXQTQrvE4Ye//wVUNRwagoEIgTV82e
e8lLgwabi3TDNyt/GBjqyAY/6L/8+gTvwRt8/L8fg/VtevPp31qMPSV1oI/0dPz/tD2wpV6x74+oo6uu
nzNAG7kwW+B+wqMo/uAiyXTs7MA7pseK1NFnFstTV+IDtAA03xzkAmCfOfyGgNB6cETn8LqESK5NyPT1
/77SmiStTa9yFLrXv8KJ8ehRl1leSYZctdrQ49DtU3cn/y0EkruiQEDYOKUnfPLsO5Zho/vkFOeFNM4y
khh+1QtzMW/muEw66zSQ=\",\n \"Expiration\" : \"2025-09-27T19:30:24Z\"\n}"}'''.replace("\\n", "").replace("\\\"", "\"")
# End of RAW

# -------- helper functions --------
def sh_single_quote(s: str) -> str:
    """Return a shell-safe single-quoted string (handles single quotes inside)."""
    return "'" + s.replace("'", "'\"'\"'") + "'"

def collapse_whitespace(s: str) -> str:
    """Remove all whitespace (spaces/newlines/tabs) which were likely injected by formatting."""
    return re.sub(r'\s+', '', s)

# -------- extraction patterns --------
def extract_field(raw: str, key: str, collapse_ws=True):
    """
    Try a robust regex to find "key" : "value" allowing whitespace/newlines.
    If collapse_ws is True, collapse internal whitespace in the captured value.
    """
    # Regex: look for "Key" optionally padded, colon, optional whitespace/newlines, then opening quote
    pattern = re.compile(r'"' + re.escape(key) + r'"\s*:\s*"([\s\S]*?)"', re.IGNORECASE)
    m = pattern.search(raw)
    if not m:
        return None
    val = m.group(1)
    if collapse_ws:
        val = collapse_whitespace(val)
    else:
        val = val.strip()
    return val

def main():
    ak = extract_field(RAW, 'AccessKeyId', collapse_ws=True)
    sk = extract_field(RAW, 'SecretAccessKey', collapse_ws=True)
    token = extract_field(RAW, 'Token', collapse_ws=True)
    expiration = extract_field(RAW, 'Expiration', collapse_ws=False)

    # Fallback attempts (some providers use different capitalization)
    if not ak:
        ak = extract_field(RAW, 'accesskeyid', collapse_ws=True)
    if not sk:
        sk = extract_field(RAW, 'secretaccesskey', collapse_ws=True)
    if not token:
        token = extract_field(RAW, 'token', collapse_ws=True)
    if not expiration:
        expiration = extract_field(RAW, 'expiration', collapse_ws=False)

    # Report errors if any required field missing
    missing = []
    if not ak: missing.append('AccessKeyId')
    if not sk: missing.append('SecretAccessKey')
    if not token: missing.append('Token')
    if missing:
        print("ERROR: could not extract fields:", ", ".join(missing), file=sys.stderr)
        print("Raw input snippet (first 400 chars):")
        print(RAW[:400])
        return

    # Print exports
    print("# Run these commands in a shell to set the temporary credentials:")
    print("export AWS_ACCESS_KEY_ID=" + sh_single_quote(ak))
    print("export AWS_SECRET_ACCESS_KEY=" + sh_single_quote(sk))
    print("export AWS_SESSION_TOKEN=" + sh_single_quote(token))
    if expiration:
        print("\n# Token Expiration (raw):")
        print("# " + expiration.strip())

    # Also print an ~/.aws/credentials profile snippet
    print("\n# ~/.aws/credentials profile (paste into file):")
    print("[claws-role]")
    print("aws_access_key_id = {}".format(ak))
    print("aws_secret_access_key = {}".format(sk))
    print("aws_session_token = {}".format(token))
    
    # Also print enumerator
    print()
    print(f"~/go/bin/aws-enumerator cred -aws_access_key_id {ak} -aws_region ap-southeast-1a -aws_secret_access_key {sk} -aws_session_token {token}")

if __name__ == "__main__":
    main()

