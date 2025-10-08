import base64, json

def b64url_decode(data: str) -> bytes:
    # normalise to correct padding
    data += "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data)

# paste your values here
client_data_json_b64 = "eyJ0eXBlIjoid2ViYXV0aG4uY3JlYXRlIiwiY2hhbGxlbmdlIjoiUE0tTDZoSjZaekpQX3JxeHRWWlpBcEJtb1dfTGFqMzJJdDdVejJTT1FtUSIsIm9yaWdpbiI6Imh0dHBzOi8vcGFzc2tleS5jaGFscy50aXNjMjUuY3RmLnNnIiwiY3Jvc3NPcmlnaW4iOmZhbHNlLCJvdGhlcl9rZXlzX2Nhbl9iZV9hZGRlZF9oZXJlIjoiZG8gbm90IGNvbXBhcmUgY2xpZW50RGF0YUpTT04gYWdhaW5zdCBhIHRlbXBsYXRlLiBTZWUgaHR0cHM6Ly9nb28uZ2wveWFiUGV4In0"
attestation_object_b64 = "o2NmbXRkbm9uZWdhdHRTdG10oGhhdXRoRGF0YViUxwgw9416p0vIny4ypoanXkcXJdFxRlkGzC1FwfdONH9dAAAAAOqbjWZNAR0hPOS2tIy1ddQAEAMGz4IcgdYGe4LLkWA0laalAQIDJiABIVggJImqdqPmJZ75wdpeylF7CoU7YAZEs864T8ldmB4HOa4iWCDbCFC3_2JUk0Kc9hVBExQPfXyoNxBx_G-OK_fdufYXcg"

# decode client_data_json
client_data = json.loads(b64url_decode(client_data_json_b64))
print("Client data JSON:")
print(json.dumps(client_data, indent=2))

# decode attestation_object (requires CBOR decoder)
import cbor2
attestation = cbor2.loads(b64url_decode(attestation_object_b64))
print("\nAttestation object (top-level):")
print(json.dumps({k: (v if not isinstance(v, bytes) else v.hex()) for k,v in attestation.items()}, indent=2))
