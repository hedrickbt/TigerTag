import unittest

from tigertag.notifier import *


class TestNotifier(unittest.TestCase):
    def setUp(self):
        self.s = Notifier('test_notifier', False)

    def test_init(self):
        self.assertEqual(self.s.name, 'test_notifier')
        self.assertEqual(self.s.enabled, False)

    def test_notify_not_implemented(self):
        self.assertRaises(NotImplementedError, self.s.notify, NotificationInfo('ex subject', 'ex message'))


class TestNotifierManager(unittest.TestCase):
    def setUp(self):
        self.sm = NotifierManager()
        self.s = Notifier('test_notifier_2', True)
        self.sm.add(self.s)

    def test_notifier_exists(self):
        self.assertGreater(len(self.sm.notifiers), 0)
        self.assertIn('test_notifier_2', self.sm.notifiers)
        self.assertEqual(self.s, self.sm.notifiers['test_notifier_2'])

    def test_notify_not_implemented(self):
        self.assertRaisesRegex(
            NotImplementedError,
            'The {} notifier has not implemented the notify method.'.format(self.s.name),
            self.sm.notify, NotificationInfo('ex subject', 'ex message'))


class TestEnvironmentNotifierManagerBuilder(unittest.TestCase):
    def setUp(self):
        os.environ['NOTIFIER_TEST_NAME'] = 'tigertag.notifier.Notifier'
        os.environ['NOTIFIER_TEST_ENABLED'] = 'True'
        os.environ['NOTIFIER_TEST_SPECIAL_PROPERTY'] = 'MySpecialPropertyValue'
        self.smb = EnvironmentNotifierManagerBuilder(NotifierManager)

    def test_build_success(self):
        sm = self.smb.build()
        self.assertIn('TEST', sm.notifiers)
        self.assertIn('SPECIAL_PROPERTY', sm.notifiers['TEST'].props)
        self.assertEqual('MySpecialPropertyValue', sm.notifiers['TEST'].props['SPECIAL_PROPERTY'])

    def test_notify_not_implemented(self):
        sm = self.smb.build()
        self.assertRaises(NotImplementedError, sm.notify, NotificationInfo('ex subject', 'ex message'))
