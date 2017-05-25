"""
Server and cracker mixed in one file
To run server:
python -c "import challenge32; challenge32.run_server(True)" 18080
To run cracker:
python -c "import challenge32; challenge32.cracker()"
"""

import challenge31 as c31


c31.SLEEP_TIME = 0.01


class NullOutputStream(object):

    def write(self, data):
        pass


def run_server(no_log=False):
    if no_log:
        import sys
        sys.stdout = NullOutputStream()
        sys.stderr = NullOutputStream()
    c31.run_server()


def cracker():
    c31.cracker(10, 0.01)
