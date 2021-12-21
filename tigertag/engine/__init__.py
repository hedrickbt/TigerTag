import logging
import os
import re
from collections import namedtuple

from tigertag import Pluggable
from tigertag.util import str2bool

logger = logging.getLogger(__name__)

TagInfo = namedtuple('TagInfo', 'path tags')


class Engine(Pluggable):
    RESERVED_PROPS = ['NAME', 'ENABLED', 'PREFIX']

    def __init__(self, name, prefix, enabled):
        self.name = name
        self.enabled = enabled
        self.props = {}
        self.prefix = prefix
        self.listeners = []  # EngineListeners

    def tag(self, path: str, temp: str = None, ext_id: str = None):
        raise NotImplementedError('The {} engine has not implemented the tag method.'.format(self.name))

    def calc_tag_name(self, tag_name):
        return '{}_{}'.format(self.prefix, tag_name)


class EngineListener:
    def on_tags(self, engine: Engine, tag_info: TagInfo, ext_id: str):
        pass


class EngineManager:
    def __init__(self):
        self.engines = {}
        self.listeners = []  # EngineListener array

    def add(self, engine):
        self.engines[engine.name] = engine

    def tag(self, path: str, temp: str = None, ext_id: str = None):
        prefixes = []
        if len(self.engines) == 0:
            logger.warning('No tag engines configured.  Please check your configuration')
        for engine_name, engine in self.engines.items():
            if engine.prefix is None:
                raise AttributeError('The {} engine is missing the prefix attribute.'.format(engine_name))
            if engine.prefix in prefixes:
                raise ValueError('Duplicate prefix {} found in {} engine.  Removing the engine or changing the '
                                 'prefix will resolve the issue.'.format(engine.prefix, engine_name))
            if engine.enabled:
                engine.listeners = []
                for engine_listener in self.listeners:
                    engine.listeners.append(engine_listener)
                engine.tag(path, temp, ext_id)
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
                logger.debug('Configuring engine {}:{}'.format(env_name, env_value))
                engine_env_name = match.group('engine')
                engine_klass_name = env_value
                enabled = False
                if os.environ['ENGINE_{}_ENABLED'.format(engine_env_name)] is not None:
                    enabled = str2bool(os.environ['ENGINE_{}_ENABLED'.format(engine_env_name)])
                prefix = os.environ['ENGINE_{}_PREFIX'.format(engine_env_name)]
                engine_klass = self.get_class(engine_klass_name)
                engine = engine_klass(engine_env_name, prefix, enabled)

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
