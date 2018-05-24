#!/usr/bin/python3

import sys
import math
import json
import re
import textwrap
import os
import collections

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from random import randint
from terminaltables import AsciiTable
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from util import utils
# global declarations 
non_rel_rochio = set()

docids = []
doc_sizes = []
postings = {}
vocab = []
positions = {}
titles = []
headings = []
descriptions = []
summaries = []
query_vector = []


def main():
    # code for testing offline
    if len(sys.argv) < 2:
        print('usage: ./retriever.py term [term ...]')
        sys.exit(1)
    query_terms = sys.argv[1:]
    answer = []

    read_index_files()

    answer = tf_idf_vector(query_terms)

    print('Query: ', query_terms)
    i = 0
    for docid in answer:
        i += 1
        print(i, docids[int(docid)])


def read_index_files():
    ''' 
        Reads existing data from index files: docids, vocab, postings
        uses JSON to preserve list/dictionary data structures
        declare refs to global variables
    '''
    global docids
    global doc_sizes
    global postings
    global vocab
    global headings
    global titles
    global descriptions
    global summaries

    path = "index/"
    in_d = open(path + 'docids.txt', 'r')
    in_s = open(path + 'doc_sizes.txt', 'r')
    in_v = open(path + 'vocab.txt', 'r')
    in_p = open(path + 'postings.txt', 'r')
    in_heading = open(path + 'headings.txt', 'r')
    in_titles = open(path + 'titles.txt', 'r')
    in_description = open(path + 'descriptions.txt', 'r')
    in_summary = open(path + 'summaries.txt', 'r')
    
    # load the data
    docids = json.load(in_d)
    doc_sizes = json.load(in_s)
    doc_sizes = { int(k):v for k,v in doc_sizes.items()}
    vocab = json.load(in_v)
    postings = json.load(in_p)
    postings = { int(k):v for k,v in postings.items()}
    headings = json.load(in_heading)
    titles = json.load(in_titles)
    descriptions = json.load(in_description)
    summaries = json.load(in_summary)


    # close the files
    in_d.close()
    in_s.close()
    in_v.close()
    in_p.close()
    in_heading.close()
    in_titles.close()
    in_description.close()
    in_summary.close()

    return

def retrieve(query_terms, rocchio=False, data=None, should_print=True):
    '''
        Does a retrieval of a query including
        the option to give relevance feedback
    '''
    global docids
    global postings
    global vocab
    global doclengths
    global titles
    global headings
    global descriptions
    global summaries
    global rocchio_non_rel_docs
    global query_vector

    if not rocchio:
        rocchio_non_rel_docs = set()
        query_vector = []

    print(rocchio_non_rel_docs)
    if (data):
        docids = data.doc_ids
        doclengths = data.doc_lengths
        postings = data.postings
        vocab = data.vocab
        titles = data.titles
        headings = data.headings
        descriptions = data.descriptions
        summaries = data.summaries

    query_terms = set(query_terms)
    scores = tf_idf_vector(query_terms, rocchio)

    if should_print:
        amount_to_print = 10
        i = -1
        rochio_scores = collections.OrderedDict()
        for docid in sorted(scores, key=scores.get, reverse=True):
            i += 1
            rochio_scores[docid] = scores[docid]
            if (i == amount_to_print):
                option = ''
                option = input("Type 'f' for feedback or 'e' to exit...\n")
                if (option == "e"):
                    return
                elif (option == "f"):
                    rocchio_alg(query_terms, rochio_scores)
                    return
            table = build_answer_table(i, query_terms, docid)
            print(table.table)
    else:
        return scores
def get_relevant_sentences(query_terms, docid):
    '''
        Returns relevant setences for query using position in postings
    '''
    summary = summaries[docid]
    sentences = []
    pos_list = list(utils.flatten_list(positions[docid]))
    subtractFromIndex = 0
    query_terms = [query.rstrip('?!.;:,').lower() for query in query_terms]
    for sentence in sent_tokenize(summary):
        for index in pos_list:
            if 0 < index - subtractFromIndex < len(sentence):
                sentence = re.sub("("+"|".join(query_terms)+")", r'\1',sentence, flags=re.IGNORECASE)
                sentences.append(sentence)
                break
        subtractFromIndex += len(sentence)
    return sentences
def build_answer_table(index, query_terms, docid):
    table_data = [[],[]]
    
    wrap_title = textwrap.wrap(titles[docid])
    table_data[0] = [str(index) + " - " + '\n'.join(wrap_title) + " | " + docids[docid]]

    snippet = get_snippet(query_terms, docid)
    wrapped = textwrap.wrap(snippet)
    table_data[1].append('\n'.join(wrapped))
    return AsciiTable(table_data)

def tf_idf_vector(query_terms, rocchio = False):
    '''
        Main retrieving function that calculates tf_idf
        vectors and cosine distance between docs and query vectors
    '''
    read_index_files()
    global docids
    global doc_sizes
    global postings
    global vocab
    global positions
    global query_vector
    global non_rel_rochio

    idf = {}
    scores = {}
    terms_to_weight = {}

    query_set = set(query_terms) # remove duplicates in querry
    query_set = utils.stem_terms(query_set) # stemm querry

    for term in query_set:
        try: 
            term_id = vocab.index(term.lower())
            terms_to_weight[term_id] = term
            print(term_id)
        except: 	# the term is not in the vocab
            print ('Term :',term, 'is not in corpus')
            continue
        idf[term_id] = (1+math.log(len(postings.get(term_id))))/(len(doc_sizes)) 
        
    i = -1
    for term_id in sorted(idf, key=idf.get, reverse=True):
        i += 1
        if not rocchio:
            query_vector.append(idf[term_id]/len(query_set))

        for post in postings.get(term_id):
            if post[0] in positions:
                positions[post[0]].append(post[2])
            else:
                positions[post[0]] = [post[2]]
            weighted_term = get_weight(post[0], terms_to_weight[term_id])

            if post[0] not in non_rel_rochio:
    
                if post[0] in scores:
                    scores[post[0]] += ((idf.get(term_id) * post[1]) / doc_sizes.get(post[0]) * query_vector[i]) * weighted_term
                else:
                    scores[post[0]] = ((idf.get(term_id) * post[1]) / doc_sizes.get(post[0]) * query_vector[i]) * weighted_term

    # rank the list	
    # for docid in sorted(scores, key=scores.get, reverse=True):
    #     result.append([scores.get(docid),docids[docid]])
        
    return scores
def get_weight(docid, term):
    '''
    Get weight of a term if present in tile, 
    description or heading of a document with docid
    '''
    global titles
    global descriptions
    global headings

    weight = 1 
    title = titles[docid]
    description = descriptions[docid]
    heading = headings[docid]

    if re.search(term, title, re.M|re.I):
        weight *= 1.4
    if re.search(term, description, re.M|re.I):
        weight *= 1.2
    if re.search(term, heading, re.M|re.I):
        weight *= 1.1
    return weight
def get_snippet(query_terms, docid):
    '''
    Decide what snippet to return 
    from summary, description and title 
    in order of preferance for a given qurrys terms
    '''
    snippet = ''
    summary = summaries[docid]
    description = descriptions[docid]
    title = titles[docid]

    # if doc has description return it in snippet
    # else if it has summary, return snippet of summary
    # otherwise it will return title snippet
    if description != "" and not summary.isspace():
        snippet = sent_tokenize(descriptions[docid])[0]
    elif summary != "" and not summary.isspace():
        snippet = get_relevant_sentences(query_terms, docid)
        snippet = sent_tokenize(summary)[0] if not snippet else snippet[0]
    else:
        snippet = title
    
    # if for some reason, the snippet is more than threshold, cut it and add...
    threshold = 300
    if (len(snippet) > threshold):
        snippet = snippet[:threshold] + "..."
    return snippet

def rocchio_alg(query_terms, scores):
    # Get original query vector
    global query_vector
    global rocchio_non_rel_docs

    ALPHA = 1
    BETA = 0.5
    GAMMA = 0.25

    rel_docs_user = input("Enter the number of each relevant doc you see:\n")

    rel_scores = [0]
    rel_docids = []

    if rel_docs_user != "" and not rel_docs_user.isspace():
        rel_docs_user = list(rel_docs_user)
        for i in rel_docs_user: # 0, 1, 2, 3 ... 10
            k = list(scores.keys())[int(i)]
            rel_scores.append(scores.get(k))
            rel_docids.append(k)

    for docid in rel_docids:
        del scores[docid]
    # Add to the total of documents that have to be ommited
    rocchio_non_rel_docs |= set(scores.keys())

    
    # relevant docs mean 
    rel_mean = sum(rel_scores) / len(rel_scores)
    # non-relevant docs mean
    non_rel_mean = sum(scores.values()) / len(scores)
    
    new_query_vector = []
    for vector in query_vector:
        new_vector = vector + (BETA * rel_mean) - (GAMMA * non_rel_mean)
        if new_vector > 0:
            new_query_vector.append(new_vector)
        else:
            new_query_vector.append(0)

    query_vector = new_query_vector
    retrieve(query_terms, rocchio=True)
if __name__ == '__main__':
    main()
