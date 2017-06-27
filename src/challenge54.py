""" Solution for challenge 54

HOW TO RUN:
1. Generate hash collision tree by calling gen_collision_tree(k=8). Tree leaf count will be 1 << k
2. Run test_find_tail_for_msg(k=8, load=True) with the same k you have just used.
3. Watch

"""
import os
import random
import sys
import pickle
import glob
import string


""" must be 'easy' or 'hard'
"""
DIFFICULTY = 'easy'
if DIFFICULTY == 'hard':
    from md_hash import hash_hard as hash_func, HARD_BLOCK_LEN_BYTES as BLOCK_LEN_BYTES, enum_block
elif DIFFICULTY == 'easy':
    from md_hash import hash_easy as hash_func, EASY_BLOCK_LEN_BYTES as BLOCK_LEN_BYTES, enum_block
else:
    assert False, 'Wrong config of DIFFUCULTY'

""" A hack for efficient collision-finding

In easy mode, this should equal BLOCK_LEN_BYTES. Given initial hash states s0 and s1, we need to find a state m such that hash_func(m, s0) == hash_func(m, s1).

However, due to a small state space, sometimes there's no such m for a given pair of s0 and s1. So we employ a larger block for collision finding, whose length is defined here. 
"""
COLLISION_STATE_LEN_BYTES = 4

ALPHABET = string.digits + string.letters


class Node(object):
    def __init__(self, cb, s):
        """
        :param cb: collision block
        :param s: resulting hash state
        """
        self.cb = cb
        self.s = s


def get_single_random_state(l, alphabet=None):
    """
    Generate a single random state
    :param l: length in bytes
    :param alphabet: 
    :return: a bytearray of random bytes
    """
    if alphabet is not None:
        return ''.join(random.choice(alphabet) for i in range(l))
    return os.urandom(l)


def get_random_states(n, alphabet=None):
    """
    Generate non-duplicated random states 
    :param n: number of states to return
    :param l: length of each state, in bytes
    :param alphabet: if not given, each byte can be any of [0, 255]
    :return: an iterator of bytearray, non-duplicated
    """
    dedup = set()
    for x in xrange(n):
        while True:
            s = get_single_random_state(BLOCK_LEN_BYTES, alphabet)
            if s not in dedup:
                dedup.add(s)
                break
    return dedup


def gen_hash_init(k):
    """
    Generate 2**k hash initial states
    :param k: 
    :return: 
    """
    states = get_random_states(1 << k)
    return [Node(None, x) for x in states]


def find_collision2(s0, s1):
    """
    A stupid enumerating finder
    :param s0: 
    :param s1: 
    :return: 
    """
    ctr = 0
    for m in enum_block(COLLISION_STATE_LEN_BYTES):
        if ctr & 0xff == 0xff:
            print '\rFinding collision {s0}, {s1}, ctr={ctr:x}'.format(s0=s0.encode('hex'), s1=s1.encode('hex'),
                                                                       ctr=ctr),
            sys.stdout.flush()
        ctr += 1
        t0 = hash_func(m, s0)
        t1 = hash_func(m, s1)
        if t0 == t1:
            print 'Found collision: {s0}, {s1}, {m}, {t}'.format(m=str(m).encode('hex'), t=str(t0).encode('hex'),
                                                                 s0=s0.encode('hex'), s1=s1.encode('hex'))
            return Node(m, t0)
    assert False, 'Cannot find collision after enumerating all possible values'


def find_collision(s0, s1):
    """
    Find collision block for 2 hash states
    :param s0: hash state 
    :param s1: hash state
    :return: a Node object
    """
    ctr = 0
    while True:
        if ctr & 0xfff == 0xfff:
            print '\rFinding collision {s0}, {s1}, ctr={ctr:x}'.format(s0=s0.encode('hex'), s1=s1.encode('hex'),
                                                                       ctr=ctr),
            sys.stdout.flush()
        ctr += 1
        m = get_single_random_state(COLLISION_STATE_LEN_BYTES)
        t0 = hash_func(m, s0)
        t1 = hash_func(m, s1)
        if t0 == t1:
            print 'Found collision: {s0}, {s1}, {m}, {t}'.format(m=str(m).encode('hex'), t=str(t0).encode('hex'),
                                                                 s0=s0.encode('hex'), s1=s1.encode('hex'))
            return Node(m, str(t0))


def gen_next_level(level):
    """
    Pair hash states and generate single-block collisions
    :param level: [Node] * 2n
    :type level: list of Node
    :return: [Node] * n
    """
    l = len(level)
    assert l % 2 == 0, "Uneven inputs"
    ret = []
    for idx in xrange(0, l, 2):
        print 'Generating next level {idx}/{total}'.format(idx=idx, total=l)
        c = find_collision(level[idx].s, level[idx + 1].s)
        ret.append(c)
    return ret


def save_tree(tree):
    leaves = len(tree[0])
    root = tree[-1][0].s.encode('hex')
    file_name = '{leaves}_{root}.tree'.format(leaves=leaves, root=root)
    with open(file_name, 'w') as f:
        pickle.dump(tree, f)
    print 'Saved to file {fn}'.format(fn=file_name)


def load_tree(leaves, root=None):
    file_name = None
    if root is None:
        trees = glob.glob('{leaves}_*.tree'.format(leaves=leaves))
        if len(trees) == 0:
            return None
        file_name = random.choice(trees)
    else:
        file_name = '{leaves}_{root}.tree'.format(leaves=leaves, root=root.encode('hex'))
    ret = None
    try:
        with open(file_name, 'r') as f:
            ret = pickle.load(f)
    except Exception as e:
        print 'Exception loading from file {f}'.format(f=file_name)
        print e
    finally:
        return ret


def gen_collision_tree(k=8):
    """
    Generate a k+1 level binary tree of collision states
    :param k: 
    :return: 
    """
    levels = []
    leaves = gen_hash_init(k)
    levels.append(leaves)
    for x in range(1, k + 1):
        print 'Generating level {lv}/{k}'.format(lv=x, k=k)
        levels.append(gen_next_level(levels[x - 1]))
    save_tree(levels)
    return levels


def test_collision_tree(ctree):
    """
    :param ctree: the tree, a list of levels. ctree[0] are leaves
    :type ctree: list of (list of Node)
    :return: 
    """
    for lv in range(1, len(ctree)):
        cur_lv = ctree[lv]
        prev_lv = ctree[lv - 1]
        for idx in range(len(cur_lv)):
            child0 = prev_lv[idx * 2]
            child1 = prev_lv[idx * 2 + 1]
            t0 = hash_func(cur_lv[idx].cb, child0.s)
            t1 = hash_func(cur_lv[idx].cb, child1.s)
            assert t0 == t1, 'Hash collision failed'
    print 'Test pass'


def test_gen_collision_tree(k=4):
    ctree = gen_collision_tree(k)
    test_collision_tree(ctree)


def test_load_collision_tree():
    k = 4
    tree = load_tree(1 << k)
    test_collision_tree(tree)


def gen_collision_path(tree, leaf_state):
    idx = None
    for x in range(len(tree[0])):
        if tree[0][x].s == leaf_state:
            idx = x
    assert idx is not None, 'Failed to find leaf'
    ret = []
    for i in range(1, len(tree)):
        idx = idx >> 1
        ret.append(tree[i][idx].cb)
    return ''.join(ret)


def test_gen_collision_path():
    tree = load_tree(256)
    root = tree[-1][0].s
    n_round = 10
    for x in range(n_round):
        leaf_s = random.choice(tree[0]).s
        collision_path = gen_collision_path(tree, leaf_s)
        check_s = hash_func(collision_path, leaf_s)
        assert check_s == root
    print 'Test pass'


def gen_glue(s_from, s_to_list, lb, alphabet=None):
    """
    Generate glue blocks with length lb (of blocks), that connects
    hash state s_from to s_to
    :param alphabet: the alphabet for glue
    :param s_from: hash state to glue from
    :type s_from: str
    :param s_to_list: list of hash states to glue to
    :type s_to_list: list of str
    :param lb: glue block length, in blocks
    :return: a list of glue blocks
    :rtype: list of str
    """
    print 'Finding glue from {f} to {t} states'.format(f=s_from.encode('hex'), t=len(s_to_list))
    s_to = set(s_to_list)
    ctr = 0
    while True:
        glue_head = bytearray(get_single_random_state((lb - 1) * BLOCK_LEN_BYTES, alphabet))
        s_half = hash_func(glue_head, s_from)
        for glue_tail in enum_block(BLOCK_LEN_BYTES, alphabet):
            if ctr & 0xfff == 0xfff:
                print '\rTrying ctr={ctr:x}'.format(ctr=ctr),
                sys.stdout.flush()
            ctr += 1
            s_tail = str(hash_func(glue_tail, s_half))
            if s_tail in s_to:
                glue = glue_head + glue_tail
                print 'Found glue {g}'.format(g=str(glue))
                return glue, s_tail


def test_gen_glue():
    alphabet = None
    glue_len = 8
    n_round = 10
    to_len = 1 << 2
    s_to_list = [get_single_random_state(BLOCK_LEN_BYTES, alphabet) for x in range(to_len)]
    for x in range(n_round):
        s_from = get_single_random_state(BLOCK_LEN_BYTES, alphabet)
        s_to = get_single_random_state(BLOCK_LEN_BYTES, alphabet)
        glue, s_tail = gen_glue(s_from, s_to_list, glue_len, alphabet)
        s_check = hash_func(glue, s_from)
        assert s_check in s_to_list, 'Hash check failed, need {n}, get {g}'.format(n=s_to.encode('hex'),
                                                                                   g=s_check.encode('hex'))
    print 'Test pass'


def find_tail_for_msg(msg, iv, tree=None):
    tree = tree or load_tree(1 << 8)
    # pad msg to block length with ' '
    msg_pad_len = len(msg) % BLOCK_LEN_BYTES
    msg_pad = ' ' * msg_pad_len
    # get hash state of padded msg
    s_from = str(hash_func(msg + msg_pad, iv))
    s_to_list = [node.s for node in tree[0]]
    glue, s_glue = gen_glue(s_from, s_to_list, 8)
    collision_path = gen_collision_path(tree, s_glue)
    return msg_pad + glue + collision_path


def test_find_tail_for_msg(k=8, load=True):
    tree = load_tree(1 << k) if load else None
    if tree is None:
        tree = gen_collision_tree(k)
    else:
        print 'Tree loaded'
    root = tree[-1][0].s
    iv = bytearray(BLOCK_LEN_BYTES)
    n_round = 10
    for x in range(n_round):
        msg_len = random.randrange(10, 200)
        msg = get_single_random_state(msg_len, ALPHABET)
        print 'len={l}, msg={msg}'.format(l=len(msg), msg=msg)
        tail = find_tail_for_msg(msg, iv, tree)
        print 'tail={tail}'.format(tail=tail)
        s_check = str(hash_func(msg + tail, iv))
        assert s_check == root, 'Failed'
    print 'Test pass'
