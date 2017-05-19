from rsa_g4z3 import rsa_gen_key, rsa_encrypt, BLOCK_LEN_BYTES
from math_g4z3 import inv_mod
from converts import bin_str_to_big_int, big_int_to_bin_str


E = 11


def get_nt_ms_inv_mods(pks):
    ns = zip(*pks)[1]
    nt = reduce(lambda x, y: x * y, ns)
    mss = [nt / i for i in ns]
    inv_mods = [inv_mod(mss[i], ns[i]) for i in range(len(ns))]
    return nt, mss, inv_mods


# code snippet from Markus Jarderot@stackoverflow.com
def find_invpow(x, n):
    """Finds the integer component of the n'th root of x,
    an integer such that y ** n <= x < (y + 1) ** n.
    """
    high = 1
    while high ** n <= x:
        high *= 2
    low = high / 2
    while low < high:
        mid = (low + high) // 2
        if low < mid and mid ** n < x:
            low = mid
        elif high > mid and mid ** n > x:
            high = mid
        else:
            return mid
    return mid + 1


def crack():
    msg = "I am the innocent message..."
    print "Original message\n{m}".format(m=msg.encode('hex'))
    # generate key pairs
    kps = zip(*[rsa_gen_key(E) for i in range(E)])
    pks = kps[0]
    nt, mss, inv_mods = get_nt_ms_inv_mods(pks)
    ciphers = [rsa_encrypt(msg, pk) for pk in pks]
    # only decrypt block 0 for simplicity
    cs = [bin_str_to_big_int(cipher[:BLOCK_LEN_BYTES]) for cipher in ciphers]
    all_params = zip(cs, mss, inv_mods)
    adds = [reduce(lambda x, y: x * y, param_set) for param_set in all_params]
    final = reduce(lambda x, y: x + y, adds) % nt
    msg_int = find_invpow(final, E)
    msg_crack = big_int_to_bin_str(msg_int)
    print "Cracked partial message\n{m}".format(m=msg_crack.encode('hex'))


crack()
