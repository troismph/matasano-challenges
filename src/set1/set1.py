#!/usr/bin/python

import unittest
from common.converts import unhex, b64encode


def hex2b64(hexstr):
    return b64encode(unhex(hexstr))

def fixed_xor(buffer_a, buffer_b):
    assert(len(buffer_a) == len(buffer_b))
    buffer_c = bytearray(len(buffer_a))
    for i in range(len(buffer_a)):
        buffer_c[i] = buffer_a[i] ^ buffer_b[i]
    return buffer_c

class MatasanoSet1(unittest.TestCase):

    def challenge1(self):
        si = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
        so = "SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"
        to = hex2b64(si)
        self.assertEqual(so, to)

    def challenge2(self):
        ia = unhex("1c0111001f010100061a024b53535009181c")
        ib = unhex("686974207468652062756c6c277320657965")
        ic = unhex("746865206b696420646f6e277420706c6179")
        tc = fixed_xor(ia, ib)
        self.assertEqual(ic, tc)

if __name__ == '__main__':
    unittest.main()
