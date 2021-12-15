import logging
import os
import sqlalchemy
from sqlalchemy import create_engine, select, delete
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

from tigertag.db.models import *

logger = logging.getLogger(__name__)


class DbEngine:
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


class DbEngineBuilder:
    def __init__(self):
        pass

    def build(self):
        raise NotImplementedError


class EnvironmentDbEngineBuilder(DbEngineBuilder):
    def __init__(self):
        super().__init__()

    def build(self):
        if 'DB_URL' in os.environ:
            db_url = os.environ.get('DB_URL')
            return DbEngine(db_url)
        else:
            raise ValueError("DB_URL environment variable missing.")


class Persist:
    def __init__(self, dbengine):
        self.engine = dbengine

    @staticmethod
    def _row_to_dict(row):
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)
            # if isinstance(column.type, sqlalchemy.types.Integer):
            #     d[column.name] = getattr(row, column.name)
            # else:
            #     d[column.name] = str(getattr(row, column.name))
        return d

    # @staticmethod
    # def _rows_to_dict(rows):
    #     results = []
    #     for row in rows:
    #         results.append(Persist._row_to_dict(row))
    #     return results

    @staticmethod
    def _handle_tags(session, resource, engine, tags):
        if engine is not None:
            if tags is not None:
                session.execute(delete(ResourceTag).where(ResourceTag.resource_id == resource.id))
                temp_resource_tags = []
                for tag_name, tag_values in tags.items():
                    tag = Tag(
                        name=tag_name,
                        engine=engine,
                    )
                    resource_tag = ResourceTag(
                        resource=resource,
                        tag=tag,
                        confidence=tag_values['confidence'],
                    )
                    session.add(tag)
                    session.add(resource_tag)
                #     temp_resource_tags.append(tag)
                # resource.tags = temp_resource_tags
            else:
                raise ValueError('While trying to set a resource, the tags were None.')
        else:
            if tags is not None:
                raise ValueError('While trying to set a resource, the engine was None.')

    def set_resource(self, location, name=None, hashval=None, last_indexed=None, description=None, engine=None,
                     tags=None):
        with self.engine.session() as session, session.begin():
            existing_resource = session.execute(select(Resource).filter_by(location=location)).one_or_none()
            new_record = False
            if existing_resource is None:
                logger.debug('Adding new resource {}'.format(location))
                resource = Resource()
                new_record = True
            else:
                logger.debug('Updating existing resource {}'.format(location))
                resource = existing_resource.Resource

            if name is not None:
                resource.name = name
            if location is not None:
                resource.location = location
            if hashval is not None:
                resource.hashval = hashval
            if last_indexed is not None:
                resource.last_indexed = last_indexed

            if description is not None:
                resource.description = description
            if new_record:
                session.add(resource)
            Persist._handle_tags(session, resource, engine, tags)

            return Persist._row_to_dict(resource)

    def get_resource_by_id(self, id):
        with self.engine.session() as session, session.begin():
            row = session.query(Resource).get(id)
            return Persist._row_to_dict(row)

    def get_resource_by_location(self, location):
        with self.engine.session() as session, session.begin():
            row = session.query(Resource) \
                .filter(Resource
                .location == location) \
                .one_or_none()
            if row is None:
                return None
            else:
                return Persist._row_to_dict(row)

    def get_tags_by_resource_id(self, id):
        result = {}
        with self.engine.session() as session, session.begin():
            row = session.query(Resource).get(id)
            for resource_tag in row.tags:
                tag_detail = Persist._row_to_dict(resource_tag.tag)
                tag_detail['confidence'] = resource_tag.confidence
                result[resource_tag.tag.name] = tag_detail
        return result
