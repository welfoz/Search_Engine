import sys
import os
from utils import load_inverted_index, load_lexicon, load_internal_id_to_docno, tokenize

def intersect(posting_list1: list[tuple[int, int]], posting_list2: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """
    Intersect two postings lists.

    Args:
        postings_list1: The first postings list.
        postings_list2: The second postings list.

    Returns:
        List of tuples (internal doc id, frequency) that satisfy the intersection.
    """
    result = []
    index_list_1 = 0
    index_list_2 = 0

    # we stop when one list exceed 
    while index_list_1 != len(posting_list1) and index_list_2 != len(posting_list2):
        frequency_1, doc_id_1 = posting_list1[index_list_1]
        frequency_2, doc_id_2 = posting_list2[index_list_2]

        if doc_id_1 == doc_id_2: 
            result.append(posting_list1[index_list_1])
            index_list_1 += 1
            index_list_2 += 1
        # we increment the smaller index with the smallest doc id 
        elif doc_id_1 < doc_id_2:
            index_list_1 += 1
        else: 
            index_list_2 += 1
            
    return result

def intersect_postings_lists(postings_lists: list[list[tuple[int, int]]]) -> list[int]:
    """
    Intersect the postings lists of the terms in the query.

    Args:
        postings_lists: A list of postings lists of the terms in the query.

    Returns:
        A list of internal doc ids that satisfy the query.
    """
    if len(postings_lists) == 0:
        return []

    result = postings_lists[0]
    current_list_index = 1
    # we stop when we reach the end of the postings lists or the result is empty
    while current_list_index != len(postings_lists) and len(result) != 0:
        result = intersect(result, postings_lists[current_list_index])
        current_list_index += 1

    return result

def main():
    # make sure the command line inputs are correct
    if len(sys.argv) != 4:
        print(
"""
Please provide the correct command line inputs
The program accepts:
    1. the path to the storage directory of the index
    2. the path to the queries file
    3. the path to the output file
example: 
    python BooleanAND.py C:/Users/.../storage C:/Users/.../queries.txt C:/Users/.../output.txt
"""
        )
        sys.exit()
    
    # extract the command line inputs
    storage_path = sys.argv[1]
    queries_file_path = sys.argv[2]
    output_file_path = sys.argv[3]

    # output result
    result = ""

    # check if the storage directory exists
    if not os.path.exists(storage_path):
        print("The storage directory does not exist. Please provide the correct path.")
        sys.exit()
    
    # check if the queries file exists
    if not os.path.exists(queries_file_path):
        print("The queries file does not exist. Please provide the correct path.")
        sys.exit()

    # load the inverted index, lexicon, and internal_id_to_docno
    inverted_index = load_inverted_index(storage_path)
    lexicon = load_lexicon(storage_path)
    internal_id_to_docno = load_internal_id_to_docno(storage_path)
    print("Finished loading the inverted index, lexicon, and internal_id_to_docno.")


    # [(topic_number, query), ...]
    queries = []
    # read the queries file
    with open(queries_file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 2):
            topic_number = lines[i].strip()
            query = lines[i+1].strip()
            queries.append((topic_number, query))
    
    for query in queries:
        topic_number, query_text = query
        # tokenize the query
        tokens = []
        tokenize(query_text, tokens)

        # find the term ids from the lexicon
        term_ids = []
        for token in tokens:
            if token in lexicon:
                term_ids.append(lexicon[token])
        
        # get the postings list of the terms in the query
        postings_lists = [inverted_index[str(term_id)] for term_id in term_ids]

        # sort the postings lists by the length of the list to start with the smallest list and optimize the intersection
        postings_lists.sort(key=lambda x: len(x))

        # intersect the postings lists of the terms in the query
        postings_lists_intersection = intersect_postings_lists(postings_lists)

        rank = 1
        # we sort the result by the doc_id to have a consistent output
        postings_lists_intersection.sort(key=lambda x: x[1])

        docs_number_retrieved = len(postings_lists_intersection)
        for frequency, doc_id in postings_lists_intersection:
            docno = internal_id_to_docno[doc_id]
            score = docs_number_retrieved - rank
            # topicID Q0 docno rank score runTag
            result += f"{topic_number} Q0 {docno} {rank} {score} fmichelAND\n"
            rank += 1

    # save the output to the output file
    with open(output_file_path, 'w') as file:
        file.write(result)

    # save "B. Run your program with the latimes and the 45 queries and name the results file hw2-results-fmichel.txt"
    with open("hw2-results-fmichel.txt", 'w') as file:
        file.write(result)

    print("Finished writing the output to the output file.")

if __name__ == "__main__":
    main()