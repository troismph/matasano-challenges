from challenge21 import MT19937
import time


MT = MT19937(0)
MTConfig = MT.config
LOW_MASK = (1 << MTConfig.w) - 1


def temper_right(y, s, k):
    return LOW_MASK & (y ^ ((y >> s) & k))


def temper_left(y, s, k):
    return LOW_MASK & (y ^ ((y << s) & k))


def translate(value):
    """
    Given an int value, translate into an array of binary digits.
    Index 0 as most significant digit. Padded to width according to MT19937 params.
    :param value: integer
    :return: an array of binary digits.
    """
    bs = bin(value & 0xFFFFFFFF)
    pad = [0] * (MTConfig.w - (len(bs) - 2))
    return pad + [int(x, 2) for x in bs[2:]]


def untranslate(valuestr):
    return int(''.join(map(str, valuestr)), 2)


def untemper_right(x, s, k):
    """
    Reverse function of temper_right
    :param x: result from temper_right
    :param s: shift distance
    :param k: binary AND parameter
    :return: untempered value
    """
    tk = translate(k)
    tx = translate(x)
    ty = [0] * MTConfig.w
    ty[0:s] = tx[0:s]
    for idx in range(s, MTConfig.w):
        ty[idx] = tx[idx] ^ (ty[idx - s] & tk[idx])
    return untranslate(ty)


def untemper_left(x, s, k):
    tk = translate(k)
    tx = translate(x)
    ty = [0] * MTConfig.w
    ty[-s:] = tx[-s:]
    for idx in range(MTConfig.w - s - 1, -1, -1):
        ty[idx] = tx[idx] ^ (ty[idx + s] & tk[idx])
    return untranslate(ty)


def temper(y):
    y = y ^ ((y >> MTConfig.u) & MTConfig.d)
    y = y ^ ((y >> MTConfig.s) & MTConfig.b)
    y = y ^ ((y << MTConfig.t) & MTConfig.c)
    y = y ^ (y >> MTConfig.l)

    return LOW_MASK & y


def temperhelp(y):
    y = temper_right(y, MTConfig.u, MTConfig.d)
    y = temper_right(y, MTConfig.s, MTConfig.b)
    y = temper_left(y, MTConfig.t, MTConfig.c)
    y = temper_right(y, MTConfig.l, 0xFFFFFFFF)

    return LOW_MASK & y


def untemper(x):
    x = untemper_right(x, MTConfig.l, 0xFFFFFFFF)
    x = untemper_left(x, MTConfig.t, MTConfig.c)
    x = untemper_right(x, MTConfig.s, MTConfig.b)
    x = untemper_right(x, MTConfig.u, MTConfig.d)
    return LOW_MASK & x


def test_temper(r=10000):
    MT.seed(int(time.time()))
    for i in range(r):
        y = MT.get_next()
        xa = temper(y)
        xb = temperhelp(y)
        if xa != xb:
            print "Failed y={y}, xa={xa}, xb={xb}".format(y=y, xa=xa, xb=xb)


def test_untemper(r=1000):
    MT.seed(int(time.time()))
    for i in range(r):
        y = MT.get_next()
        x = temper(y)
        yt = untemper(x)
        if y != yt:
            print "Failed y={y}, yt={yt}, x={x}".format(y=y, yt=yt, x=x)


def test_temper_left(r=1000):
    MT.seed(int(time.time()))
    for i in range(r):
        y = MT.get_next()
        s = MT.get_next() % 20 + 1
        k = MT.get_next()
        x = temper_left(y, s, k)
        yt = untemper_left(x, s, k)
        if yt != y:
            print "Failed y={y}, s={s}, k={k}, x={x}, yt={yt}".format(y=y, s=s, k=k, x=x, yt=yt)


def test_temper_right(r=1000):
    MT.seed(int(time.time()))
    for i in range(r):
        y = MT.get_next()
        s = MT.get_next() % 20 + 1
        k = MT.get_next()
        x = temper_right(y, s, k)
        yt = untemper_right(x, s, k)
        if yt != y:
            print "Failed y={y}, s={s}, k={k}, x={x}, yt={yt}".format(y=y, s=s, k=k, x=x, yt=yt)


def clone_mt(mt):
    """
    Clone MT19937 instance
    :param mt: MT19937 object, must be just-twisted
    :return: a cloned MT19937 object
    """
    mt_clone = MT19937(0)
    for idx in range(mt.config.n):
        x = mt.get_next()
        mt_clone.MT[idx] = untemper(x)
    result = True
    for idx in range(100):
        s = mt.get_next()
        t = mt_clone.get_next()
        if s != t:
            print "{pf}\t{s}:{t}".format(pf="Pass" if s == t else "Fail", s=s, t=t)
            result = False
    print "Pass" if result else ""


def run():
    mt = MT19937(int(time.time()))
    clone_mt(mt)


run()
