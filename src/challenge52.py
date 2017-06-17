import sys

from md_hash import find_collision, make_combines, HARD_BLOCK_LEN_BYTES, hash_easy, hash_hard


EASY_KEY = bytearray(b'\x9es')
HARD_KEY = bytearray(b'\xbc\x78\x2f\xa2')


def collisions_for_debug():
    return [['4Ku0N1Q7V2', 'XO'],
            ['5uo9TBlOdEff', 'Oh6jCq'],
            ['AHJ2s4', 'NXuj5lEkBdsoqoK9FEEpExIm'],
            ['RMuAZ5gY9z4R7T0OofmSzfNm', 'mKMe66'],
            ['HhrHro39Bm', '5ZA94XSADxPIL5Z2XuewkXhg'],
            ['PghKnn4dDHGRrgfAmUs6CNKyr4', 'nH'],
            ['LQ', 'Snytw1dtFcxHMcRO24m9sDYShX8J'],
            ['S30YGmNHyT3s', '2Gd20tieLvvB7CkiifoX'],
            ['MPwbuQ8vDjNyOfdZ1tAeUAI6riRlUd', 'Nt8H4GDZAs6NKeHvkYE73zmE'],
            ['Gy', '12gXVVzYRZMJmaUKDZq8mo'],
            ['rc0UwRLtfkKMpAQzExSkxLGn', 'piVe8sQ47KZWbwAPCIa7kn'],
            ['TxIWPhUKgFV0BqUFD2TgbHp6Yf', 'nQeIKc'],
            ['hnf4rDmICo4fCpjDVksAVDFd7LAL', '31TrrYJIcr7TkaXt4t'],
            ['gM72Zm', 'fIxXQtpWgV2jAo58WZXl'],
            ['ahNWFKG0KIZ25LSR9YfK', 'LcCDQCjhX9h5hV5Q0XJvJ0ARYphE'],
            ['dpgW', 'RcOKJK8sbuZztihZ8s']]


def find_2n_collision(n):
    collisions = []
    h = EASY_KEY
    while len(collisions) < n:
        r = find_collision(h, hash_easy)
        if r is None:
            print "Bad luck, retrying"
            continue
        m0, m1 = r
        h = hash_easy(m0, h)
        print "Collision found {m0}, {m1}, {h}".format(m0=m0, m1=m1, h=str(h).encode('hex'))
        collisions.append(r)
    return make_combines(collisions)


def test_find_2n_collision(n):
    h = None
    head_c = None
    for t in find_2n_collision(n):
        c = ''.join(t)
        if h is None:
            h = hash_easy(c, EASY_KEY)
            head_c = c
            continue
        h_ = hash_easy(c, EASY_KEY)
        assert h == h_, 'Inequal hash {head_c}, {c}'.format(head_c=head_c, c=c)
    print 'Pass'


def find_collision_in_pool(pool, ps):
    nb = {}
    ctr = 0
    for p in pool:
        m = ''.join(p)
        ctr += 1
        if ctr & 0xff == 0xff:
            print '\rSearching {ctr:x}/{ps:x}'.format(ctr=ctr, ps=ps) + ' ' * 10,
            sys.stdout.flush()
        h = str(hash_hard(m, HARD_KEY))
        if h not in nb:
            nb[h] = [m]
        else:
            nb[h].append(m)
            print "\nFound, {h}:{ms}".format(h=str(h).encode('hex'), ms=nb[h])
    ret = []
    for k, v in nb.items():
        if len(v) > 1:
            ret.append(v)
    return ret


def test_find_collision_in_pool():
    basis = collisions_for_debug()
    pool = make_combines(basis)
    ret = find_collision_in_pool(pool, 1 << (HARD_BLOCK_LEN_BYTES * 8 / 2))
    assert len(ret) > 0, 'Failed to find collisions in pool'
    for x in ret:
        h = hash_hard(x[0], HARD_KEY)
        print "hash: {h}".format(h=str(h).encode('hex'))
        for y in x:
            print y


def find_chain_collision():
    easy_collisions = find_2n_collision(HARD_BLOCK_LEN_BYTES * 8 / 2)
    ps = 1 << (HARD_BLOCK_LEN_BYTES * 8 / 2)
    ret = find_collision_in_pool(easy_collisions, ps)
    if len(ret) > 0:
        print "Found harder collision"
        for x in ret:
            h = hash_hard(x[0], HARD_KEY)
            print "hash: {h}".format(h=str(h).encode('hex'))
            for y in x:
                print y
