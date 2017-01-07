#!/usr/bin/python

from common.converts import unhex


def eval_dup(s):
    stat = {}
    chips = [s[x : x + 16] for x in range(0, len(s), 16)]
    for c in chips:
        stat[c] = stat.get(c, 0) + 1
    return stat

def detect_stat(stat):
    ret = {}
    for key, val in stat.items():
        if val > 1:
            ret[key] = val
    return ret

def run():
    with open("set1/8.txt") as f:
        ciphers = [str(unhex(line.rstrip())) for line in f.readlines()]
    lc = 0
    for c in ciphers:
        stat = eval_dup(c)
        detect = detect_stat(stat)
        if len(detect) > 0:
            print "ECB detected at line %d" % lc
            print detect
        lc += 1

run()
