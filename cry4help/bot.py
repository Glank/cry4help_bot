import praw
import json

class Bot:
  def __init__(self, credential_file_name):
    with open(credential_file_name) as f:
      self.creds = json.load(f)
    print(list(self.creds.keys()))
    self.reddit = praw.Reddit(**self.creds, user_agent='python')
    # to extend this to multiple subreddits, put loseit+askreddit or whatever
    self.subreddit = self.reddit.subreddit('loseit')
  def listen_for_new_submissions(self, callback, limit=10):
    count = 0
    for id in self.subreddit.stream.submissions():
      submission = self.reddit.submission(id=id)
      callback(submission)
      count += 1
      if limit is not None and count >= limit:
        break
  @staticmethod
  def read_submission(submission):
    if submission.author is None:
      raise RuntimeError('Could not fetch author.')
    data = {
      'id': str(submission.id),
      'title': submission.title,
      'selftext': submission.selftext,
      'url': submission.url,
      'created_utc': submission.created_utc,
      'author': {
        'id': submission.author.id,
        'comment_karma': submission.author.comment_karma,
        'link_karma': submission.author.link_karma,
        'created_utc': submission.author.created_utc,
        'name': submission.author.name,
      },
    }
    return data
