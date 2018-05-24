#!/usr/bin/python3

import re
from s_engine import retriever
from util import utils
from decimal import *
def main():
    option = ""
    query_list = []
    res_file_name = "results.csv"
    print("This is a search engine : Type -query followed by a sequence of terms or -file followed by a file path or -exit to Exit")
    while True: 
        option = input("Type in an option (-exit, -query, -file) :")
        print(option)
        option = re.sub(r"[^A-Za-z0-9%\s\-'+]","", option)
        print(option)
        option = option.lower()
        option = option.split()
        print(option)
        if option[0] == '-query':
            print(option[1:])
            docs =  process_query(option[1:])

            write_results_file("result/"+res_file_name, docs)

        elif option[0] == '-file':
            path = option[1]
            query_list = read_querys_file(path)

            i = 0
            for query in query_list:
                i += 1
                docs = process_query(query)
                # write_results_file('result/'+res_file_name, docs, i)

        elif option[0] == "-exit":
            print("Exiting!")
            break
        else:
            print("Invalid choice, try again")
            

    
def process_query(query_terms):
        
    query_terms = utils.stem_terms(query_terms)
    docs = retriever.retrieve(query_terms)

    return docs

def write_results_file(path, docs, query_no = "1"):
    try:
        result_file = open(path, 'a')
        for ranking in docs:
    
            rank = str(query_no) + "," + str(ranking[0]) + ',' + str(ranking[1])
            result_file.write('{0},{1},{2}\n'.format(query_no, (ranking[0]), ranking[1]))
        print ("DONE ! Ranks have been written to: " + path)
    except:
        print("Wrong write file path, try again !")
    result_file.close()
    return

def read_querys_file(path):
    query_list = []
    try:
        with open(path, 'r') as read_file:
            for line in read_file:
                line = re.sub(r"[^A-Za-z0-9%\s'+]", "", line)
                terms = line.split()
                terms = utils.stem_terms(terms)
                query_list.append(terms)
        
        return query_list
    except:
        print("Wrong file path, try again !")  
    return

def search():
    option = ""
    query_list = []
    res_file_name = "results.csv"
    print("This is a search engine : Type -query followed by a sequence of terms or -file followed by a file path or -exit to Exit")
    while True: 
        option = input("Type in an option (-exit, -query, -file) :")
        option = re.sub(r"[^A-Za-z0-9%\s'\-+]","", option)
        option = option.split()
        if option[0] == "-query":
            docs =  process_query(option[1:])
            write_results_file(res_file_name, docs)

        elif option[0] == "-file":
            path = option[1]
            query_list = read_querys_file(path)

            i = 0
            for query in query_list:
                i += 1
                docs = process_query(query)
                write_results_file(res_file_name, docs, i)

        elif option[0] == "-exit":
            print("Exiting!")
            break
        else:
            print("Invalid choice, try again")
if __name__ == '__main__':
    main()