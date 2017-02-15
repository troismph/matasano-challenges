from converts import pkcs7_unpad


BLOCK_LEN = 16

def run():
    cases = [
        [bytearray("ICE ICE BABY\x04\x04\x04\x04"), bytearray("ICE ICE BABY")],
        [bytearray("ICE ICE BABY\x05\x05\x05\x05"), None],
        [bytearray("ICE ICE BABY\x01\x02\x03\x04"), None]
    ]
    for c in cases:
        if c[1] is None:
            try:
                pkcs7_unpad(c[0], BLOCK_LEN)
                print "Case fail, raise expected: {c}".format(c=c[0])
            except ValueError as e:
                print "Case pass: {c}".format(c=c[0])
                continue
        else:
            pkcs7_unpad(c[0], BLOCK_LEN)
            if c[0] == c[1]:
                print "Case pass: {c}".format(c=c[0])
            else:
                print "Case fail: {c} -> {d}".format(c=c[0], d=c[1])

run()


