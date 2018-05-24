import sys
import csv
import os
import json
import subprocess
from web_crawler import PCcrawler as crawler
from s_engine import search_engine
def main():
    if len(sys.argv) <= 1 or len(sys.argv) > 5:
        help()
        sys.exit(2)
    else:
        opt = sys.argv.pop(1)
        if opt == '-index':
            crawler.start_crawl(sys.argv)
        elif opt == '-search':
            search_engine.search()
    
def help():
    print("Usage -index followed by domain-pattern seed-url  [max-num-pages-visited]")
    print("-search")
if __name__=="__main__":
    main()