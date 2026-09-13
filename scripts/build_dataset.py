"""Builds reconstructed conversation datasets, applies temporal splitting, and audits data leakage."""

import json
import os
import sys
import re
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.conversation.reconstructor import ThreadReconstructor, parse_twitter_timestamp
from src.conversation.splitter import ConversationSplitter
from src.preprocessing.text_cleaner import clean_tweet_text, assess_message_quality
from src.intent.taxonomy import IntentTaxonomy


def infer_conversation_intent(customer_text: str, brand_reply: str) -> str:
    """Infers intent from customer inquiry text and brand resolution patterns."""
    text = (customer_text + " " + (brand_reply or "")).lower()

    # Rule-based precision matching for Amazon operational intents
    if any(k in text for k in ["fraud", "unauthorized", "stolen", "hacked", "identity theft"]):
        return "fraud_or_unauthorized_charge"
    if any(k in text for k in ["lawyer", "attorney", "sue", "legal action", "police", "court", "better business bureau", "ftc"]):
        return "legal_or_severe_complaint"
    if any(k in text for k in ["prime", "membership", "subscription", "annual fee", "billing", "invoice", "receipt", "charge on card"]):
        return "subscription_and_billing"
    if any(k in text for k in ["cancel", "stop order", "cancellation", "cancel my order"]):
        return "cancellation_request"
    if any(k in text for k in ["damaged", "broken", "shattered", "defective", "wrong item", "missing item", "missing piece", "leaking"]):
        return "damaged_or_incorrect_item"
    if any(k in text for k in ["return", "refund", "returns center", "drop off", "ups drop", "kohls drop", "refund status"]):
        return "return_and_refund_inquiry"
    if any(k in text for k in ["kindle", "prime video", "streaming", "fire tv", "fire stick", "echo", "alexa", "app crash", "error code"]):
        return "digital_services_and_devices"
    if any(k in text for k in ["coupon", "promo code", "discount", "promotion", "gift card", "price drop", "price match"]):
        return "promotional_and_pricing"
    if any(k in text for k in ["login", "log in", "otp", "2fa", "two-step", "password", "locked out", "verify account", "verification code"]):
        return "account_access_and_otp"
    if any(k in text for k in ["delivery", "delivered", "shipping", "shipped", "carrier", "tracking", "late", "where is my", "package", "transit", "usps", "ups", "courier", "driver"]):
        return "delivery_delay_or_status"

    return "delivery_delay_or_status"  # Default modal retail intent


def build_dataset(
    csv_path: str = "data/raw/twcs.csv",
    brand_handle: str = "AmazonHelp",
    max_tweets_to_scan: int = 1500000,
    target_conversation_count: int = 4000,
):
    print(f"Loading tweets for brand: {brand_handle} from {csv_path}...")
    matched_rows = []

    # Stream through CSV and extract brand tweets + conversation ancestors
    chunk_size = 200000
    rows_scanned = 0

    for chunk in pd.read_csv(
        csv_path,
        chunksize=chunk_size,
        dtype={
            "tweet_id": str,
            "author_id": str,
            "inbound": str,
            "created_at": str,
            "text": str,
            "response_tweet_id": str,
            "in_response_to_tweet_id": str,
        },
        low_memory=False,
    ):
        rows_scanned += len(chunk)

        # Filter for brand tweets or customer tweets mentioning the brand
        is_brand = chunk["author_id"].str.lower() == brand_handle.lower()
        mentions_brand = chunk["text"].str.contains(f"@{brand_handle}", case=False, na=False)
        target_mask = is_brand | mentions_brand

        matched = chunk[target_mask]
        if len(matched) > 0:
            matched_rows.append(matched)

        if len(matched_rows) * chunk_size >= max_tweets_to_scan and len(matched_rows) > 10:
            print(f"Reached target scan limit of {rows_scanned:,} rows.")
            break

    if not matched_rows:
        raise ValueError(f"No tweets found for brand {brand_handle}")

    combined_df = pd.concat(matched_rows, ignore_index=True)
    combined_df = combined_df.drop_duplicates(subset=["tweet_id"])
    print(f"Extracted {len(combined_df):,} candidate tweets relevant to {brand_handle}.")

    # Reconstruct threads
    reconstructor = ThreadReconstructor(brand_handle=brand_handle)
    conversations = reconstructor.reconstruct_from_dataframe(
        combined_df, max_conversations=target_conversation_count
    )
    print(f"Successfully reconstructed {len(conversations):,} chronological conversations.")

    # Filter for quality: valid customer text & has brand response for grounding
    valid_convs = []
    for c in conversations:
        is_ok, _ = assess_message_quality(c.first_customer_message)
        if is_ok and c.has_brand_response and c.first_brand_reply:
            c.inferred_intent = infer_conversation_intent(
                c.first_customer_message, c.first_brand_reply
            )
            valid_convs.append(c)

    print(f"Retained {len(valid_convs):,} high-quality resolved conversations.")

    # Temporal splitting (70% train, 15% val, 15% test)
    splitter = ConversationSplitter(train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    train_convs, val_convs, test_convs = splitter.split_temporally(valid_convs)

    # Audit leakage
    leakage_audit = splitter.audit_leakage(train_convs, val_convs, test_convs)
    os.makedirs("reports", exist_ok=True)
    with open("reports/leakage_report.json", "w", encoding="utf-8") as f:
        json.dump(leakage_audit, f, indent=2)
    print("Leakage audit complete. Zero leakage verified:", leakage_audit["is_leak_free"])

    # Save to JSONL
    os.makedirs("data/sample", exist_ok=True)

    def serialize_conv(c) -> Dict[str, Any]:
        return {
            "conversation_id": c.conversation_id,
            "brand": c.brand,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "turn_count": c.turn_count,
            "first_customer_message": c.first_customer_message,
            "first_brand_reply": c.first_brand_reply,
            "final_brand_reply": c.final_brand_reply,
            "inferred_intent": c.inferred_intent,
            "turns": [
                {
                    "tweet_id": t.tweet_id,
                    "author_id": t.author_id,
                    "is_customer": t.is_customer,
                    "timestamp": t.timestamp,
                    "text": t.text,
                }
                for t in c.turns
            ],
        }

    for name, conv_list in [
        ("train_conversations.jsonl", train_convs),
        ("val_conversations.jsonl", val_convs),
        ("test_conversations.jsonl", test_convs),
    ]:
        path = os.path.join("data/sample", name)
        with open(path, "w", encoding="utf-8") as f:
            for c in conv_list:
                f.write(json.dumps(serialize_conv(c)) + "\n")
        print(f"Saved {len(conv_list)} conversations to {path}")

    return train_convs, val_convs, test_convs


if __name__ == "__main__":
    build_dataset()
