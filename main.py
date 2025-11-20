from articles import Articles
from bm25_ranker import rank_articles
from sbert_reranker import SBERRanker

def run_pipeline(query, K=10):
    # Shared articles object
    articles = Articles()

    print(f"\nQuery: {query}\n")

    # 1. Retrieve + BM25 rank 
    bm25_ranked = rank_articles(articles, query, pages=2)

    print("\n=== Top BM25 Results ===")
    for i, (url, score) in enumerate(bm25_ranked[:K], 1):
        print(f"{i}. {url} (BM25={score:.4f})")

    # 2. Prepare Top-K fulltexts 
    top_k_urls = [url for url, _ in bm25_ranked[:K]]
    top_k_texts = [articles._url_fulltext_dict[url] for url in top_k_urls]

    # 3. SBERT reranking
    reranker = SBERRanker("all-mpnet-base-v2")
    sbert_results = reranker.rerank(query, top_k_urls, top_k_texts)

    print("\n=== Top SBERT Results ===")
    for i, (url, _, score) in enumerate(sbert_results[:K], 1):
        print(f"{i}. {url} (Semantic={score:.4f})")


if __name__ == "__main__":
    query = input("Enter your news query: ")
    run_pipeline(query, K=10)
