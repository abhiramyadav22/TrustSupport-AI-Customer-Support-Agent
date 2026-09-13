"""End-to-end production AI Support Agent pipeline."""

from typing import List, Dict, Any, Optional
from ..schema import AgentOutput, RoutingDecision, RetrievedEvidence
from ..preprocessing.text_cleaner import clean_tweet_text, assess_message_quality
from ..intent.classifier import CalibratedIntentClassifier
from ..retrieval.historical_index import HistoricalSupportIndex
from ..escalation.policy import EscalationPolicyEngine
from ..generation.generator import GroundedReplyGenerator


class TrustSupportAgent:
    """Production customer support agent with grounded historical retrieval and calibrated human escalation."""

    def __init__(
        self,
        classifier: CalibratedIntentClassifier,
        retrieval_index: HistoricalSupportIndex,
        escalation_engine: Optional[EscalationPolicyEngine] = None,
        reply_generator: Optional[GroundedReplyGenerator] = None,
        brand_name: str = "AmazonHelp",
    ):
        self.brand_name = brand_name
        self.classifier = classifier
        self.retrieval_index = retrieval_index
        self.escalation_engine = escalation_engine or EscalationPolicyEngine()
        self.reply_generator = reply_generator or GroundedReplyGenerator(brand_name=brand_name)

    def process_message(
        self, customer_message: str, top_k_retrieval: int = 3
    ) -> AgentOutput:
        """Processes a customer tweet through the full safety-first AI support pipeline."""
        cleaned_msg = clean_tweet_text(customer_message, brand_handle=self.brand_name)

        # 1. Quality Check
        is_sufficient, quality_reason = assess_message_quality(cleaned_msg)
        if not is_sufficient:
            # Short, noisy, or extreme length messages escalate with explicit reason
            return AgentOutput(
                customer_message=customer_message,
                intent="unsupported_or_ambiguous",
                intent_confidence=0.20,
                top_k_intents=[{"intent": "unsupported_or_ambiguous", "confidence": 0.20}],
                retrieved_evidence=[],
                evidence_ids=[],
                reply=(
                    "We'd like to help you with this. Could you please send us a direct message "
                    "with additional details about your order so we can assist?"
                ),
                decision=RoutingDecision.ESCALATE,
                escalation_reason=f"Customer message failed quality check ({quality_reason}); manual triage required.",
                risk_score=0.90,
                risk_flags=["INSUFFICIENT_MESSAGE_SUBSTANCE"],
            )

        # 2. Intent Classification with calibrated confidence
        intent, confidence, top_k = self.classifier.predict_single(cleaned_msg, top_k=3)

        # 3. Historical Support Case Retrieval
        evidence = self.retrieval_index.retrieve(
            query=cleaned_msg, predicted_intent=intent, top_k=top_k_retrieval
        )

        # 4. Risk-Aware Escalation Policy Evaluation
        decision, escalation_reason, risk_score, risk_flags = self.escalation_engine.evaluate(
            customer_message=cleaned_msg,
            intent=intent,
            intent_confidence=confidence,
            retrieved_evidence=evidence,
        )

        # 5. Grounded Reply Generation & Verification
        agent_output = self.reply_generator.generate(
            customer_message=cleaned_msg,
            predicted_intent=intent,
            intent_confidence=confidence,
            top_k_intents=top_k,
            retrieved_evidence=evidence,
            decision=decision,
            escalation_reason=escalation_reason,
            risk_score=risk_score,
            risk_flags=risk_flags,
        )

        return agent_output
