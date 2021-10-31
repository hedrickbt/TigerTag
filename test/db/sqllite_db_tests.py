import datetime
import os.path
import unittest

from tigertag.db import *
from tigertag.db.models import *
from alembic import command

from sqlalchemydiff.util import (
    destroy_database,
    new_db,
)

from alembicverify.util import (
    make_alembic_config,
)

from sqlalchemy.sql import select, text

DB_NAME = 'tigertag_demo.db'
DB_URL = 'sqlite:///{}'.format(DB_NAME)
ALEMBIC_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'alembic')
ALEMBIC_LOG_CONFIG = os.path.join(os.path.dirname(__file__), '..', '..', 'alembic.ini')


class TestEngine(unittest.TestCase):
    def setUp(self):
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
        self.e = Engine(DB_URL)
        # self.c = None

    def test_init(self):
        self.assertEqual(self.e.db_url, DB_URL)

    # def test_connect(self):
    #     self.c = self.e.connect()

    def tearDown(self):
        # if self.c:
        #     self.c.close()
        self.e.dispose()
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)


class BaseSqlite(unittest.TestCase):
    def setUp(self):
        # HELPFUL https://alembic-verify.readthedocs.io/en/latest/example_unittest.html
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)

        self.test_uri = DB_URL
        self.alembic_config = make_alembic_config(
            self.test_uri, ALEMBIC_ROOT)
        self.alembic_config.config_file_name = ALEMBIC_LOG_CONFIG
        new_db(self.test_uri)
        command.upgrade(self.alembic_config, 'head')

    def tearDown(self):
        self.e.dispose()
        destroy_database(self.test_uri)
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)


class TestEnvironmentEngineBuilder(BaseSqlite):
    def setUp(self):
        super().setUp()
        os.environ['DB_URL'] = DB_URL
        builder = EnvironmentEngineBuilder()
        self.e = builder.build()

    def test_current_time_raw(self):
        date_format = "%Y-%m-%d"
        with self.e.connect() as con:
            rs = con.execute("SELECT strftime('{}','now')".format(date_format))
            for row in rs:
                temp_date = datetime.date.today().strftime(date_format)
                self.assertEqual(row[0], temp_date)
                break

    def test_current_time_raw_text(self):
        date_format = "%Y-%m-%d"
        statement = text("""SELECT strftime('{}','now')""".format(date_format))
        with self.e.connect() as con:
            rs = con.execute(statement)
            for row in rs:
                temp_date = datetime.date.today().strftime(date_format)
                self.assertEqual(row[0], temp_date)
                break


class TestEngineWithData(BaseSqlite):
    def setUp(self):
        super().setUp()
        self.e = Engine(DB_URL)

    def temp_tag_obj(self):
        return Tag(
            name='person',
            engine='IMAGGA',
            percent_match=45
        )

    def temp_resource_obj(self, temp_date_time):
        return Resource(
            name='smile.png',
            location='data/images/input/smile.png',
            hash='3e44cfaa9a914f1312d157130810300f',
            last_indexed=temp_date_time,
        )

    def test_tag(self):
        person_tag = self.temp_tag_obj()
        with self.e.session() as session, session.begin():
            session.add(person_tag)
            session.flush()
            self.assertEqual(1, person_tag.id)
        # inner context [session.begin()] calls session.commit(), if there were no exceptions
        # outer context calls session.close()

        with self.e.session() as session, session.begin():
            person_tag = session.execute(select(Tag).filter_by(id=1)).scalar_one()
            self.assertEqual('person', person_tag.name)
            self.assertEqual('IMAGGA', person_tag.engine)
            self.assertEqual(45, person_tag.percent_match)

    def test_resource(self):
        temp_date_time = datetime.datetime.now()
        smile_resource = self.temp_resource_obj(temp_date_time)
        with self.e.session() as session, session.begin():
            session.add(smile_resource)
            session.flush()
            self.assertEqual(1, smile_resource.id)

        with self.e.session() as session, session.begin():
            smile_resource = session.execute(select(Resource).filter_by(id=1)).scalar_one()
            self.assertEqual('smile.png', smile_resource.name)
            self.assertEqual('data/images/input/smile.png', smile_resource.location)
            self.assertEqual('3e44cfaa9a914f1312d157130810300f', smile_resource.hash)
            self.assertEqual(temp_date_time, smile_resource.last_indexed)

    def test_resource_tag(self):
        # HELPFUL https://programmer.help/blogs/sqlalchemy-many-to-many-relationship.html
        person_tag = self.temp_tag_obj()
        temp_date_time = datetime.datetime.now()
        smile_resource = self.temp_resource_obj(temp_date_time)
        with self.e.session() as session, session.begin():
            session.add(person_tag)
            smile_resource.tags = [person_tag]
            session.add(smile_resource)

        with self.e.session() as session, session.begin():
            smile_resource = session.execute(select(Resource).filter_by(id=1)).scalar_one()
            new_tag = smile_resource.tags[0]
            self.assertEqual('person', new_tag.name)
            self.assertEqual('IMAGGA', new_tag.engine)
            self.assertEqual(45, new_tag.percent_match)
