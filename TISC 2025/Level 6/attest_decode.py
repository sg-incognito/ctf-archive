import base64
import cbor2
import struct

def parse_attestation_object(attestation_b64):
    # Decode base64url
    attestation_bytes = base64.urlsafe_b64decode(attestation_b64 + '==')

    # Decode CBOR
    attestation = cbor2.loads(attestation_bytes)

    fmt = attestation.get('fmt')
    authData = attestation.get('authData')
    attStmt = attestation.get('attStmt')

    print(f"Attestation Format: {fmt}")
    print(f"Attestation Statement: {attStmt}")
    print(f"authData length: {len(authData)} bytes")

    # Parse authData
    rp_id_hash = authData[0:32]
    flags = authData[32]
    sign_count = struct.unpack('>I', authData[33:37])[0]

    print(f"RP ID hash (hex): {rp_id_hash.hex()}")
    print(f"Flags: {flags:08b}")
    print(f"Signature counter: {sign_count}")

    # Check if attested credential data flag is set (bit 6)
    if flags & 0x40:
        # Credential data present
        aaguid = authData[37:53]
        cred_id_len = struct.unpack('>H', authData[53:55])[0]
        cred_id = authData[55:55+cred_id_len]
        # The remaining bytes are the CBOR public key
        public_key_bytes = authData[55+cred_id_len:]
        public_key = cbor2.loads(public_key_bytes)

        print(f"AAGUID: {aaguid.hex()}")
        print(f"Credential ID: {cred_id.hex()}")
        print(f"Public Key: {public_key}")

    else:
        print("No attested credential data present in authData")

    return attestation

# Example usage:

## ACTUAL
attestation_b64 = input().strip()

attestation = parse_attestation_object(attestation_b64)
