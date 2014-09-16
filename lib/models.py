from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Date, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload, backref

from contextlib import contextmanager

dbpath = ':memory:'
dbpath = 'anime.db'

engine = create_engine('sqlite:///' + dbpath)
Session = sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def session_scope():
  session = Session()
  try:
    yield session
    session.commit()
  except:
    session.rollback()
    raise
  finally:
    session.close()

Base = declarative_base()
class Helper(object):
    @classmethod
    def exists(cls, filter):
        with session_scope() as session:
            q = session.query(cls).filter_by(**filter)
            return session.query(q.exists()).scalar()

    @classmethod
    def get(cls, filter):
        with session_scope() as session:
            return session.query(cls).options(joinedload('*')).filter_by(**filter).scalar()

    @classmethod
    def getAll(cls):
        with session_scope() as session:
            return session.query(cls).options(joinedload('*')).all()

    @classmethod
    def add(cls, data):
        if not cls.exists(data):
            with session_scope() as session:
                session.add(cls(**data))
        return cls.get(data)

    @classmethod
    def addAll(cls, items):
        if len(items):
            items = list(map(lambda data:cls(**data), items))
            with session_scope() as session:
                session.add_all(items)

"""
    Files table
"""
class File(Base, Helper):
  __tablename__ = 'files'

  ed2k = Column(String, primary_key=True, unique=True)
  path = Column(String)
  aid = Column(Integer, ForeignKey('anime.id'))
  eid = Column(Integer, ForeignKey('episodes.id'))
  
  def __repr__(self):
    return self.path

"""
    Episodes table
"""
class Episode(Base, Helper):
  __tablename__ = 'episodes'

  id = Column(Integer, primary_key=True, unique=True)
  aid = Column(Integer, ForeignKey('anime.id'))
  epno = Column(Integer)
  title = Column(String)
  title_ro = Column(String)
  title_jp = Column(String)
  aired_date = Column(Date)

  files = relationship("File", backref="episode")

  def __repr__(self):
    return self.get_title()

  def get_title(self):
    return self.title or self.title_ro or self.title_jp

  def get_titles(self):
    titles = [self.title, self.title_ro, self.title_jp]
    return [ title for title in titles if title ]

"""
    Downloads table
"""
class Download(Base, Helper):
    __tablename__ = 'downloads'

    id = Column(Integer, primary_key=True)
    eid = Column(Integer, ForeignKey('episodes.id'))

    episode = relationship("Episode", backref=backref("download", uselist=False))

"""
    Groups table
"""
class Group(Base, Helper):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, nullable=False)

"""
    Group Status table
"""
class GroupStatus(Base, Helper):
    __tablename__ = 'groupstatus'

    id = Column(Integer, primary_key=True)
    aid = Column(Integer, ForeignKey('anime.id'), nullable=False)
    gid = Column(Integer, ForeignKey('groups.id'), nullable=False)
    completed_state = Column(String)
    episode_range = Column(String)
    last_episode = Column(Integer)
    rating = Column(Integer)
    votes = Column(Integer)

    group = relationship("Group")

"""
    Anime table
"""
class Anime(Base, Helper):
    __tablename__ = 'anime'

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String)
    name_jp = Column(String)
    name_en = Column(String)
    episode_count = Column(Integer)
    description = Column(String)
    picture = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)

    files = relationship("File", order_by=File.path, backref="anime")
    episodes = relationship("Episode", order_by=Episode.epno, backref="anime")
    groups = relationship("GroupStatus", order_by=(desc(GroupStatus.last_episode), desc(GroupStatus.rating)), backref="anime")

    def __repr__(self):
        return self.get_name()

    def get_name(self):
        return self.name or self.name_en or self.name_jp

    def get_names(self):
        names = [self.name, self.name_en, self.name_jp]
        return [name for name in names if name]

"""
    Subscriptions table
"""
class Subscription(Base, Helper):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, nullable=False)
    aid = Column(Integer, ForeignKey('anime.id'), unique=True, nullable=False)
    anime = relationship("Anime", backref="subscription")

# create all the tables that haven't been created
Base.metadata.create_all(engine)
