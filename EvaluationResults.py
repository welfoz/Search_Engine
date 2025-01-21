import sys
import math
from collections import defaultdict

def load_results(results_path: str) -> dict:
    """
    Load the results file and return a dictionary mapping topic IDs to ranked document lists.
    """
    results = defaultdict(list)
    try:
        with open(results_path, 'r') as file:
            for line in file:
                parts = line.split()
                if len(parts) != 6:
                    raise ValueError("Results file format is incorrect")
                topic_id, _, doc_id, rank, score, _ = parts
                if int(topic_id) < 401 or int(topic_id) > 450:
                    raise ValueError("Topic ID is out of range: " + topic_id)
                results[topic_id].append((doc_id, int(rank), float(score)))
        # Sort results for each topic by score and then docno as a tie-breaker (both descending)
        for topic in results:
            results[topic].sort(key=lambda x: (-x[2], x[0]))
        return results
    except Exception as e:
        print(f"Error reading results file: {e}")
        sys.exit()

def load_qrels(qrels_path: str) -> dict:
    """
    Load the qrels file and return a dictionary mapping topic IDs to document relevances.
    """
    qrels = defaultdict(dict)
    try:
        with open(qrels_path, 'r') as file:
            for line in file:
                topic_id, _, doc_id, judgment = line.split()
                qrels[topic_id][doc_id] = int(judgment)
        return qrels
    except Exception as e:
        print(f"Error reading qrels file: {e}")
        sys.exit()

def calculate_average_precision(results, qrels, topic_id):
    """
    Calculate the Average Precision (AP) for a given topic.
    """
    relevant_docs = qrels.get(topic_id, {})
    retrieved_docs = results.get(topic_id, [])

    total_relevant_docs = sum(1 for doc_id, judgment in relevant_docs.items() if judgment > 0)

    if not retrieved_docs or not relevant_docs:
        return 0.0

    precision_sum = 0.0
    num_relevant_retrieved_at_rank = 0
    for rank, (doc_id, rank, score) in enumerate(retrieved_docs, start=1):
        if rank > 1000: 
            print(f"Warning: More than 1000 documents retrieved for topic {topic_id}")
        # if the retrieved document is relevant, increment the number of relevant documents retrieved
        if doc_id in relevant_docs and relevant_docs[doc_id] > 0:
            num_relevant_retrieved_at_rank += 1
            precision_sum += num_relevant_retrieved_at_rank / rank

    return precision_sum / total_relevant_docs if relevant_docs else 0.0

def calculate_precision_at_k(results, qrels, topic_id, k):
    """
    Calculate Precision@k for a given topic.
    """
    relevant_docs = qrels.get(topic_id, {})
    retrieved_docs = results.get(topic_id, [])[:k]

    num_relevant_retrieved = sum(1 for doc_id, _, _ in retrieved_docs if doc_id in relevant_docs and relevant_docs[doc_id] > 0)
    return num_relevant_retrieved / k

def calculate_dcg(results, qrels, topic_id, k):
    """
    Calculate DCG@k for a given topic.
    """
    relevant_docs = qrels.get(topic_id, {})
    retrieved_docs = results.get(topic_id, [])[:k]

    dcg = 0.0
    for rank, (doc_id, _, _) in enumerate(retrieved_docs, start=1):
        if doc_id in relevant_docs:
            rel = relevant_docs[doc_id]
            dcg += rel / math.log2(rank + 1)

    return dcg

def calculate_ndcg(results, qrels, topic_id, k):
    """
    Calculate NDCG@k for a given topic.
    """
    dcg = calculate_dcg(results, qrels, topic_id, k)
    # we sort all relevant docs, the highest relevance first
    ideal_relevances = sorted([rel for rel in qrels.get(topic_id, {}).values() if rel > 0], reverse=True)
    idcg = sum(rel / math.log2(rank + 1) for rank, rel in enumerate(ideal_relevances[:k], start=1))

    return dcg / idcg if idcg > 0 else 0.0

def main():
    if len(sys.argv) != 3:
        print(
            """
            Please provide the correct command line inputs.
            The program accepts:
                1. the path to the results file
                2. the path to the qrels file
            Example:
                python EvaluateResults.py C:/path/to/results.txt C:/path/to/qrels.txt
            """
        )
        sys.exit()

    results_path = sys.argv[1]
    qrels_path = sys.argv[2]

    results = load_results(results_path)
    qrels = load_qrels(qrels_path)

    total_ap = 0.0
    total_p_at_10 = 0.0
    total_ndcg_at_10 = 0.0
    total_ndcg_at_1000 = 0.0
    num_topics = len(qrels)

    csv_results = []

    print(f"{'Topic ID':<10}{'AP':<15}{'P@10':<15}{'NDCG@10':<15}{'NDCG@1000':<15}")
    print("-" * 60)

    for topic_id in qrels:
        ap = calculate_average_precision(results, qrels, topic_id)
        p_at_10 = calculate_precision_at_k(results, qrels, topic_id, k=10)
        ndcg_at_10 = calculate_ndcg(results, qrels, topic_id, k=10)
        ndcg_at_1000 = calculate_ndcg(results, qrels, topic_id, k=1000)

        total_ap += ap
        total_p_at_10 += p_at_10
        total_ndcg_at_10 += ndcg_at_10
        total_ndcg_at_1000 += ndcg_at_1000

        csv_results.append([topic_id, ap, p_at_10, ndcg_at_10, ndcg_at_1000])

        print(f"{topic_id:<10}{ap:<15.3f}{p_at_10:<15.3f}{ndcg_at_10:<15.3f}{ndcg_at_1000:<15.3f}")

    print("\nOverall Averages:")
    print(f"Mean AP: {total_ap / num_topics:.3f}")
    print(f"Mean P@10: {total_p_at_10 / num_topics:.3f}")
    print(f"Mean NDCG@10: {total_ndcg_at_10 / num_topics:.3f}")
    print(f"Mean NDCG@1000: {total_ndcg_at_1000 / num_topics:.3f}")

    # save results to csv
    with open("evaluation_results-baseline.csv", "w") as file:
        file.write("Topic ID,AP,P@10,NDCG@10,NDCG@1000\n")
        for row in csv_results:
            file.write(",".join(map(str, row)) + "\n")


if __name__ == "__main__":
    main()

