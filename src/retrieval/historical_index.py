"""Historical support case retrieval and evidence indexing."""

import json
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from ..schema import RetrievedEvidence, Conversation
from ..preprocessing.text_cleaner import clean_tweet_text


class HistoricalSupportIndex:
    """Indexes historical resolved support cases and retrieves grounded evidence for queries."""

    def __init__(self, mode: str = "intent_filtered"):
        """Modes: 'none', 'generic', 'intent_filtered', 'intent_resolution_aware'."""
        self.mode = mode
        self.cases: List[Dict[str, Any]] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.case_matrix: Optional[np.ndarray] = None
        self.intent_to_indices: Dict[str, List[int]] = {}

    def build_from_conversations(self, conversations: List[Conversation]):
        """Builds retrieval index from historical resolved conversations."""
        self.cases = []
        texts_to_vectorize = []

        for conv in conversations:
            if not conv.has_brand_response or not conv.first_brand_reply:
                continue

            # Ensure clean customer problem and reply
            problem = clean_tweet_text(conv.first_customer_message)
            reply = conv.first_brand_reply.strip()
            if not problem or not reply or len(reply) < 15:
                continue

            intent = conv.inferred_intent or "general_inquiry"

            # Derive resolution action from reply keywords
            action = self._infer_resolution_action(reply)

            case_idx = len(self.cases)
            case_data = {
                "case_id": f"case_{conv.conversation_id}",
                "customer_problem": problem,
                "historical_reply": reply,
                "intent": intent,
                "resolution_action": action,
                "timestamp": conv.start_time,
                "turn_count": conv.turn_count,
            }
            self.cases.append(case_data)
            texts_to_vectorize.append(problem)

            if intent not in self.intent_to_indices:
                self.intent_to_indices[intent] = []
            self.intent_to_indices[intent].append(case_idx)

        if texts_to_vectorize:
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                stop_words="english",
                sublinear_tf=True,
            )
            self.case_matrix = self.vectorizer.fit_transform(texts_to_vectorize)

    def _infer_resolution_action(self, reply: str) -> str:
        """Categorizes the brand's operational resolution action."""
        r_lower = reply.lower()
        if "dm" in r_lower or "direct message" in r_lower or "private" in r_lower:
            return "secure_dm_redirect"
        if "track" in r_lower or "deliver" in r_lower or "carrier" in r_lower:
            return "carrier_tracking_guidance"
        if "return" in r_lower or "refund" in r_lower or "label" in r_lower:
            return "return_portal_procedure"
        if "cancel" in r_lower:
            return "cancellation_guidance"
        if "restart" in r_lower or "app" in r_lower or "update" in r_lower:
            return "technical_troubleshooting"
        return "general_guidance"

    def retrieve(
        self, query: str, predicted_intent: Optional[str] = None, top_k: int = 3
    ) -> List[RetrievedEvidence]:
        """Retrieves top-k historical support cases according to configured ablation mode."""
        if self.mode == "none" or not self.cases or self.vectorizer is None or self.case_matrix is None:
            return []

        cleaned_query = clean_tweet_text(query)
        if not cleaned_query:
            return []

        query_vec = self.vectorizer.transform([cleaned_query])

        # Candidate selection based on ablation mode
        if self.mode == "generic" or not predicted_intent:
            candidate_indices = list(range(len(self.cases)))
        elif self.mode in ("intent_filtered", "intent_resolution_aware"):
            candidate_indices = self.intent_to_indices.get(predicted_intent, [])
            if len(candidate_indices) < top_k:
                # Backfill from generic pool if class has few historical examples
                candidate_indices = list(range(len(self.cases)))
        else:
            candidate_indices = list(range(len(self.cases)))

        if not candidate_indices:
            return []

        sub_matrix = self.case_matrix[candidate_indices]
        sims = cosine_similarity(query_vec, sub_matrix).flatten()

        top_local_idx = np.argsort(sims)[::-1][:top_k]

        results = []
        for loc in top_local_idx:
            global_idx = candidate_indices[loc]
            case = self.cases[global_idx]
            sim_score = float(sims[loc])

            evidence = RetrievedEvidence(
                case_id=case["case_id"],
                customer_problem=case["customer_problem"],
                historical_reply=case["historical_reply"],
                intent=case["intent"],
                similarity_score=sim_score,
                timestamp=case["timestamp"],
                resolution_action=case["resolution_action"],
                metadata={"turn_count": case["turn_count"]},
            )
            results.append(evidence)

        return results
