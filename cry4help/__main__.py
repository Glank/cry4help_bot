import bot
import database

def dump_new_posts_to_db():
  rbot = bot.Bot('creds.json')
  db = database.Database('posts.db')
  def callback(submission):
    try:
      data = bot.Bot.read_submission(submission)
      print(data)
      db.upsert_post(data)
    except Exception as e:
      print(e)
  rbot.listen_for_new_submissions(callback, limit=None)

def main():
  dump_new_posts_to_db()

if __name__=='__main__':
  main()
