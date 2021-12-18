import os
import unittest

from tigertag.stasher import *


class TestStasher(unittest.TestCase):
    def setUp(self):
        self.s = Stasher('test_stasher', False)

    def test_init(self):
        self.assertEqual(self.s.name, 'test_stasher')
        self.assertEqual(self.s.enabled, False)

    def test_stash_not_implemented(self):
        self.assertRaises(NotImplementedError, self.s.stash, None, 'path_ex', {}, 'ext_id_ex')


class TestStasherManager(unittest.TestCase):
    def setUp(self):
        self.sm = StasherManager()
        self.s = Stasher('test_stasher_2', True)
        self.sm.add(self.s)

    def test_stasher_exists(self):
        self.assertGreater(len(self.sm.stashers), 0)
        self.assertIn('test_stasher_2', self.sm.stashers)
        self.assertEqual(self.s, self.sm.stashers['test_stasher_2'])

    def test_stash_not_implemented(self):
        self.assertRaisesRegex(
            NotImplementedError,
            'The {} stasher has not implemented the stash method.'.format(self.s.name),
            self.sm.stash,
            None,
            'path_ex',
            {},
            'ext_id_ex'
        )


class TestEnvironmentStasherManagerBuilder(unittest.TestCase):
    def setUp(self):
        os.environ['STASHER_TEST_NAME'] = 'tigertag.stasher.Stasher'
        os.environ['STASHER_TEST_ENABLED'] = 'True'
        os.environ['STASHER_TEST_SPECIAL_PROPERTY'] = 'MySpecialPropertyValue'
        self.smb = EnvironmentStasherManagerBuilder(StasherManager)

    def test_build_success(self):
        sm = self.smb.build()
        self.assertIn('TEST', sm.stashers)
        self.assertIn('SPECIAL_PROPERTY', sm.stashers['TEST'].props)
        self.assertEqual('MySpecialPropertyValue', sm.stashers['TEST'].props['SPECIAL_PROPERTY'])

    def test_stash_not_implemented(self):
        sm = self.smb.build()
        self.assertRaises(NotImplementedError, sm.stash, None, 'path_ex', {}, 'ext_id_ex')
