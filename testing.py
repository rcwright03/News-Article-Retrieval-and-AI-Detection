from articles import Articles
from ai_detector import AIBertDetector

def test_retrieve_articles():
    articles = Articles()
    articles.retrieve_articles('taylor swift')

    for url, tokens in articles._url_processedtext_dict.items():
        print(f"Article url: {url}")
        print(f"First 20 stemmed tokens: {tokens[:20]}")
        break

    for token, ids in articles._inverted_index.items():
        print(f"Token: {token}")
        print(f"Article ids: {ids}")
        break

def test_article_classifier():
    detector = AIBertDetector("best_distilbert_model_CURRENT.pt")
    import os
    # get articles from folder

    file_contents = []
    for filename in os.listdir('test_articles'):
        if filename.endswith('.txt'):
            file_path = os.path.join('test_articles', filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content=file.read()
                file_contents.append((filename, content))

    final_results = []

    for filename, fulltext in file_contents:
    # ---- paragraph-based detection ----
        ai_prob = detector.predict_proba(fulltext)
        ai_pct  = detector.ai_percentage(fulltext)
        para_probs = detector.paragraph_probs(fulltext)
        # Add to results
        final_results.append((filename, ai_prob, ai_pct, para_probs))

    for filename, ai_prob, ai_pct, para_probs in final_results:
        print("File: ", filename, "\nAI prob: ", ai_prob, "\nAI %: ", ai_pct, "\nParagraph Probs: ", para_probs)

if __name__ == "__main__":
    # test_retrieve_articles()
    test_article_classifier()