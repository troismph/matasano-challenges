#!/usr/bin/python

import unittest
from common.converts import unhex, b64encode, b64decode, fixed_xor, xor_cipher


def hex2b64(hexstr):
    return b64encode(unhex(hexstr))

class Set1(unittest.TestCase):

    def b64decode(self):
        si = "SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"
        so = unhex("49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d")
        to = b64decode(si)
        self.assertEqual(so, to)
        si = "SSBhbSBiaWchIEl0J3MgdGhlIHBpY3R1cmVzIHRoYXQgZ290IHNtYWxsLg=="
        so = bytearray("I am big! It's the pictures that got small.")
        to = b64decode(si)
        self.assertEqual(so, to)
        si = "SSdtIHRoZSBraW5nIG9mIHRoZSB3b3JsZCE="
        so = bytearray("I'm the king of the world!")
        to = b64decode(si)
        self.assertEqual(so, to)

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

    def challenge5(self):
        key = bytearray("ICE")
        si = bytearray("Burning 'em, if you ain't quick and nimble\nI go crazy when I hear a cymbal")
        so = unhex("0b3637272a2b2e63622c2e69692a23693a2a3c6324202d623d63343c2a26226324272765272a282b2f20430a652e2c652a3124333a653e2b2027630c692b20283165286326302e27282f")
        to = xor_cipher(si, key)
        self.assertEqual(so, to)

if __name__ == '__main__':
    unittest.main()
