import os
import sys
import unittest

from tigertag.scanner import *
from tigertag.scanner.plex import *

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


class TestPlexScanner(unittest.TestCase):
    def on_file(self, scanner: Scanner, file_info: FileInfo):
        self.found_files[file_info.path] = file_info

    def setUp(self):
        self.found_files: dict[str, FileInfo] = {}
        self.s = PlexScanner('plex_scammer', True)
        self.s.props['TOKEN'] = os.environ['PLEX_TOKEN']
        self.s.props['SECTION'] = os.environ['PLEX_SECTION']
        self.s.props['URL'] = os.environ['PLEX_URL']
        sl = ScannerListener()
        sl.on_file = self.on_file
        self.s.listeners.append(sl)

    def test_run(self):
        self.s.scan()

        # Since these tests depend on your personal library, they have to be very generic
        self.assertGreater(len(self.found_files), 0)

