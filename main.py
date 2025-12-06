from articles import Articles
from bm25_ranker import rank_articles
from sbert_reranker import SBERRanker
from ai_detector import AIBertDetector

def run_pipeline(query, K=10):
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
    for i, (url, fulltext, score) in enumerate(sbert_results[:K], 1):
        print(f"{i}. {url} (Semantic={score:.4f})")
        # print(f"   {fulltext[:200]}...\n")

    # 4. AI Detector
    detector = AIBertDetector("best_distilbert_model_CURRENT.pt")
    print(f"\nLoaded threshold = {detector.threshold}")

    print("\n=== AI Detection (Article-level) ===")
    final_results = []

    for url, fulltext, sem_score in sbert_results[:K]:
    # ---- paragraph-based detection ----
        ai_prob = detector.predict_proba(fulltext)
        ai_pct  = detector.ai_percentage(fulltext)
        para_probs = detector.paragraph_probs(fulltext)
        # Add to results
        final_results.append((url, sem_score, ai_prob, ai_pct, para_probs))


    print("\n=== FINAL RESULTS ===")
    for i, (url, sem, ai_prob, ai_pct, para_probs) in enumerate(final_results, 1):
        print(f"{i}. {url}\n"
              f"   Semantic={sem:.4f}, Paragraph_Prob = [{para_probs}], AI_prob={ai_prob:.4f}, AI%={ai_pct:.2%}")

if __name__ == "__main__":
    query = input("Enter your news query: ")
    run_pipeline(query, K=10)
