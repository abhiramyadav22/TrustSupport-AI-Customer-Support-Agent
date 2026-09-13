export interface SimulatedEvidence {
  caseId: string;
  similarity: number;
  intent: string;
  historicalProblem: string;
  historicalReply: string;
  resolutionAction: string;
  // Aliases for snake_case compatibility
  case_id: string;
  similarity_score: number;
  customer_problem: string;
  historical_reply: string;
  resolution_action: string;
}

export interface SimulatedOutput {
  customerMessage: string;
  cleanedMessage: string;
  intent: string;
  intentConfidence: number;
  topKIntents: Array<{ intent: string; confidence: number }>;
  retrievedEvidence: SimulatedEvidence[];
  decision: "AUTO_HANDLE" | "ESCALATE";
  escalationReason: string;
  riskScore: number;
  riskFlags: string[];
  reply: string;

  // Aliases for snake_case compatibility
  customer_message: string;
  cleaned_message: string;
  intent_confidence: number;
  top_k_intents: Array<{ intent: string; confidence: number }>;
  retrieved_evidence: SimulatedEvidence[];
  escalation_reason: string;
  risk_score: number;
  risk_flags: string[];
}

function createEvidenceItem(
  caseId: string,
  similarity: number,
  intent: string,
  problem: string,
  reply: string,
  action: string
): SimulatedEvidence {
  return {
    caseId,
    similarity,
    intent,
    historicalProblem: problem,
    historicalReply: reply,
    resolutionAction: action,
    case_id: caseId,
    similarity_score: similarity,
    customer_problem: problem,
    historical_reply: reply,
    resolution_action: action,
  };
}

export function simulateAgent(input: string): SimulatedOutput {
  const cleaned = input.replace(/@\w+/g, "").replace(/\s+/g, " ").trim();
  const lower = cleaned.toLowerCase();

  // Quality check
  const words = cleaned.split(/\s+/).filter(Boolean);
  if (words.length < 3) {
    const briefReason = "Customer message failed quality check (extreme brevity < 3 words); manual triage required.";
    const briefFlags = ["INSUFFICIENT_MESSAGE_SUBSTANCE", "EXTREME_BREVITY_AMBIGUOUS"];
    const briefReply = "We'd like to help you with this. Could you please send us a direct message with additional details so we can assist?";
    return {
      customerMessage: input,
      cleanedMessage: cleaned,
      intent: "unsupported_or_ambiguous",
      intentConfidence: 0.15,
      topKIntents: [{ intent: "unsupported_or_ambiguous", confidence: 0.15 }],
      retrievedEvidence: [],
      decision: "ESCALATE",
      escalationReason: briefReason,
      riskScore: 0.95,
      riskFlags: briefFlags,
      reply: briefReply,
      // snake_case aliases
      customer_message: input,
      cleaned_message: cleaned,
      intent_confidence: 0.15,
      top_k_intents: [{ intent: "unsupported_or_ambiguous", confidence: 0.15 }],
      retrieved_evidence: [],
      escalation_reason: briefReason,
      risk_score: 0.95,
      risk_flags: briefFlags,
    };
  }

  // Intent classification
  let intent = "delivery_delay_or_status";
  let conf = 0.68;
  let topK = [
    { intent: "delivery_delay_or_status", confidence: 0.68 },
    { intent: "cancellation_request", confidence: 0.18 },
    { intent: "return_and_refund_inquiry", confidence: 0.14 },
  ];

  if (lower.includes("fraud") || lower.includes("unauthorized") || lower.includes("hacked") || lower.includes("stolen card")) {
    intent = "fraud_or_unauthorized_charge";
    conf = 0.92;
    topK = [
      { intent: "fraud_or_unauthorized_charge", confidence: 0.92 },
      { intent: "account_access_and_otp", confidence: 0.05 },
      { intent: "subscription_and_billing", confidence: 0.03 },
    ];
  } else if (lower.includes("lawyer") || lower.includes("attorney") || lower.includes("sue") || lower.includes("police") || lower.includes("court")) {
    intent = "legal_or_severe_complaint";
    conf = 0.89;
    topK = [
      { intent: "legal_or_severe_complaint", confidence: 0.89 },
      { intent: "fraud_or_unauthorized_charge", confidence: 0.07 },
      { intent: "delivery_delay_or_status", confidence: 0.04 },
    ];
  } else if (lower.includes("cancel") || lower.includes("stop order") || lower.includes("revoke")) {
    intent = "cancellation_request";
    conf = 0.78;
    topK = [
      { intent: "cancellation_request", confidence: 0.78 },
      { intent: "delivery_delay_or_status", confidence: 0.14 },
      { intent: "return_and_refund_inquiry", confidence: 0.08 },
    ];
  } else if (lower.includes("damaged") || lower.includes("broken") || lower.includes("shattered") || lower.includes("cracked")) {
    intent = "damaged_or_incorrect_item";
    conf = 0.84;
    topK = [
      { intent: "damaged_or_incorrect_item", confidence: 0.84 },
      { intent: "return_and_refund_inquiry", confidence: 0.11 },
      { intent: "delivery_delay_or_status", confidence: 0.05 },
    ];
  } else if (lower.includes("return") || lower.includes("refund") || lower.includes("drop off")) {
    intent = "return_and_refund_inquiry";
    conf = 0.81;
    topK = [
      { intent: "return_and_refund_inquiry", confidence: 0.81 },
      { intent: "damaged_or_incorrect_item", confidence: 0.12 },
      { intent: "cancellation_request", confidence: 0.07 },
    ];
  } else if (lower.includes("prime") || lower.includes("charged") || lower.includes("subscription") || lower.includes("membership")) {
    intent = "subscription_and_billing";
    conf = 0.79;
    topK = [
      { intent: "subscription_and_billing", confidence: 0.79 },
      { intent: "cancellation_request", confidence: 0.12 },
      { intent: "account_access_and_otp", confidence: 0.09 },
    ];
  } else if (lower.includes("kindle") || lower.includes("echo") || lower.includes("fire stick") || lower.includes("streaming") || lower.includes("alexa")) {
    intent = "digital_services_and_devices";
    conf = 0.85;
    topK = [
      { intent: "digital_services_and_devices", confidence: 0.85 },
      { intent: "subscription_and_billing", confidence: 0.10 },
      { intent: "account_access_and_otp", confidence: 0.05 },
    ];
  } else if (lower.includes("password") || lower.includes("otp") || lower.includes("login") || lower.includes("locked account")) {
    intent = "account_access_and_otp";
    conf = 0.86;
    topK = [
      { intent: "account_access_and_otp", confidence: 0.86 },
      { intent: "fraud_or_unauthorized_charge", confidence: 0.10 },
      { intent: "digital_services_and_devices", confidence: 0.04 },
    ];
  }

  // Precedent evidence
  let evidence: SimulatedEvidence[] = [
    createEvidenceItem(
      "case_amazon_1842",
      0.442,
      intent,
      "Package tracking shows in transit but delivery date passed two days ago.",
      "We're sorry for the delay! You can check the latest tracking progress and carrier delivery window in Your Orders: [URL].",
      "track_package_carrier_link"
    ),
    createEvidenceItem(
      "case_amazon_0931",
      0.385,
      intent,
      "Late package status update inquiry.",
      "Please send us a DM with your tracking number so we can investigate with carrier logistics.",
      "dm_escalation_link"
    ),
  ];

  if (intent === "damaged_or_incorrect_item") {
    evidence = [
      createEvidenceItem(
        "case_amazon_2214",
        0.495,
        intent,
        "Item arrived crushed in transit with packaging torn.",
        "We apologize for this experience! You can arrange an immediate replacement or print a prepaid return label via Returns Center: [URL].",
        "returns_replacement_portal"
      ),
      createEvidenceItem(
        "case_amazon_0782",
        0.412,
        intent,
        "Broken screen on delivery.",
        "Please head to the Returns Center at [URL] to select 'Item Damaged' for a replacement shipment.",
        "returns_replacement_portal"
      ),
    ];
  } else if (intent === "cancellation_request") {
    evidence = [
      createEvidenceItem(
        "case_amazon_1109",
        0.468,
        intent,
        "Ordered wrong size by mistake, want to cancel before it ships.",
        "You can request cancellation directly from 'Your Orders' if dispatch has not begun: [URL].",
        "self_service_cancel_link"
      ),
    ];
  } else if (intent === "fraud_or_unauthorized_charge") {
    evidence = [
      createEvidenceItem(
        "case_amazon_0411",
        0.428,
        intent,
        "Card billed for items never ordered.",
        "To secure your account immediately, please reach our fraud protection team via private DM [URL].",
        "secure_fraud_escalation"
      ),
    ];
  }

  // Escalation policy
  const riskFlags: string[] = [];
  let decision: "AUTO_HANDLE" | "ESCALATE" = "AUTO_HANDLE";
  let reason = "";

  const uncertainty = Math.max(0, 1.0 - conf);
  const topSim = evidence.length > 0 ? evidence[0].similarity : 0.0;
  const retrievalWeakness = Math.max(0, 1.0 - topSim);
  const compositeRisk = 0.40 * uncertainty + 0.30 * retrievalWeakness + 0.10 * (intent.includes("billing") ? 0.5 : 0.0);

  // Check mandatory safety intents
  if (intent === "fraud_or_unauthorized_charge") {
    decision = "ESCALATE";
    riskFlags.push("MANDATORY_SAFETY_INTENT: fraud_or_unauthorized_charge");
    reason = "Escalated to human agent because intent involves unauthorized financial transactions or compromised credentials.";
  } else if (intent === "legal_or_severe_complaint") {
    decision = "ESCALATE";
    riskFlags.push("MANDATORY_SAFETY_INTENT: legal_or_severe_complaint");
    reason = "Escalated to human agent because customer made explicit threats of litigation or regulatory enforcement.";
  } else if (intent === "account_access_and_otp") {
    decision = "ESCALATE";
    riskFlags.push("MANDATORY_SAFETY_INTENT: account_access_and_otp");
    reason = "Escalated to human agent because account authentication requires private credential verification.";
  } else if (compositeRisk > 0.46) {
    decision = "ESCALATE";
    riskFlags.push(`HIGH_COMPOSITE_RISK: ${compositeRisk.toFixed(3)} > 0.460`);
    reason = `Escalated to human agent because composite risk score (${compositeRisk.toFixed(2)}) exceeded automation tolerance (0.46).`;
  } else if (conf < 0.38) {
    decision = "ESCALATE";
    riskFlags.push(`LOW_INTENT_CONFIDENCE: ${conf.toFixed(3)} < 0.380`);
    reason = `Escalated to human agent because intent confidence (${(conf * 100).toFixed(1)}%) fell below required threshold (38.0%).`;
  } else {
    decision = "AUTO_HANDLE";
    reason = `High intent confidence (${(conf * 100).toFixed(1)}%) and historical precedent similarity (${topSim.toFixed(2)}) justify safe automated resolution.`;
  }

  // Reply generation
  let reply = "";
  if (decision === "ESCALATE") {
    if (intent === "fraud_or_unauthorized_charge") {
      reply = "We take account security very seriously. To protect your sensitive account information, we are routing your case immediately to our Security and Fraud Specialists. Please message us directly via private DM [URL] so we can securely verify your details.";
    } else if (intent === "legal_or_severe_complaint") {
      reply = "Thank you for contacting us. Your message has been escalated directly to our Senior Support & Customer Relations team for formal review. A specialist will follow up with you directly.";
    } else {
      reply = "We want to make sure your issue is resolved thoroughly. We have escalated your inquiry to a specialized human support agent. Please send us a direct message with your order or account email so we can take a closer look.";
    }
  } else {
    if (intent === "delivery_delay_or_status") {
      reply = "We apologize for the delivery delay. You can view the live carrier tracking updates and latest delivery estimate directly in your 'Your Orders' page: [URL]. If the package does not arrive by the revised date, please send us a DM so we can assist.";
    } else if (intent === "damaged_or_incorrect_item") {
      reply = "We're sorry to hear your item arrived in that condition. You can initiate a swift replacement or return label through our Online Returns Center here: [URL]. If you need additional help, feel free to reach out via DM.";
    } else if (intent === "cancellation_request") {
      reply = "If your order has not yet entered dispatch, you can cancel it directly from Your Orders: [URL]. If dispatch is already in progress, you can refuse delivery or set up a return once delivered.";
    } else if (intent === "return_and_refund_inquiry") {
      reply = "To return your item or check your refund status, please visit the Returns Center at [URL]. Once the return carrier scans your drop-off, refunds typically process within 3-5 business days.";
    } else if (intent === "subscription_and_billing") {
      reply = "You can review your active subscription charges, payment methods, and renewal dates by visiting Manage Prime Membership in your account settings: [URL]. Send us a DM if you notice an unrecognized charge.";
    } else {
      reply = "We'd like to help resolve this for you. Please check our Help Hub guidelines at [URL], or message us directly with your order details.";
    }
  }

  return {
    customerMessage: input,
    cleanedMessage: cleaned,
    intent,
    intentConfidence: conf,
    topKIntents: topK,
    retrievedEvidence: evidence,
    decision,
    escalationReason: reason,
    riskScore: compositeRisk,
    riskFlags,
    reply,
    // snake_case aliases
    customer_message: input,
    cleaned_message: cleaned,
    intent_confidence: conf,
    top_k_intents: topK,
    retrieved_evidence: evidence,
    escalation_reason: reason,
    risk_score: compositeRisk,
    risk_flags: riskFlags,
  };
}
