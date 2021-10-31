from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import Table, Column, Integer, String, DateTime

Base = declarative_base()

resource_tag_table = Table(
    'resource_tag',
    Base.metadata,
    Column('resource_id', ForeignKey('resource.id'), primary_key=True),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True)
)


class Resource(Base):
    __tablename__ = 'resource'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    hashval = Column(String, nullable=False)
    last_indexed = Column(DateTime, nullable=False)
    description = Column(String)
    __table_args__ = (UniqueConstraint('location', name='uix_1'),)  # _name_engine_uc

    tags = relationship(
        "Tag",
        secondary=resource_tag_table,
        back_populates="resources"
    )

    def __repr__(self):
        return f"Tag(id={self.id!r}, name={self.name!r}, location={self.location!r}, " \
               f"hashval={self.hashval!r}, last_indexed={self.last_indexed!r}, " \
               f"description={self.description!r})"


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    engine = Column(String(100), nullable=False)
    description = Column(String)
    confidence = Column(Integer, nullable=False)  # 0-100.  Percent likelihood the tag is correct
    __table_args__ = (UniqueConstraint('name', 'engine', name='uix_1'),)  # _name_engine_uc

    resources = relationship(
        "Resource",
        secondary=resource_tag_table,
        back_populates="tags"
    )

    def __repr__(self):
        return f"Tag(id={self.id!r}, name={self.name!r}, description={self.description!r}, " \
               f"confidence={self.confidence!r})"
