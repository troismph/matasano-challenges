def mod_exp(b, e, m):
    if m == 1:
        return 0
    ret = 1
    b = b % m
    while e > 0:
        if e % 2 == 1:
            ret = (ret * b) % m
        e = e >> 1
        b = (b * b) % m
    return ret


def mod_mult(a, b, m):
    return (a * b) % m


def mod_add(a, b, m):
    return (a + b) % m


def test_mod_exp():
    cases = [
        (2, 10, 1000),
        (12341234, 1234234, 8979879),
        (545634523, 3467345, 9879879734958698237495),
        (1234121312344123412543678564327689088674533, 3245647586956453313235, 23451324512341)
    ]
    test_pass = True
    for case in cases:
        x = mod_exp(case[0], case[1], case[2])
        y = pow(case[0], case[1], case[2])
        if x != y:
            test_pass = False
            print "Case fail {c}".format(c=case)
    if test_pass:
        print "Test Pass"


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def egcd(a, b):
    rpp = a
    rp = b
    spp = 1
    sp = 0
    tpp = 0
    tp = 1
    while rp != 0:
        q = rpp / rp
        rpp, rp = rp, rpp % rp
        spp, sp = sp, spp - q * sp
        tpp, tp = tp, tpp - q * tp
    return rpp, spp, tpp


def test_egcd():
    cases = [[18, 27], [18, 7]]
    for case in cases:
        r, s, t = egcd(case[0], case[1])
        assert case[0] * s + case[1] * t == r, "Bezout equation unsatisfied"
        print "{a}*{s} + {b}*{t}=gcd({a}, {b})={r}".format(a=case[0], b=case[1], s=s, t=t, r=r)
        g = gcd(case[0], case[1])
        assert r == g, "GCD mutual verification failed, get {r}, should {g}".format(r=r, g=g)
    print "Test pass"


def inv_mod(e, m):
    """
    Must have that gcd(e, m) = 1
    :param e: 
    :param m: 
    :return: 
    """
    r, s, t = egcd(e, m)
    assert r == 1, "Non-coprime inputs {e}, {m}, gcd={r}".format(e=e, m=m, r=r)
    return s % m


def test_inv_mod():
    cases = [[17, 3120]]
    for case in cases:
        im = inv_mod(case[0], case[1])
        print "{im}*{e} % {m} = 1".format(im=im, e=case[0], m=case[1])
        assert (im * case[0]) % case[1] == 1, "Non-inverse detected"
        assert 0 <= im < case[1], "Out of range"
    print "Test pass"
