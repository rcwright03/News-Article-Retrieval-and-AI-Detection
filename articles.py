import requests
from secrets import currents_api_key
from newspaper import Article

url_text_dict = {}

def retrieve_articles(keywords):
    # need to add code ensuring that keywords is a string
    for page in range(1, 2):
        params = {
            "keywords": keywords,
            "language": 'en',
            "apiKey": currents_api_key,
            "page_number": page
        }
        try:
            response = requests.get('https://api.currentsapi.services/v1/search', params=params)
            response.raise_for_status()
            data = response.json()

            for news_item in data.get("news", []):
                # add url and paragraph text to dict if possible
                try:
                    article_url = Article(news_item.get('url'))
                    article_url.download()
                    article_url.parse()

                    # adding article url, paragraph text to dict
                    url_text_dict.setdefault(article_url, article_url.text)
                except Exception as e:
                    print(f"Skipping URL: {article_url} due to the following error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")