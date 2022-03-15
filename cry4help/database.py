import sqlite3
import json

class CursorPtr:
  def __init__(self, cur):
    self.cur = cur
  def __enter__(self):
    return self.cur
  def __exit__(self, exc_type, exc_value, traceback):
    self.cur.close()
    if exc_type is not None:
      raise RuntimeError(exc_value)

class Database:
  def __init__(self, filename):
    self.con = sqlite3.connect(filename,
      detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    self.con.execute('''
      CREATE TABLE IF NOT EXISTS Posts (id VARCHAR(16) PRIMARY KEY, data BLOB) 
    ''')
  def upsert_post(self, data):
    with CursorPtr(self.con.cursor()) as cur:
      cur.execute('INSERT OR REPLACE INTO Posts VALUES (?, ?)', (data['id'], json.dumps(data)))
  def iter_posts(self):
    with CursorPtr(self.con.cursor()) as cur:
      result = cur.execute('''
        SELECT id, data FROM Posts
      ''')
      for row in result:
        yield json.loads(row[1])
