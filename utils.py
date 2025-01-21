import sys
import re
from collections import defaultdict
import os
import json

def get_file_path_with_docno(storage_path: str, docno: str) -> str:
    """
    Get the file path of a document by its DOCNO
    """
    return f"{storage_path}/{docno[6:8]}/{docno[2:4]}/{docno[4:6]}/{docno}"

def get_text_from_document_without_headline(doc: str) -> str:
    """
    The text of a document should come from the following tags: TEXT, HEADLINE, GRAPHIC
    """
    text = ""
    if "<TEXT>" in doc:
        raw_text = doc.split("<TEXT>")[1].split("</TEXT>")[0].strip()
        # remove tags from the text
        text = re.sub(r'<[^>]+>', ' ', raw_text).replace("\n", "").strip()
    # if "<HEADLINE>" in doc:
    #     raw_headline = doc.split("<HEADLINE>")[1].split("</HEADLINE>")[0].strip()
    #     # remove tags from the headline
    #     headline = re.sub(r'<[^>]+>', ' ', raw_headline).replace("\n", "").strip()
    #     text += headline
    if "<GRAPHIC>" in doc:
        raw_graphic = doc.split("<GRAPHIC>")[1].split("</GRAPHIC>")[0].strip()
        # remove tags from the graphic
        graphic = re.sub(r'<[^>]+>', ' ', raw_graphic).replace("\n", "").strip()
        text += graphic
    return text

def load_inverted_index(storage_path: str) -> dict:
    """
    Load the inverted index from the storage directory and handle exceptions.
    """
    try:
        with open(f"{storage_path}/postings-list.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("The inverted index file does not exist. Please provide the correct path.")
        sys.exit()

def load_lexicon(storage_path: str) -> dict:
    """
    Load the lexicon from the storage directory and handle exceptions.
    """
    try:
        with open(f"{storage_path}/lexicon.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("The lexicon file does not exist. Please provide the correct path.")
        sys.exit()

def load_internal_id_to_docno(storage_path: str) -> dict:
    """
    Load the internal_id_to_docno from the storage directory and handle exceptions.
    """
    try:
        with open(f"{storage_path}/internal_id_to_docno.json", 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("The internal_id_to_docno file does not exist. Please provide the correct path.")
        sys.exit()

def load_doc_lengths(storage_path: str) -> list[int]:
    """
    Load the doc_lengths from the storage directory and handle exceptions.
    """
    try:
        with open(f"{storage_path}/doc-lengths.txt", 'r') as file:
            return list(map(int, file.readlines()))
    except FileNotFoundError:
        print("The doc-lengths file does not exist. Please provide the correct path.")
        sys.exit()

# This function takes a string and breaks it up into "words".  
# It returns an array of these words.
#
# Based on SimpleTokenizer by Trevor Strohman, 
# http://www.galagosearch.org/
#
# text is the string to tokenize and tokens is a list to which tokens will be appended
def tokenize(text, tokens):
    text = text.lower() 

    start = 0 
    i = 0

    for currChar in text:
        if not currChar.isdigit() and not currChar.isalpha() :
            if start != i :
                token = text[start:i]
                tokens.append(token)
                
            start = i + 1

        i = i + 1

    if start != i :
        tokens.append(text[start:i])

def extract_document_metadata(doc: str) -> tuple[str, str, int, int, int]:
    """
    Extracts the metadata from the document.
    
    Args:
        doc: The document from which to extract metadata.

    Returns:
        A tuple containing the docno (str), headline (str), year (int), month (int), and day (int).
    """
    # docno example: LA010189-0001
    docno = doc.split("<DOCNO>")[1].split("</DOCNO>")[0].strip()

    headline = ""
    if "<HEADLINE>" in doc:
        # extract headline if it exists with regex to replace tags with spaces
        raw_headline = doc.split("<HEADLINE>")[1].split("</HEADLINE>")[0].strip()
        # replace tags with spaces, tags are in the form <...> and removing new lines
        headline = re.sub(r'<[^>]+>', ' ', raw_headline).replace("\n", "").strip()

    # the date of the document is encoded in the DOCNO as LAMMDDYY-NNNN
    year = docno[6:8]
    month = docno[2:4]
    day = docno[4:6]
    return docno, headline, year, month, day

def save_document_to_storage(doc, storage_path):
    """
    Saves the document to the absolute storage path and creates the directories if they do not exist.
    """
    # create the directories if they do not exist, if they exist, do nothing
    os.makedirs(os.path.dirname(storage_path), exist_ok=True)
    with open(storage_path, 'w') as file:
        file.write(doc)

def get_text_from_document(doc: str) -> str:
    """
    The text of a document should come from the following tags: TEXT, HEADLINE, GRAPHIC
    """
    text = ""
    if "<TEXT>" in doc:
        raw_text = doc.split("<TEXT>")[1].split("</TEXT>")[0].strip()
        # remove tags from the text
        text = re.sub(r'<[^>]+>', ' ', raw_text).replace("\n", "").strip()
    if "<HEADLINE>" in doc:
        raw_headline = doc.split("<HEADLINE>")[1].split("</HEADLINE>")[0].strip()
        # remove tags from the headline
        headline = re.sub(r'<[^>]+>', ' ', raw_headline).replace("\n", "").strip()
        text += headline
    if "<GRAPHIC>" in doc:
        raw_graphic = doc.split("<GRAPHIC>")[1].split("</GRAPHIC>")[0].strip()
        # remove tags from the graphic
        graphic = re.sub(r'<[^>]+>', ' ', raw_graphic).replace("\n", "").strip()
        text += graphic
    return text

def format_date(year: int, month: int, day: int) -> str:
    """
    Formats the date as Month DD, YYYY
    """
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    formatted_month = months[month - 1]
    return f"{formatted_month} {day}, 19{year}"
