import gzip
import sys
import os
import json
import re
from collections import defaultdict

from utils import get_text_from_document, extract_document_metadata, format_date, save_document_to_storage, tokenize

def main():
    # make sure the command line inputs are correct
    if len(sys.argv) != 3:
        print(
"""
Please provide the correct command line inputs
The program accepts:
    1. the path to the latimes.gz file in your file system
    2. the path where you want to store the documents and metadata

Example: 
    python IndexEngine.py C:/Users/.../latimes.gz C:/Users/.../documents
"""
        )
        sys.exit()
    
    # extract the command line inputs
    latimes_file_path = sys.argv[1]
    storage_path = sys.argv[2]

    # check if the latimes file exists
    if not os.path.exists(latimes_file_path):
        print("The path to the latimes file does not exist. Please provide the correct path.")
        sys.exit()
    
    # check if the storage directory exists
    if os.path.exists(storage_path):
        print("The storage directory already exists. Please provide a new directory path.")
        sys.exit()

    os.makedirs(storage_path)
    print(f"Directory created at {storage_path}")

    # initialize variables
    current_doc_lines = []
    internal_id_counter = 0
    # the array position represents the internal ID of the document and the value is the DOCNO
    docnos = []
    # the dictionary key is the DOCNO and the value is the internal ID
    docno_to_internal_id = {}
    # we will store the document length in a separate file, with one document length per line where the document length on line 1 goes with document 1, and so forth
    documents_length = ""
    # our lexicon consists of a dictionary that maps from a term to its unique integer id.
    lexicon = {}
    # we keep track of the term id counter, for each new term we increment this counter, starting from 0. Used to assign unique integer ids to terms in the lexicon.
    term_id_counter = 0
    # the postings list is a dictionary where the key is the term id and the value is a list of tuples (frequency, internal_id) where frequency is the number of times the term appears in the document with the internal_id
    postings_list = defaultdict(list)

    # read the latimes file
    with gzip.open(latimes_file_path, 'rt') as file:
        print(f"Reading the latimes file from {latimes_file_path}")
        for line in file:
            if line.startswith("</DOC>"):
                # end of a document
                # we store it in the storage directory
                current_doc = "".join(current_doc_lines)
                docno, headline, year, month, day = extract_document_metadata(current_doc)
                # save one file docno.txt with the content of the document at the storagePath/YY/MM/DD/docno.txt
                save_document_to_storage(current_doc, f"{storage_path}/{year}/{month}/{day}/{docno}.txt")

                # save one file docno.metadata.json with the metadata at the storagePath/YY/MM/DD/docno.metadata.json
                metadata = {
                    "id": internal_id_counter,
                    "docno": docno,
                    "headline": headline,
                    "date": format_date(int(year), int(month), int(day))
                }
                save_document_to_storage(json.dumps(metadata), f"{storage_path}/{year}/{month}/{day}/{docno}.metadata.json")

                # get text from the document from the following tags: TEXT, HEADLINE, GRAPHIC
                document_text = get_text_from_document(current_doc)
                # tokenize the text
                tokens = []
                tokenize(document_text, tokens)

                # append the document length to the documents_length string
                document_length = len(tokens)
                documents_length += f'{document_length}\n'

                # count the frequency of each token in the document
                tokens_counter = defaultdict(int)
                for token in tokens:
                    tokens_counter[token] += 1

                    # update the lexicon if the term is not already in the lexicon
                    if token not in lexicon:
                        lexicon[token] = term_id_counter
                        term_id_counter += 1

                # update the postings list
                for token, frequency in tokens_counter.items():
                    # append (frequency, internal_id) to the postings list of the term
                    postings_list[lexicon[token]].append((frequency, internal_id_counter))
                
                # store the docno in the array
                docnos.append(docno)
                # store the docno and internal id in the dictionary
                docno_to_internal_id[docno] = internal_id_counter
                
                # reset the current_doc 
                current_doc_lines = []
                # increment the internal id counter
                internal_id_counter += 1
                continue
        
            current_doc_lines.append(line)

    # save the docnos array and the docno_to_internal_id dictionary to the storage directory
    save_document_to_storage(json.dumps(docnos), f"{storage_path}/internal_id_to_docno.json")
    save_document_to_storage(json.dumps(docno_to_internal_id), f"{storage_path}/docno_to_internal_id.json")
    save_document_to_storage(documents_length, f"{storage_path}/doc-lengths.txt")
    save_document_to_storage(json.dumps(lexicon), f"{storage_path}/lexicon.json")
    save_document_to_storage(json.dumps(postings_list), f"{storage_path}/postings-list.json")

    print("Finished reading and storing the documents and metadata from the latimes file.")

if __name__ == "__main__":
    main()
