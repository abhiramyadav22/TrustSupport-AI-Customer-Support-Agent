"""Trains intent classification baselines and main calibrated model, and builds retrieval index."""

import json
import os
import sys
import pickle
from typing import List
from src.schema import Conversation, ConversationTurn
from src.intent.classifier import (
    TrivialMajorityClassifier,
    TfIdfLogisticClassifier,
    CalibratedIntentClassifier,
)
from src.retrieval.historical_index import HistoricalSupportIndex
from src.preprocessing.text_cleaner import clean_tweet_text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def load_conversations(path: str) -> List[Conversation]:
    convs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                turns = [
                    ConversationTurn(
                        tweet_id=t["tweet_id"],
                        author_id=t["author_id"],
                        is_customer=t["is_customer"],
                        timestamp=t["timestamp"],
                        text=t["text"],
                    )
                    for t in data["turns"]
                ]
                convs.append(
                    Conversation(
                        conversation_id=data["conversation_id"],
                        brand=data["brand"],
                        start_time=data["start_time"],
                        end_time=data["end_time"],
                        turns=turns,
                        first_customer_message=data["first_customer_message"],
                        first_brand_reply=data["first_brand_reply"],
                        final_brand_reply=data["final_brand_reply"],
                        turn_count=data["turn_count"],
                        has_brand_response=True,
                        inferred_intent=data.get("inferred_intent"),
                    )
                )
    return convs


def train_models():
    print("Loading training and validation conversations...")
    train_convs = load_conversations("data/sample/train_conversations.jsonl")
    val_convs = load_conversations("data/sample/val_conversations.jsonl")

    X_train = [c.first_customer_message for c in train_convs]
    y_train = [c.inferred_intent for c in train_convs]

    X_val = [c.first_customer_message for c in val_convs]
    y_val = [c.inferred_intent for c in val_convs]

    print(f"Training dataset size: {len(X_train)} samples across {len(set(y_train))} intents.")

    # 1. Train Baseline 1 (Trivial Majority)
    print("Fitting Baseline 1 (Trivial Majority)...")
    trivial_model = TrivialMajorityClassifier()
    trivial_model.fit(X_train, y_train)

    # 2. Train Baseline 2 (TF-IDF + Logistic Regression)
    print("Fitting Baseline 2 (TF-IDF + Balanced Logistic Regression)...")
    tfidf_model = TfIdfLogisticClassifier(C=1.0)
    tfidf_model.fit(X_train, y_train)

    # 3. Train Main Model (Calibrated Intent Classifier)
    print("Fitting Main Model (Temperature-Calibrated N-gram Classifier)...")
    main_model = CalibratedIntentClassifier(C=2.5, max_features=15000)
    main_model.fit(X_train, y_train)

    # 4. Build Historical Support Retrieval Index
    print("Building historical support case retrieval index from training evidence...")
    retrieval_index = HistoricalSupportIndex(mode="intent_filtered")
    retrieval_index.build_from_conversations(train_convs)
    print(f"Indexed {len(retrieval_index.cases)} resolved historical support cases.")

    # Save artifacts
    os.makedirs("data/sample/models", exist_ok=True)

    with open("data/sample/models/trivial_baseline.pkl", "wb") as f:
        pickle.dump(trivial_model, f)

    with open("data/sample/models/tfidf_baseline.pkl", "wb") as f:
        pickle.dump(tfidf_model, f)

    with open("data/sample/models/calibrated_intent.pkl", "wb") as f:
        pickle.dump(main_model, f)

    with open("data/sample/models/historical_index.pkl", "wb") as f:
        pickle.dump(retrieval_index, f)

    print("All models and index artifacts successfully serialized to data/sample/models/")


if __name__ == "__main__":
    train_models()
