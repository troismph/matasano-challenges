#!/usr/bin/python

from converts import unhex, fixed_xor


def challenge2():
    ia = unhex("1c0111001f010100061a024b53535009181c")
    ib = unhex("686974207468652062756c6c277320657965")
    ic = unhex("746865206b696420646f6e277420706c6179")
    tc = fixed_xor(ia, ib)
    if ic != tc:
        raise "Challenge 2 fail"
    else:
        print "Pass"

challenge2()
