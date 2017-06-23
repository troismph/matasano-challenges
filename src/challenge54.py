from md_hash import hash_easy, get_random_m


class Node(object):
    def __init__(self, cb, s):
        self.cb = cb
        self.s = s


class Level(object):
    def __init__(self, nodes):
        self.nodes = [node for node in nodes]

    def


def gen_hash_init(k):
    """
    Generate 2**k hash initial states
    :param k: 
    :return: 
    """
    pass


def pair_up(hash_states):
    """
    Pair hash states and generate single-block collisions
    :param hash_states: 
    :return: [collision block, resulting state] * n
    """
    pass


