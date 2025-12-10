# R&D: News Retrieval and AI Detection
## Overview
Our tool, R&D, collects, analyzes, and ranks news articles from different sources based on a user's query. The system gathers relevant news articles from multiple sources. It ranks the retrieved articles with Okapi BM25 for the initial order. Then our tool reranks the top results using a SBERT bi-encoder reranker, which computes embeddings of the query and articles and orders them by cosine similarity to capture context. Each result shows an estimated AI authorship score generated from a classifier trained to distinguish human-written and AI-generated text. You can view a demo of the tool [here.](https://brian-jin.github.io/CS547_news_retrieval_ai_detection/)

## The Value of our Tool
There is an increasing prevalence of AI usage in content creation, making it difficult for readers to discern between human-written and AI generated texts. Readers are exposed to a constant stream of articles and a growing share may be machine written. In fact, according to a study conducted by Graphite using web crawling & Surfer AI detection, they found that over 50% of articles are being written by AI as of 2024 with an massive growth from the launch of ChatGPT in 2022. Our tool helps users judge relevance and the likelihood of articles being AI-generated before clicking. It effectively supports students, instructors, and casual users who want reliable, and trustworthy sources of news.

## Our Tool vs. Existing Tools
Paste-in detectors, such as ZeroGPT, score text that the user provides. Our tool goes further by dynamically fetching articles for user queries, ranking them based on relevance, and showing the likelihood of AI-generated content before the user even clicks into the news page. This makes for an intuitive and easy way for users to explore news topics and find the most credible content.

## Our Methodology
- Articles are first retrieved by sending keyword-based queries to the Current News API. This returns a JSON object that contains a collection of news items with metadata. Full article content is retrieved with the Newspaper3k library and preprocessed to create an inverted index.
- Next, the retrieved articles ranked based on the user's query using Okapi BM25 retrieval. This enables our tool to find the top-k candidate articles. From there, our tool utilizes a SBERT bi-encoder reranker to compute semantic similarity scores. Our double ranking system allows for a refined method to retireve the most relevant articles for the rest of our pipeline.
- We trained a DistilBERT classifier, using a A100 GPU, on a custom dataset comprised of 1,879,577 labeled AI-generated and human-written essay samples. Our model was evaluated on an unseen test set from our custom dataset, as well as an out of distribution baseline set used in prior research. We note high accuracy in both the original test set, at 97.52%, and the OOD test set, at 89.77%.
- Finally, we utilize our trained classifier to detect the AI percentage of the ranked retrieved articles. Articles are evaluated paragraph by paragraph to meet BERT's maximum sequence length limit of 512 tokens. The article-level proability is then calculated as the mean of the paragraph probabilities to output a final AI-generated proability.

## Resources
Classification Datasets
- [AI Vs Human Text Dataset (Kaggle)](https://www.kaggle.com/datasets/shanegerami/ai-vs-human-text)
- [AI Text Detection Pile (Hugging Face)](https://huggingface.co/datasets/artem9k/ai-text-detection-pile)
- [Test Dataset (Al Bataineh et al., 2025)](https://github.com/rsickle1/human-v-ai)
- Articles are dynamically retrieved with Currents News API

Requirements
- PorterStemmer
- requests
- newspaper3k
- lxml_html_clean
- rank_bm25
- nltk
- sentence_transformers
- Torch
- transformers
- sklearn
-Numpy, pandas
