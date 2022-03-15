import cry4help as c4h

def creation_test():
  db = c4h.database.Database(':memory:')
  
def insert_upsert_test():
  db = c4h.database.Database(':memory:')
  db.upsert_post({'id': 'abc', 'content': 'bla', 'created_utc':0})
  db.upsert_post({'id': 'efg', 'content': 'foo', 'created_utc':1})
  db.upsert_post({'id': 'abc', 'content': 'bar', 'created_utc':2}, {'parsed':True})
  fin_posts = {}
  fin_parsed = {}
  for post, parse in db.iter_posts():
    fin_posts[post['id']] = post
    fin_parsed[post['id']] = parse
  if fin_posts['abc']['content'] != 'bar':
    raise RuntimeError("Expected row at id 'abc' to have content 'bar'")
  if fin_parsed['abc'] is None:
    raise RuntimeError("Expected parse for abc")
  if fin_posts['efg']['content'] != 'foo':
    raise RuntimeError("Expected row at id 'efg' to have content 'foo'")
  if fin_parsed['efg'] is not None:
    raise RuntimeError("Expected no parse for efg")
  if len(fin_posts) != 2:
    raise RuntimeError("Expected 2 posts")

def main():
  creation_test()
  insert_upsert_test()
