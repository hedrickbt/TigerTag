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
    hash = Column(String, nullable=False)
    last_indexed = Column(DateTime, nullable=False)
    description = Column(String)

    tags = relationship(
        "Tag",
        secondary=resource_tag_table,
        back_populates="resources"
    )

    def __repr__(self):
        return f"Tag(id={self.id!r}, name={self.name!r}, location={self.location!r}, " \
               f"hash={self.hash!r}, last_indexed={self.last_indexed!r}, description={self.description!r})"


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    engine = Column(String(100), nullable=False)
    description = Column(String)
    percent_match = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('name', 'engine', name='uix_1'),) # _name_engine_uc

    resources = relationship(
        "Resource",
        secondary=resource_tag_table,
        back_populates="tags"
    )

    def __repr__(self):
        return f"Tag(id={self.id!r}, name={self.name!r}, description={self.description!r}, " \
               f"percent_match={self.percent_match!r})"
