import sys
import os
import re
import json
from nltk.stem import PorterStemmer, WordNetLemmatizer

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from util import utils
import unidecode


# global declarations
docids = []
doc_sizes = []
postings = {}
vocab = []
descriptions = []
summaries = []
headings = []
titles = []


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
    global doc_sizes
    global postings
    global vocab
    global descriptions
    global summaries
    global headings
    global titles
    
    path = "index/"

    # writes to index files: docids, vocab, postings
    outlist1 = open(path+"docids.txt", 'w')
    outlist2 = open(path+"doc_sizes.txt", 'w')
    outlist3 = open(path+"vocab.txt", 'w')
    outlist4 = open(path+"postings.txt", 'w')
    outlist5 = open(path+"descriptions.txt", 'w')
    outlist6 = open(path+"summaries.txt", 'w')
    outlist7 = open(path+"headings.txt", 'w')
    outlist8 = open(path+"titles.txt", 'w')
    

    json.dump(docids, outlist1)
    json.dump(doc_sizes, outlist2)
    json.dump(vocab, outlist3)
    json.dump(postings, outlist4)
    json.dump(descriptions, outlist5)
    json.dump(summaries, outlist6)
    json.dump(headings, outlist7)
    json.dump(titles, outlist8)

    outlist1.close()
    outlist2.close()
    outlist3.close()
    outlist4.close()
    outlist5.close()
    outlist6.close()
    outlist7.close()
    outlist8.close()
    return

# remove markup from html page contents
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
    summary = save_doc(doc_id, page_contents)

    page_contents = unidecode.unidecode(page_contents)
    page_text = page_text.lower()
    term_list = page_text.split()

    index_terms(term_list, doc_id, summary, nltk_stem = True)

    return
def index_terms(term_list, doc_id, summary, nltk_lem = False, nltk_stem = False, uea_stem = False):
    if nltk_lem:
        term_list = utils.lemmatize_terms(term_list)  #Lematize from nltk
    if nltk_stem:
        term_list = utils.stem_terms(term_list)       #Porter Stemmer
    if uea_stem:
        term_list = utils.uea_stemmer(term_list)      #Uealite Stemmer

    global postings
    global vocab
    global doc_sizes
    doc_size = 0
    term_positions = []
    for term in term_list:
        doc_size += 1
        # vocab table
        if term not in vocab:
            term_id = len(vocab)
            vocab.append(term)
            
        # postings table
        term_id = vocab.index(term)
        postings_list = postings.get(term_id)
        # positional tokens for snipet retrieval
        pos_tokens = re.finditer(re.escape(term), summary, re.IGNORECASE)
        term_positions = [m.start(0) for m in pos_tokens]

        # get index of current doc in list of [docids,freq]
        if postings_list is not None:
            doc_index = [ind for ind, term_doc in enumerate(postings_list) if term_doc[0] == doc_id]

            # if not empty then increment freq at doc_index
            if len(doc_index) is not 0:
                postings_list[doc_index[0]][1] += 1
            # else append new list to term_id in postings
            else:
                postings[term_id].append([doc_id, 1, term_positions])
        # current doc is not in list of [docids,freq] so add it
        else:
            postings[term_id] = [[doc_id, 1, term_positions]]
    doc_sizes.append(doc_size)

def save_doc(doc_id, doc_contents):
    global descriptions
    global summaries
    global headings
    global titles

    re_content = r'(<div class="portlet-body">.*?<footer.*?>)'
    re_lists = r'<li.*?>.*?<\/li>|<ul.*?>.*?<\/ul>'
    re_title = r'<title>(.+)<\/title>'
    re_heading = r'<h1>([\w].*)<\/h1>'
    re_spans = r'<span.*?>.*?<\/span>'
    re_desc = r'name="description"[^>]*content="([^"]+)"|content="([^"]+)"[^>]*name="description"'
    re_tags = r'<script.*?>.*?<\/script>|<style.*?>.*?<\/style>|<.+?>|&nbsp|&amp'

    doc_contents = doc_contents.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    doc_contents = unidecode.unidecode(doc_contents)

    title = re.search(re_title, doc_contents)
    heading = re.search(re_heading, doc_contents)
    description = re.findall(re_desc, doc_contents)

    summary = re.sub(re_spans, ' ', doc_contents)
    summary = re.sub(re_lists, ' ', summary)
    summary = re.sub(re_heading, ' ', summary)
    summary = re.search(re_content, summary)

    if (summary):
        summary = re.sub(re_tags, ' ', summary.group(1))
        # Get rid of spaces and punctuation
        summary = re.sub(r'(\w)\s([,.:])|;', r"\1\2", summary)
        summary = re.sub(r';|\s{2,}', ' ', summary)
    else:
        summary = ''

    heading = '' if not heading else heading.group(1)
    description = ' '.join(str(group) for group in description[0]) if description else ''

    titles.append(title.group(1))
    headings.append(heading)
    summaries.append(summary)
    descriptions.append(description)

    return summary
    
# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
