from rsa_g4z3 import rsa_gen_key, rsa_encrypt, rsa_decrypt
from converts import bin_str_to_big_int, big_int_to_bin_str, b64decode
from math_g4z3 import mod_mult, mod_exp
import random
import sys


class ParityOracle:
    def __init__(self):
        self.pk, self._sk = rsa_gen_key(len=1024)

    def is_even(self, cipher):
        p = rsa_decrypt(cipher, self._sk)
        n = bin_str_to_big_int(p)
        return n % 2 == 0


class Client:
    def __init__(self, pk):
        self.msg = str(b64decode('VGhhdCdzIHdoeSBJIGZvdW5kIHlvdSBkb24ndCBwb'
                                 'GF5IGFyb3VuZCB3aXRoIHRoZSBGdW5reSBDb2xkIE1lZGluYQ=='))
        print 'Target={t}'.format(t=bin_str_to_big_int(self.msg))
        self.cipher = rsa_encrypt(self.msg, pk)


class BinNavAbstract(object):
    def __init__(self):
        pass

    def nav(self, lb, ub, lv):
        """
        :rtype: bool
        """
        return True

    def check(self, p):
        """
        :rtype: book
        """
        return True


class BinNavEqual(BinNavAbstract):
    def __init__(self, target):
        self.target = target
        super(BinNavEqual, self).__init__()

    def nav(self, lb, ub, lv):
        p = (lb + ub) / 2
        return self.target <= p

    def check(self, p):
        return p == self.target


class BinNavParity(BinNavAbstract):
    def __init__(self, oracle, cipher):
        """
        :type oracle: ParityOracle 
        """
        self._oracle = oracle
        self._cipher = bin_str_to_big_int(cipher)
        self._n = self._oracle.pk[1]
        self._e = self._oracle.pk[0]
        super(BinNavParity, self).__init__()

    def nav(self, lb, ub, lv):
        m = mod_exp(mod_exp(2, lv, self._n), self._e, self._n)
        c = mod_mult(m, self._cipher, self._n)
        parity = self._oracle.is_even(big_int_to_bin_str(c))
        return parity

    def check(self, p):
        c = bin_str_to_big_int(rsa_encrypt(big_int_to_bin_str(p), self._oracle.pk))
        return c == self._cipher


def zoom_in(lb, ub, low, checker):
    s = lb + ub
    p = s / 2
    if s % 2 != 0:
        if low:
            return lb, p
        else:
            return p + 1, ub
    else:
        if checker(p):
            return p, p
        if low:
            return lb, p - 1
        else:
            return p + 1, ub


def final_search(lb, ub, nav):
    for x in range(lb, ub + 1):
        if nav.check(x):
            return x
    return None


def bin_search(lb, ub, nav):
    lv = 0
    print "{lb}, {ub}".format(lb=lb, ub=ub)
    while ub - lb > 16:
        lv += 1
        low = nav.nav(lb, ub, lv)
        lb, ub = zoom_in(lb, ub, low, nav.check)
        # print "{d} {r} : {lb}, {ub}".format(d='L' if low else 'U', r=ub-lb, lb=lb, ub=ub)
        print "\rRange length {l}".format(l=len(str(ub - lb))) + " " * 40,
        sys.stdout.flush()
    if ub != lb:
        lb = final_search(lb, ub, nav)
    print "Found {lb}, {ub}".format(lb=lb, ub=ub)
    return lb


def test_bin_search():
    lb = 0
    ub = 999999999999999
    target = random.randrange(lb, ub)
    nav = BinNavEqual(target)
    print "Begin search for {t}".format(t=target)
    f = bin_search(lb, ub, nav)
    assert f == target, "Bin search test failed"


def crack():
    oracle = ParityOracle()
    client = Client(oracle.pk)
    lb = 0
    ub = oracle.pk[1] - 1
    nav = BinNavParity(oracle, client.cipher)
    print "Begin crack"
    f = bin_search(lb, ub, nav)
    if f is None:
        print 'pk={pk}, sk={sk}'.format(pk=oracle.pk, sk=oracle._sk)
    assert f is not None, "Failed, original number {n}".format(n=bin_str_to_big_int(client.msg))
    msg_ = big_int_to_bin_str(f)
    print "Found message {m}".format(m=msg_)
    print "Found number {f}".format(f=f)
    print "Original number {n}".format(n=bin_str_to_big_int(client.msg))


def test_rsa_mult():
    msg = 'Test message...'
    x = 2 << 5
    pk, sk = rsa_gen_key(len=1024)
    c = rsa_encrypt(msg, pk)
    c_n = bin_str_to_big_int(c)
    p = mod_exp(x, pk[0], pk[1])
    c2_n = mod_mult(c_n, p, pk[1])
    c2 = big_int_to_bin_str(c2_n)
    msg2 = rsa_decrypt(c2, sk)
    msg3 = big_int_to_bin_str(bin_str_to_big_int(msg) * x)
    print msg.encode('hex')
    print msg2.encode('hex')
    print msg3.encode('hex')
