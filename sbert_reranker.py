from sentence_transformers import SentenceTransformer, util

class SBERRanker:
    def __init__(self, model_name="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)

    def rerank(self, query, urls, texts):
        # 1. Encode query + docs
        query_emb = self.model.encode(query, convert_to_tensor=True)
        doc_embs = self.model.encode(texts, convert_to_tensor=True)

        # 2. Compute cosine similarity
        cos_scores = util.cos_sim(query_emb, doc_embs)[0]

        # 3. Sort by similarity
        ranked = sorted(
            zip(urls, texts, cos_scores.tolist()),
            key=lambda x: x[2],
            reverse=True
        )

        return ranked
