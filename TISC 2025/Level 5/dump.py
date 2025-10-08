#!/usr/bin/env python3
import codecs

def hexdump(b: bytes):
    for i in range(0, len(b), 16):
        chunk = b[i:i+16]
        hexpart = ' '.join(f'{c:02x}' for c in chunk)
        asciipart = ''.join(chr(c) if 32 <= c < 127 else '.' for c in chunk)
        print(f'{i:04x}: {hexpart:<48} {asciipart}')
    print()

# The raw bodies from your curls, converted to bytes with escapes decoded
req1 = codecs.decode(r":æñ\\\u0083\u0084²\u001e\u0001\u0000\u0000\u0000\u0081\u0000\u0000\u0000\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0084ò\u008a[", 'unicode_escape').encode('latin1')
req2 = codecs.decode(r":æñ\\\u0083\u0084²\u001e\u0002\u0000\u0000\u0000±\u0000\u0000\u0000\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0084ò\u008a[\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u00007û\u008a[", 'unicode_escape').encode('latin1')
req3 = codecs.decode(r":æñ\\\u0083\u0084²\u001e\u0003\u0000\u0000\u0000s\u0000\u0000\u0000\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0084ò\u008a[\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u00007û\u008a[\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000Çý\u008a[", 'unicode_escape').encode('latin1')
req4 = codecs.decode(r":æñ\\\u0083\u0084²\u001e\u0004\u0000\u0000\u0000$\u0000\u0000\u0000\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000\u0084ò\u008a[\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u00007û\u008a[\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000Çý\u008a[\u0004\u0000\u0000\u0000\u0000\u0000\u0000\u0000Tþ\u008a[", 'unicode_escape').encode('latin1')

for i, req in enumerate([req1, req2, req3, req4], 1):
    print(f"--- Request {i} ---")
    hexdump(req)
