import cry4help as c4h
import json

def print_submission(submission):
  data = c4h.bot.Bot.read_submission(submission)
  print(json.dumps(data, indent='  '))

def main():
  bot = c4h.bot.Bot("creds.json")
  bot.listen_for_new_submissions(callback=print_submission, limit=3)
