create table files(
  path TEXT NOT NULL UNIQUE,
  hash TEXT,
  aid INTEGER,
  eid INTEGER,
  PRIMARY KEY (path),
  FOREIGN KEY (aid) REFERENCES anime(aid),
  FOREIGN KEY (eid) REFERENCES episode(eid)
);

create table episodes(
  eid INTEGER NOT NULL UNIQUE,
  aid INTEGER NOT NULL,
  epno INTEGER,
  title TEXT,
  title_ro TEXT,
  title_jp TEXT,
  air_date DATE,
  PRIMARY KEY (eid),
  FOREIGN KEY (aid) REFERENCES anime(aid)
);

create table anime(
  aid INTEGER NOT NULL UNIQUE,
  name TEXT,
  name_ro TEXT,
  name_jp TEXT,
  episode_count INTEGER,
  description TEXT,
  picture TEXT,
  start_date DATE,
  end_date DATE,
  PRIMARY KEY (aid)
);
