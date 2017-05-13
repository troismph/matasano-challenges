from dh import DHClient, DH_p, DH_g
from converts import encrypt_aes_128_cbc, decrypt_aes_128_cbc
import hashlib
import os


def enc_msg(msg, key):
    hash_obj = hashlib.sha1()
    hash_obj.update(key)
    session_key = hash_obj.digest()[:16]
    iv = bytearray(os.urandom(16))
    cipher = encrypt_aes_128_cbc(msg, session_key, iv)
    return cipher, iv


def dec_msg(msg, iv, key):
    hash_obj = hashlib.sha1()
    hash_obj.update(key)
    session_key = hash_obj.digest()[:16]
    plain = decrypt_aes_128_cbc(msg, session_key, iv)
    return plain


def dh_mitm():
    a2b_plain = bytearray("Message from A to B")
    print "A send\n{a2b}".format(a2b=a2b_plain)
    dha = DHClient()
    dhb = DHClient()
    skb = dhb.get_shared_key(DH_p)
    ska = dha.get_shared_key(DH_p)
    a2m, iv_a2m = enc_msg(a2b_plain, ska)
    # relay a->b
    m2b, iv_m2b = a2m, iv_a2m
    b_rcv_plain = dec_msg(m2b, iv_m2b, skb)
    print "B receive\n{br}".format(br=b_rcv_plain)
    b2m, iv_b2m = enc_msg(b_rcv_plain, skb)
    # relay b->a
    m2a, iv_m2a = b2m, iv_b2m
    a_rcv_plain = dec_msg(m2a, iv_m2a, ska)
    print "A receive\n{ar}".format(ar=a_rcv_plain)
    # m's attack
    # m knows ska = skb = '\x00'
    skm = '\x00'
    m_decrypt_plain = dec_msg(a2m, iv_a2m, skm)
    print "M decrypted\n{md}".format(md=m_decrypt_plain)
    if a2b_plain == b_rcv_plain and a2b_plain == a_rcv_plain and a2b_plain == m_decrypt_plain:
        print "Crack OK"
    else:
        print "Crack fail"
