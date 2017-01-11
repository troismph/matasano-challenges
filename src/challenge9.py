#!/usr/bin/python

from converts import pkcs7_pad


def run():
    buf = bytearray("YELLOW SUBMARINE")
    shouldbe = bytearray("YELLOW SUBMARINE\x04\x04\x04\x04")
    pkcs7_pad(buf, 20)
    if buf != shouldbe:
        raise AssertionError("Challenge 9 fails")
    else:
        print "Pass"

run()
