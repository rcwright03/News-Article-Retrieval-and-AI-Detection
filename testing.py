from articles import Articles

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

if __name__ == "__main__":
    test_retrieve_articles()