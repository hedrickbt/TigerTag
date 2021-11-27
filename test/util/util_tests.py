import os
import tempfile
import unittest

from tigertag.util import str2bool
from tigertag.util import calc_digest


class TestStr2Bool(unittest.TestCase):
    def test_values(self):
        ("yes", "true", "t", "1")
        self.assertTrue(str2bool("yes"))
        self.assertTrue(str2bool("YES"))
        self.assertTrue(str2bool("Yes"))
        self.assertTrue(str2bool("true"))
        self.assertTrue(str2bool("TRUE"))
        self.assertTrue(str2bool("True"))
        self.assertTrue(str2bool("t"))
        self.assertTrue(str2bool("T"))
        self.assertTrue(str2bool("1"))
        self.assertFalse(str2bool(" yes"))
        self.assertFalse(str2bool("yess"))
        self.assertFalse(str2bool("no"))
        self.assertFalse(str2bool("NO"))
        self.assertFalse(str2bool("No"))
        self.assertFalse(str2bool("false"))
        self.assertFalse(str2bool("FALSE"))
        self.assertFalse(str2bool("False"))
        self.assertFalse(str2bool("f"))
        self.assertFalse(str2bool("F"))
        self.assertFalse(str2bool("0"))
        self.assertFalse(str2bool("11"))


class TestStr2Bool(unittest.TestCase):
    def setUp(self):
        file, self.file_path = tempfile.mkstemp()
        os.close(file)
        with open(self.file_path, 'w') as file:
            file.write('Test file!!')

    def test_calc_digest(self):
        hash_result = calc_digest(self.file_path)
        self.assertEqual('3195ef5da827122ffaadaab5c7c2f396f0245ad06a741fa9e966957284130f61', hash_result)

    def tearDown(self):
        os.remove(self.file_path)
