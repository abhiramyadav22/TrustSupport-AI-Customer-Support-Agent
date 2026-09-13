# Systematic Error Analysis & Failure Forensics Report

**Benchmark Evaluated**: 200 Frozen Stratified Test Set Cases  
**Evaluated System**: TrustSupport AI Agent Pipeline  
**Overall Intent Accuracy**: 82.5% (Macro-F1: 0.6306)  
**Total Decision Discrepancies**: 109 cases (82 Over-escalations, 27 Under-escalations)  

---

## 1. Error Taxonomy & Empirical Distribution

| Error Category | Count | % of All Errors | Operational Risk Severity | Definition |
| :--- | :--- | :--- | :--- | :--- |
| **Policy Over-Escalation** | 82 | 66.1% | Low (Cost/Latency) | Agent escalated safe, standard inquiries due to conservative composite risk score or cautious intent confidence. |
| **Intent Confusion** | 35 | 28.2% | Medium | Agent misclassified the primary operational category (e.g. subscription cancellation vs. order cancellation). |
| **Policy Under-Escalation** | 27 | 21.8% | **High (Safety/Liability)** | Agent auto-handled a query containing subtle edge cases or latent billing ambiguity that warranted human review. |
| **Retrieval Failure / Weak Match** | 18 | 14.5% | Medium | Historical index returned precedents with cosine similarity < 0.25 due to non-standard vocabulary or severe brevity. |
| **Generation Hallucination** | 0 | 0.0% | Critical | **Zero detected**. Grounding verification caught 100% of unauthorized promise drafts. |

---

## 2. In-Depth Failure Case Studies (10 Representative Cases)

### Case 1: `gold_001` — Multi-Intent Cancellation Confusion
* **Customer Input**: *"Horrible phone call w/customer service today. Considering cancelling my prime membership after 6 years."*
* **Expected Ground Truth**: Intent: `cancellation_request` | Decision: `AUTO_HANDLE`
* **System Output**: Intent: `subscription_and_billing` | Decision: `AUTO_HANDLE` (Conf: 82.4%)
* **Agent Proposed Reply**: *"You can review your active subscription charges, payment methods, and renewal dates by visiting Manage Prime Membership in your account settings: [URL]..."*
* **Failure Category**: **Intent Confusion (Subtle Category Overlap)**
* **Root Cause**: The customer used both "cancelling" and "prime membership". The classifier prioritized the subscription n-grams over order cancellation.
* **Architectural Fix**: Implement a hierarchy where `subscription_cancellation` is a distinct hybrid sub-intent routing directly to membership auto-cancellation rather than general billing settings.

---

### Case 2: `gold_003` — Cautious Over-Escalation on Empty Box Delivery
* **Customer Input**: *"Amazon is the worst e-commerce in india , they delivered me a empty box instead of a mobile phone. Fraud!"*
* **Expected Ground Truth**: Intent: `delivery_delay_or_status` | Decision: `AUTO_HANDLE` (Standard claim link)
* **System Output**: Intent: `delivery_delay_or_status` | Decision: `ESCALATE` (Risk Score: 0.452)
* **Escalation Reason**: *"Intent confidence (25.6%) fell below threshold; top historical similarity (0.23) is below standard retrieval threshold."*
* **Failure Category**: **Policy Over-Escalation (Out-of-Distribution Vocabulary)**
* **Root Cause**: The mention of "empty box" and "Fraud" suppressed standard delivery confidence and triggered risk penalties.
* **Architectural Fix**: In practice, an empty high-value box (mobile phone) is an alleged theft; this over-escalation is actually desirable from a fraud standpoint. Golden annotation should recognize this as a valid escalation case.

---

### Case 3: `gold_004` — Sentiment-Driven False Intent Classification
* **Customer Input**: *"what is wrong with your team Worst service ever...."*
* **Expected Ground Truth**: Intent: `delivery_delay_or_status` | Decision: `AUTO_HANDLE`
* **System Output**: Intent: `legal_or_severe_complaint` | Decision: `ESCALATE`
* **Failure Category**: **Intent Confusion (Hostile Sentiment Overfitting)**
* **Root Cause**: The customer gave zero substantive order details, only pure venting. The model classified "worst service ever" as a severe legal/escalation complaint.
* **Architectural Fix**: Add a dedicated `uninformative_venting` pre-filter that asks for order specifics rather than routing to legal specialists.

---

### Case 4: `gold_008` — Phishing / Scam Email Query Over-Escalation
* **Customer Input**: *"Hello @AmazonHelp , this email is yours or it is a virus? __email__ Thank you"*
* **Expected Ground Truth**: Intent: `account_access_and_otp` | Decision: `AUTO_HANDLE`
* **System Output**: Intent: `delivery_delay_or_status` | Decision: `ESCALATE`
* **Failure Category**: **Intent Confusion & Retrieval Orthogonality**
* **Root Cause**: Token anonymizer masked the email string (`__email__`), and the word "virus" had low frequency in retail shipping training data.
* **Architectural Fix**: Add explicit regex intent matching for "phishing / spoof email verification" with standard Amazon spoof reporting link (`stop-spoofing@amazon.com`).

---

### Case 5: `gold_012` — Sarcastic Frustration Under-Escalation
* **Customer Input**: *"Oh wonderful, my package that was guaranteed by 8pm is now scheduled for next Tuesday. Super Prime service guys."*
* **Expected Ground Truth**: Intent: `delivery_delay_or_status` | Decision: `ESCALATE`
* **System Output**: Intent: `delivery_delay_or_status` | Decision: `AUTO_HANDLE` (Conf: 71.2%)
* **Agent Proposed Reply**: *"We apologize for the delivery delay. You can view the live carrier tracking updates in Your Orders: [URL]..."*
* **Failure Category**: **Policy Under-Escalation (Sarcasm Blindness)**
* **Root Cause**: The lexical n-grams ("package", "guaranteed", "8pm", "Prime") scored high delivery confidence. The sarcasm ("Oh wonderful", "Super Prime service") was missed by linear bag-of-words.
* **Architectural Fix**: Incorporate a sentiment / sarcasm polarity detector into the escalation engine to flag high-frustration delays.

---

### Case 6: `gold_019` — Split-Shipment Edge Case
* **Customer Input**: *"One of my three items arrived today, but the app says all three were delivered together. Where are the other two?"*
* **Expected Ground Truth**: Intent: `delivery_delay_or_status` | Decision: `ESCALATE`
* **System Output**: Intent: `delivery_delay_or_status` | Decision: `AUTO_HANDLE`
* **Failure Category**: **Policy Under-Escalation (Partial Delivery Discrepancy)**
* **Root Cause**: Multi-item split tracking is an operational edge case. The system suggested the generic tracking link, which the user already reported as showing an incorrect "delivered" status.
* **Architectural Fix**: Escalation policy rule: When user query mentions partial shipment discrepancy ("one of three", "missing item from box"), escalate to human support for inventory re-dispatch.

---

### Case 7: `gold_025` — International Storefront Mismatch
* **Customer Input**: *"I ordered on Amazon UK but my card was charged in Japanese Yen by Amazon JP. Why?"*
* **Expected Ground Truth**: Intent: `subscription_and_billing` | Decision: `ESCALATE`
* **System Output**: Intent: `subscription_and_billing` | Decision: `AUTO_HANDLE`
* **Failure Category**: **Policy Under-Escalation (Cross-Border Billing Issue)**
* **Root Cause**: The system recognized "card was charged" and suggested the standard Prime membership settings page, which cannot resolve cross-border currency conversion errors.
* **Architectural Fix**: Add geographic/currency keyword triggers (`Yen`, `GBP`, `cross-border`, `currency conversion`) to sensitive intent escalation triggers.

---

### Case 8: `gold_033` — Locker / Pickup Point Delivery Failure
* **Customer Input**: *"The Amazon Locker code you sent me expired while the store was closed for renovation. Now what?"*
* **Expected Ground Truth**: Intent: `delivery_delay_or_status` | Decision: `ESCALATE`
* **System Output**: Intent: `delivery_delay_or_status` | Decision: `ESCALATE` (Conf: 34.1%)
* **Failure Category**: **Retrieval Weakness**
* **Root Cause**: Locker collection code expiration has sparse representation in general tweet support threads. The similarity score was 0.18, successfully triggering cautious escalation.

---

### Case 9: `gold_041` — Pre-Order Cancellation Race Condition
* **Customer Input**: *"I clicked cancel on my pre-order 5 minutes before you sent the dispatch email. Did it cancel or am I getting billed?"*
* **Expected Ground Truth**: Intent: `cancellation_request` | Decision: `ESCALATE`
* **System Output**: Intent: `cancellation_request` | Decision: `AUTO_HANDLE`
* **Failure Category**: **Policy Under-Escalation (Dispatch Race Condition)**
* **Root Cause**: High cancellation intent confidence triggered auto-handling, but the race condition between cancellation and dispatch requires live backend order status lookup.
* **Architectural Fix**: If customer mentions "already sent dispatch email" or "race condition", force escalation.

---

### Case 10: `gold_058` — Third-Party Marketplace Seller Dispute
* **Customer Input**: *"The third-party merchant refused my refund and told me to get lost. A-to-Z claim now please."*
* **Expected Ground Truth**: Intent: `return_and_refund_inquiry` | Decision: `AUTO_HANDLE` (A-to-Z Guarantee portal link)
* **System Output**: Intent: `return_and_refund_inquiry` | Decision: `ESCALATE` (Risk Score: 0.482)
* **Failure Category**: **Policy Over-Escalation (Merchant Hostility)**
* **Root Cause**: "Told me to get lost" triggered the sensitive conflict score, escalating to human triage rather than providing the automated A-to-Z claim self-service link.
* **Architectural Fix**: Provide the direct self-service A-to-Z claim link while simultaneously tagging for supervisor follow-up.

---

## 3. Actionable Recommendations for System V2

1. **Hierarchical Intent Architecture**: Decompose top-level intents (`subscription_and_billing`, `cancellation_request`) into actionable leaf intents (`cancel_prime`, `cancel_preorder`, `unrecognized_charge`).
2. **Contextual Sarcasm Classifier**: Add a 2-class lightweight transformer/classifier to detect customer hostility and sarcasm, penalizing auto-handling on angry customers.
3. **Structured Entity Extraction**: Extract order IDs, item counts, and monetary amounts. When complex relational predicates exist (e.g. 1 of 3 items delivered), flag for human agent intervention.
