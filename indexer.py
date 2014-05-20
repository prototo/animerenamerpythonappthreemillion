import sqlite3

DATABASE = 'anime.db'

db = None

def get_db():
  global db
  if db is None:
    db = sqlite3.connect(DATABASE)
  return db

def init_db():
  db = get_db()
  with app.open_resource('schema.sql', mode='r') as f:
    db.cursor().executescript(f.read())
  db.commit()
    
def close_connection():
  db = get_db()
  if db is not None:
    db.close()
    db = None

def exists(table, key, value):
  db = get_db()
  with db:
    cur = db.cursor()
    cur.execute("SELECT EXISTS(SELECT 1 FROM {0} WHERE {1}=?)".format(table, key), (value,))
    exists = cur.fetchone()[0]
    return bool(exists)

def indexFile(filepath, ed2k=None, aid=None, eid=None, **args):
  if exists('files', 'path', filepath):
    return False
  db = get_db()
  with db:
    cur = db.cursor()
    cur.execute("INSERT INTO files VALUES(?,?,?,?)", (filepath, ed2k, aid, eid))
    print("Indexed file\n\t",filepath)

def indexEpisode(eid, aid, epno=None, title=None, romaji_title=None, kanji_title=None, aired=None, **args):
  if exists('episodes', 'eid', eid):
    return False
  db = get_db()
  with db:
    cur = db.cursor()
    cur.execute("INSERT INTO episodes VALUES(?,?,?,?,?,?,?)", (eid, aid, epno, title, romaji_title, kanji_title, aired))
    print("Indexed episode\n\t",epno,title)

def indexAnime(aid, name=None, romaji_name=None, kanji_name=None, epcount=None, desc=None, picture=None, start_date=None, end_date=None, **args):
  if exists('anime', 'aid', aid):
    return False
  db = get_db()
  with db:
    cur = db.cursor()
    cur.execute("INSERT INTO anime VALUES(?,?,?,?,?,?,?,?,?)", (aid, name, romaji_name, kanji_name, epcount, desc, picture, start_date, end_date))
    print("Indexed anime\n\t",name or romaji_name)

