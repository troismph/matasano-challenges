#!/bin/python

from converts import decrypt_aes_128_cbc, b64decode


def run():
    with open("10.txt") as f:
        cipher = b64decode(f.read().replace('\n', ''))
    key = bytearray("YELLOW SUBMARINE")
    iv = bytearray(16)
    plain = decrypt_aes_128_cbc(cipher, key, iv)
    print str(plain)

run()

