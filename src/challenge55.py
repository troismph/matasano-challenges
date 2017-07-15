import md4_g4z3
import os
import struct
import random
from converts import ez_hash


def set_bit(x, ops):
    for n, b in ops:
        assert n < 32, 'Value error'
        assert b == 0 or b == 1, 'Value error'
        if b == 1:
            x = x | (1 << n)
        else:
            x = x & (~(1 << n) & 0xffffffff)
    return x


def get_bit(x, n):
    assert n < 32, 'Value error'
    return 1 if x & (1 << n) else 0


def test_bit_op():
    x = 0b101010101110
    assert get_bit(x, 0) == 0
    assert get_bit(x, 1) == 1
    assert get_bit(x, 4) == 0
    assert get_bit(x, 5) == 1
    assert get_bit(x, 25) == 0
    assert set_bit(x, [[0, 1]]) == 0b101010101111
    assert set_bit(x, [[1, 1]]) == 0b101010101110
    assert set_bit(x, [[2, 0], [9, 0]]) == 0b100010101010
    print 'Pass'


def getter(name, seq, n, t):
    """
    A helper function to retrieve bit value of
     name_(seq,n)
     according to notations of Table 6, Wang05
    :param name: a, b, c, or d
    :param seq: 0, 1, 2, ...
    :param n: bit position, starting from 1
    :param t: a list of all previous a, b, c, d, ...
    :return: bit value
    """
    if seq == 0:
        x = t[ord(name) - ord('a')]
    else:
        x = t[seq * 4 + (4 - (ord(name) - ord('a'))) % 4]
    return get_bit(x, n - 1)


def test_getter():
    t = [0b10101010, 0b01010101, 0b00001111, 0b11110000,
         0b11100011, 0b00011100, 0b00110011, 0b11001100,
         0b11100001, 0b10000010, 0b00111101, 0b11011000]
    assert getter('a', 0, 1, t) == 0
    assert getter('a', 0, 4, t) == 1
    assert getter('c', 0, 5, t) == 0
    assert getter('a', 1, 6, t) == 1
    assert getter('d', 1, 7, t) == 0
    assert getter('b', 2, 8, t) == 1
    print 'Pass'


def setter(x, ops):
    """
    Helper function to set bit value according to
    notations of Table 6, Wang05 
    """
    ops_ = [(n - 1, b) for n, b in ops]
    return set_bit(x, ops_)


def correct_state(s, v, t):
    """
    Correct hash states according to Table 6 in Wang's paper
    :param s: step
    :param v: value to be corrected
    :param t: results from previous steps
    :return: value after correction
    """
    if s == 0:
        ops = [(7, getter('b', 0, 7, t))]
    elif s == 1:
        ops = [(7, 0),
               (8, getter('a', 1, 8, t)),
               (11, getter('a', 1, 11, t))]
        return setter(v, ops)
    elif s == 2:
        ops = [(7, 1),
               (8, 1),
               (11, 0),
               (26, getter('d', 1, 26, t))]
    elif s == 3:
        ops = [(7, 1),
               (8, 0),
               (11, 0),
               (26, 0)]
    elif s == 4:
        ops = [(8, 1),
               (11, 1),
               (26, 0),
               (14, getter('b', 1, 14, t))]
    elif s == 5:
        ops = [(14, 0),
               (19, getter('a', 2, 19, t)),
               (20, getter('a', 2, 20, t)),
               (21, getter('a', 2, 21, t)),
               (22, getter('a', 2, 22, t)),
               (26, 1)]
    elif s == 6:
        ops = [(13, getter('d', 2, 13, t)),
               (14, 0),
               (15, getter('d', 2, 15, t)),
               (19, 0),
               (20, 0),
               (21, 1),
               (22, 0)]
    elif s == 7:
        ops = [(13, 1),
               (14, 1),
               (15, 0),
               (17, getter('c', 2, 17, t)),
               (19, 0),
               (20, 0),
               (21, 0),
               (22, 0)]
    elif s == 8:
        ops = [(13, 1),
               (14, 1),
               (15, 1),
               (17, 0),
               (19, 0),
               (20, 0),
               (21, 0),
               (22, 1),
               (23, getter('b', 2, 23, t)),
               (26, getter('b', 2, 26, t))]
    elif s == 9:
        ops = [(13, 1),
               (14, 1),
               (15, 1),
               (17, 0),
               (20, 0),
               (21, 1),
               (22, 1),
               (23, 0),
               (26, 1),
               (30, getter('a', 3, 30, t))]
    elif s == 10:
        ops = [(17, 1),
               (20, 0),
               (21, 0),
               (22, 0),
               (23, 0),
               (26, 0),
               (30, 1),
               (32, getter('d', 3, 32, t))]
    elif s == 11:
        ops = [(20, 0),
               (21, 1),
               (22, 1),
               (23, getter('c', 3, 23, t)),
               (26, 1),
               (30, 0),
               (32, 0)]
    elif s == 12:
        ops = [(23, 0),
               (26, 0),
               (27, getter('b', 3, 27, t)),
               (29, getter('b', 3, 29, t)),
               (30, 1),
               (32, 0)]
    elif s == 13:
        ops = [(23, 0),
               (26, 0),
               (27, 1),
               (29, 1),
               (30, 0),
               (32, 1)]
    elif s == 14:
        ops = [(19, getter('d', 4, 19, t)),
               (23, 1),
               (26, 1),
               (27, 0),
               (29, 0),
               (30, 0)]
    elif s == 15:
        ops = [(19, 0),
               (26, 1),
               (27, 1),
               (29, 1),
               (30, 0)]
    elif s == 16:
        ops = [(19, getter('c', 4, 19, t)),
               (26, 1),
               (27, 0),
               (29, 1),
               (32, 1)]
    elif s == 17:
        ops = [(19, getter('a', 5, 19, t)),
               (26, getter('b', 4, 26, t)),
               (27, getter('b', 4, 27, t)),
               (29, getter('b', 4, 29, t)),
               (32, getter('b', 4, 32, t))]
    elif s == 18:
        ops = [(26, getter('d', 5, 26, t)),
               (27, getter('d', 5, 27, t)),
               (29, getter('d', 5, 29, t)),
               (30, getter('d', 5, 30, t)),
               (32, getter('d', 5, 32, t))]
    elif s == 19:
        ops = [(29, getter('c', 5, 29, t)),
               (30, 1),
               (32, 0)]
    elif s == 20:
        ops = [(29, 1),
               (32, 1)]
    elif s == 21:
        ops = [(29, getter('b', 5, 29, t))]
    elif s == 22:
        ops = [(29, getter('d', 6, 29, t)),
               (30, 1 - getter('d', 6, 30, t)),
               (32, 1 - getter('d', 6, 32, t))]
    elif s == 35:
        ops = [(32, 1)]
    elif s == 36:
        ops = [(32, 1)]
    else:
        ops = []

    return setter(v, ops)


def rrot(x, n):
    nn = n % 32
    return ((x >> nn) & 0xffffffff) | ((x << (32 - nn)) & 0xffffffff)


# Reverse function of phy0, phy1, and phy2 in md4_g4z3
# Given
# phy(h, m, s) = x,
# this function returns a special m_, such that
# phy(h, m_, s) = y
# :param h: the 4-int hash state, input of phy0
# :param r: the left rotate offset in phy0
# :param y: the 1-int hash state that we desire for phy0
# :return: a special message int
def rev_phy0(h, r, y):
    t = rrot(y, r)
    m = (t - h[0] - md4_g4z3.F(h[1], h[2], h[3])) % (2 ** 32)
    return m


def rev_phy1(h, r, y):
    t = rrot(y, r)
    m = (t - h[0] - md4_g4z3.G(h[1], h[2], h[3]) - 0x5a827999) % (2 ** 32)
    return m


def rev_phy2(h, r, y):
    t = rrot(y, r)
    m = (t - h[0] - md4_g4z3.H(h[1], h[2], h[3]) - 0x6ed9eba1) % (2 ** 32)
    return m


def test_rev_phy():
    n_round = 1000
    for x in range(n_round):
        h = map(lambda z: random.randrange(1 << 32), range(4))
        m = random.randrange(1 << 32)
        s = random.randrange(32)
        h_next = md4_g4z3.phy0(h, m, s)
        m_ = rev_phy0(h, s, h_next)
        assert m == m_, 'Failed'
        h_next = md4_g4z3.phy1(h, m, s)
        m_ = rev_phy1(h, s, h_next)
        assert m == m_, 'Failed'
        h_next = md4_g4z3.phy2(h, m, s)
        m_ = rev_phy2(h, s, h_next)
        assert m == m_, 'Failed'
    print "Pass after {n} rounds".format(n=n_round)


rev_phy_list = [rev_phy0, rev_phy1, rev_phy2]


def rev_phy(s, h, r, y):
    """
    A wrapper for phy0, phy1, and phy2
    """
    idx = (s % 48) / 16
    return rev_phy_list[idx](h, r, y)


class Manipulator(object):
    def __init__(self):
        self._m = None
        self._h = None
        self._trace = list(md4_g4z3.INIT_STATE)
        self.phy = (md4_g4z3.phy0, md4_g4z3.phy1, md4_g4z3.phy2)

    def set_m(self, m):
        self._m = m

    def get_m(self):
        return self._m

    def set_h(self, h):
        self._h = h

    def go(self, r, w_idx, h_idx, h_next, h_rot, lrot_offset):
        step = len(self._trace) - 4
        # if step >= 16:
        #     self._trace.append(h_next)
        #     self._h[h_idx] = h_next
        #     return
        h_c = correct_state(step, h_next, self._trace)
        m_c = rev_phy(step, h_rot, lrot_offset, h_c)

        # verify m_c, debug only
        # h_v = self.phy[r](h_rot, m_c, lrot_offset)
        # assert h_c == h_v, 'Logic error'

        self._m[w_idx] = m_c
        self._trace.append(h_c)
        self._h[h_idx] = h_c


def compose(m):
    manipulator = Manipulator()
    md4 = md4_g4z3.MD4(manipulator)
    md4.update(m)
    m_in = struct.unpack('<16I', m)
    m_ = manipulator.get_m()
    assert m_ != m_in, 'Logic error'
    return m_


def get_companion(m):
    # check viability
    # if not (get_bit(m[1], 31) == 0
    #         and get_bit(m[2], 31) == 0
    #         and get_bit(m[2], 28) == 1
    #         and get_bit(m[12], 16) == 1):
    #     return None
    m_ = list(m)
    m_[1] = set_bit(m_[1], [(31, 1)])
    m_[2] = set_bit(m_[2], [(31, 1), (28, 0)])
    m_[12] = set_bit(m_[12], [(16, 0)])
    return m_


def get_random_msg():
    return os.urandom(64)
    # base = os.urandom(64)
    # m = list(struct.unpack('<16I', base))
    # m[1] = set_bit(m[1], [(31, 0)])
    # m[2] = set_bit(m[2], [(31, 0), (28, 1)])
    # m[12] = set_bit(m[12], [(16, 1)])
    # return struct.pack('<16I', *m)


def find_collision():
    wasted = 0
    concord_max = 0
    i = 0
    while True:
        if i & 0xfff == 0xfff:
            print 'Trying round {x:x}, wasted {w:x}, effective {e:x}'.format(x=i, w=wasted, e=i-wasted)
        base = get_random_msg()
        m_list = compose(base)
        m_list_ = get_companion(m_list)
        if m_list_ is None or m_list == m_list_:
            wasted += 1
            continue
        m = struct.pack('<16I', *m_list)
        m_ = struct.pack('<16I', *m_list_)
        md4 = md4_g4z3.MD4()
        md4.update(m)
        hash_m = md4.digest()
        md4_ = md4_g4z3.MD4()
        md4_.update(m_)
        hash_m_ = md4_.digest()
        # trace = md4.get_trace()
        # trace_ = md4_.get_trace()
        # concord = 0
        # z = zip(trace, trace_)
        # for t, t_ in z:
        #     if t == t_:
        #         concord += 1
        #     else:
        #         break
        # if concord > concord_max:
        #     print i, concord, '#' * concord
        #     concord_max = concord
        concord = 0
        # for t, t_ in z[21:25]:
        #     if t == t_:
        #         concord += 1
        # if concord > 0:
        #     print i, '=' * concord
        # concord = 0
        # for t, t_ in z[37:41]:
        #     if t == t_:
        #         concord += 1
        # if concord > 0:
        #     print i, '+' * concord
        # hash_m = ez_hash(md4_g4z3.MD4, m)
        # hash_m_ = ez_hash(md4_g4z3.MD4, m_)
        if hash_m == hash_m_:
            print "Found with hash={h}".format(h=hash_m.encode('hex'))
            print "{a}\n{b}".format(a=m.encode('hex'), b=m_.encode('hex'))
            if m == m_:
                print 'wtf!!!'
                print m_list
                print m_list_
            break
        i += 1


def test_manipulated_md4():
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
    manipulator = Manipulator()
    for t, h in cases:
        md = md4_g4z3.MD4(manipulator)
        md.update(t)
        d = md.digest()
        if d == h.decode("hex"):
            print "pass"
        else:
            print "FAIL: {0}: {1}\n\texpected: {2}".format(t, d.encode("hex"), h)


if __name__ == "__main__":
    find_collision()
