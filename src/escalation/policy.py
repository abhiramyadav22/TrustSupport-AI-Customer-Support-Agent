"""Calibrated risk-aware escalation policy engine for support routing."""

from typing import List, Dict, Any, Tuple
import yaml
from ..schema import RoutingDecision, RetrievedEvidence, RiskLevel


class EscalationPolicyEngine:
    """Evaluates incoming customer requests and retrieved historical evidence to determine routing."""

    def __init__(self, config_path: str = "configs/thresholds.yaml"):
        self.config_path = config_path
        self._load_config()

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        policy = data.get("escalation_policy", {})
        self.min_intent_confidence = float(policy.get("min_intent_confidence", 0.72))
        self.min_retrieval_similarity = float(policy.get("min_retrieval_similarity", 0.65))
        self.min_evidence_agreement = float(policy.get("min_evidence_agreement", 0.60))
        self.max_risk_score = float(policy.get("max_risk_score_for_autohandle", 0.35))
        self.risk_weights = policy.get("risk_weights", {
            "uncertainty_weight": 0.35,
            "retrieval_weakness_weight": 0.25,
            "evidence_conflict_weight": 0.20,
            "sensitive_intent_weight": 0.20,
        })
        self.mandatory_escalation_intents = set(
            policy.get("mandatory_escalation_intents", [
                "fraud_or_unauthorized_charge",
                "legal_or_severe_complaint",
                "fraud_or_account_security",
            ])
        )
        self.sensitive_keywords = [
            kw.lower() for kw in policy.get("sensitive_keywords", [
                "lawyer", "attorney", "sue", "legal action", "hacked", "fraud",
                "stolen", "unauthorized charge", "police", "press"
            ])
        ]

    def evaluate(
        self,
        customer_message: str,
        intent: str,
        intent_confidence: float,
        retrieved_evidence: List[RetrievedEvidence],
    ) -> Tuple[RoutingDecision, str, float, List[str]]:
        """Evaluates message and signals to produce (decision, escalation_reason, risk_score, risk_flags)."""
        risk_flags: List[str] = []
        msg_lower = customer_message.lower()

        # 1. Check mandatory intent triggers
        if intent in self.mandatory_escalation_intents:
            risk_flags.append(f"MANDATORY_INTENT_TRIGGER: '{intent}'")
            return (
                RoutingDecision.ESCALATE,
                f"Topic '{intent}' involves high-liability fraud, legal compliance, or sensitive security procedures requiring human handling.",
                1.0,
                risk_flags,
            )

        # 2. Check sensitive keyword triggers
        triggered_keywords = [kw for kw in self.sensitive_keywords if kw in msg_lower]
        if triggered_keywords:
            risk_flags.append(f"SENSITIVE_KEYWORD_TRIGGER: {triggered_keywords}")
            return (
                RoutingDecision.ESCALATE,
                f"Customer message contains sensitive escalation triggers ({', '.join(triggered_keywords)}) requiring immediate human agent intervention.",
                0.95,
                risk_flags,
            )

        # 3. Assess intent uncertainty
        uncertainty = max(0.0, 1.0 - intent_confidence)
        if intent_confidence < self.min_intent_confidence:
            risk_flags.append(
                f"LOW_INTENT_CONFIDENCE: {intent_confidence:.3f} < {self.min_intent_confidence}"
            )

        # 4. Assess retrieval similarity
        top_sim = retrieved_evidence[0].similarity_score if retrieved_evidence else 0.0
        retrieval_weakness = max(0.0, 1.0 - top_sim)
        if top_sim < self.min_retrieval_similarity:
            risk_flags.append(
                f"WEAK_HISTORICAL_RETRIEVAL: {top_sim:.3f} < {self.min_retrieval_similarity}"
            )

        # 5. Assess evidence agreement
        if retrieved_evidence:
            intent_matches = sum(1 for e in retrieved_evidence if e.intent == intent)
            agreement = intent_matches / len(retrieved_evidence)
        else:
            agreement = 0.0

        evidence_conflict = max(0.0, 1.0 - agreement)
        if agreement < self.min_evidence_agreement:
            risk_flags.append(
                f"CONFLICTING_HISTORICAL_EVIDENCE: agreement {agreement:.2f} < {self.min_evidence_agreement}"
            )

        # 6. Assess message ambiguity / short length
        words = customer_message.split()
        if len(words) < 4:
            risk_flags.append("EXTREME_BREVITY_AMBIGUOUS")
            uncertainty = max(uncertainty, 0.45)

        # 7. Calculate composite risk score
        w = self.risk_weights
        composite_risk = (
            w.get("uncertainty_weight", 0.35) * uncertainty
            + w.get("retrieval_weakness_weight", 0.25) * retrieval_weakness
            + w.get("evidence_conflict_weight", 0.20) * evidence_conflict
            + w.get("sensitive_intent_weight", 0.20) * (0.5 if "billing" in intent or "access" in intent else 0.0)
        )
        composite_risk = min(1.0, max(0.0, composite_risk))

        # 8. Decision logic
        hard_escalate = (
            composite_risk > self.max_risk_score
            or intent_confidence < self.min_intent_confidence
            or "EXTREME_BREVITY_AMBIGUOUS" in risk_flags
            or (not retrieved_evidence)
            or (top_sim < 0.15)
        )

        if hard_escalate:
            # Build detailed human-readable reason
            reasons = []
            if intent_confidence < self.min_intent_confidence:
                reasons.append(
                    f"intent confidence ({intent_confidence:.1%}) fell below required threshold ({self.min_intent_confidence:.1%})"
                )
            if top_sim < self.min_retrieval_similarity:
                reasons.append(
                    f"top historical case similarity ({top_sim:.2f}) is below standard retrieval threshold ({self.min_retrieval_similarity:.2f})"
                )
            if agreement < self.min_evidence_agreement:
                reasons.append(
                    f"retrieved historical precedents disagree on resolution action (consistency: {agreement:.0%})"
                )
            if "EXTREME_BREVITY_AMBIGUOUS" in risk_flags:
                reasons.append("message is too brief to safely rule out edge cases")

            if not reasons:
                reasons.append(f"composite risk score ({composite_risk:.2f}) exceeded automation tolerance ({self.max_risk_score:.2f})")

            final_reason = "Escalated to human agent because " + "; ".join(reasons) + "."
            return RoutingDecision.ESCALATE, final_reason, composite_risk, risk_flags

        # Auto-handle passed all risk gates
        auto_reason = (
            f"High intent confidence ({intent_confidence:.1%}) and strong historical precedent "
            f"(similarity {top_sim:.2f}, consistency {agreement:.0%}) justify safe automated resolution."
        )
        return RoutingDecision.AUTO_HANDLE, auto_reason, composite_risk, risk_flags
