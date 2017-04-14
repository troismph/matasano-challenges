from sha1_ajalt import sha1


SECRET_PREFIX = "IAMSECRETPREFIX!"


def sha1_mac_create(buf_in):
    return sha1(SECRET_PREFIX + buf_in)


def sha1_mac_auth(buf_in, mac):
    mac_ = sha1_mac_create(buf_in)
    return mac_ == mac




