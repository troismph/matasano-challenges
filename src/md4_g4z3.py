"""
MD4 implementation by g4z3
"""
import struct


def F(x, y, z):
    return (x & y) | ((~x) & z)


def G(x, y, z):
    return (x & y) | (x & z) | (y & z)


def H(x, y, z):
    return x ^ y ^ z


def lrot(x, n):
    return ((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)


def rrot_list(x, n):
    nn = n % len(x)
    return x[-nn:] + x[:-nn]


def phy0(h, m, s):
    t = (h[0] + F(h[1], h[2], h[3]) + m) % (2 ** 32)
    return lrot(t, s)


def phy1(h, m, s):
    t = (h[0] + G(h[1], h[2], h[3]) + m + 0x5a827999) % (2 ** 32)
    return lrot(t, s)


def phy2(h, m, s):
    t = (h[0] + H(h[1], h[2], h[3]) + m + 0x6ed9eba1) % (2 ** 32)
    return lrot(t, s)


INIT_STATE = (0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476)


class MD4(object):
    def __init__(self, init_state=INIT_STATE):
        self.h = list(init_state)
        self.r3_idx = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)
        self.phy = (phy0, phy1, phy2)
        self.lrot_off = ((3, 7, 11, 19), (3, 5, 9, 13), (3, 9, 11, 15))
        self.trailing = ''
        self.msg_len = 0

    def _word_idx(self, r, s):
        if r == 0:
            return s
        elif r == 1:
            return (s % 4) * 4 + (s // 4)
        else:
            return self.r3_idx[s]

    def _add_block(self, m):
        h = list(self.h)
        blk = struct.unpack('<16I', m)
        for r in range(3):
            for s in range(16):
                state_idx = (16 - s) % 4
                word_idx = self._word_idx(r, s)
                lrot_offset = self.lrot_off[r][s % 4]
                h_rot = rrot_list(h, s % 4)
                h[state_idx] = self.phy[r](h_rot, blk[word_idx], lrot_offset)
        for i in range(4):
            self.h[i] = (self.h[i] + h[i]) % (2 ** 32)

    def update(self, m):
        self.msg_len += len(m)
        aug_m = self.trailing + m
        len_aug = len(aug_m)
        trailing_len = len_aug % 64
        self.trailing = aug_m[-trailing_len:]
        for x in range(0, len_aug - trailing_len, 64):
            self._add_block(aug_m[x: x + 64])

    def digest(self):
        self.update('\x80' + '\x00' * ((55 - self.msg_len) % 64) + struct.pack('Q', self.msg_len * 8))
        h = struct.pack('<4I', *self.h)
        return h


def test():
    cases = (
        ("", "31d6cfe0d16ae931b73c59d7e0c089c0"),
        ("a", "bde52cb31de33e46245e05fbdbd6fb24"),
        ("abc", "a448017aaf21d8525fc10ae87aa6729d"),
        ("message digest", "d9130a8164549fe818874806e1c7014b"),
        ("abcdefghijklmnopqrstuvwxyz", "d79e1c308aa5bbcdeea8ed63df412da9"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", "043f8582f241db351ce627e153e7f0e4"),
        ("12345678901234567890123456789012345678901234567890123456789012345678901234567890",
         "e33b4ddc9c38f2199c3e7b164fcc0536")
    )
    for t, h in cases:
        md = MD4()
        md.update(t)
        d = md.digest()
        if d == h.decode("hex"):
            print "pass"
        else:
            print "FAIL: {0}: {1}\n\texpected: {2}".format(t, d.encode("hex"), h)
