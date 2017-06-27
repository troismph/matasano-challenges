import os
import random
import sys
import pickle
import glob

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


def gen_collision_tree(k):
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
