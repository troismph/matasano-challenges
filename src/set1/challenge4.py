#!/usr/bin/python

from xor_cipher_eval import solve


def challenge4():
    with open('set1/4.txt') as f:
        arr_cipherhex = [x.rstrip() for x in f]
    results = solve(arr_cipherhex)
    for x in results[-20:]:
        print x[0], x[1], x[2], x[3]

challenge4()
