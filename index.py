from sqlalchemy import create_engine, Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload

from contextlib import contextmanager

dbpath = ':memory:'
dbpath = 'anime.db'

engine = create_engine('sqlite:///' + dbpath)

Base = declarative_base()

class File(Base):
  __tablename__ = 'files'

  ed2k = Column(String, primary_key=True, unique=True)
  path = Column(String)
  aid = Column(Integer, ForeignKey('anime.id'))
  eid = Column(Integer, ForeignKey('episodes.id'))
  
  def __repr__(self):
    return self.path

class Episode(Base):
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

class Anime(Base):
  __tablename__ = 'anime'

  id = Column(Integer, primary_key=True, unique=True)
  name = Column(String)
  name_ro = Column(String)
  name_jp = Column(String)
  episode_count = Column(Integer)
  description = Column(String)
  picture = Column(String)
  start_date = Column(Date)
  end_date = Column(Date)

  files = relationship("File", order_by=File.path, backref="anime")
  episodes = relationship("Episode", order_by=Episode.epno, backref="anime")

  def __repr__(self):
    return self.get_name()

  def get_name(self):
    return self.name or self.name_ro or self.name_jp

Base.metadata.create_all(engine)

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

# check a row exists in the database for
def exists(model, attribute, value):
  with session_scope() as session:
    q = session.query(model).filter(attribute == value)
    return session.query(q.exists()).scalar()

# check a filepath has already been indexed
def file_path_exists(filepath):
  return exists(File, File.path, filepath)

# extract a subset of keys from the given dict
def extract_keys(d, keys):
  return { key: d.get(key, None) for key in keys }

# add a row to a table in the database
def add(model, data):
  with session_scope() as session:
    item = model(**data)
    session.add(item)

# add a file into the files tables
def add_file(**kwargs):
  keys = ['path', 'ed2k', 'eid', 'aid']
  data = extract_keys(kwargs, keys)
  if (file_path_exists(data['path'])):
    return False
  add(File, data)
  print("file", data['path'])

# add an episode into the episodes table
def add_episode(**kwargs):
  keys = ['id', 'aid', 'epno', 'title', 'title_ro', 'title_jp', 'aired_date']
  data = extract_keys(kwargs, keys)
  if (exists(Episode, Episode.id, kwargs['id'])):
    return False
  add(Episode, data)
  # print("episode", kwargs['title'] or kwargsp['title_ro'] or kwargs['title_jp'])

def get_episode(eid):
    with session_scope() as session:
        q = session.query(Episode).options(joinedload('*')).filter(Episode.id == eid).first()
        return q

# add an anime into the anime table
def add_anime(**kwargs):
  keys = ['id', 'name', 'name_ro', 'name_jp', 'episode_count', 'description', 'picture', 'start_date', 'end_date']
  data = extract_keys(kwargs, keys)
  if (exists(Anime, Anime.id, kwargs['id'])):
    return False
  add(Anime, data)
  # print("anime", kwargs['name'] or kwargs['name_ro'] or kwargs['name_jp'])

def get_anime(aid):
  with session_scope() as session:
    q = session.query(Anime).options(joinedload('*')).filter(Anime.id == aid).first()
    return q

def get_all_anime():
  with session_scope() as session:
    q = session.query(Anime).options(joinedload('*')).all()
    return q

