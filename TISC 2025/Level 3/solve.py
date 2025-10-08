#!/usr/bin/env python3
import re
import struct

input_file = "rotary-precision.txt"
dump_file = "floats_dump.bin"

# regex to match floats in scientific notation e.g. 1.23e-45 or -9.8E+10
sci_float_re = re.compile(r'[-+]?\d+\.\d+[eE][-+]?\d+')

floats_found = []

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        # find all sci-notation floats in the line
        matches = sci_float_re.findall(line)
        if matches:  # if there are any, print the line (like grep would)
            # print(line.rstrip())  # show full line on screen
            for m in matches:
                floats_found.append(float(m))

# write as little-endian 32-bit floats to a binary file
with open(dump_file, "wb") as out:
    for num in floats_found:
        out.write(struct.pack("<f", num))  # '<f' = little-endian float32

print(f"\nExtracted {len(floats_found)} floats from '{input_file}'")
print(f"Wrote raw 32-bit float bytes to '{dump_file}'")

