#!/usr/bin/python
from converts import decrypt_aes_128_ecb, b64decode


def run():
    with open("7.txt") as f:
        cipher = str(b64decode(f.read().replace('\n', '')))
    key = "YELLOW SUBMARINE"
    plain = decrypt_aes_128_ecb(cipher, key)
    print plain

run()
