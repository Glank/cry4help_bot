import sqlite3
import json

class CursorPtr:
  def __init__(self, con):
    self.con = con
    self.cur = con.cursor()
  def __enter__(self):
    return self.cur
  def __exit__(self, exc_type, exc_value, traceback):
    self.cur.close()
    self.con.commit()
    if exc_type is not None:
      raise RuntimeError(exc_value)

class Database:
  def __init__(self, filename):
    self.con = sqlite3.connect(filename,
      detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    self.con.execute('''
      CREATE TABLE IF NOT EXISTS
      Posts (
        id VARCHAR(16) PRIMARY KEY,
        data BLOB,
        created INTEGER,
        parse BLOB
      ) 
    ''')
  def upsert_post(self, data, parse=None):
    data_blob = json.dumps(data)
    parse_blob = None if parse is None else json.dumps(parse)
    created = int(data['created_utc'])
    with CursorPtr(self.con) as cur:
      cur.execute('''
        INSERT OR REPLACE INTO Posts VALUES (?, ?, ?, ?)
      ''', (data['id'], data_blob, created, parse_blob))
  def iter_posts(self):
    with CursorPtr(self.con) as cur:
      result = cur.execute('''
        SELECT id, data, parse FROM Posts
      ''')
      for row in result:
        post = json.loads(row[1])
        parse = row[2]
        if row[2] is not None:
          parse = json.loads(parse)
        yield post, parse
