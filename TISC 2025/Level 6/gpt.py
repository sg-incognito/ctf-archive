#!/usr/bin/env python3
# save as parse_webauthn_attestation.py
import base64
import cbor2
import sys
import binascii
import hashlib
import json
from struct import unpack

# helpers
def b64url_decode(s):
    if isinstance(s, str):
        s = s.encode()
    s += b'=' * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(s)

def b64url_encode(b):
    return base64.urlsafe_b64encode(b).rstrip(b'=').decode()

def parse_authdata(authdata_bytes):
    if len(authdata_bytes) < 37:
        raise ValueError("authData too short")
    rpIdHash = authdata_bytes[0:32]
    flags = authdata_bytes[32]
    signCount = unpack(">I", authdata_bytes[33:37])[0]
    offset = 37
    attested = None
    extensions = None

    # flags bits (LSB = bit 0)
    UP = bool(flags & 0x01)   # User Present
    UV = bool(flags & 0x04)   # User Verified (bit 2 -> 0x04)
    AT = bool(flags & 0x40)   # Attested credential data included (bit 6 -> 0x40)
    ED = bool(flags & 0x80)   # Extensions included (bit 7 -> 0x80)

    if AT:
        aaguid = authdata_bytes[offset:offset+16]; offset += 16
        credLen = unpack(">H", authdata_bytes[offset:offset+2])[0]; offset += 2
        credId = authdata_bytes[offset:offset+credLen]; offset += credLen
        # remaining bytes are credentialPublicKey (CBOR/COSE) until extensions or end
        credentialPublicKey = authdata_bytes[offset:]
        # if ED is set, we need to CBOR-decode extension after credentialPublicKey; but easier to attempt a CBOR decode
        try:
            # attempt to decode credentialPublicKey as CBOR; if ED present, CBOR library will decode only the key structure
            cose_obj = cbor2.loads(credentialPublicKey)
            # get the exact bytes consumed by decoding (cbor2 doesn't give consumed length easily),
            # so we'll show the decoded object and also the raw remainder
            credentialPublicKey_cb = credentialPublicKey
            # naive: assume all of the remaining bytes are public key if no ED
            attested = {
                "aaguid": binascii.hexlify(aaguid).decode(),
                "credential_id": credId,
                "credential_id_b64url": b64url_encode(credId),
                "credentialPublicKey_cbor": cose_obj,
                "credentialPublicKey_raw": credentialPublicKey_cb
            }
        except Exception as e:
            attested = {
                "aaguid": binascii.hexlify(aaguid).decode(),
                "credential_id": credId,
                "credential_id_b64url": b64url_encode(credId),
                "credentialPublicKey_raw": credentialPublicKey
            }
    else:
        attested = None

    return {
        "rpIdHash": rpIdHash,
        "rpIdHash_hex": binascii.hexlify(rpIdHash).decode(),
        "flags_byte": flags,
        "flags": {"UP":UP,"UV":UV,"AT":AT,"ED":ED},
        "signCount": signCount,
        "attested": attested
    }

def main():
    if len(sys.argv) != 3:
        print("Usage: parse_webauthn_attestation.py <attestation_object_b64url> <client_data_json_b64url>")
        print("You can also pass '-' to read from stdin for either value.")
        sys.exit(1)

    att_b64 = sys.argv[1]
    cdata_b64 = sys.argv[2]
    if att_b64 == '-':
        att_b64 = sys.stdin.readline().strip()
    if cdata_b64 == '-':
        cdata_b64 = sys.stdin.readline().strip()

    att_bytes = b64url_decode(att_b64)
    clientdata = b64url_decode(cdata_b64)
    try:
        att_obj = cbor2.loads(att_bytes)
    except Exception as e:
        print("CBOR decode of attestation_object failed:", e)
        sys.exit(2)

    print("Top-level attestation keys:", list(att_obj.keys()))
    # att_obj typically contains 'fmt', 'authData', 'attStmt'
    authData = att_obj.get('authData')
    if not authData:
        print("No authData in attestation object")
        sys.exit(2)
    print("\n--- authenticatorData ---")
    parsed = parse_authdata(authData)
    print("rpIdHash (hex):", parsed['rpIdHash_hex'])
    print("flags byte:", hex(parsed['flags_byte']), " ->", parsed['flags'])
    print("signCount:", parsed['signCount'])
    if parsed['attested']:
        a = parsed['attested']
        print("\n--- attestedCredentialData ---")
        print("AAGUID:", a['aaguid'])
        print("credentialId (len):", len(a['credential_id']))
        print("credentialId (b64url):", a['credential_id_b64url'])
        print("credentialPublicKey (CBOR decoded):")
        try:
            print(json.dumps(a['credentialPublicKey_cbor'], indent=2, default=str))
        except Exception:
            print("   (CBOR object present but could not pretty-print)")
    else:
        print("No attested credential data present (this looks like an assertion response)")

    print("\n--- clientDataJSON ---")
    try:
        cd = json.loads(clientdata.decode())
        print(json.dumps(cd, indent=2))
    except Exception as e:
        print("clientDataJSON not valid JSON? (error: {})".format(e))
        print(clientdata)

    # optional: show computed rpIdHash for target domain
    print("\n(You can verify rpIdHash by computing sha256(rpId). Example cmd in python:")
    print(">>> import hashlib; hashlib.sha256(b'passkey.chals.tisc25.ctf.sg').hexdigest() )")

if __name__ == "__main__":
    main()
