#!/usr/bin/python

from xor_cipher_eval import solve
from converts import unhex


def challenge3():
    cipher = unhex("1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736")
    results = solve([cipher])
    for x in results:
        print x[0], x[1], x[2], x[3]

challenge3()
