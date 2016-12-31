#!/usr/bin/python

import unittest
from converts import unhex


class TestHex(unittest.TestCase):

    def test_unhex(self):
        si = '7abcdef9876543210'
        so = b'\x07\xab\xcd\xef\x98\x76\x54\x32\x10'
        to = unhex(si)
        self.assertEqual(so, to)

if __name__ == '__main__':
    unittest.main()
