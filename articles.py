"""
news_retriever.py
-----------------
Fetches and parses news articles using the Currents API and Newspaper3k.
Returns a dictionary mapping URLs to their extracted text.
"""

import requests
from newspaper import Article
from api_keys import currents_api_key


def retrieve_articles(keywords, pages=2):
    """
    Retrieve and parse news articles related to the given keywords.

    Args:
        keywords (str): Search keywords for news retrieval.
        pages (int): Number of API pages to fetch (default = 2).

    Returns:
        dict: A dictionary mapping article URLs to their text content.
    """
    if not isinstance(keywords, str):
        raise ValueError("`keywords` must be a string.")

    url_text_dict = {}

    for page in range(1, pages + 1):
        params = {
            "keywords": keywords,
            "language": "en",
            "apiKey": currents_api_key,
            "page_number": page
        }

        try:
            response = requests.get(
                "https://api.currentsapi.services/v1/search",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            for news_item in data.get("news", []):
                url = news_item.get("url")
                if not url:
                    continue

                try:
                    article = Article(url)
                    article.download()
                    article.parse()
                    text = article.text.strip()

                    if text:
                        url_text_dict[url] = text
                except Exception as e:
                    print(f"Skipping URL {url}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"API request error on page {page}: {e}")
        except ValueError as e:
            print(f"Error parsing JSON on page {page}: {e}")

    print(f"Retrieved {len(url_text_dict)} articles.")
    return url_text_dict


if __name__ == "__main__":
    # Example usage
    query = "AI-generated content"
    articles = retrieve_articles(query, pages=2)
    for i, (url, text) in enumerate(articles.items(), 1):
        print(f"\n{i}. {url}\n{text[:400]}...\n")
