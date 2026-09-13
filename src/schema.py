"""Data models and schemas for TrustSupport AI system."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class RoutingDecision(str, Enum):
    AUTO_HANDLE = "AUTO_HANDLE"
    ESCALATE = "ESCALATE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class RawTweet:
    tweet_id: int
    author_id: str
    inbound: bool
    created_at: str
    text: str
    response_tweet_id: Optional[str] = None
    in_response_to_tweet_id: Optional[str] = None


@dataclass
class ConversationTurn:
    tweet_id: int
    author_id: str
    is_customer: bool
    timestamp: str
    text: str


@dataclass
class Conversation:
    conversation_id: str
    brand: str
    start_time: str
    end_time: str
    turns: List[ConversationTurn]
    first_customer_message: str
    first_brand_reply: Optional[str] = None
    final_brand_reply: Optional[str] = None
    turn_count: int = 1
    has_brand_response: bool = False
    inferred_intent: Optional[str] = None


@dataclass
class RetrievedEvidence:
    case_id: str
    customer_problem: str
    historical_reply: str
    intent: str
    similarity_score: float
    timestamp: str
    resolution_action: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    customer_message: str
    intent: str
    intent_confidence: float
    top_k_intents: List[Dict[str, Any]]
    retrieved_evidence: List[RetrievedEvidence]
    evidence_ids: List[str]
    reply: str
    decision: RoutingDecision
    escalation_reason: str
    risk_score: float
    risk_flags: List[str]
    model_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_message": self.customer_message,
            "intent": self.intent,
            "intent_confidence": round(self.intent_confidence, 4),
            "top_k_intents": self.top_k_intents,
            "evidence_ids": self.evidence_ids,
            "reply": self.reply,
            "decision": self.decision.value,
            "escalation_reason": self.escalation_reason,
            "risk_score": round(self.risk_score, 4),
            "risk_flags": self.risk_flags,
            "model_version": self.model_version,
        }


@dataclass
class JudgeResult:
    relevance: int
    helpfulness: int
    brand_consistency: int
    historical_grounding: int
    factual_safety: int
    resolution_appropriateness: int
    conciseness: int
    escalation_appropriateness: int
    overall_score: float
    reason: str
    evaluator_type: str = "llm_judge"  # or "human"
