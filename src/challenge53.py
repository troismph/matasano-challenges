import sys
import random
import os
from md_hash import find_collision, get_random_m, EASY_BLOCK_LEN_BYTES, hash_easy
from converts import b64encode, b64decode


def blk_cnt(m, bl):
    l = len(m)
    assert l % bl == 0, 'Unaligned byte'
    return l / bl


def iter_blk(msg, bl):
    c = blk_cnt(msg, bl)
    for i in range(c):
        yield msg[i * bl: i * bl + bl]


def incr_block(block):
    """
    :type block: bytearray 
    :return: 
    """
    overflow = True
    for idx in range(len(block)):
        if block[idx] == 0xff:
            continue
        block[idx] += 1
        overflow = False
        break
    return overflow


def enum_block(bl):
    """
    An iterator to generae all possible values of one block
    :param bl: block length in bytes
    :return: 
    """
    blk = bytearray(bl)
    yield blk
    while not incr_block(blk):
        yield blk


def find_collision_block(n_blk, bl, hash_func, key):
    """
    Find collision between a 1-block message and an n-block message
    :param n_blk: 
    :param bl: block length, in bytes
    :param hash_func: the hash function
    :param key: key for hash function
    :return: two strings
    """
    m0 = get_random_m(bl)
    h0 = hash_func(m0, key)
    # init m1
    ctr = 0
    while True:
        m1_head = get_random_m((n_blk - 1) * bl)
        h1_init = hash_func(m1_head, key)
        for block in enum_block(bl):
            ctr += 1
            if ctr & 0xff == 0xff:
                print "\rTrying {ctr:x}".format(ctr=ctr) + " " * 10,
                sys.stdout.flush()
            h1_tail = hash_func(block, h1_init)
            if h1_tail == h0:
                print "\nFound {h}:{m0}:{m1}".format(h=str(h0).encode('hex'), m0=m0, m1=m1_head + str(block))
                return m0, m1_head + str(block)


def get_save_file_name(k, bl, key):
    return 'k{k}.bl{bl}.key{key}'.format(k=k, bl=bl, key=str(key).encode('hex'))


def load_exp_msgs(k, bl, key):
    file_name = get_save_file_name(k, bl, key)
    if not os.path.isfile(file_name):
        return None
    print 'Loading exp msgs from {f}'.format(f=file_name)
    with open(file_name, 'r') as f:
        ret = []
        for line in f:
            parts = line.strip().split(',')
            ret.append([str(b64decode(parts[0])), str(b64decode(parts[1]))])
        return ret


def save_exp_msgs(exp_msgs, k, bl, key):
    file_name = get_save_file_name(k, bl, key)
    to_write = ['{m0},{m1}\n'.format(m0=b64encode(bytearray(m0)), m1=b64encode(bytearray(m1))) for m0, m1 in exp_msgs]
    print to_write
    with open(file_name, 'w') as f:
        f.writelines(to_write)
    print 'Saved to {s}'.format(s=file_name)


def make_exp_msgs(k, bl, hash_func, key):
    h = key
    ret = []
    for i in range(k):
        m0, m1 = find_collision_block((1 << i) + 1, bl, hash_func, h)
        ret.append([m0, m1])
        h = hash_func(m0, h)
    return ret


def get_exp_final_state(exp_msgs, hash_func, key):
    m = ''.join([x[0] for x in exp_msgs])
    return hash_func(m, key)


def test_make_exp_msgs(k, save=False):
    bl = EASY_BLOCK_LEN_BYTES
    hash_func = hash_easy
    key = bytearray(b'\x9es')
    ret = make_exp_msgs(k, bl, hash_func, key)
    assert len(ret) == k, 'Message set size wrong, need {k} get {l}'.format(k=k, l=len(ret))
    prev_h = key
    for idx in range(len(ret)):
        m0, m1 = ret[idx]
        assert len(m0) == bl, 'Wrong message length, should be 1'
        assert len(m1) == ((1 << idx) + 1) * bl, 'Wrong message length get {l} need {n}'.format(l=len(m1),
                                                                                                n=(1 << idx) + 1)
        h0 = hash_func(m0, prev_h)
        h1 = hash_func(m1, prev_h)
        assert h0 == h1, 'No collision at idx {idx}'.format(idx=idx)
        prev_h = h0
        print "{h}:{m0}:{m1}:{l1}".format(h=h0, m0=m0, m1=m1, l1=len(m1))
    print 'Pass'
    if save:
        save_exp_msgs(ret, k, bl, key)


def compose_msg(l, m, k):
    """Create message of size l from expandable message set m"""
    assert k <= l <= k + (1 << k) - 1, "Invalid params"
    selections = []
    fmt_str = '0{k}b'.format(k=k)
    selector = [x for x in reversed(format(l - k, fmt_str))]
    for s in range(k):
        selections.append(m[s][int(selector[s])])
    return ''.join(selections)


def test_compose_msg():
    n_round = 10
    k = 4
    bl = EASY_BLOCK_LEN_BYTES
    hash_func = hash_easy
    key = os.urandom(bl)
    m = make_exp_msgs(k, bl, hash_func, key)
    # for debug convenience
    # m = load_exp_msgs('c53.save.txt')
    h = None
    for x in range(n_round):
        l = random.randrange(k, k + (1 << k) - 1)
        msg = compose_msg(l, m, k)
        print '{l}:{m}'.format(l=l, m=msg)
        assert blk_cnt(msg, bl) == l, 'Wrong message length, get {g} need {l}'.format(g=len(msg), l=l)
        if h is None:
            h = hash_func(msg, key)
        else:
            assert h == hash_func(msg, key), 'Wrong hash value'
    print 'Test pass'


def get_internal_hash_states(msg, hash_func, bl, key):
    h = key
    ret = []
    for block in iter_blk(msg, bl):
        h = hash_func(block, h)
        ret.append(h)
    return ret


def attack(msg, k, bl, hash_func, key):
    assert blk_cnt(msg, bl) == (1 << k), 'Wrong message length and/or k, blk_cnt={bc}, bl={bl}, k={k}'.format(
        bc=blk_cnt(msg, bl), bl=bl, k=k)
    # x_msgs = make_exp_msgs(k, bl, hash_func, key)
    assert k == 8, 'Cannot load, check code, or run test_make_exp_msgs() first'
    x_msgs = load_exp_msgs(k, bl, key)
    assert x_msgs is not None, 'x_msgs not loaded'
    x_final_state = get_exp_final_state(x_msgs, hash_func, key)
    hash_states = get_internal_hash_states(msg, hash_func, bl, key)
    # now let's look for the bridge
    # bridge always has 1-block
    # at least the last block from original msg should be kept
    # thus our cracking header can take length in the range:
    # [k (x_msgs minimal length), len(msg) - 2 (very long header except 1 block for bridge and 1 block for original tail)]
    # since len(msg) = 1 << k, we can safely have
    # len(msg) - 2 < (k + (1 << k) - 1)
    # which is the max possible length in x_msgs
    # in the following look, idx is the position of bridge
    bridge = None
    bridge_idx = None
    for idx in range(k + 1, (1 << k) - 2):
        target_h = hash_states[idx]
        for bridge_try in enum_block(bl):
            h_b = hash_func(bridge_try, x_final_state)
            if h_b == target_h:
                bridge = bridge_try
                bridge_idx = idx
                break
        if bridge is not None:
            break
    if bridge is None:
        return None
    # trivial step to compose final result
    x_head = compose_msg(bridge_idx, x_msgs, k)
    tail = msg[(bridge_idx + 1) * bl:]
    return x_head + str(bridge) + tail


def test_attack():
    k = 8
    bl = EASY_BLOCK_LEN_BYTES
    hash_func = hash_easy
    key = bytearray(b'\x9es')
    msg = get_random_m((1 << k) * bl)
    forge = attack(msg, k, bl, hash_func, key)
    assert forge is not None, 'Failed to find bridge'
    print '{m}\n{f}'.format(f=forge, m=msg)
    assert blk_cnt(forge, bl) == blk_cnt(msg, bl), 'Wrong forgery length'
    h0 = hash_func(msg, key)
    h1 = hash_func(forge, key)
    assert h0 == h1, 'Inequal hash'
    print 'Pass'
