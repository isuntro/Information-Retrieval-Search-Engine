import sys
import os
import csv
import json
import numpy
import matplotlib.pyplot as plt
import copy
from s_engine import retriever

docids = []
evaluation = {}
relevant_docs = {}
queries = []

basic = {}
basic_pr = {}
stemmed = {}
stemmed_pr = {}
stemmed_weigthed = {}
stemmed_weigthed_pr = {}
rel_feedback = {}
rel_feedback_pr = {}


def main():
    read_files()
    read_system_files()
    
    # plot_systems_pr()
    f_measure = 0
    for doc in basic_pr.values():
       f_measure += doc[9][3]
    print(f_measure / 10)

    f_measure = 0
    for doc in stemmed_pr.values():
       f_measure += doc[9][3]
    print(f_measure / 10)

    f_measure = 0
    for doc in stemmed_weigthed_pr.values():
       f_measure += doc[9][3]
    print(f_measure / 10)

    f_measure = 0
    for doc in rel_feedback_pr.values():
       f_measure += doc[9][3]
    print(f_measure / 10)
    

    queries_points = {}
    
    for query in queries:
        docs = []
        result = []
        index = queries.index(query) + 1
        scores = retriever.tf_idf_vector(query)
        i = 0
        for docid in sorted(scores, key=scores.get, reverse=True):
            result.append(docids[docid])
            i += 1
            if i is 41 :
                break
        docs = result[:40]
        points = get_pr_points(docs, index)
        print(points)
        queries_points[index] = points
    
        # print(points)
    plot_average_p(queries_points)

    index = 1
    query = queries[index]
    scores = retriever.tf_idf_vector(query)
    for docid in sorted(scores, key=scores.get, reverse=True):
        result.append([scores.get(docid),docids[docid]])
    docs = result[:40]

    points = get_pr_points(docs, index)
    print(points)
    plot_points(points)

    print('Exit')
def read_system_files():
    global basic
    global stemmed
    global stemmed_weigthed 
    global rel_feedback

    global basic_pr
    global stemmed_pr
    global stemmed_weigthed_pr
    global rel_feedback_pr

    with open('basic_100.csv', 'r') as in_basic:
        for i in range (0,3):
            in_basic.readline()
        csv_reader = csv.reader(in_basic)
        for line in csv_reader:
            query_no = int(line[0])
            if not basic.get(query_no):
                basic[query_no] = [line[2]]
            else:
                basic[query_no].append(line[2])
        for docs in basic:
            basic[docs] = basic[docs][:10]
            basic_pr[docs] = get_pr_points(basic[docs], docs)
        
    with open('stem_100.csv', 'r') as in_stem:
        for i in range (0,3):
            in_stem.readline()
        csv_reader = csv.reader(in_stem)
        for line in csv_reader:
            query_no = int(line[0])
            if not stemmed.get(query_no):
                stemmed[query_no] = [line[2]]
            else:
                stemmed[query_no].append(line[2])
        for docs in stemmed:
            stemmed[docs] = stemmed[docs][:10]
            stemmed_pr[docs] = get_pr_points(stemmed[docs], docs)

    with open('weighted_100.csv', 'r') as in_weighted:
        for i in range (0,3):
            in_weighted.readline()
        csv_reader = csv.reader(in_weighted)
        for line in csv_reader:
            query_no = int(line[0])
            if not stemmed_weigthed.get(query_no):
                stemmed_weigthed[query_no] = [line[2]]
            else:
                stemmed_weigthed[query_no].append(line[2])
        for docs in stemmed_weigthed:
            stemmed_weigthed[docs] = stemmed_weigthed[docs][:10]
            stemmed_weigthed_pr[docs] = get_pr_points(stemmed_weigthed[docs], docs)

    with open('relbfk.csv', 'r') as in_rel_fbk:
        for i in range (0,3):
            in_rel_fbk.readline()
        csv_reader = csv.reader(in_rel_fbk)
        for line in csv_reader:
            query_no = int(line[0])
            if not rel_feedback.get(query_no):
                rel_feedback[query_no] = [line[2]]
            rel_feedback[query_no].append(line[2])
        for docs in rel_feedback:
            rel_feedback_pr[docs] = get_pr_points(rel_feedback[docs], docs)
def get_n_docs(dictionary, n):
    for docs in dictionary:
        dictionary[docs] = dictionary[docs][:10]
    return dictionary
def plot_systems_pr():
    
    global basic_pr
    global stemmed_pr
    global stemmed_weigthed_pr
    global rel_feedback_pr
    precission_list = []
    recall_list = []
    total_retrieved = 10
    queries_points = basic_pr
    for i in range(0, total_retrieved):
        precission = 0
        recall = 0
        f_score = 0

        for query_points in queries_points.values():
            precission += query_points[i][1]
            recall += query_points[i][2]
            # f_score += query_points[i][3]
        precission_list.append(precission / total_retrieved)
        recall_list.append(recall / total_retrieved)
        # f_score_list.append(f_score / total_retrieved)
    # print(precission_list)
    # print(recall_list)
    plt.figure()
    plt.rcParams.update({'font.size': 14}) # Sets all font-sizes to 14
    plt.plot(recall_list, precission_list, '-.c+', label='Stemmed average precision-recall curve')
    plt.xlabel('Recall', weight='bold')
    plt.ylabel('Precision', weight='bold')
    plt.title('Average Precision versus recall over 10 queries for different systems')
    plt.grid()

    precission_list = []
    recall_list = []
    queries_points = stemmed_pr
    for i in range(0, total_retrieved):
        precission = 0
        recall = 0
        f_score = 0

        for query_points in queries_points.values():
            precission += query_points[i][1]
            recall += query_points[i][2]
            # f_score += query_points[i][3]
        precission_list.append(precission / total_retrieved)
        recall_list.append(recall / total_retrieved)
        # f_score_list.append(f_score / total_retrieved)
    # print(precission_list)
    # print(recall_list)
    plt.plot(recall_list, precission_list, '--g+', label='Feedback average precision-recall curve')

    precission_list = []
    recall_list = []
    queries_points = stemmed_weigthed_pr
    for i in range(0, total_retrieved):
        precission = 0
        recall = 0
        f_score = 0

        for query_points in queries_points.values():
            precission += query_points[i][1]
            recall += query_points[i][2]
            # f_score += query_points[i][3]
        precission_list.append(precission / total_retrieved)
        recall_list.append(recall / total_retrieved)
        # f_score_list.append(f_score / total_retrieved)
    # print(precission_list)
    # print(recall_list)
    plt.plot(recall_list, precission_list, ':b+', label='Weighted average precision-recall curve')
    
    precission_list = []
    recall_list = []
    queries_points = rel_feedback_pr
    for i in range(0, total_retrieved):
        precission = 0
        recall = 0
        f_score = 0

        for query_points in queries_points.values():
            precission += query_points[i][1]
            recall += query_points[i][2]

        precission_list.append(precission / total_retrieved)
        recall_list.append(recall / total_retrieved)

    plt.plot(recall_list, precission_list, '-r+', label='Basic average precision-recall curve')
    plt.legend(loc='lower left')
    plt.show()
     
def plot_system_r_prec():
    global basic
    global stemmed
    global stemmed_weigthed
    global rel_feedback

def mean_average_precision(system):
    precision = 0
    for doc in system:
        query_doc = system[doc]
        precision += query_doc[9][1]
    return precision / 10 

def read_files():
    global docids
    global relevant_docs
    global queries
    with open('index/docids.txt', 'r') as docs:
        docids = json.load(docs)
    with open('IR_queries.txt', 'r') as queries_list:
        for line in queries_list:
            terms = line.split()
            queries.append(terms)
    in_eval = open('IRpooledResults.csv', 'r')
    in_eval.readline()
    csv_reader = csv.reader(in_eval)

    for line in csv_reader:
        if line[0] != '':
            query_no = int(line[0])
            if not relevant_docs.get(query_no):
                relevant_docs[query_no] = [[line[1],line[2],line[3]]]

            else:
                relevant_docs[query_no].append([line[1],line[2],line[3]])

    # load the data

def calc_precission(rel_docs_retrieved, total_retrieved):
    '''
        Calculates precission
    '''
    return rel_docs_retrieved / total_retrieved

def calc_recall(rel_docs_retrieved, total_relevant_docs):
    '''
        Calculates recall
    '''
    return rel_docs_retrieved / total_relevant_docs

def calc_map(k):
    return

def calc_f_score(precission, recall):
    if precission == 0 or recall == 0:
        return 0
    return (2 * precission * recall) / (precission + recall)

def get_pr_points(results, query_no):
    global docids

    max_retrieved = 10
    pr_points = []
    rel_docs = []

    for doc in relevant_docs[query_no]:
        rel_docs.append(doc[2])


    nr_retrieved_docs = 0
    nr_rel_docs = 0
    total_rel_docs = len(rel_docs)

    for i in range (0,max_retrieved):
        if results[i] in rel_docs:
            nr_rel_docs += 1
        nr_retrieved_docs += 1
        precission = calc_precission(nr_rel_docs, nr_retrieved_docs)
        recall = calc_recall(nr_rel_docs, total_rel_docs)

        f_score = calc_f_score(precission, recall)
        pr_points.append([i,precission,recall, f_score])


    return pr_points

def plot_points(pr_points):
    precision = []
    recall = []
    f_score  = []

    for point in pr_points:
        precision.append(point[1])
        recall.append(point[2])
        f_score.append(point[3])

    plt.figure()
    plt.rcParams.update({'font.size': 14}) # Sets all font-sizes to 14
    plt.plot(recall, precision, '-b+', label='Original precision-recall curve')
    plt.xlabel('Recall', weight='bold')
    plt.ylabel('Precision', weight='bold')
    plt.title('Precision versus recall')
    plt.grid()

    n_docs = len(precision)
    smoothed_precision = copy.copy(precision)
    max_precision = precision[n_docs-1]
    print(max_precision)
    for i in range(n_docs-1, 0, -1):
        if precision[i] < max_precision:
            smoothed_precision[i] = max_precision
        else:
            max_precision = precision[i];

    # Plot the smoothed curve on top of the original
    plt.plot(recall, smoothed_precision, '-r*', label='Smoothed precision-recall curve')
    plt.legend(loc='lower left')
    plt.show()
# precision 1 recall 2
def plot_average_p(queries_points):
    precission_list = []
    recall_list = []
    f_score_list  = []
    total_retrieved = len(queries_points[1])
    print("total retrieved " + str(total_retrieved))
    for i in range(0, total_retrieved):
        precission = 0
        recall = 0
        f_score = 0

        for query_points in queries_points.values():
            precission += query_points[i][1]
            recall += query_points[i][2]
            # f_score += query_points[i][3]
        precission_list.append(precission / total_retrieved)
        recall_list.append(recall / total_retrieved)
        # f_score_list.append(f_score / total_retrieved)
    print(precission_list)
    print(recall_list)
    plt.figure()
    plt.rcParams.update({'font.size': 14}) # Sets all font-sizes to 14
    plt.plot(recall_list, precission_list, '-b+', label='Original precision-recall curve')
    plt.xlabel('Recall', weight='bold')
    plt.ylabel('Precision', weight='bold')
    plt.title('Average Precision versus recall over 10 queries')
    plt.grid()

    plt.show()
if __name__ == '__main__':
    main()