"""Conversation thread reconstruction engine for Twitter customer support datasets."""

from typing import Dict, List, Optional, Generator, Any
from datetime import datetime
import pandas as pd
from ..schema import ConversationTurn, Conversation


def parse_twitter_timestamp(ts_str: str) -> Optional[datetime]:
    """Parses standard Twitter timestamp: 'Tue Oct 31 22:10:47 +0000 2017'."""
    if not isinstance(ts_str, str) or not ts_str.strip():
        return None
    try:
        # Standard Twitter timestamp format
        return datetime.strptime(ts_str.strip(), "%a %b %d %H:%M:%S +0000 %Y")
    except Exception:
        try:
            return pd.to_datetime(ts_str).to_pydatetime()
        except Exception:
            return None


class ThreadReconstructor:
    """Reconstructs multi-turn conversational threads from raw Twitter records."""

    def __init__(self, brand_handle: Optional[str] = None):
        self.brand_handle = brand_handle.lower() if brand_handle else None

    def reconstruct_from_dataframe(
        self, df: pd.DataFrame, max_conversations: Optional[int] = None
    ) -> List[Conversation]:
        """Reconstructs chronological conversations from a DataFrame of tweets.

        Expected columns:
            tweet_id, author_id, inbound, created_at, text,
            response_tweet_id, in_response_to_tweet_id
        """
        df = df.copy()
        df["tweet_id"] = pd.to_numeric(df["tweet_id"], errors="coerce")
        df = df.dropna(subset=["tweet_id"])
        df["tweet_id"] = df["tweet_id"].astype(int)

        # Index tweets by tweet_id for O(1) graph traversal
        tweet_lookup: Dict[int, Dict[str, Any]] = {}
        for _, row in df.iterrows():
            tid = int(row["tweet_id"])
            inbound_val = row.get("inbound")
            if isinstance(inbound_val, str):
                is_inbound = inbound_val.strip().lower() == "true"
            else:
                is_inbound = bool(inbound_val)

            tweet_lookup[tid] = {
                "tweet_id": tid,
                "author_id": str(row.get("author_id", "")),
                "inbound": is_inbound,
                "created_at": str(row.get("created_at", "")),
                "text": str(row.get("text", "")),
                "in_response_to_tweet_id": (
                    int(row["in_response_to_tweet_id"])
                    if pd.notna(row.get("in_response_to_tweet_id"))
                    and str(row.get("in_response_to_tweet_id")).strip() != ""
                    else None
                ),
                "response_tweet_id": str(row.get("response_tweet_id", ""))
                if pd.notna(row.get("response_tweet_id"))
                else "",
            }

        # Identify conversation root tweets:
        # A root tweet has in_response_to_tweet_id as None, or its parent is not in our dataset
        # For customer support: inbound=True (customer initiated) is the standard root of customer service requests
        conversations: List[Conversation] = []

        # Find all candidate roots
        roots = []
        for tid, t in tweet_lookup.items():
            is_root = t["in_response_to_tweet_id"] is None or t["in_response_to_tweet_id"] not in tweet_lookup
            if is_root and t["inbound"]:  # Initiated by customer
                roots.append(tid)

        # Sort roots chronologically by created_at if possible
        roots.sort(key=lambda x: parse_twitter_timestamp(tweet_lookup[x]["created_at"]) or datetime.min)

        for root_id in roots:
            if max_conversations and len(conversations) >= max_conversations:
                break

            chain = self._traverse_thread(root_id, tweet_lookup)
            if not chain:
                continue

            # Check if this thread involves the target brand
            thread_brand = None
            for item in chain:
                if not item["inbound"]:
                    thread_brand = item["author_id"]
                    break

            if self.brand_handle and thread_brand and thread_brand.lower() != self.brand_handle:
                continue

            # Build Conversation object
            turns: List[ConversationTurn] = []
            for item in chain:
                turns.append(
                    ConversationTurn(
                        tweet_id=item["tweet_id"],
                        author_id=item["author_id"],
                        is_customer=item["inbound"],
                        timestamp=item["created_at"],
                        text=item["text"],
                    )
                )

            first_customer_msg = turns[0].text if turns else ""
            brand_replies = [t.text for t in turns if not t.is_customer]

            # Determine start and end timestamps
            start_time = turns[0].timestamp if turns else ""
            end_time = turns[-1].timestamp if turns else ""

            conv = Conversation(
                conversation_id=str(root_id),
                brand=thread_brand or (self.brand_handle or "unknown"),
                start_time=start_time,
                end_time=end_time,
                turns=turns,
                first_customer_message=first_customer_msg,
                first_brand_reply=brand_replies[0] if brand_replies else None,
                final_brand_reply=brand_replies[-1] if brand_replies else None,
                turn_count=len(turns),
                has_brand_response=len(brand_replies) > 0,
            )
            conversations.append(conv)

        return conversations

    def _traverse_thread(
        self, root_id: int, tweet_lookup: Dict[int, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Traverses a thread starting from root_id following response links."""
        visited = set()
        chain = []
        current_ids = [root_id]

        while current_ids:
            next_ids = []
            for tid in current_ids:
                if tid in visited or tid not in tweet_lookup:
                    continue
                visited.add(tid)
                node = tweet_lookup[tid]
                chain.append(node)

                # Find child tweets from response_tweet_id (may be comma-separated list)
                resp_str = node.get("response_tweet_id", "")
                if resp_str:
                    for child_str in resp_str.split(","):
                        try:
                            child_id = int(child_str.strip())
                            if child_id in tweet_lookup and child_id not in visited:
                                next_ids.append(child_id)
                        except ValueError:
                            continue
            current_ids = next_ids

        # Sort the thread chronologically
        chain.sort(
            key=lambda x: parse_twitter_timestamp(x["created_at"]) or datetime.min
        )
        return chain
