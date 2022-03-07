import cry4help as c4h

def creation_test():
  db = c4h.database.Database(':memory:')
  
def insert_upsert_test():
  db = c4h.database.Database(':memory:')
  db.upsert_post({'id': 'abc', 'content': 'bla'})
  db.upsert_post({'id': 'efg', 'content': 'foo'})
  db.upsert_post({'id': 'abc', 'content': 'bar'})
  fin_posts = {}
  for post in db.iter_posts():
    fin_posts[post['id']] = post
  if fin_posts['abc']['content'] != 'bar':
    raise RuntimeError("Expected row at id 'abc' to have content 'bar'")
  if fin_posts['efg']['content'] != 'foo':
    raise RuntimeError("Expected row at id 'efg' to have content 'foo'")

def main():
  creation_test()
  insert_upsert_test()
