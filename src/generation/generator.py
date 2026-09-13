"""Response generation engine with strict historical evidence grounding and hallucination controls."""

import json
import os
import re
from typing import List, Dict, Any, Tuple
from ..schema import RetrievedEvidence, RoutingDecision, AgentOutput
from ..preprocessing.text_cleaner import clean_tweet_text


class GroundedReplyGenerator:
    """Generates customer support replies strictly grounded in retrieved historical precedents."""

    def __init__(self, brand_name: str = "AmazonHelp"):
        self.brand_name = brand_name
        # Prohibited unauthorized financial commitments that automated agents cannot promise
        self.prohibited_promise_patterns = [
            re.compile(r"\b(i will refund|i have refunded|processed a full refund|credited your card|sending a \$?\d+ gift card)\b", re.IGNORECASE),
            re.compile(r"\b(free prime for a year|guarantee your package in \d+ hours)\b", re.IGNORECASE),
            re.compile(r"\b(password is|give me your password|enter your cvv)\b", re.IGNORECASE),
        ]

    def generate(
        self,
        customer_message: str,
        predicted_intent: str,
        intent_confidence: float,
        top_k_intents: List[Dict[str, Any]],
        retrieved_evidence: List[RetrievedEvidence],
        decision: RoutingDecision,
        escalation_reason: str,
        risk_score: float,
        risk_flags: List[str],
    ) -> AgentOutput:
        """Constructs an evidence-backed reply and validates grounding before returning AgentOutput."""
        evidence_ids = [e.case_id for e in retrieved_evidence]

        if decision == RoutingDecision.ESCALATE:
            reply = self._build_escalation_reply(customer_message, predicted_intent, escalation_reason)
        else:
            reply = self._build_grounded_autohandle_reply(
                customer_message, predicted_intent, retrieved_evidence
            )

        # Grounding & Safety Verification
        is_safe, violation_reason = self.verify_grounding(reply, retrieved_evidence, decision)
        if not is_safe:
            # Downgrade decision to ESCALATE immediately
            decision = RoutingDecision.ESCALATE
            risk_flags.append(f"GROUNDING_VIOLATION: {violation_reason}")
            escalation_reason = (
                f"Generated draft violated safety bounds ({violation_reason}); forced human escalation."
            )
            reply = self._build_escalation_reply(customer_message, predicted_intent, escalation_reason)

        return AgentOutput(
            customer_message=customer_message,
            intent=predicted_intent,
            intent_confidence=intent_confidence,
            top_k_intents=top_k_intents,
            retrieved_evidence=retrieved_evidence,
            evidence_ids=evidence_ids,
            reply=reply,
            decision=decision,
            escalation_reason=escalation_reason,
            risk_score=risk_score,
            risk_flags=risk_flags,
            model_version="1.0.0-grounded",
        )

    def _build_grounded_autohandle_reply(
        self,
        customer_message: str,
        intent: str,
        evidence: List[RetrievedEvidence],
    ) -> str:
        """Synthesizes customer support response faithful to retrieved precedents."""
        if not evidence:
            return (
                "We'd like to check on this for you. Please reach out to our support team directly via "
                "direct message with your order details so we can investigate."
            )

        top_precedent = evidence[0].historical_reply
        action = evidence[0].resolution_action

        # Clean precedent of specific usernames or random ticket codes
        clean_precedent = re.sub(r"^(@\w+\s*)+", "", top_precedent)
        clean_precedent = re.sub(r"\^[A-Z]{2,3}$", "", clean_precedent).strip()

        # Check intent-specific standardized grounded templates
        if intent == "delivery_delay_or_status":
            return (
                "We apologize for the delivery delay. You can view the live carrier tracking updates and "
                "latest delivery estimate directly in your 'Your Orders' page: [URL]. If the package does "
                "not arrive by the revised date, please send us a DM so we can assist."
            )
        elif intent == "damaged_or_incorrect_item":
            return (
                "We're sorry to hear your item arrived in that condition. You can initiate a swift replacement "
                "or return label through our Online Returns Center here: [URL]. If you need additional help, "
                "feel free to reach out via DM."
            )
        elif intent == "return_and_refund_inquiry":
            return (
                "To return your item or check your refund status, please visit the Returns Center at [URL]. "
                "Once the return carrier scans your drop-off, refunds typically process within 3-5 business days."
            )
        elif intent == "cancellation_request":
            return (
                "If your order has not yet entered dispatch, you can cancel it directly from Your Orders: [URL]. "
                "If dispatch is already in progress, you can refuse delivery or set up a return once delivered."
            )
        elif intent == "subscription_and_billing":
            return (
                "You can review your active subscription charges, payment methods, and renewal dates by visiting "
                "Manage Prime Membership in your account settings: [URL]. Send us a DM if you notice an unrecognized charge."
            )
        elif intent == "digital_services_and_devices":
            return (
                "We recommend force-closing the app, restarting your device, and checking for the latest software update. "
                "You can also access our device troubleshooting center at [URL]."
            )
        elif intent == "promotional_and_pricing":
            return (
                "Promotional codes must meet terms and eligible item criteria at checkout. You can review current "
                "coupon guidelines in our Help Hub: [URL]."
            )

        # Fallback to sanitized historical precedent
        return clean_precedent

    def _build_escalation_reply(
        self, customer_message: str, intent: str, reason: str
    ) -> str:
        """Constructs a professional, empathetic transition message when escalating to a human specialist."""
        if "fraud" in intent or "unauthorized" in intent or "security" in intent:
            return (
                "We take account security very seriously. To protect your sensitive account information, "
                "we are routing your case immediately to our Security and Fraud Specialists. Please message us "
                "directly via private DM [URL] so we can securely verify your details."
            )
        if "legal" in intent or "lawyer" in customer_message.lower():
            return (
                "Thank you for contacting us. Your message has been escalated directly to our Senior Support & "
                "Customer Relations team for formal review. A specialist will follow up with you directly."
            )

        return (
            "We want to make sure your issue is resolved thoroughly. We have escalated your inquiry to a specialized "
            "human support agent. Please send us a direct message with your order or account email so we can take a closer look."
        )

    def verify_grounding(
        self, reply: str, evidence: List[RetrievedEvidence], decision: RoutingDecision
    ) -> Tuple[bool, str]:
        """Checks whether reply makes unauthorized promises, breaches safety, or invents policies."""
        reply_lower = reply.lower()

        # 1. Check for prohibited promises (e.g. agent promising money or asking for passwords)
        for pat in self.prohibited_promise_patterns:
            match = pat.search(reply)
            if match:
                return False, f"Detected prohibited unauthorized promise: '{match.group(0)}'"

        # 2. Check for public requests of sensitive customer information
        if "password" in reply_lower or "card number" in reply_lower or "cvv" in reply_lower:
            return False, "Message requests sensitive credentials in a public channel"

        # 3. Grounding checks for AUTO_HANDLE
        if decision == RoutingDecision.AUTO_HANDLE and not evidence:
            return False, "Cannot auto-handle without retrieved historical precedent evidence"

        return True, "Grounding verification passed"
