#!/usr/bin/python

import unittest
from converts import unhex, b64encode


class TestConverts(unittest.TestCase):

    def test_unhex(self):
        si = '7abcdef9876543210'
        so = b'\x07\xab\xcd\xef\x98\x76\x54\x32\x10'
        to = unhex(si)
        self.assertEqual(so, to)

    def test_b64encode(self):
        si = "I'm gonna make him an offer he can't refuse."
        so = "SSdtIGdvbm5hIG1ha2UgaGltIGFuIG9mZmVyIGhlIGNhbid0IHJlZnVzZS4="
        to = b64encode(si)
        self.assertEqual(so, to)
        si = "May the Force be with you"
        so = "TWF5IHRoZSBGb3JjZSBiZSB3aXRoIHlvdQ=="
        to = b64encode(si)
        self.assertEqual(so, to)
        si = "You talking to me?"
        so = "WW91IHRhbGtpbmcgdG8gbWU/"
        to = b64encode(si)
        self.assertEqual(so, to)

if __name__ == '__main__':
    unittest.main()
