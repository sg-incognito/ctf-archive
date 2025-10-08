ciphertext = "aWnegWRi18LwQXnXgxqEF}blhs6G2cVU_hOz3BEM2{fjTb4BI4VEovv8kISWcks4"

def rot_rot_decrypt(cipher, key):
    charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}_"
    shift = key
    plain = ""
    for char in cipher:
        index = charset.index(char)
        plain += charset[(index - shift) % len(charset)]  # subtract shift
        shift = (shift + key) % len(charset)
    return plain

charset_len = len("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}_")

for k in range(1, charset_len):
    try:
        candidate = rot_rot_decrypt(ciphertext, k)
        if candidate.startswith("TISC{"):
            print(f"Found key {k}: {candidate}")
            break  # stop once found
    except ValueError:
        continue

