"""
Server and cracker mixed in one file
To run server:
python -c "import challenge31; challenge31.run_server()" 18080
To run cracker:
python -c "import challenge31; challenge31.cracker()"
"""

import web, urllib2
from time import sleep, time
from binascii import hexlify
from sys import stdout
import logging


urls = (
    '/test', 'Index'
)


SECRET_SIGNATURE = bytearray("87f0e629a264fc551001ecb27628bec7293a1192".decode('hex'))


class Index:
    def __init__(self):
        self.sig = SECRET_SIGNATURE

    def check_signature(self, signature):
        if len(signature) != len(self.sig):
            return False
        for x in range(len(signature)):
            if self.sig[x] != signature[x]:
                return False
            sleep(0.05)
        return True

    def GET(self):
        url_input = web.input(file=None, signature=None)
        signature = bytearray(url_input.signature.decode('hex'))
        return "{r}".format(r="Pass" if self.check_signature(signature) else "Fail")


def run_server():
    app = web.application(urls, globals())
    app.run()


def delay_test():
    # let's check what happens when trial signature errors in different digits
    for x in range(len(SECRET_SIGNATURE)):
        t = SECRET_SIGNATURE[:x] + '0' * (len(SECRET_SIGNATURE) - x)
        s = hexlify(t)
        begin_time = time()
        ret = urllib2.urlopen("http://127.0.0.1:18080/test?file=foo&signature={s}".format(s=s)).read()
        end_time = time()
        print ret, s, end_time - begin_time


def get_delay_avg(buf, n):
    s = hexlify(buf)
    query_url = "http://127.0.0.1:18080/test?file=foo&signature={s}".format(s=s)
    time_measures = []
    for x in range(n):
        begin_time = time()
        ret = urllib2.urlopen(query_url).read()
        end_time = time()
        time_measures.append(end_time - begin_time)
    return sum(time_measures) / len(time_measures)


def verify_guess(buf):
    s = hexlify(buf)
    query_url = "http://127.0.0.1:18080/test?file=foo&signature={s}".format(s=s)
    ret = urllib2.urlopen(query_url).read()
    print ret
    return ret == "Pass"


def analyze_delays(delays):
    # expect a single outstanding value
    threshold = 0.04
    delay_avg = sum([x[0] for x in delays]) / len(delays)
    diffs = [x for x in delays if x[0] - delay_avg > threshold]
    diffs.sort(reverse=True)
    return delay_avg, diffs


def cracker():
    logging.basicConfig(filename='c31.log', level=logging.DEBUG)
    logger = logging.getLogger('c31')
    avg_width = 1
    sig_len = len(SECRET_SIGNATURE)
    sig_guess = bytearray(sig_len)
    pos = 0
    while pos < sig_len:
        print "Guessing for pos {p}".format(p=pos)
        logger.debug("Guessing for pos {p}".format(p=pos))
        delays = []
        for byte_guess in range(256):
            sig_guess[pos] = byte_guess
            d = get_delay_avg(sig_guess, avg_width)
            delays.append([d, byte_guess])
            print "Trying value {v:02x} delay {d}\r".format(v=byte_guess, d=d),
            stdout.flush()
            logger.debug("Trying value {v:02x} delay {d}".format(v=byte_guess, d=d))
        delay_avg, diffs = analyze_delays(delays)
        if len(diffs) == 0:
            print "No outstanding delay found, retrying"
            logger.debug("No outstanding delay found, retrying")
            continue
        elif len(diffs) > 1:
            print "Multiple outstanding delays found, avg {a}, will retry".format(a=delay_avg)
            logger.debug("Multiple outstanding delays found, avg {a}, will retry".format(a=delay_avg))
            for d in diffs:
                print "Delay {x} guess {y:02x}".format(x=d[0], y=d[1])
                logger.debug("Delay {x} guess {y:02x}".format(x=d[0], y=d[1]))
                continue
        else:
            hit = diffs[0]
            sig_guess[pos] = hit[1]
            print "Pos {n} delay {d} delay_avg {da} guess {g:02x}".format(n=pos, d=hit[0], da=delay_avg, g=hit[1])
            logger.debug("Pos {n} delay {d} delay_avg {da} guess {g:02x}".format(n=pos, d=hit[0], da=delay_avg, g=hit[1]))
            pos = pos + 1
    if verify_guess(sig_guess):
        print "Cracked, " + hexlify(sig_guess)
    else:
        print "Failed"
