#!/usr/bin/python

import unittest
from converts import unhex, b64encode, b64decode, encrypt_aes_128_ecb, decrypt_aes_128_ecb


class TestConverts(unittest.TestCase):

    def test_b64decode(self):
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

    def test_aes_128_ecb(self):
        key = bytearray("YELLOW SUBMARINE")
        si = bytearray("I'll give him an offer he can't refuse.")
        eo = encrypt_aes_128_ecb(si, key)
        do = decrypt_aes_128_ecb(eo, key)
        self.assertEqual(si, do)

if __name__ == "__main__":
    unittest.main()
