import os
import sys
import unittest

from tigertag.scanner import *
from tigertag.scanner.directory import *

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(name)s : %(funcName)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


class TestDirectoryScanner(unittest.TestCase):
    def on_file(self, scanner, file_info):
        self.found_files[file_info['file_path']] = file_info

    def setUp(self):
        self.scan_path = os.path.join(os.getcwd(), 'data')
        self.found_files = {}
        self.s = DirectoryScanner('directory_scanner', True)
        self.s.props['PATH'] = self.scan_path
        sl = ScannerListener()
        sl.on_file = self.on_file
        self.s.listeners.append(sl)

    def test_run(self):
        self.s.scan()

        self.assertEqual(4, len(self.found_files))
        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'boy.jpg'))
        self.assertIn(test_file_path, self.found_files)
        file_info = self.found_files[test_file_path]
        self.assertEqual('2b87de0a02694a0448471066fe0bff79b1ab555da4d16c36560e14b18d22e42a',
                         file_info['file_hash'])
        self.assertEqual('boy.jpg', file_info['file_name'])

        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'girl.jpg'))
        self.assertIn(test_file_path, self.found_files)
        file_info = self.found_files[test_file_path]
        self.assertEqual('d88456c386f2f4a1165728162419a230d7dc75f73198aa685a0ac03cf3ba2ab2',
                         file_info['file_hash'])
        self.assertEqual('girl.jpg', file_info['file_name'])

        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'puppy.jpg'))
        self.assertIn(test_file_path, self.found_files)
        file_info = self.found_files[test_file_path]
        self.assertEqual('f4d9d946c0ff1ded0ce1c5139a5a0eb8d0e514d5e4256ee5afe6d89bba68470c',
                         file_info['file_hash'])
        self.assertEqual('puppy.jpg', file_info['file_name'])

        test_file_path = os.path.normpath(os.path.join(os.getcwd(), 'data', 'images', 'input', 'sunflower.jpg'))
        self.assertIn(test_file_path, self.found_files)
        file_info = self.found_files[test_file_path]
        self.assertEqual('7bbafa42a91fba3eea845133afa79f7e665c80ffc1d8e2ca53be25120c4cfe66',
                         file_info['file_hash'])
        self.assertEqual('sunflower.jpg', file_info['file_name'])


