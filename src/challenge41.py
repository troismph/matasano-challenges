from rsa_g4z3 import rsa_gen_key, rsa_encrypt, rsa_decrypt, BLOCK_LEN_BYTES
from math_g4z3 import inv_mod, mod_exp, mod_mult
from converts import bin_str_to_big_int, big_int_to_bin_str


def crack():
    msg = "I am the innocent message..."
    print "Original message\n{m}".format(m=msg)
    pk, sk = rsa_gen_key()
    cipher = rsa_encrypt(msg, pk)
    # handle only first block for simplicity
    c = bin_str_to_big_int(cipher[:BLOCK_LEN_BYTES])
    s = 2
    c0 = mod_mult(mod_exp(s, pk[0], pk[1]), c, pk[1])
    p0_str = rsa_decrypt(big_int_to_bin_str(c0), sk)
    p0_int = bin_str_to_big_int(p0_str)
    inv_s = inv_mod(s, pk[1])
    p = mod_mult(p0_int, inv_s, pk[1])
    msg0 = big_int_to_bin_str(p)
    print "Cracked message\n{m}".format(m=msg0)
    print "Cracked part len={n}".format(n=len(msg0))
    assert msg[:len(msg0)] == msg0, "Crack failed!!!"


crack()
