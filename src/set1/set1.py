#!/usr/bin/python

import unittest
from common.converts import unhex, b64encode


class MatasanoSet1(unittest.TestCase):

    def challenge1(self):
        si = "49276d206b696c6c696e6720796f757220627261696e206c696b65206120706f69736f6e6f7573206d757368726f6f6d"
        so = "SSdtIGtpbGxpbmcgeW91ciBicmFpbiBsaWtlIGEgcG9pc29ub3VzIG11c2hyb29t"
        to = b64encode(unhex(si))
        self.assertEqual(so, to)


if __name__ == '__main__':
    unittest.main()
