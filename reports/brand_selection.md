# Brand Selection Decision Analysis

**Selected Brand**: **`AmazonHelp`** (Amazon Customer Support)  
**Primary Runner-Up**: **`AppleSupport`** (Apple Support)  

---

## 1. Candidate Comparison Matrix

The candidate selection score evaluates candidate brands across five weighted dimensions (Max 100 points):
1. **Volume & Evidence Density (25%)**: Ample historical resolved interactions for retrieval grounding and golden test curation.
2. **Intent Diversity & Learnability (25%)**: A rich, distinct set of operational support workflows (not just a single recurring complaint).
3. **Resolution Actionability (20%)**: Historical brand replies contain actionable guidance rather than uniform deflection templates.
4. **Risk & Escalation Spectrum (15%)**: Clear operational boundary between low-risk self-service FAQs and high-liability fraud/legal escalations.
5. **Data Completeness & Linguistic Noise (15%)**: High English text quality, minimal spam, and clear customer problem statements.

| Brand | Domain | Tweet Volume | Intent Diversity | Actionability | Risk Spectrum | Data Quality | **Composite Score** |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **AmazonHelp** | E-Commerce / Logistics | **169,840** | **25 / 25** | **20 / 20** | **14 / 15** | **14 / 15** | **98 / 100** (SELECTED) |
| **AppleSupport** | Tech / OS / Hardware | 106,860 | 22 / 25 | 17 / 20 | 13 / 15 | 14 / 15 | **90 / 100** (Runner-Up) |
| **Uber_Support** | Ride Logistics | 56,270 | 18 / 25 | 16 / 20 | 14 / 15 | 12 / 15 | **79 / 100** |
| **Delta** | Airline Passenger Travel | 42,250 | 16 / 25 | 15 / 20 | 12 / 15 | 13 / 15 | **72 / 100** |
| **sprintcare** | Telecom / Carrier | 107,488 | 15 / 25 | 11 / 20 | 12 / 15 | 10 / 15 | **70 / 100** |
| **SpotifyCares** | Digital Streaming | 22,460 | 14 / 25 | 15 / 20 | 10 / 15 | 13 / 15 | **66 / 100** |

---

## 2. Why AmazonHelp Instead of AppleSupport (The Second-Best Candidate)?

While **AppleSupport** is the second-highest volume brand in the dataset (106,860 tweets), **AmazonHelp** was selected due to critical methodological advantages:

1. **Clear, Operationally Distinct Support Workflows**:
   - In `AmazonHelp`, customer inquiries map cleanly to distinct operational actions:
     - Delivery delay $\to$ Carrier tracking link / transit buffer guidance.
     - Damaged item $\to$ Online Returns Center portal / replacement dispatch.
     - Cancellation $\to$ Self-service order modification cutoff window.
     - Subscription billing $\to$ Manage Prime membership portal.
     - Fraud/unauthorized charge $\to$ Mandatory high-priority escalation.
   - In contrast, `AppleSupport` is dominated by device troubleshooting (e.g., iOS 11 battery drain, iPhone reboot loops, Bluetooth pairing) where public responses almost exclusively ask the user to DM their iOS version or schedule a Genius Bar appointment. This provides less diversity of actionable resolution paths.

2. **Grounded Risk-Sensitive Boundary**:
   - In retail support, the safety boundaries are stark and measurable: an automated agent must NEVER promise a financial refund or credit without human authorization.
   - In consumer tech, the line between an automated hardware troubleshooting step and a warranty repair is diffuse, making risk-calibrated escalation harder to evaluate objectively.

3. **High Resolution Precedent in Historical Data**:
   - `AmazonHelp` demonstrates consistent, well-documented guidance linking customer problems directly to verified help endpoints (returns center, order history, digital content management), providing ideal retrieval grounding for an AI agent.

4. **Multi-Turn Thread Quality**:
   - `AmazonHelp` has the highest absolute number of complete multi-turn resolved threads, providing rich end-to-end evidence for our evaluation suite.

---

## 3. Decision Summary

`AmazonHelp` is selected as the production brand benchmark. All subsequent pipeline stages (conversation reconstruction, temporal splitting, intent discovery, golden set annotation, retrieval index, and escalation calibration) are anchored in Amazon customer support data.
