# Search Engine

In this project, the dataset was a collection of 144k news articles from the LA Times from 1989-1990. The goal was to implement a search engine from scratch, evaluate different retrieval algorithms ( BooleanAND, basic TF.IDF, BM25, Cosine Similarity), and compare the results.

## Installation Requirements
- Python 3.x
- No additional packages required

## Overview

### SearchEngine
`SearchEngine.py` is an interactive search engine that uses the BM25 algorithm to rank documents based on user queries. It loads precomputed indices and lexicons from a specified storage path and allows users to input queries to retrieve ranked documents.

```bash
python SearchEngine.py <storage_path>
```

- The program will prompt the user to enter queries and will display the top 10 ranked documents with snippets.
- Users can view full documents by entering the rank number, start a new query, or quit the program.

---

### To index the collection
```bash
python IndexEngine.py <path_to_collection> <path_to_store>
```

e.g.

```bash
python IndexEngine.py C:/Users/miche/Desktop/Waterloo/mse541/latimes.gz C:/Users/miche/Desktop/Waterloo/mse541/storage
```

---
### Evaluate the results
`EvaluationResults.py` is a Python program that evaluates information retrieval system results by comparing them against relevance judgments (qrels). The program:

1. Loads and validates input files:
   - Results file containing ranked document lists per topic (topics 401-450)
   - Qrels file containing relevance judgments
   
2. Computes standard IR evaluation metrics:
   - **Average Precision (AP)**: Evaluates the overall ranking quality by averaging precision at each relevant document position
   - **Precision@10 (P@10)**: Measures precision considering only the top 10 retrieved documents
   - **NDCG@10**: Normalized Discounted Cumulative Gain for top 10 results, accounting for both relevance and rank position
   - **NDCG@1000**: Same as NDCG@10 but for top 1000 results

3. Outputs:
   - Per-topic scores for all metrics
   - Overall mean scores across all topics
   - Saves detailed results to `evaluation_results.csv`

#### Usage
Run the program from command line with paths to both input files:

```bash
python EvaluationResults.py <path_to_results> <path_to_qrels>
```
---
### To perform the Boolean AND retrieval
BooleanAnd takes 3 arguments: the directory location of your index, the queries file, and the name of a file to store your output

```bash
python BooleanAND.py <path_to_store> <path_to_queries> <path_to_output>
```

e.g.

```bash
python BooleanAND.py C:/Users/miche/Desktop/Waterloo/mse541/storage C:/Users/miche/Desktop/Waterloo/mse541/queries.txt C:/Users/miche/Desktop/Waterloo/mse541/output.txt
```



