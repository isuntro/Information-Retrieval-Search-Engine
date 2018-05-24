import sys
import re
import string
import json
from nltk.stem import PorterStemmer, WordNetLemmatizer

# global declarations for doclist, postings, vocabulary
docids = []
postings = {}
vocab = []


# main is used for offline testing only
def main():
    # code for testing offline
    if len(sys.argv) != 2:
        print('usage: ./indexer.py file')
        sys.exit(1)
    filename = sys.argv[1]

    try:
        input_file = open(filename, 'r')
    except (IOError) as ex:
        print('Cannot open ', filename, '\n Error: ', ex)

    else:
        page_contents = input_file.read()  # read the input file
        url = 'http://www.' + filename + '/'
        print(url, page_contents)
        make_index(url, page_contents)

    finally:
        input_file.close()


def write_index():
    # declare refs to global variables
    global docids
    global postings
    global vocab


    # writes to index files: docids, vocab, postings
    outlist1 = open("docids.txt", 'w')
    outlist2 = open("vocab.txt", 'w')
    outlist3 = open("postings.txt", 'w')
        
    json.dump(docids, outlist1)
    json.dump(vocab, outlist2)
    json.dump(postings, outlist3)

    outlist1.close()
    outlist2.close()
    outlist3.close()

    return

# remove and markup from html page contents
# return plain text
def clean_html(page_contents):

    re_tags = r"<[\s\S]+?>"
    re_comments = r"<!--(.*?)-->"
    re_script = r"<script[\S\s]*?<\/script>"
    re_style = r"<style[\S\s]*?<\/style>"
    re_nbsp = r"&nbsp;"
    re_amp = r"&amp;"
    re_spaces = r"\s+"
    re_punctuation = r"[^A-Za-z0-9%'+]"
    re_alt_img = r'<img alt="(.+?)".+?>'

    page_contents = re.sub(re_script, " ", page_contents)
    page_contents = re.sub(re_comments, " ", page_contents)
    page_contents = re.sub(re_style, " ", page_contents)
    page_contents = re.sub(re_alt_img, r"\1", page_contents)
    page_contents = re.sub(re_tags, " ", page_contents)
    page_contents = re.sub(re_nbsp, "", page_contents)
    page_contents = re.sub(re_amp, "", page_contents)
    page_contents = re.sub(re_punctuation, " ", page_contents)
    page_contents = re.sub(re_spaces, " ", page_contents)
    
    return page_contents

#  create docids, vocab and postings table from cleaned html content
def make_index(url, page_contents):
    # declare refs to global variables
    global docids
    global postings
    global vocab

    # first convert bytes to string if necessary
    if isinstance(page_contents, bytes):
        page_contents = page_contents.decode('utf-8', "ignore")

    print('===============================================')
    print('make_index: url = ', url)
    print('===============================================')
    # clean html first
    page_text = clean_html(page_contents)

    # docids table
    doc_id = len(docids)
    docids.append(url)

    page_text = page_text.lower()
    term_list = page_text.split()

    # term_list = lemmatize_terms(term_list)
    # term_list = stem_terms(term_list)

    for term in term_list:
        # vocab table
        if term not in vocab:
            term_id = len(vocab)
            vocab.append(term)

        # postings table
        term_id = vocab.index(term)
        postings_list = postings.get(term_id)

        # get index of current doc in list of [docids,freq]
        if postings_list is not None:
            doc_index = [ind for ind, term_doc in enumerate(postings_list) if term_doc[0] == doc_id]

            # if not empty then increment freq at doc_index
            if len(doc_index) is not 0:
                postings_list[doc_index[0]][1] += 1
            # else append new list to term_id in postings
            else:
                postings[term_id].append([doc_id, 1])
        # current doc is not in list of [docids,freq] so add it
        else:
            postings[term_id] = [[doc_id, 1]]

    return
# Take the stem of each term in term_list and return new list
# uses code from nltk foundation 
def stem_terms(term_list):
    stemmed_list = []
    stemmer = PorterStemmer(mode='NLTK_EXTENSIONS')

    for term in term_list:
        stemmed_list.append(stemmer.stem(term))
    return stemmed_list
# Lemmatize every term  in term_list and returns new list 
# uses code from nltk foundation 
def lemmatize_terms(term_list):
    lmtzed_list = []
    lmtzr = WordNetLemmatizer()

    for term in term_list:
        lmtzed_list.append(lmtzr.lemmatize(term))
    return lmtzed_list

# Unfinished turn terms such as she'd into she and would respectivly 
def normalizer(term):
    terms = term.split("'")
    if term[1] == "d":
        term[1] = "would"
    elif term[1] == "s":
        term[1] = "is"
    elif term[1] == "re":
        term[1] = "are"
    elif term[1] == "ll":
        term[1] = "will"
    elif term[1] == "m":
        term[1] = "am"
    elif term[1] == "t":
        term[1] = "not"

    return terms
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
