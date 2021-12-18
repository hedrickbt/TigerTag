import logging
import os
import re

from tigertag.util import str2bool
from tigertag.engine import Engine

logger = logging.getLogger(__name__)


class Stasher:
    RESERVED_PROPS = ['NAME', 'ENABLED']

    def __init__(self, name, enabled):
        self.name = name
        self.enabled = enabled
        self.props = {}

    def stash(self, engine: Engine, path: str, tags: dict, ext_id: str):
        raise NotImplementedError('The {} stasher has not implemented the stash method.'.format(self.name))


class StasherManager:
    def __init__(self):
        self.stashers = {}

    def add(self, stasher):
        self.stashers[stasher.name] = stasher

    def stash(self, engine: Engine, path: str, tags: dict, ext_id: str):
        if len(self.stashers) == 0:
            logger.warning('No stashers configured.  Please check your configuration')
        for stasher_name, stasher in self.stashers.items():
            if stasher.enabled:
                stasher.stash(engine, path, tags, ext_id)


class StasherManagerBuilder:
    def __init__(self, stasher_manager_klass):
        self.stasher_manager_klass = stasher_manager_klass

    def build(self):
        raise NotImplementedError


class EnvironmentStasherManagerBuilder(StasherManagerBuilder):
    def __init__(self, stasher_manager_klass):
        super().__init__(stasher_manager_klass)

    def get_class(self, klass_name):
        parts = klass_name.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m

    def build(self):
        sm = self.stasher_manager_klass()
        stasher_detect = re.compile('^STASHER_(?P<stasher>[A-Z0-9]*)_NAME')

        # Find and create the stashers
        for env_name, env_value in os.environ.items():
            match = stasher_detect.match(env_name)
            if match is not None:
                logger.debug('Configuring stasher {}:{}'.format(env_name, env_value))
                stasher_env_name = match.group('stasher')
                stasher_klass_name = env_value
                enabled = False
                if os.environ['STASHER_{}_ENABLED'.format(stasher_env_name)] is not None:
                    enabled = str2bool(os.environ['STASHER_{}_ENABLED'.format(stasher_env_name)])
                stasher_klass = self.get_class(stasher_klass_name)
                stasher = stasher_klass(stasher_env_name, enabled)

                # Collect all the stasher properties
                prop_detect = re.compile('^STASHER_{}_(?P<prop>[A-Z0-9_]*)'.format(stasher_env_name))
                for env_prop_name, env_prop_value in os.environ.items():
                    prop_match = prop_detect.match(env_prop_name)
                    if prop_match is not None:
                        prop_name = prop_match.group('prop')
                        if prop_name not in [Stasher.RESERVED_PROPS]:
                            stasher.props[prop_name] = env_prop_value
                sm.add(stasher)
        return sm
