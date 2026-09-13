"""Intent classification models: Trivial Baseline, TF-IDF Baseline, and Calibrated Main Classifier."""

import os
import pickle
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from ..preprocessing.text_cleaner import clean_tweet_text


class TrivialMajorityClassifier:
    """Trivial baseline that always predicts the modal intent class."""

    def __init__(self):
        self.majority_intent: str = "delivery_delay_or_status"
        self.classes_: List[str] = [self.majority_intent]

    def fit(self, texts: List[str], labels: List[str]):
        from collections import Counter
        counts = Counter(labels)
        self.majority_intent = counts.most_common(1)[0][0]
        self.classes_ = sorted(list(set(labels)))

    def predict(self, texts: List[str]) -> List[str]:
        return [self.majority_intent for _ in texts]

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        # Uniform or concentrated probability
        probs = np.zeros((len(texts), len(self.classes_)))
        idx = self.classes_.index(self.majority_intent)
        probs[:, idx] = 1.0
        return probs


class TfIdfLogisticClassifier:
    """Simple but meaningful baseline using sublinear TF-IDF + Logistic Regression."""

    def __init__(self, C: float = 1.0, max_features: int = 10000):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 2),
            stop_words="english",
            sublinear_tf=True,
        )
        self.model = LogisticRegression(
            C=C, max_iter=1000, class_weight="balanced", random_state=42
        )
        self.classes_: List[str] = []

    def fit(self, texts: List[str], labels: List[str]):
        cleaned = [clean_tweet_text(t) for t in texts]
        X = self.vectorizer.fit_transform(cleaned)
        self.model.fit(X, labels)
        self.classes_ = list(self.model.classes_)

    def predict(self, texts: List[str]) -> List[str]:
        cleaned = [clean_tweet_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned)
        return list(self.model.predict(X))

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        cleaned = [clean_tweet_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned)
        return self.model.predict_proba(X)


class CalibratedIntentClassifier:
    """Production-grade intent classifier with confidence calibration and top-k output."""

    def __init__(self, C: float = 2.0, max_features: int = 15000):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=(1, 3),
            stop_words="english",
            sublinear_tf=True,
            min_df=2,
        )
        self.model = LogisticRegression(
            C=C, max_iter=1000, class_weight="balanced", random_state=42, solver="lbfgs"
        )
        self.classes_: List[str] = []
        self.temperature: float = 1.15  # Temperature scaling calibration

    def fit(self, texts: List[str], labels: List[str]):
        cleaned = [clean_tweet_text(t) for t in texts]
        X = self.vectorizer.fit_transform(cleaned)
        self.model.fit(X, labels)
        self.classes_ = list(self.model.classes_)

    def predict_single(self, text: str, top_k: int = 3) -> Tuple[str, float, List[Dict[str, Any]]]:
        cleaned = clean_tweet_text(text)
        X = self.vectorizer.transform([cleaned])
        logits = self.model.decision_function(X)

        # Apply temperature scaling to soften overconfident probabilities
        scaled_logits = logits / self.temperature
        exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
        calibrated_probs = (exp_logits / np.sum(exp_logits)).flatten()

        top_indices = np.argsort(calibrated_probs)[::-1][:top_k]
        top_k_list = [
            {"intent": self.classes_[i], "confidence": round(float(calibrated_probs[i]), 4)}
            for i in top_indices
        ]

        best_intent = self.classes_[top_indices[0]]
        best_confidence = float(calibrated_probs[top_indices[0]])

        return best_intent, best_confidence, top_k_list

    def predict(self, texts: List[str]) -> List[str]:
        cleaned = [clean_tweet_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned)
        return list(self.model.predict(X))

    def predict_proba(self, texts: List[str]) -> np.ndarray:
        cleaned = [clean_tweet_text(t) for t in texts]
        X = self.vectorizer.transform(cleaned)
        return self.model.predict_proba(X)

    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, filepath: str) -> "CalibratedIntentClassifier":
        with open(filepath, "rb") as f:
            return pickle.load(f)
