import logging

import yaml

from tigertag.engine import Engine
from tigertag.stasher import Stasher

logger = logging.getLogger(__name__)


class ConsoleStasher(Stasher):
    def __init__(self, name, enabled):
        super().__init__(name, enabled)

    def stash(self, engine: Engine, path: str, tags: dict):
        print(f'path: {path}')
        print(f'engine: {engine.name}')
        print(f'engine prefix: {engine.prefix}')
        print('tags:')
        print(yaml.safe_dump(tags))
