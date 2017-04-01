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

    def __init__(self, w, n, m, r, a, u, d, s, b, t, c, l, f):
        self.config = self.Config(w, n, m, r, a, u, d, s, b, t, c, l, f)
        self.MT = [0] * self.config.n
        self.index = self.config.n + 1
        # possible signed/unsigned problem with bit ops?
        self.lower_mask = (1 << self.config.r) - 1
        self.upper_mask = ((1 << self.config.w) - 1) & (~self.lower_mask)
        self.lowest_w_mask = (1 << self.config.w) - 1

    def seed(self, seed):
        self.index = self.config.n
        self.MT[0] = seed
        for i in xrange(1, self.config.n):
            self.MT[i] = self.lowest_w_mask & (i + self.config.f * self.MT[i-1] ^ (self.MT[i-1] >> (self.config.w - 1)))

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



