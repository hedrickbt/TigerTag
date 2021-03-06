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
        self.e = DbEngine(DB_URL)
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
        builder = EnvironmentDbEngineBuilder()
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
        self.e = DbEngine(DB_URL)

    def temp_tag_obj(self):
        return Tag(
            name='person',
            engine='IMAGGA',
        )

    def temp_resource_obj(self, temp_date_time):
        return Resource(
            name='smile.png',
            location='data/images/input/smile.png',
            hashval='3e44cfaa9a914f1312d157130810300f',
            last_indexed=temp_date_time,
        )

    def temp_resource_tag_obj(self, temp_date_time):
        temp_resource = self.temp_resource_obj(temp_date_time)
        temp_tag = self.temp_tag_obj()

        return temp_resource, \
            temp_tag, \
            ResourceTag(
                confidence=45,
                resource=temp_resource,
                tag=temp_tag,
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
            self.assertEqual('3e44cfaa9a914f1312d157130810300f', smile_resource.hashval)
            self.assertEqual(temp_date_time, smile_resource.last_indexed)

    def test_resource_tag(self):
        # HELPFUL https://programmer.help/blogs/sqlalchemy-many-to-many-relationship.html
        temp_date_time = datetime.datetime.now()
        temp_resource, temp_tag, temp_resource_tag = self.temp_resource_tag_obj(temp_date_time)
        with self.e.session() as session, session.begin():
            session.add(temp_tag)
            session.add(temp_resource)
            session.add(temp_resource_tag)

        with self.e.session() as session, session.begin():
            smile_resource = session.execute(select(Resource).filter_by(id=1)).scalar_one()
            new_resource_tag = smile_resource.tags[0]
            self.assertEqual('person', new_resource_tag.tag.name)
            self.assertEqual('IMAGGA', new_resource_tag.tag.engine)
            self.assertEqual(45, new_resource_tag.confidence)


class TestPersist(BaseSqlite):
    def setUp(self):
        super().setUp()
        self.e = DbEngine(DB_URL)
        self.p = Persist(self.e)

    def test_set_resource_minimum(self):
        temp_date_time = datetime.datetime.now()
        self.p.set_resource(
            'data/images/input/smile.png',
            'smile.png',
            '3e44cfaa9a914f1312d157130810300f',
            temp_date_time,
        )
        resource = self.p.get_resource_by_id(1)
        self.assertEqual('smile.png', resource['name'])

    def test_set_resource_update(self):
        temp_date_time = datetime.datetime.now()
        self.p.set_resource(
            'data/images/input/smile.png',
            'smile.png',
            '3e44cfaa9a914f1312d157130810300f',
            temp_date_time,
        )
        self.p.set_resource(
            'data/images/input/smile.png',
            'smile.png',
            'changed',
            temp_date_time,
        )
        resource = self.p.get_resource_by_id(1)
        self.assertEqual('changed', resource['hashval'])

    def test_set_resource_rescan(self):
        temp_date_time = datetime.datetime.now()
        self.p.set_resource(
            'data/images/input/smile.png',
            'smile.png',
            '3e44cfaa9a914f1312d157130810300f',
            temp_date_time,
        )
        self.p.set_resource_rescan(
            'data/images/input/smile.png'
        )
        resource = self.p.get_resource_by_id(1)
        self.assertEqual('rescan', resource['hashval'])
        self.assertLess(temp_date_time, resource['last_indexed'] )

    def test_get_resources_by_location(self):
        temp_date_time = datetime.datetime.now()
        self.p.set_resource(
            'data/images/input/smile.png',
            'smile.png',
            '3e44cfaa9a914f1312d157130810300f',
            temp_date_time,
        )
        resource = self.p.get_resource_by_location('data/images/input/smile.png')
        self.assertEqual('smile.png', resource['name'])

    def test_get_resources_by_location_missing(self):
        resource = self.p.get_resource_by_location('data/images/input/smile.png')
        self.assertIsNone(resource)

    def test_set_resource_with_tags(self):
        temp_date_time = datetime.datetime.now()
        tags = {
            'smile': {
                'confidence': 100
            },
            'face': {
                'confidence': 95
            },
            'circle': {
                'confidence': 25
            }
        }
        self.p.set_resource(
            'data/images/input/smile.png',
            'smile.png',
            '3e44cfaa9a914f1312d157130810300f',
            temp_date_time,
            engine='TESTENGINE',
            tags=tags
        )

        tags = self.p.get_tags_by_resource_id(1)
        self.assertEqual(3, len(tags))
        self.assertEqual('smile', tags['smile']['name'])
        self.assertEqual(100, tags['smile']['confidence'])
        self.assertEqual('face', tags['face']['name'])
        self.assertEqual(95, tags['face']['confidence'])
        self.assertEqual('circle', tags['circle']['name'])
        self.assertEqual(25, tags['circle']['confidence'])

    def test_set_resource_with_tags_update(self):
        temp_date_time = datetime.datetime.now()
        # Add tags for TESTENGINE
        tags = {
            'smile': {
                'confidence': 100
            },
            'face': {
                'confidence': 95
            },
            'circle': {
                'confidence': 25
            }
        }
        self.p.set_resource(
            'data/images/input/smile.png',
            'smile.png',
            '3e44cfaa9a914f1312d157130810300f',
            temp_date_time,
            engine='TESTENGINE',
            tags=tags
        )

        # Add tags for ANOTHERENGINE
        tags = {
            'chevette': {
                'confidence': 10
            },
            'ferrari': {
                'confidence': 5
            },
        }
        self.p.set_resource(
            'data/images/input/smile.png',
            engine='ANOTHERENGINE',
            tags=tags
        )

        # Replace tags for TESTENGINE
        tags = {
            'clown': {
                'confidence': 99
            },
            'circus': {
                'confidence': 33
            },
        }
        self.p.set_resource(
            'data/images/input/smile.png',
            engine='TESTENGINE',
            tags=tags
        )

        tags = self.p.get_tags_by_resource_id(1)
        self.assertEqual(4, len(tags))
        self.assertEqual('clown', tags['clown']['name'])
        self.assertEqual('TESTENGINE', tags['clown']['engine'])
        self.assertEqual(99, tags['clown']['confidence'])
        self.assertEqual('circus', tags['circus']['name'])
        self.assertEqual('TESTENGINE', tags['circus']['engine'])
        self.assertEqual(33, tags['circus']['confidence'])
        self.assertEqual('chevette', tags['chevette']['name'])
        self.assertEqual('ANOTHERENGINE', tags['chevette']['engine'])
        self.assertEqual(10, tags['chevette']['confidence'])
        self.assertEqual('ferrari', tags['ferrari']['name'])
        self.assertEqual('ANOTHERENGINE', tags['ferrari']['engine'])
        self.assertEqual(5, tags['ferrari']['confidence'])


    def test_set_resource_with_tags_duplicate_tags(self):
        # This should not throw an exception.  The hair
        # tag should be shared by the face and leg resource
        # and not try to create the tag twice.

        temp_date_time = datetime.datetime.now()
        # Add tags for face
        tags = {
            'face': {
                'confidence': 95
            },
            'hair': {
                'confidence': 25
            }
        }
        self.p.set_resource(
            'data/images/input/face.png',
            'face.png',
            'no matter',
            temp_date_time,
            engine='TESTENGINE',
            tags=tags
        )

        # Add tags for leg
        tags = {
            'leg': {
                'confidence': 95
            },
            'hair': {
                'confidence': 25
            }
        }
        self.p.set_resource(
            'data/images/input/leg.png',
            'leg.png',
            'no matter',
            temp_date_time,
            engine='TESTENGINE',
            tags=tags
        )

