"""
Implements Okapi BM25 ranking for retrieved news articles.
Uses the rank_bm25 library for scoring and ranking.
"""

from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize
from articles import retrieve_articles
import nltk
nltk.download('punkt_tab')

# Download tokenizer data once (needed for word_tokenize)
# nltk.download('punkt', quiet=True)


def rank_articles(query, pages=2):
    """
    Retrieve and rank articles using Okapi BM25.

    Args:
        query (str): User's search query.
        pages (int): Number of pages to retrieve from the API.

    Returns:
        list of tuples: [(url, score), ...] ranked from highest to lowest.
    """
    # Step 1: Retrieve articles
    articles = retrieve_articles(query, pages=pages)

    if not articles:
        print("No articles found.")
        return []

    # Step 2: Prepare corpus for BM25
    corpus = [word_tokenize(text.lower()) for text in articles.values()]
    bm25 = BM25Okapi(corpus)

    # Step 3: Compute scores
    query_tokens = word_tokenize(query.lower())
    scores = bm25.get_scores(query_tokens)

    # Step 4: Rank URLs by score
    ranked_results = sorted(
        zip(articles.keys(), scores),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked_results


if __name__ == "__main__":
    user_query = input("Enter your news query: ")
    ranked = rank_articles(user_query, pages=2)

    if ranked:
        print("\nTop Ranked Articles:\n")
        for i, (url, score) in enumerate(ranked[:10], 1):
            print(f"{i}. {url}  |  BM25 Score: {score:.4f}")
    else:
        print("No articles retrieved.")
