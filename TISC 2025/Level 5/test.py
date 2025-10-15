#!/usr/bin/env python3
import struct
import binascii
import requests  # only if you want to send automatically

# --- 1. Header / magic sequence (from your capture)
header = bytes([
    0x6e, 0xb2, 0x8d, 0x3c, 0xcd, 0x03, 0xdc, 0xfe
])

# --- 2. Payload fields you want to send.
# Replace these numbers with the little-endian ints that match the baseline.
# Each entry is a 32-bit unsigned integer (<I).
fields = [
    2,           # e.g. record id
    0x6d,        # some value
    4,           # another value
    0,           # padding
    0x5a5bf11c,  # just an example, your checksum/constant
    4,
    0,
    0x5a5bf373,  # second checksum/constant
]

# Pack into little endian bytes
payload = b''.join(struct.pack('<I', x) for x in fields)

# Final body
body = header + payload

# --- 3. Hexdump for verification
def hexdump(b):
    for i in range(0, len(b), 16):
        chunk = b[i:i+16]
        hexpart = ' '.join(f'{c:02x}' for c in chunk)
        asciipart = ''.join(chr(c) if 32 <= c < 127 else '.' for c in chunk)
        print(f'{i:04x}: {hexpart:<48} {asciipart}')

hexdump(body)

# --- 4. Optionally send to the challenge
# url = 'http://chals.tisc25.ctf.sg:57190/?t=1758157599603'
# headers = {
#     'Accept': '*/*',
#     'H': str(len(body)),
#     'R': 'application/octet-stream'
# }
# r = requests.post(url, headers=headers, data=body)
# print(r.status_code, r.content)

"""

0000: 6e b2 8d 3c cd 03 dc fe 01 00 00 00 19 00 00 00  n..<............
0010: 04 00 00 00 00 00 00 00 1c f1 5b 5a              ..........[Z


0000: 6e b2 8d 3c cd 03 dc fe 02 00 00 00 6d 00 00 00  n..<........m...
0010: 04 00 00 00 00 00 00 00 1c f1 5b 5a 04 00 00 00  ..........[Z....
0020: 00 00 00 00 73 f3 5b 5a                          ....s.[Z




"""