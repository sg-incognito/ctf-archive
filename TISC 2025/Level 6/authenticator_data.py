import base64
import struct

def b64url_decode(data: str) -> bytes:
    data += '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data)

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def parse_flags(flag_byte: int) -> dict:
    # Spec bits (bit numbering from LSB = bit0)
    return {
        "UP": bool(flag_byte & 0x01),   # User Present
        "RFU1": bool(flag_byte & 0x02), # reserved
        "UV": bool(flag_byte & 0x04),   # User Verified
        "RFU2": bool(flag_byte & 0x08), # reserved
        "RFU3": bool(flag_byte & 0x10), # reserved
        "RFU4": bool(flag_byte & 0x20), # reserved
        "AT": bool(flag_byte & 0x40),   # Attested Credential Data present
        "ED": bool(flag_byte & 0x80),   # Extension Data present
    }

def flags_to_byte(flags: dict) -> int:
    b = 0
    if flags.get("UP"): b |= 0x01
    if flags.get("RFU1"): b |= 0x02
    if flags.get("UV"): b |= 0x04
    if flags.get("RFU2"): b |= 0x08
    if flags.get("RFU3"): b |= 0x10
    if flags.get("RFU4"): b |= 0x20
    if flags.get("AT"): b |= 0x40
    if flags.get("ED"): b |= 0x80
    return b

def parse_authenticator_data(b64authdata: str):
    data = b64url_decode(b64authdata)
    rp_id_hash = data[:32]
    flag_byte = data[32]
    sign_count = struct.unpack(">I", data[33:37])[0]
    rest = data[37:]
    flags = parse_flags(flag_byte)
    return {
        "rpIdHash": rp_id_hash,
        "flagByte": flag_byte,
        "flags": flags,
        "signCount": sign_count,
        "rest": rest
    }

def rebuild_authenticator_data(parsed: dict) -> str:
    flag_byte = flags_to_byte(parsed["flags"])
    out = parsed["rpIdHash"] + struct.pack("B", flag_byte) + struct.pack(">I", parsed["signCount"]) + parsed["rest"]
    return b64url_encode(out)

# Example usage:
authdata_b64 = input("Base64url authenticatorData: ")
parsed = parse_authenticator_data(authdata_b64)
print("rpIdHash:", parsed["rpIdHash"].hex())
print("signCount:", parsed["signCount"])
print("Flags breakdown:")
for k,v in parsed["flags"].items():
    print(f"  {k}: {v}")

# Toggle a flag:
flag_to_toggle = input("Flag to toggle (UP, UV, AT, ED or leave blank): ")
if flag_to_toggle in parsed["flags"]:
    parsed["flags"][flag_to_toggle] = not parsed["flags"][flag_to_toggle]

new_b64 = rebuild_authenticator_data(parsed)
print("Modified authenticatorData (base64url):", new_b64)
