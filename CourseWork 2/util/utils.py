import os
import sys
from nltk.stem import PorterStemmer, WordNetLemmatizer
import collections

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from UEAlite import stem
# Take the stem of each term in term_list and return new list
# uses code from nltk foundation 
def stem_terms(term_list):
    '''
        Uses nltk stemmer
        to stem a list of terms
    '''
    stemmed_list = []
    stemmer = PorterStemmer(mode='NLTK_EXTENSIONS')

    for term in term_list:
        stemmed_list.append(stemmer.stem(term))
        
    return stemmed_list
# Lemmatize every term  in term_list and returns new list 
# uses code from nltk foundation 

def lemmatize_terms(term_list):
    '''
        Uses nltk lemmatizer
        to lemmatize a list of terms
    '''
    lmtzed_list = []
    lmtzr = WordNetLemmatizer()

    for term in term_list:
        lmtzed_list.append(lmtzr.lemmatize(term))

    return lmtzed_list
# calls uea lite stemmer
def uea_stemmer(term_list):
    '''
        Uses uea lite stemmer
        to stem a list of terms
    '''
    stemmed_list = []
    for term in term_list:
        stemmed_list.append(stem(term))

    return stemmed_list
        
def normalizer(term):
    '''
        Normalize terms 
    '''
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
def flatten_list(list):
    for el in list:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten_list(el)
        else:
            yield el