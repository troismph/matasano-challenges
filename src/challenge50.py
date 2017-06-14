from converts import fixed_xor, big_int_to_bin_str, cbc_mac_128, encrypt_aes_128_cbc

KEY = bytearray("YELLOW SUBMARINE")
MAC = bytearray(big_int_to_bin_str(int('296b8d7cb78a243dda4d0a61d33bbdd1', 16)))


def get_js():
    return "alert('MZA who was that?');\n"


def pad_with(s, c, block_len):
    """
    :type s: str 
    :type c: str
    :param block_len: 
    :return: 
    """
    n = block_len - (len(s) % block_len)
    return s + (c * n)


def get_forged_js(payload):
    payload = payload + "</script><noscript>"
    payload = pad_with(payload, "\n", 16)
    mask = encrypt_aes_128_cbc(bytearray(payload), KEY, None, False)[-16:]
    victim_js = get_js()
    malform = str(fixed_xor(bytearray(victim_js), mask)) + victim_js[16:]
    return payload + malform


def browser(get_js_func):
    """
    :type get_js_func:function 
    :return: 
    """
    template = '<script>{js}</script>'
    js = get_js_func()
    mac = cbc_mac_128(bytearray(js), KEY)
    assert mac == MAC, "MAC verification failed"
    with open('50.html', 'w') as f:
        f.write(template.format(js=js))
    print 'HTML written to 50.html, open it with a real browser.'


def crack():
    browser(lambda: get_forged_js("alert('Ayo, the Wu is back!');"))
