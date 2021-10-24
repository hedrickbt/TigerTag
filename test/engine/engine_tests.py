import unittest

from tigertag.engine import *


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.e = Engine('test_engine', False)

    def test_init(self):
        self.assertEqual(self.e.name, 'test_engine')
        self.assertEqual(self.e.enabled, False)

    def test_run_not_implemented(self):
        self.assertRaises(NotImplementedError, self.e.run)


class TestEngineManager(unittest.TestCase):
    def setUp(self):
        self.em = EngineManager()
        self.e = Engine('test_engine_2', True)
        self.em.add(self.e)

    def test_engine_exists(self):
        self.assertGreater(len(self.em.engines), 0)
        self.assertIn('test_engine_2', self.em.engines)
        self.assertEqual(self.e, self.em.engines['test_engine_2'])

    def test_run_not_implemented(self):
        self.assertRaises(NotImplementedError, self.em.run)


class TestEnvironmentEngineManagerBuilder(unittest.TestCase):
    def setUp(self):
        os.environ['ENGINE_TEST_NAME'] = 'tigertag.engine.Engine'
        os.environ['ENGINE_TEST_ENABLED'] = 'True'
        os.environ['ENGINE_TEST_SPECIAL_PROPERTY'] = 'MySpecialPropertyValue'
        self.emb = EnvironmentEngineManagerBuilder(EngineManager)

    def test_build_success(self):
        em = self.emb.build()
        self.assertIn('TEST', em.engines)
        self.assertIn('SPECIAL_PROPERTY', em.engines['TEST'].props)
        self.assertEqual('MySpecialPropertyValue', em.engines['TEST'].props['SPECIAL_PROPERTY'])

    def test_run_not_implemented(self):
        em = self.emb.build()
        self.assertRaises(NotImplementedError, em.run)
