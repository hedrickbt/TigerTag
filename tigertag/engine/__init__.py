import logging
import os
import re

from tigertag.util import str2bool

logger = logging.getLogger(__name__)


class Engine:
    RESERVED_PROPS = ['NAME', 'ENABLED']

    def __init__(self, name, enabled):
        self.name = name
        self.enabled = enabled
        self.props = {}
        self.prefix = None
        self.on_tags = None  # callback to receive tags for each resource as it is processed

    def run(self):
        raise NotImplementedError('The {} engine has not implemented the run method.'.format(self.name))


class EngineManager:
    def __init__(self):
        self.engines = {}

    def add(self, engine):
        self.engines[engine.name] = engine

    def run(self):
        prefixes = []
        for engine_name, engine in self.engines.items():
            if engine.prefix is None:
                raise AttributeError('The {} engine is missing the prefix attribute.'.format(engine_name))
            if engine.prefix in prefixes:
                raise ValueError('Duplicate prefix {} found in {} engine.  Removing the engine or changing the '
                                 'prefix will resolve the issue.'.format(engine.prefix, engine_name))
            if engine.enabled:
                engine.run()
                prefixes.append(engine.prefix)


class EngineManagerBuilder:
    def __init__(self, engine_manager_klass):
        self.engine_manager_klass = engine_manager_klass

    def build(self):
        raise NotImplementedError


class EnvironmentEngineManagerBuilder(EngineManagerBuilder):
    def __init__(self, engine_manager_klass):
        super().__init__(engine_manager_klass)

    def get_class(self, klass_name):
        parts = klass_name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def build(self):
        em = self.engine_manager_klass()
        engine_detect = re.compile('^ENGINE_(?P<engine>[A-Z0-9]*)_NAME')

        # Find and create the engines
        for env_name, env_value in os.environ.items():
            match = engine_detect.match(env_name)
            if match is not None:
                print(env_name + ':', env_value)
                engine_env_name = match.group('engine')
                engine_klass_name = env_value
                enabled = False
                if os.environ['ENGINE_{}_ENABLED'.format(engine_env_name)] is not None:
                    enabled = str2bool(os.environ['ENGINE_{}_ENABLED'.format(engine_env_name)])
                engine_klass = self.get_class(engine_klass_name)
                engine = engine_klass(engine_env_name, enabled)

                # Collect all the engine properties
                prop_detect = re.compile('^ENGINE_{}_(?P<prop>[A-Z0-9_]*)'.format(engine_env_name))
                for env_prop_name, env_prop_value in os.environ.items():
                    prop_match = prop_detect.match(env_prop_name)
                    if prop_match is not None:
                        prop_name = prop_match.group('prop')
                        if prop_name not in [Engine.RESERVED_PROPS]:
                            engine.props[prop_name] = env_prop_value
                em.add(engine)
        return em
