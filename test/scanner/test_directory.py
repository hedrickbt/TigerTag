import os
import sys
import unittest

from tigertag.scanner import *
from tigertag.scanner.directory import *

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class TestDirectoryScanner(unittest.TestCase):
    def on_file(self, scanner, file_info):
        self.found_files[file_info['file_path']] = file_info

    def setUp(self):
        self.scan_path = os.path.join(os.getcwd(), 'data')
        self.found_files = {}
        self.s = DirectoryScanner('directory_scanner', True, self.scan_path)
        sl = ScannerListener()
        sl.on_file = self.on_file
        self.s.listeners.append(sl)

    def test_run(self):
        self.s.scan()

        self.assertEqual(4, len(self.found_files))
        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'boy.jpg'))
        self.assertIn(test_file_path, self.found_files)
        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'girl.jpg'))
        self.assertIn(test_file_path, self.found_files)
        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'puppy.jpg'))
        self.assertIn(test_file_path, self.found_files)
        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'sunflower.jpg'))
        self.assertIn(test_file_path, self.found_files)


