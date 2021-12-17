import sys
import unittest
from contextlib import contextmanager
from io import StringIO

from tigertag.stasher import *
from tigertag.stasher.console import *

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    try:
        command(*args, **kwargs)
        sys.stdout.seek(0)
        yield sys.stdout.read()
    finally:
        sys.stdout = out


class TestConsoleStasher(unittest.TestCase):
    def setUp(self):
        self.s = ConsoleStasher('console_stasher', True)

    def test_run(self):
        with capture(self.s.stash, Engine('test_engine', True), '/image.png', {'tag': 'hi'}) as output:
            self.assertEquals('path: /image.png\nengine: test_engine\ntags:\ntag: hi\n\n', output)

