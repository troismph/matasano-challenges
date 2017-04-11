#!/bin/python


class MT19937:
    class Config:
        def __init__(self, w, n, m, r, a, u, d, s, b, t, c, l, f):
            self.w = w
            self.n = n
            self.m = m
            self.r = r
            self.a = a
            self.u = u
            self.d = d
            self.s = s
            self.b = b
            self.t = t
            self.c = c
            self.l = l
            self.f = f

    def __init__(self, seed):
        """ default initializer for 32-bit MT19937
        """
        w = 32
        n = 624
        m = 397
        r = 31
        a = 0x9908b0df
        u = 11
        d = 0xffffffff
        s = 7
        b = 0x9d2c5680
        t = 15
        c = 0xefc60000
        l = 18
        f = 1812433253
        self.config = self.Config(w, n, m, r, a, u, d, s, b, t, c, l, f)
        self.MT = [0] * self.config.n
        self.index = self.config.n + 1
        # possible signed/unsigned problem with bit ops?
        self.lower_mask = (1 << self.config.r) - 1
        self.upper_mask = ((1 << self.config.w) - 1) & (~self.lower_mask)
        self.lowest_w_mask = (1 << self.config.w) - 1
        self.seed(seed)

    def seed(self, seed):
        self.index = self.config.n
        self.MT[0] = seed
        for i in xrange(1, self.config.n):
            self.MT[i] = self.lowest_w_mask & (i + self.config.f * (self.MT[i-1] ^ (self.MT[i-1] >> (self.config.w - 2))))

    def get_next(self):
        if self.index >= self.config.n:
            if self.index > self.config.n:
                raise "Generator unseeded"
            self.twist()

        y = self.MT[self.index]
        y = y ^ ((y >> self.config.u) & self.config.d)
        y = y ^ ((y >> self.config.s) & self.config.b)
        y = y ^ ((y << self.config.t) & self.config.c)
        y = y ^ (y >> self.config.l)

        self.index = self.index + 1
        return self.lowest_w_mask & y

    def twist(self):
        for i in xrange(self.config.n):
            x = (self.MT[i] & self.upper_mask) + (self.MT[(i+1) % self.config.n] & self.lower_mask)
            xa = x >> 1
            if x % 2 != 0:
                xa = xa ^ self.config.a
            self.MT[i] = self.MT[(i + self.config.m) % self.config.n] ^ xa
        self.index = 0


def _int32(x):
    # Get the 32 least significant bits.
    return int(0xFFFFFFFF & x)


class MT19937Ref:

    def __init__(self, seed):
        # Initialize the index to 0
        self.index = 624
        self.mt = [0] * 624
        self.mt[0] = seed  # Initialize the initial state to the seed
        for i in range(1, 624):
            self.mt[i] = _int32(
                1812433253 * (self.mt[i - 1] ^ self.mt[i - 1] >> 30) + i)

    def extract_number(self):
        if self.index >= 624:
            self.twist()

        y = self.mt[self.index]

        # Right shift by 11 bits
        y = y ^ y >> 11
        # Shift y left by 7 and take the bitwise and of 2636928640
        y = y ^ y << 7 & 2636928640
        # Shift y left by 15 and take the bitwise and of y and 4022730752
        y = y ^ y << 15 & 4022730752
        # Right shift by 18 bits
        y = y ^ y >> 18

        self.index = self.index + 1

        return _int32(y)

    def twist(self):
        for i in range(624):
            # Get the most significant bit and add it to the less significant
            # bits of the next number
            y = _int32((self.mt[i] & 0x80000000) +
                       (self.mt[(i + 1) % 624] & 0x7fffffff))
            self.mt[i] = self.mt[(i + 397) % 624] ^ y >> 1

            if y % 2 != 0:
                self.mt[i] = self.mt[i] ^ 0x9908b0df
        self.index = 0
