from challenge21 import MT19937
import time
import random


def target_routine():
    start_time = int(time.time())
    seed = start_time + random.randrange(40, 1000)
    mt = MT19937(seed)
    return mt.get_next(), seed


def seed_finder():
    rn, seed = target_routine()
    seed_base = int(time.time())
    try_range = 1000
    guess = None
    for x in range(seed_base, seed_base + try_range):
        mt = MT19937(x)
        if mt.get_next() == rn:
            guess = x
            break
    if guess == seed:
        print 'guess match'
    else:
        print 'guess failed'
    print 'target RNG 1st number: {trn}, seed: {ts}'.format(trn=rn, ts=seed)
    print 'guess seed: {gs}'.format(gs=guess)


seed_finder()
