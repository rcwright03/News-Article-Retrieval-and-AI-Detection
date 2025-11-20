import requests
import PorterStemmer
from secrets import currents_api_key
from newspaper import Article

class Articles(object):
    def __init__(self):
        self._url_fulltext_dict = {}
        self._url_processedtext_dict = {}
        self._url_id_dict = {}
        self._inverted_index = {}

    def retrieve_articles(self, keywords):
        # need to add code ensuring that keywords is a string

        # article id
        article_id = 0

        # print(f"Retrieving articles for keyword: {keywords}") #testing
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

                # go thru news objects and retrieve urls
                for news_item in data.get("news", []):
                    # add url and paragraph text to dict if possible
                    article_url = news_item.get('url')
                    #print(f"article url: {article_url}") # printing article urls for testing

                    try:
                        article = Article(article_url)
                        article.download()
                        article.parse()
                        article_text = article.text # get article text

                        # add url, paragraph text to dict
                        self._url_fulltext_dict.setdefault(article_url, article_text)
                        # add url, id to dict
                        self._url_id_dict.setdefault(article_url, article_id)
                        article_id += 1

                        # tokenize text
                        article_tokens = self.tokenize(article_text)
                        # stem
                        stemmed_article_tokens = self.stemming(article_tokens)

                        # add url, processed text to dict
                        self._url_processedtext_dict.setdefault(article_url, stemmed_article_tokens)

                        # populate inverted index
                        self.create_index()
                    except Exception as e:
                        print(f"Skipping url: {article_url} due to the following error: {e}")
            except requests.exceptions.RequestException as e:
                print(f"Error making API request: {e}")
            except ValueError as e:
                print(f"Error parsing JSON response: {e}")
    def tokenize(self, text):
        import re
        clean_string = re.sub('[^a-z0-9 ]', ' ', text.lower())
        tokens = clean_string.split()
        return tokens
    
    def stemming(self, tokens):
        stemmed_tokens = []
        stemmer = PorterStemmer.PorterStemmer()
        for token in tokens:
            stemmed_token = stemmer.stem(token, 0, len(token)-1)
            stemmed_tokens.append(stemmed_token)
        return stemmed_tokens
    
    def create_index(self):
        for url, text in self._url_processedtext_dict.items():
            article_id = self._url_id_dict.get(url)
            for item in text:
                if item not in self._inverted_index:
                    self._inverted_index[item] = {article_id}
                else:
                    # if item already in dict add it to the dict's items
                    self._inverted_index[item].add(article_id)