"""
MD4 implementation by g4z3
"""


def F(x, y, z):
    return (x & y) | ((~x) & z)


def G(x, y, z):
    return (x & y) | (x & z) | (y & z)


def H(x, y, z):
    return x ^ y ^ z


def lrot(x, n):
    return ((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)


def phy0(a, b, c, d, m, s):
    pass
