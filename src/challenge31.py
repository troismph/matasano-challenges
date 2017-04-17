import web, urllib2
from time import sleep, time


urls = (
    '/test', 'Index'
)


SECRET_SIGNATURE = "87f0e629a264fc551001ecb27628bec7293a1192"


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
        signature = url_input.signature
        return "{r}".format(r="Pass" if self.check_signature(signature) else "Fail")


def run_server():
    app = web.application(urls, globals())
    app.run()


def delay_test():
    sig = bytearray(20)
    # let's check what happens when trial signature errors in different digits
    for x in range(len(SECRET_SIGNATURE)):
        t = SECRET_SIGNATURE[:x] + '0' * (len(SECRET_SIGNATURE) - x)
        begin_time = time()
        ret = urllib2.urlopen("http://127.0.0.1:18080/test?file=foo&signature={s}".format(s=t)).read()
        end_time = time()
        print ret, t, end_time - begin_time

