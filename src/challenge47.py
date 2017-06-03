from rsa_g4z3 import rsa_gen_key, rsa_decrypt, rsa_encrypt
from converts import bin_str_to_big_int, big_int_to_bin_str, pkcs15_pad, pkcs15_unpad
from math_g4z3 import mod_mult, mod_exp
import sys
import inspect


class Oracle(object):
    def __init__(self):
        self.pk, self._sk = rsa_gen_key(len=256)

    def is_conform(self, cipher):
        m = rsa_decrypt(cipher, self._sk, True)
        return m[:2] == '\x00\x02'


def test_oracle():
    oracle = Oracle()
    msg = 'our pitch'
    msg_pad = pkcs15_pad(msg, 32, '\x02')
    cipher = rsa_encrypt(msg_pad, oracle.pk)
    assert oracle.is_conform(cipher), 'Test failed'


def search_up(begin, c, oracle, fn):
    e = oracle.pk[0]
    n = oracle.pk[1]
    print '{fn} begin'.format(fn=fn)
    ret = None
    x = begin
    while x < n:
        if x & 0xff == 0xff:
            print '\r{fn}:{x:x}'.format(fn=fn, x=x) + ' ' * 40,
            sys.stdout.flush()
        t = mod_mult(c, mod_exp(x, e, n), n)
        t_str = big_int_to_bin_str(t)
        if oracle.is_conform(t_str):
            ret = x
            break
        x += 1
    print '\n{fn} finish'.format(fn=fn)
    return ret


def step_2_a(B, c, oracle):
    fn = inspect.stack()[0][3]
    n = oracle.pk[1]
    return search_up(n / (3 * B), c, oracle, fn)


def step_2_b(c, s, oracle):
    fn = inspect.stack()[0][3]
    return search_up(s + 1, c, oracle, fn)


def round_div_int(a, b, floor=True):
    if floor:
        return a / b
    else:
        return a / b + (1 if a % b > 0 else 0)


def step_2_c(m, c, s, B, oracle):
    fn = inspect.stack()[0][3]
    a, b = m
    e = oracle.pk[0]
    n = oracle.pk[1]
    r = round_div_int(2 * (b * s - 2 * B), n, False)
    ret = None
    print '{fn} begin'.format(fn=fn)
    while r < n:
        _s = round_div_int(2 * B + r * n, b, False)
        _s_max = round_div_int(3 * B + r * n, a, False)
        print '{fn} r={r} s_range={s_range}'.format(fn=fn, r=r, s_range=_s_max - _s)
        while _s < _s_max:
            if _s ^ 0xff == 0xff:
                print '\r{fn}:{x:x}'.format(x=_s) + ' ' * 40,
                sys.stdout.flush()
            t = mod_mult(c, mod_exp(_s, e, n), n)
            t_str = big_int_to_bin_str(t)
            if oracle.is_conform(t_str):
                ret = _s
                break
            _s += 1
        if ret is not None:
            break
        r += 1
    print '\n{fn} finish'.format(fn=fn)
    return ret


def step_3(M, n, s, B):
    ret = []
    fn = inspect.stack()[0][3]
    print '{fn} begin M={M_len}'.format(fn=fn, M_len=len(M))
    for m in M:
        a, b = m
        r = round_div_int(a * s - 3 * B + 1, n, False)
        r_max = round_div_int(b * s - 2 * B, n)
        print '{fn} r range={r_range}'.format(fn=fn, r_range=r_max - r)
        while r <= r_max:
            l = round_div_int(2 * B + r * n, s, False)
            lb = max(a, l)
            u = round_div_int(3 * B - 1 + r * n, s)
            ub = min(b, u)
            if lb <= ub:
                ret.append([lb, ub])
            r += 1
    print '{fn} finish'.format(fn=fn)
    return ret


def crack():
    msg = 'pitch is ours'
    oracle = Oracle()
    msg_pad = pkcs15_pad(msg, 32, '\x02')
    B = 1 << (8 * (32 - 2))
    cipher = rsa_encrypt(msg_pad, oracle.pk)
    # init values s0, c0, and M0
    s = 1
    c = bin_str_to_big_int(cipher)
    M = [[2 * B, 3 * B - 1]]
    m = None
    for i in range(9999):
        # calculate new s
        if i == 1:
            # step 2.a
            s = step_2_a(B, c, oracle)
            assert s is not None, 'Failed in step 2 a'
            print 's={s:x}'.format(s=s)
        elif len(M) > 1:
            # step 2.b
            s = step_2_b(c, s, oracle)
            assert s is not None, 'Failed in step 2 b'
            print 's={s:x}'.format(s=s)
        else:
            # step 2.c
            s = step_2_c(M[0], c, s, B, oracle)
            assert s is not None, 'Failed in step 2 c'
            print 's={s:x}'.format(s=s)
        # calculate new M according to new s and previous M
        M = step_3(M, oracle.pk[1], s, B)
        # in case of len(M) == 1
        if len(M) == 1:
            if M[0][0] == M[0][1]:
                m = M[0][0]
                break
    msg_crack = big_int_to_bin_str(m)
    print 'Crack finished, msg\n{msg}'.format(msg=msg_crack)
    msg_crack = '\x00' * (32 - len(msg_crack)) + msg_crack
    unpadded_msg = pkcs15_unpad(msg_crack, False, '\x02')
    print 'Unpadded msg\n{msg}'.format(msg=unpadded_msg)
    assert msg == unpadded_msg, 'Crack failed'
