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
