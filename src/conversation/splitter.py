"""Temporal and conversation-aware dataset splitting to guarantee zero leakage."""

from typing import List, Tuple, Dict, Any, Set
from datetime import datetime
from ..schema import Conversation
from .reconstructor import parse_twitter_timestamp


class ConversationSplitter:
    """Partitions conversations chronologically into train, validation, and test splits.

    Guarantees:
    1. Entire conversation threads (all turns) remain strictly within a single partition.
    2. Zero overlap in conversation IDs across train, val, and test.
    3. Temporal ordering: Train (oldest) <= Validation <= Test (newest).
    """

    def __init__(
        self,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
    ):
        assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-5
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio

    def split_temporally(
        self, conversations: List[Conversation]
    ) -> Tuple[List[Conversation], List[Conversation], List[Conversation]]:
        """Sorts conversations chronologically by start timestamp and splits sequentially."""
        # Filter out conversations with unparseable timestamps
        valid_convs = []
        for c in conversations:
            ts = parse_twitter_timestamp(c.start_time)
            if ts:
                valid_convs.append((ts, c))

        if not valid_convs:
            # Fallback if timestamps are missing
            valid_convs = [(datetime.min, c) for c in conversations]

        # Sort chronologically
        valid_convs.sort(key=lambda x: x[0])
        sorted_convs = [item[1] for item in valid_convs]

        n = len(sorted_convs)
        train_end = int(n * self.train_ratio)
        val_end = int(n * (self.train_ratio + self.val_ratio))

        train = sorted_convs[:train_end]
        val = sorted_convs[train_end:val_end]
        test = sorted_convs[val_end:]

        return train, val, test

    @staticmethod
    def audit_leakage(
        train: List[Conversation],
        val: List[Conversation],
        test: List[Conversation],
    ) -> Dict[str, Any]:
        """Performs rigorous leakage checks across partitions."""
        train_ids = {c.conversation_id for c in train}
        val_ids = {c.conversation_id for c in val}
        test_ids = {c.conversation_id for c in test}

        # Check conversation ID overlap
        train_val_overlap = train_ids.intersection(val_ids)
        train_test_overlap = train_ids.intersection(test_ids)
        val_test_overlap = val_ids.intersection(test_ids)

        # Check tweet ID overlap across all individual turns
        def get_all_tweet_ids(conv_list: List[Conversation]) -> Set[int]:
            return {turn.tweet_id for c in conv_list for turn in c.turns}

        train_tids = get_all_tweet_ids(train)
        val_tids = get_all_tweet_ids(val)
        test_tids = get_all_tweet_ids(test)

        tid_train_val_overlap = train_tids.intersection(val_tids)
        tid_train_test_overlap = train_tids.intersection(test_tids)
        tid_val_test_overlap = val_tids.intersection(test_tids)

        # Measure temporal boundaries
        train_start = min((c.start_time for c in train), default="N/A")
        train_end = max((c.start_time for c in train), default="N/A")
        val_start = min((c.start_time for c in val), default="N/A")
        val_end = max((c.start_time for c in val), default="N/A")
        test_start = min((c.start_time for c in test), default="N/A")
        test_end = max((c.start_time for c in test), default="N/A")

        is_leak_free = (
            len(train_val_overlap) == 0
            and len(train_test_overlap) == 0
            and len(val_test_overlap) == 0
            and len(tid_train_val_overlap) == 0
            and len(tid_train_test_overlap) == 0
            and len(tid_val_test_overlap) == 0
        )

        return {
            "is_leak_free": is_leak_free,
            "train_count": len(train),
            "val_count": len(val),
            "test_count": len(test),
            "conversation_id_overlap": {
                "train_val": list(train_val_overlap),
                "train_test": list(train_test_overlap),
                "val_test": list(val_test_overlap),
            },
            "tweet_id_overlap_count": {
                "train_val": len(tid_train_val_overlap),
                "train_test": len(tid_train_test_overlap),
                "val_test": len(tid_val_test_overlap),
            },
            "temporal_boundaries": {
                "train": {"start": train_start, "end": train_end},
                "val": {"start": val_start, "end": val_end},
                "test": {"start": test_start, "end": test_end},
            },
        }
