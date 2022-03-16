import sys
import os
sys.path.append(os.getcwd())
import scraping_tests
import bot_tests
import database_tests
import vectorize_tests

def main():
  scraping_tests.main()
  #bot_tests.main()
  database_tests.main()
  vectorize_tests.main()
  print("All tests passed.")

if __name__=="__main__":
  main()
