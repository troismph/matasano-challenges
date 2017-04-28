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


urls = (
    '/test', 'Index'
)


SECRET_SIGNATURE = bytearray("87f0e629a264fc551001ecb27628bec7293a1192".decode('hex'))
SLEEP_TIME = 0.05


class Index:
    def __init__(self):
        self.sig = SECRET_SIGNATURE
        print "sleep time {s}".format(s=SLEEP_TIME)

    def check_signature(self, signature):
        if len(signature) != len(self.sig):
            return False
        for x in range(len(signature)):
            if self.sig[x] != signature[x]:
                return False
            sleep(SLEEP_TIME)
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
    # if n >= 5:
    #     max_delay = max(time_measures)
    #     min_delay = min(time_measures)
    #     time_measures.remove(max_delay)
    #     time_measures.remove(min_delay)
    return sum(time_measures) / len(time_measures)


def verify_guess(buf):
    s = hexlify(buf)
    query_url = "http://127.0.0.1:18080/test?file=foo&signature={s}".format(s=s)
    ret = urllib2.urlopen(query_url).read()
    return ret == "Pass"


def analyze_delays(delays, threshold):
    # expect a single outstanding value
    delay_avg = sum([x[0] for x in delays]) / len(delays)
    diffs = [x for x in delays if x[0] - delay_avg > threshold]
    diffs.sort(reverse=True)
    return delay_avg, diffs


def update_candidates(cand, new_diff):
    if len(cand) == 0:
        return [x[1] for x in new_diff]
    else:
        return [x[1] for x in new_diff if x[1] in cand]


def cracker(avg_width=1, threshold=0.04):
    sig_len = len(SECRET_SIGNATURE)
    sig_guess = bytearray(sig_len)
    candidates = []
    pos = 0
    while pos < sig_len:
        print "Guessing for pos {p}".format(p=pos)
        delays = []
        for byte_guess in range(256):
            sig_guess[pos] = byte_guess
            d = get_delay_avg(sig_guess, avg_width)
            delays.append([d, byte_guess])
            print "Trying value {v:02x} delay {d}\r".format(v=byte_guess, d=d),
            stdout.flush()
        delay_avg, diffs = analyze_delays(delays, threshold)
        if len(diffs) == 0:
            print "No outstanding delay found, retrying"
            continue
        elif len(diffs) > 1:
            print "Multiple outstanding delays found, avg {a}".format(a=delay_avg)
            for d in diffs:
                print "Delay {x} guess {y:02x}".format(x=d[0], y=d[1])
            candidates = update_candidates(candidates, diffs)
            if len(candidates) == 1:
                print "Speculation from recent retries: {n:02x}".format(n=candidates[0])
                sig_guess[pos] = candidates[0]
                candidates = []
                pos = pos + 1
            else:
                print "Candidates updated to:"
                for c in candidates:
                    print "{c:02x}".format(c=c),
                print ""
                continue
        else:
            candidates = []
            hit = diffs[0]
            sig_guess[pos] = hit[1]
            print "Pos {n} delay {d} delay_avg {da} guess {g:02x}".format(n=pos, d=hit[0], da=delay_avg, g=hit[1])
            pos = pos + 1
    if verify_guess(sig_guess):
        print "Cracked, " + hexlify(sig_guess)
    else:
        print "Failed"
