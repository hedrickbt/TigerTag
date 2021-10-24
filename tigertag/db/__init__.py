import logging
import os

from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class Engine:
    RESERVED_PROPS = ['DB_URL']

    def __init__(self, db_url):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(self.engine)

    def connect(self, **kwargs):
        return self.engine.connect(**kwargs)

    def session(self):
        return self.Session()

    def dispose(self):
        self.engine.dispose()


class EngineBuilder:
    def __init__(self):
        pass

    def build(self):
        raise NotImplementedError


class EnvironmentEngineBuilder(EngineBuilder):
    def __init__(self):
        super().__init__()

    def build(self):
        if 'DB_URL' in os.environ.items():
            db_url = os.environ.get('DB_URL')
            return Engine(db_url)
        else:
            raise ValueError("DB_URL environment variable missing.")
