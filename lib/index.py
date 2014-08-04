from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Date, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload

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
    def add(cls, data):
        if not cls.exists(data):
            with session_scope() as session:
                session.add(cls(**data))

    @classmethod
    def exists(cls, filter):
        with session_scope() as session:
            q = session.query(cls).filter_by(**filter)
            return session.query(q.exists()).scalar()

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

    episode = relationship("Episode", backref="download")

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

# create all the tables that haven't been created
Base.metadata.create_all(engine)

# check a row exists in the database for
def exists(model, attribute, value):
  with session_scope() as session:
    q = session.query(model).filter(attribute == value)
    return session.query(q.exists()).scalar()


# delete a row from the given table
def delete(model, attribute, value):
  with session_scope() as session:
    q = session.query(model).filter(attribute == value).first()
    if q:
      session.delete(q)

def get_episode(eid):
    with session_scope() as session:
        q = session.query(Episode).options(joinedload('*')).filter(Episode.id == eid).first()
        return q

def get_anime(aid):
  with session_scope() as session:
    q = session.query(Anime).options(joinedload('*')).filter(Anime.id == aid).first()
    return q

def get_all_anime():
  with session_scope() as session:
    q = session.query(Anime).options(joinedload('*')).all()
    return q
