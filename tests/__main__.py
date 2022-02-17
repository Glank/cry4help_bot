import sys
import os
sys.path.append(os.getcwd())
import scraping_tests

def main():
  scraping_tests.main()
  print("All tests passed.")

if __name__=="__main__":
  main()
