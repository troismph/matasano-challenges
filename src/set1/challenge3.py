#!/usr/bin/python

from xor_cipher_eval import solve


def challenge3():
    results = solve(["1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736"])
    for x in results:
        print x[0], x[1], x[2]

challenge3()
