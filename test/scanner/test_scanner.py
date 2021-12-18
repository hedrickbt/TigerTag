import unittest

from tigertag.scanner import *


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.s = Scanner('test_scanner', False)

    def test_init(self):
        self.assertEqual(self.s.name, 'test_scanner')
        self.assertEqual(self.s.enabled, False)

    def test_scan_not_implemented(self):
        self.assertRaises(NotImplementedError, self.s.scan)


class TestScannerManager(unittest.TestCase):
    def setUp(self):
        self.sm = ScannerManager()
        self.s = Scanner('test_scanner_2', True)
        self.sm.add(self.s)

    def test_scanner_exists(self):
        self.assertGreater(len(self.sm.scanners), 0)
        self.assertIn('test_scanner_2', self.sm.scanners)
        self.assertEqual(self.s, self.sm.scanners['test_scanner_2'])

    def test_scan_not_implemented(self):
        self.assertRaisesRegex(
            NotImplementedError,
            'The {} scanner has not implemented the scan method.'.format(self.s.name),
            self.sm.scan)


class TestEnvironmentScannerManagerBuilder(unittest.TestCase):
    def setUp(self):
        os.environ['SCANNER_TEST_NAME'] = 'tigertag.scanner.Scanner'
        os.environ['SCANNER_TEST_ENABLED'] = 'True'
        os.environ['SCANNER_TEST_SPECIAL_PROPERTY'] = 'MySpecialPropertyValue'
        self.smb = EnvironmentScannerManagerBuilder(ScannerManager)

    def test_build_success(self):
        sm = self.smb.build()
        self.assertIn('TEST', sm.scanners)
        self.assertIn('SPECIAL_PROPERTY', sm.scanners['TEST'].props)
        self.assertEqual('MySpecialPropertyValue', sm.scanners['TEST'].props['SPECIAL_PROPERTY'])

    def test_scan_not_implemented(self):
        sm = self.smb.build()
        self.assertRaises(NotImplementedError, sm.scan)
