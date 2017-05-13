from dh import DHClient, DH_p, DH_g
from challenge34 import enc_msg, dec_msg
from converts import big_int_to_bin_str


def keys_from_g(g, p):
    # returns public and session key derived from g
    if g == 1:
        return 1, big_int_to_bin_str(1)
    if g == p:
        return 0, big_int_to_bin_str(0)
    if g == (p - 1):
        return 1, big_int_to_bin_str(1)
    raise "Undefined g {g}".format(g=g)


# It is impossible to accomplish this task by attacking only g on b.
# Two options are:
# 1. attack g on both a and b, which is no longer MITM.
# 2. attack both g and pka
# Here we try option 2.
def dh_mitm(g):
    a2b_plain = bytearray("Message_from_A_to_B")
    print "A send\n{a2b}".format(a2b=a2b_plain)
    dha = DHClient()
    # m sends manipulated g to b
    # dhb is compromised, providing predictable public key
    dhb = DHClient(DH_p, g)
    # session key as seen by each party
    ska = dha.get_shared_key(dhb.pub_key)
    # pka also attacked by m, so we can predict skb
    skb = dhb.get_shared_key(1)
    # public and session keys used by a as predicted by m
    pkma, skma = keys_from_g(g, DH_p)
    # since skb is compromised with a fake pka(1),
    # we can easily calculate skmb
    skmb = big_int_to_bin_str(1)
    assert skmb == skb, "skmb and skb mismatch"
    # we must have that skma == ska,
    # since ska is derived from compromised dhb
    assert skma == ska, "skma and ska mismatch"
    # messages
    a2m, iv_a2m = enc_msg(a2b_plain, ska)
    # m decrypts message with its skm on hand
    m_rcv_plain = dec_msg(a2m, iv_a2m, skma)
    print "M decrypted\n{m}".format(m=m_rcv_plain)
    m2b, iv_m2b = enc_msg(m_rcv_plain, skmb)
    b_rcv_plain = dec_msg(m2b, iv_m2b, skb)
    print "B received\n{m}".format(m=b_rcv_plain)
    b2m, iv_b2m = enc_msg(b_rcv_plain, skb)
    m_rcv_plain2 = dec_msg(b2m, iv_b2m, skmb)
    print "M decrypted\n{m}".format(m=m_rcv_plain2)
    m2a, iv_m2a = enc_msg(m_rcv_plain2, skma)
    a_rcv_plain = dec_msg(m2a, iv_m2a, ska)
    print "A received\n{m}".format(m=a_rcv_plain)
    if a2b_plain == m_rcv_plain and a2b_plain == b_rcv_plain and a2b_plain == m_rcv_plain2 and a2b_plain == a_rcv_plain:
        print "Pass"
    else:
        print "Fail"


def run():
    print "Try g = 1 >>>>>>>>>>>>>>>>>>>"
    dh_mitm(1)
    print "Try g = p - 1 >>>>>>>>>>>>>>>"
    dh_mitm(DH_p - 1)
    print "Try g = p >>>>>>>>>>>>>>>>>>>"
    dh_mitm(DH_p)
