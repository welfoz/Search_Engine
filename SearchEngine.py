import sys
import math
import re
from collections import defaultdict
import os
import json
import time
import heapq

from utils import get_file_path_with_docno, get_text_from_document_without_headline, load_inverted_index, load_lexicon, load_internal_id_to_docno, load_doc_lengths, tokenize

def main():
    # make sure the command line inputs are correct
    if len(sys.argv) != 2:
        print(
"""
Please provide the correct command line inputs
The program accepts:
    1. the path to the storage directory of the index
example: 
    python SearchEngine.py C:/Users/.../storage 
"""
        )
        sys.exit()

    # remove trailing slash
    storage_path = sys.argv[1].rstrip('/')

    # check if the storage directory exists
    if not os.path.exists(storage_path):
        print("The storage directory does not exist. Please provide the correct path.")
        sys.exit()

    print("Loading the inverted index, lexicon...")

    inverted_index = load_inverted_index(storage_path)
    lexicon = load_lexicon(storage_path)
    internal_id_to_docno = load_internal_id_to_docno(storage_path)
    doc_lengths = load_doc_lengths(storage_path)

    print("Finished loading the inverted index, lexicon, and internal_id_to_docno.")

    # compute average document length
    num_docs = len(doc_lengths)
    avg_doc_length = sum(doc_lengths) / num_docs

    while True:
        query = input("Enter your query: ")
        start_time = time.time()
        query_score = defaultdict(float)

        # tokenize the query
        query_terms = []
        tokenize(query, query_terms)

        # find the term ids from the lexicon
        query_terms_id = []
        for query_term in query_terms:
            if query_term in lexicon:
                query_terms_id.append(str(lexicon[query_term]))

        # BM25 score
        for term_id in query_terms_id:
            number_of_docs_with_term = len(inverted_index[term_id])
            term_idf = math.log((num_docs - number_of_docs_with_term + 0.5) / (number_of_docs_with_term + 0.5))

            posting_list = inverted_index[term_id]
            for freq_docid in posting_list:
                frequency = freq_docid[0]
                doc_id = freq_docid[1]

                doc_length = doc_lengths[doc_id] 
                doc_length_normalized = doc_length / avg_doc_length
                
                k1 = 1.2
                b = 0.75
                K = k1 * (1 - b + b * doc_length_normalized)

                tf = ((k1 + 1) * frequency) / (K + frequency)
                query_score[doc_id] += tf * term_idf
        
        # print the top 10 results with snippet
        top_10_results = sorted(query_score.items(), key=lambda x: x[1], reverse=True)[:10]
        for rank, (doc_id, score) in enumerate(top_10_results, start=1):
            docno = internal_id_to_docno[doc_id]

            doc_path = get_file_path_with_docno(storage_path, docno) + ".txt"
            metadata_path = get_file_path_with_docno(storage_path, docno) + ".metadata.json"

            snippet = ""
            with open(doc_path, 'r') as file:
                doc_text = file.read()
                doc_content = get_text_from_document_without_headline(doc_text)

                # From Turpin et al. 2007 (Fig 2) DOI: 10.1145/1277741.1277766
                # "?<=" to keep the punctuation in sentences
                sentences = re.split(r'(?<=[.!?])', doc_content)
                # we want to combine small sentences with the next one
                combined_sentences = []
                sentence_to_combine = ""
                for sentence in sentences:
                    sentence_to_combine += sentence
                    if len(sentence) > 20:
                        combined_sentences.append(sentence_to_combine)
                        sentence_to_combine = ""
                
                if len(sentence_to_combine) > 0:
                    combined_sentences.append(sentence_to_combine)

                # max heap to store the best summaries
                best_summaries = []
                for index, sentence in enumerate(combined_sentences, start=0):
                    sentence_tokens = []
                    tokenize(sentence, sentence_tokens)

                    first_sentences_bonus = 0 
                    if index == 0:
                        first_sentences_bonus = 2
                    elif index == 1:
                        first_sentences_bonus = 1
                    
                    total_occurrences = 0
                    distinct_query_terms = 0
                    consecutive_query_term_count = {}
                    for query_term in query_terms:
                        query_term_count = 0
                        for i, token in enumerate(sentence_tokens):
                            if token == query_term:
                                query_term_count += 1
                                # if the previous token is a query term, increment the count
                                if consecutive_query_term_count.get(i - 1) is not None:
                                    consecutive_query_term_count[i - 1] += 1
                                consecutive_query_term_count[i] = 1

                        if query_term_count > 0:
                            total_occurrences += query_term_count
                            distinct_query_terms += 1
                    
                    max_consecutive_query_term_count = max(consecutive_query_term_count.values()) if consecutive_query_term_count else 0

                    # we keep weights at 1 for now, keep it simple
                    score = first_sentences_bonus + total_occurrences + distinct_query_terms + max_consecutive_query_term_count
                    # we normalize the score by the number of tokens in the sentence to avoid favoring long sentences
                    normalized_score = score / len(sentence_tokens) if len(sentence_tokens) > 0 else 0

                    heapq.heappush(best_summaries, (-normalized_score, sentence))
                
                MAX_SNIPPET_LENGTH = 200
                for best_summary in best_summaries:
                    snippet += best_summary[1]
                    if len(snippet) >= MAX_SNIPPET_LENGTH:
                        break
                    
            metadata = json.load(open(metadata_path))
                
            headline = metadata["headline"] if metadata["headline"] else snippet[:50] + "..."
            print(f"{rank}. {headline} ({metadata['date']})")
            print(f"{snippet} ({docno})\n")

        end_time = time.time()
        print(f"Retrieval took {end_time - start_time:.2f} seconds.")

        # ask menu to the user
        next_action = ""
        exit_loop = False
        while not exit_loop:
            next_action = input("Enter the rank to see the document, 'N' for next query, 'Q' to quit: ")
            if next_action == 'N' or next_action == 'Q':
                exit_loop = True
            elif next_action.isdigit():
                rank = int(next_action)
                if rank > len(top_10_results):
                    print(f"Invalid rank, please enter a rank between 1 and {len(top_10_results)}")
                    continue
                doc_id, score = top_10_results[rank - 1]
                docno = internal_id_to_docno[doc_id]

                doc_path = get_file_path_with_docno(storage_path, docno) + ".txt"
                with open(doc_path, 'r') as file:
                    doc_text = file.read()
                    print(doc_text)
            else:
                print("Invalid input. Please enter 'N', 'Q', or a rank number.")
        
        if next_action == 'Q':
            print("Quitting...")
            break
        elif next_action == 'N':
            continue
        else: 
            print("Unexpected error.")

if __name__ == "__main__":
    main()
