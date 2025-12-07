# ai_detector.py

import torch
import torch.nn as nn
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertModel

MAX_LEN = 512


# -----------------------------
# 1. Classifier (same as training)
# -----------------------------
class DistilBERTClassifier(nn.Module):
    def __init__(self, dropout=0.3):
        super().__init__()
        self.bert = DistilBertModel.from_pretrained("distilbert-base-uncased")
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(self.bert.config.hidden_size, 1)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]  # CLS token
        x = self.dropout(pooled_output)
        return self.classifier(x)


# -----------------------------
# 2. Detector wrapper
# -----------------------------
class AIBertDetector:
    def __init__(self, model_path: str):
        # Device
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        self.tokenizer = DistilBertTokenizerFast.from_pretrained(
            "distilbert-base-uncased"
        )

        self.model = DistilBERTClassifier().to(self.device)

        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        state_dict = checkpoint.get("model_state_dict", checkpoint)
        self.model.load_state_dict(state_dict)
        self.model.eval()

        # Load threshold if saved
        self.threshold = checkpoint.get("threshold", 0.5)

    # ------------------------------------------------
    # Paragraph-based classifier
    # ------------------------------------------------
    def _split_paragraphs(self, text: str):
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        return paragraphs

    def _predict_single_paragraph(self, paragraph: str) -> float:
        enc = self.tokenizer(
            paragraph,
            truncation=True,
            max_length=MAX_LEN,
            padding="max_length",
            return_tensors="pt"
        )

        input_ids = enc["input_ids"].to(self.device)
        attention_mask = enc["attention_mask"].to(self.device)

        with torch.no_grad():
            logits = self.model(input_ids, attention_mask)
            prob = torch.sigmoid(logits).item()

        return float(prob)

    # -----------------------------
    # Predict probability for entire article
    # -----------------------------
    def predict_proba(self, fulltext: str) -> float:
        paragraphs = self._split_paragraphs(fulltext)

        if not paragraphs:
            return 0.0

        probs = [self._predict_single_paragraph(p) for p in paragraphs]
        return float(np.mean(probs))

    # -----------------------------
    # Return label for article
    # -----------------------------
    def predict_label(self, fulltext: str) -> int:
        prob = self.predict_proba(fulltext)
        return int(prob >= self.threshold)

    # -----------------------------
    # Paragraph-wise AI percentage
    # -----------------------------
    def ai_percentage(self, fulltext: str) -> float:
        paragraphs = self._split_paragraphs(fulltext)

        if not paragraphs:
            return 0.0

        # Probability per paragraph
        probs = [self._predict_single_paragraph(p) for p in paragraphs]

        num_ai = sum(p >= self.threshold for p in probs)
        return num_ai / len(paragraphs)

    # -----------------------------
    # Return paragraph probabilities too
    # -----------------------------
    def paragraph_probs(self, fulltext: str):
        paragraphs = self._split_paragraphs(fulltext)
        return [self._predict_single_paragraph(p) for p in paragraphs]
