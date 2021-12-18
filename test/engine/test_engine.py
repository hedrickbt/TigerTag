import unittest

from tigertag.engine import *


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.e = Engine('test_engine', 'tst', False)

    def test_init(self):
        self.assertEqual(self.e.name, 'test_engine')
        self.assertEqual(self.e.prefix, 'tst')
        self.assertEqual(self.e.enabled, False)

    def test_tag_not_implemented(self):
        self.assertRaises(NotImplementedError, self.e.tag, 'path_ex', 'temp_ex', 'ext_id_ex')


class TestEngineManager(unittest.TestCase):
    def setUp(self):
        self.em = EngineManager()
        self.e = Engine('test_engine_2', 'tst', True)
        self.em.add(self.e)

    def test_engine_exists(self):
        self.assertGreater(len(self.em.engines), 0)
        self.assertIn('test_engine_2', self.em.engines)
        self.assertEqual(self.e, self.em.engines['test_engine_2'])

    def test_tag_not_implemented(self):
        self.assertRaisesRegex(
            NotImplementedError,
            'The {} engine has not implemented the tag method.'.format(self.e.name),
            self.em.tag, 'path_ex', 'temp_ex', 'ext_id_ex')

    def _tag_stub(self, path: str, temp: str, ext_id: str):
        pass

    def test_duplicate_prefix(self):
        self.e.tag = self._tag_stub
        self.e3 = Engine('test_engine_3', 'tst', True)
        self.e3.tag = self._tag_stub
        self.em.add(self.e3)
        self.assertRaisesRegex(
            ValueError,
            'Duplicate prefix {} found in {} engine.  Removing the engine or changing the prefix '
            'will resolve the issue.'.format(self.e3.prefix, self.e3.name),
            self.em.tag, 'Not Needed')

    def test_missing_prefix(self):
        self.e.prefix = None
        self.assertRaisesRegex(
            AttributeError,
            'The {} engine is missing the prefix attribute'.format(self.e.name),
            self.em.tag, 'path_ex', 'temp_ex', 'ext_id_ex')


class TestEnvironmentEngineManagerBuilder(unittest.TestCase):
    def setUp(self):
        os.environ['ENGINE_TEST_NAME'] = 'tigertag.engine.Engine'
        os.environ['ENGINE_TEST_PREFIX'] = 'tst'
        os.environ['ENGINE_TEST_ENABLED'] = 'True'
        os.environ['ENGINE_TEST_SPECIAL_PROPERTY'] = 'MySpecialPropertyValue'
        self.emb = EnvironmentEngineManagerBuilder(EngineManager)

    def test_build_success(self):
        em = self.emb.build()
        self.assertIn('TEST', em.engines)
        self.assertIn('SPECIAL_PROPERTY', em.engines['TEST'].props)
        self.assertEqual('MySpecialPropertyValue', em.engines['TEST'].props['SPECIAL_PROPERTY'])

    def test_tag_not_implemented(self):
        em = self.emb.build()
        em.engines['TEST'].prefix = 'ttt'
        self.assertRaises(NotImplementedError, em.tag, 'path_ex', 'temp_ex', 'ext_id_ex')
