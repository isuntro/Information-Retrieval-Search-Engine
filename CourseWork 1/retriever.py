#!/usr/bin/python3
# needs improving to remove forced type conversions

import sys
import re
import json

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []


def main():
    # code for testing offline
    if len(sys.argv) < 2:
        print('usage: ./retriever.py term [term ...]')
        sys.exit(1)
    query_terms = sys.argv[1:]
    answer = []

    read_index_files()

    answer = retrieve_bool(query_terms)

    print('Query: ', query_terms)
    i = 0
    for docid in answer:
        i += 1
        print(i, docids[int(docid)])


def read_index_files():
    ## reads existing data from index files: docids, vocab, postings
    # uses JSON to preserve list/dictionary data structures
    # declare refs to global variables
    global docids
    global postings
    global vocab
    # open the files
    in_d = open('docids.txt', 'r')
    in_v = open('vocab.txt', 'r')
    in_p = open('postings.txt', 'r')
    # load the data
    docids = json.load(in_d)
    vocab = json.load(in_v)
    postings = json.load(in_p)
    # close the files
    in_d.close()
    in_v.close()
    in_p.close()

    return


def retrieve_bool(query_terms):
    ## a function to perform Boolean retrieval with ANDed terms
    answer = []
    #### your code starts here ####

    #### your code ends here ####
    return answer


# Standard boilerplate to call the main() function
if __name__ == '__main__':
    main()
