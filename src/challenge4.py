#!/usr/bin/python

from xor_cipher_eval import solve
from converts import unhex


def challenge4():
    with open('4.txt') as f:
        arr_cipherhex = [bytearray(unhex(x.rstrip())) for x in f]
    results = solve(arr_cipherhex)
    for x in results[:50]:
        print x[0], x[1], x[2], x[3]

challenge4()
