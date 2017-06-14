import urlparse
import os
import random
from string import digits
from converts import encrypt_aes_128_cbc, fixed_xor, pkcs7_pad


def cbc_mac_128(buf, key, iv):
    return encrypt_aes_128_cbc(bytearray(buf), key, iv)[-16:]


class Server(object):
    def __init__(self, key):
        self._key = key

    def verify(self, req):
        msg = req['message']
        iv = req['iv']
        mac = req['mac']
        mac_mine = cbc_mac_128(msg, self._key, iv)
        if mac != mac_mine:
            return False
        params = urlparse.parse_qs(msg)
        print 'Server transfering {amnt} from {src} to {dst}'.format(amnt=params['amount'][0], src=params['from'][0],
                                                                     dst=params['to'][0])
        return True

    @staticmethod
    def buggy_to_int(s):
        return int(filter(lambda x: x in digits, s))

    def verify_batch(self, req):
        msg = req['message']
        mac = req['mac']
        mac_mine = cbc_mac_128(msg, self._key, None)
        if mac != mac_mine:
            return False
        params = msg.split('&')
        for param in params:
            if param[:5] == 'from=':
                print 'Server transferring from {src}'.format(src=param[5:])
            elif param[:8] == 'tx_list=':
                print 'transactions'
                tx_list = param[8:].split(';')
                for tx in tx_list:
                    tx_parts = tx.split(':')
                    if len(tx_parts) != 2:
                        continue
                    dst = self.buggy_to_int(tx_parts[0])
                    amnt = self.buggy_to_int(tx_parts[1])
                    print 'to {dst} amount {amnt}'.format(dst=dst, amnt=amnt)
        return True


class Client(object):
    def __init__(self, key):
        self._key = key

    def make_req(self, src, dst, amnt):
        msg = 'from={src:#08}&to={dst:#08}&amount={amnt}'.format(src=src, dst=dst, amnt=amnt)
        iv = bytearray(os.urandom(16))
        mac = cbc_mac_128(msg, self._key, iv)
        return {'message': msg, 'iv': iv, 'mac': mac}

    def make_req_batch(self, src, dst_amnt_list):
        msg = 'from={src}&tx_list='.format(src=src)
        for dst, amnt in dst_amnt_list:
            msg += '{dst}:{amnt};'.format(dst=dst, amnt=amnt)
        mac = cbc_mac_128(msg, self._key, None)
        return {'message': msg, 'mac': mac}


def test_normal():
    n_round = 10
    key = bytearray(os.urandom(16))
    server = Server(key)
    client = Client(key)
    for x in range(n_round):
        src = random.randrange(999, 99999)
        dst = random.randrange(999, 99999)
        amnt = random.randrange(99999, 999999)
        req = client.make_req(src, dst, amnt)
        print req
        assert server.verify(req), 'Server verification failed'
    print 'Pass after {n} rounds'.format(n=n_round)


def forge_iv(req, victim_id):
    blk0 = req['message'][:16]
    blk_ = 'from={v_id:#08}{tail}'.format(v_id=victim_id, tail=blk0[13:])
    msg_ = blk_ + req['message'][16:]
    iv = req['iv']
    iv_ = fixed_xor(fixed_xor(bytearray(blk0), iv), bytearray(blk_))
    return iv_, msg_


def test_forge_iv():
    n_round = 10
    key = bytearray(os.urandom(16))
    server = Server(key)
    client = Client(key)
    victim_id = 9527
    for x in range(n_round):
        print 'Round {n} ============================='.format(n=x)
        src = random.randrange(999, 99999)
        dst = random.randrange(999, 99999)
        amnt = random.randrange(99999, 999999)
        req = client.make_req(src, dst, amnt)
        print 'Original request verified by server'
        assert server.verify(req), 'Server verification failed'
        iv_, msg_ = forge_iv(req, victim_id)
        req['iv'] = iv_
        req['message'] = msg_
        print 'Forged request verified by server'
        assert server.verify(req), 'Server verification failed'
    print 'Pass after {n} rounds'.format(n=n_round)


def forge_batch_mac(client, req, dst, amnt):
    """
    :type client: Client 
    :param req: 
    :param dst: 
    :param amnt: 
    :return: 
    """
    msg = bytearray(req['message'])
    pkcs7_pad(msg, 16)
    req_s = client.make_req_batch(dst, [(dst, amnt)])
    msg_s = req_s['message']
    msg_head = fixed_xor(bytearray(msg_s[:16]), req['mac'])
    msg_ = str(msg) + str(msg_head) + msg_s[16:]
    return msg_, req_s['mac']


def test_forge_batch_mac():
    key = bytearray(os.urandom(16))
    server = Server(key)
    client = Client(key)
    victim = 9527
    req = client.make_req_batch(victim, [(987, 100), (654, 1000)])
    print 'Original request verified by server'
    assert server.verify_batch(req), 'Server verification failed'
    msg, mac = forge_batch_mac(client, req, 55, 1000000)
    req_ = {'message': msg, 'mac': mac}
    print 'Forged request verified by server'
    assert server.verify_batch(req_), 'Server verification failed'
