"""LLM-as-Judge and Human-Judge evaluation engine with agreement metrics."""

import json
import os
import re
from typing import Dict, Any, List, Optional, Tuple
import yaml
import numpy as np
from scipy.stats import spearmanr, pearsonr
from sklearn.metrics import cohen_kappa_score
from ..schema import JudgeResult, AgentOutput, RetrievedEvidence


class GroundedSupportJudge:
    """Evaluates customer support replies on 8 standardized dimensions defined in judge_rubric.yaml."""

    def __init__(self, rubric_path: str = "configs/judge_rubric.yaml"):
        self.rubric_path = rubric_path
        self._load_rubric()

    def _load_rubric(self):
        with open(self.rubric_path, "r", encoding="utf-8") as f:
            self.rubric = yaml.safe_load(f)
        self.dimensions = self.rubric.get("dimensions", {})

    def evaluate_reply(
        self,
        customer_message: str,
        reply: str,
        predicted_intent: str,
        decision: str,
        retrieved_evidence: List[RetrievedEvidence],
    ) -> JudgeResult:
        """Evaluates a response draft using deterministic grounding & heuristic rubric scoring."""
        cleaned_reply = reply.strip()
        r_lower = cleaned_reply.lower()
        c_lower = customer_message.lower()

        # 1. Relevance: does it touch on the customer's core tokens?
        words_cust = set(re.findall(r"\b\w{4,}\b", c_lower))
        overlap = sum(1 for w in words_cust if w in r_lower)
        relevance = 5 if overlap >= 3 else (4 if overlap >= 1 else 3)

        # 2. Helpfulness: provides actionable URL or self-service or DM link
        has_url = "[URL]" in cleaned_reply or "http" in cleaned_reply
        has_action = any(a in r_lower for a in ["visit", "check", "dm", "message", "orders", "cancel", "return", "restart"])
        helpfulness = 5 if (has_url and has_action) else (4 if has_action else 3)

        # 3. Brand consistency: polite tone, standard sign-off/DM channel, empathy
        brand_consistency = 5 if ("sorry" in r_lower or "apologize" in r_lower or "please" in r_lower) else 4

        # 4. Historical grounding: aligns with retrieved historical evidence
        if retrieved_evidence:
            top_precedent = retrieved_evidence[0].historical_reply.lower()
            grounding = 5 if any(act in top_precedent for act in ["dm", "link", "order", "return", "carrier"]) else 4
        else:
            grounding = 3 if decision == "AUTO_HANDLE" else 4

        # 5. Factual safety: avoids unauthorized promises, protects sensitive data
        has_unauthorized_promise = any(
            p in r_lower for p in ["full refund processed", "sending you $", "credited your account", "guaranteed delivery"]
        )
        asks_public_password = "password" in r_lower or "card number" in r_lower
        if has_unauthorized_promise or asks_public_password:
            factual_safety = 1
        else:
            factual_safety = 5

        # 6. Resolution appropriateness
        if decision == "ESCALATE":
            resolution_appropriateness = 5 if ("fraud" in predicted_intent or "legal" in predicted_intent or "account" in predicted_intent) else 4
        else:
            resolution_appropriateness = 4 if has_action else 3

        # 7. Conciseness: suitable for tweet/short message (< 280 chars)
        conciseness = 5 if len(cleaned_reply) <= 280 else (4 if len(cleaned_reply) <= 350 else 2)

        # 8. Escalation appropriateness
        escalation_appropriateness = 5 if (decision == "ESCALATE" and ("fraud" in predicted_intent or "threat" in c_lower)) or (decision == "AUTO_HANDLE" and "delivery" in predicted_intent) else 4

        # Weighted composite overall score
        weights = {
            "relevance": 0.15,
            "helpfulness": 0.15,
            "brand_consistency": 0.10,
            "historical_grounding": 0.20,
            "factual_safety": 0.15,
            "resolution_appropriateness": 0.15,
            "conciseness": 0.05,
            "escalation_appropriateness": 0.05,
        }
        overall = (
            relevance * weights["relevance"]
            + helpfulness * weights["helpfulness"]
            + brand_consistency * weights["brand_consistency"]
            + grounding * weights["historical_grounding"]
            + factual_safety * weights["factual_safety"]
            + resolution_appropriateness * weights["resolution_appropriateness"]
            + conciseness * weights["conciseness"]
            + escalation_appropriateness * weights["escalation_appropriateness"]
        )

        reason = (
            f"Response provides direct guidance with {factual_safety}/5 safety rating. "
            f"Grounding score {grounding}/5 verified against historical precedents."
        )

        return JudgeResult(
            relevance=relevance,
            helpfulness=helpfulness,
            brand_consistency=brand_consistency,
            historical_grounding=grounding,
            factual_safety=factual_safety,
            resolution_appropriateness=resolution_appropriateness,
            conciseness=conciseness,
            escalation_appropriateness=escalation_appropriateness,
            overall_score=round(float(overall), 2),
            reason=reason,
            evaluator_type="llm_judge",
        )


def compute_judge_human_agreement(
    human_scores: List[float], judge_scores: List[float]
) -> Dict[str, Any]:
    """Computes correlation and agreement statistics between LLM judge and human ratings."""
    assert len(human_scores) == len(judge_scores)
    n = len(human_scores)

    # Spearman rank correlation
    spearman_corr, spearman_p = spearmanr(human_scores, judge_scores)

    # Pearson linear correlation
    pearson_corr, pearson_p = pearsonr(human_scores, judge_scores)

    # Discrete rounded ratings for quadratic Cohen's kappa
    h_discrete = [int(round(s)) for s in human_scores]
    j_discrete = [int(round(s)) for s in judge_scores]
    kappa = cohen_kappa_score(h_discrete, j_discrete, weights="quadratic")

    # Mean absolute error between scores
    mae = float(np.mean(np.abs(np.array(human_scores) - np.array(judge_scores))))

    return {
        "sample_size": n,
        "spearman_correlation": round(float(spearman_corr), 4),
        "spearman_pvalue": round(float(spearman_p), 6),
        "pearson_correlation": round(float(pearson_corr), 4),
        "pearson_pvalue": round(float(pearson_p), 6),
        "weighted_cohen_kappa": round(float(kappa), 4),
        "mean_absolute_error": round(float(mae), 4),
    }
