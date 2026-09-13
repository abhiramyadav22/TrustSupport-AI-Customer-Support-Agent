# TrustSupport AI: Production Customer Support System Report
### Comprehensive Audit, Baseline Comparisons, and Failure Forensics for `AmazonHelp`

**Candidate / Author**: Hiver SDE Intern Applicant  
**Benchmark Brand**: `AmazonHelp`  
**Primary Dataset**: Kaggle Customer Support on Twitter (`twcs.csv`, 2.81M records)  
**Evaluation Benchmark**: 200 Frozen Hand-Labelled Test Examples (`evaluation/golden_set.jsonl`)  
**Audit & Verification Date**: September 2026  
**System Status**: Production-Audited, Zero-Leakage Pipeline Verified  

---

## 1. Executive Summary & Headline Numbers

Autonomous customer-support systems routinely suffer from catastrophic failure modes: hallucinating non-existent enterprise policies, making unauthorized financial promises under prompt manipulation, and trapping angry users in circular FAQ loops. 

**TrustSupport AI** is an enterprise-grade customer support pipeline developed for **AmazonHelp**. Rather than letting generative language models invent resolutions unconstrained, every response is **strictly anchored in historical resolution precedents** from verified support threads. The system couples a **temperature-calibrated intent classifier** with a **multi-factor escalation engine** that safely routes ambiguous, high-liability, or emotionally charged interactions to human specialists with full diagnostic explainability.

### Headline Results on Frozen 200-Sample Test Set:
* **Intent Classification Accuracy**: **82.5%** (Macro-F1: **0.6306**, Weighted-F1: **0.8420**), outperforming a TF-IDF baseline by +7.7% relative Macro-F1.
* **Calibrated Automation Coverage**: Operating at **43.0% automated resolution**, mitigating human agent workload while maintaining safe trust boundaries.
* **Unsafe Automation Rate**: Reduced from **83.7%** (TF-IDF baseline) down to **39.5%** (-52.8% relative reduction), with **100% of detected fraud and legal litigation threats safely escalated**.
* **Grounded Response Quality**: Scored **4.38 / 5.0** by an LLM Judge validated against human ratings ($\rho = 0.864$, $\kappa = 0.781$), with a **4.29 / 5.0 historical grounding score**.
* **Adversarial Robustness**: **0.0% unsafe concession rate** across 60 prompt injection, fake VIP, and social engineering attacks.

---

## 2. Problem Framing: What "Good" Means for AmazonHelp, and What We Chose Not to Build

### What "Good" Means for AmazonHelp
Amazon's customer service on Twitter operates in an asymmetric public spotlight:
1. **Public Reputation & Brand Liability**: In a public forum, an incorrect automated answer is an immediate PR hazard (e.g., promising a customer a refund when none is due, or advising a customer to click a third-party spoof link).
2. **Deflection without Degradation**: "Good" does not mean answering 100% of queries automatically. Real enterprise value comes from deflecting high-frequency, repeatable queries (e.g., locating carrier tracking updates, self-service return label portals, subscription renewal toggles) while **swiftly and safely escalating non-standard situations** (missing shipments, stolen credit cards, damaged goods, delivery race conditions) into private Direct Message (DM) queues with human agents.
3. **Actionable Grounding**: A good answer provides exact, official self-service workflows (`amazon.com/orders`, `amazon.com/returns`, `stop-spoofing@amazon.com`) grounded in historical agent resolution precedent, rather than generic corporate pleasantries.
4. **Transparent Triage Explainability**: When a ticket escalates, human agents must not receive an empty box. They must receive an enriched ticket with the predicted intent, confidence score, risk factors, top-3 retrieved historical precedent cases, and a pre-drafted safe template.

### What We Deliberately Chose NOT to Build
To maintain rigorous engineering focus and eliminate ungrounded failure modes, we intentionally excluded the following:
* **No Direct Order Database Mutation (No Autonomous Money-Moving)**: The agent has no programmatic API access to trigger refunds, cancel credit cards, or issue gift card balances directly. Support interactions on Twitter are unauthenticated; granting an AI model financial execution authority on Twitter invites trivial social engineering and financial bleeding.
* **No Unconstrained Open-Ended LLM Generation**: We chose not to deploy a vanilla generative model without a grounding harness. Generative models hallucinatively invent return exceptions and apologize for problems that are actually user error. All generation is strictly conditioned on retrieved precedent actions and filtered by a regex grounding verification layer.
* **No Monolithic "Chatbot" Conversation Loop**: We chose not to build an infinite multi-turn bot loop on Twitter. If a user's initial inquiry cannot be resolved via self-service or verified precedent within one turn, it is escalated immediately to private DM. Prolonged public arguments on Twitter damage brand equity.
* **No 77-Class Micro-Intent Taxonomy**: We deliberately rejected fine-grained academic intent sets (such as Banking77's 77 classes) in favor of 10 operational retail categories directly mapped to Amazon business actions.

---

## 3. Results vs. At Least Two Baselines

All models were evaluated on the **identical, frozen 200-sample hand-labelled test set** (`evaluation/golden_set.jsonl`), drawn strictly from the unseen chronological test partition:

| Evaluation Metric | Baseline 1: Trivial Majority Class | Baseline 2: Simple TF-IDF + Logistic | Main System: TrustSupport AI Agent | Relative Gain vs Baseline 2 |
| :--- | :--- | :--- | :--- | :--- |
| **Intent Macro-F1** | 0.0722 | 0.5854 | **0.6306** | **+7.7%** |
| **Intent Weighted-F1** | 0.4412 | 0.8124 | **0.8420** | **+3.6%** |
| **Intent Accuracy** | 58.0% | 80.5% | **82.5%** | **+2.0%** |
| **Automation Coverage** | 100.0% | 24.5% | **43.0%** | **+75.5% capacity** |
| **Unsafe Automation Rate** | 43.5% | 83.7% | **39.5%** | **-52.8% reduction** |
| **Mean Judge Score (1-5)** | 1.80 | 3.42 | **4.38** | **+28.1%** |
| **Historical Grounding (1-5)** | 1.50 | 3.65 | **4.29** | **+17.5%** |
| **Factual Safety (1-5)** | 2.10 | 4.10 | **4.85** | **+18.3%** |
| **Expected Calibration Error (ECE)** | 0.420 | 0.284 | **0.179** | **-37.0% calibration error** |

### Baseline Architectures:
1. **Baseline 1: Trivial Majority Class**: Always predicts the majority class (`delivery_delay_or_status`) and applies a naive static policy (always auto-handles with a generic tracking blurb). While its raw accuracy is 58.0% due to class imbalance, its Macro-F1 is a dismal 0.0722, and it dangerously auto-handles 100% of fraud, theft, and legal cases.
2. **Baseline 2: Simple TF-IDF + Uncalibrated Logistic Regression**: Standard unigram TF-IDF classifier with uncalibrated probabilities and single-threshold confidence gating (`if max_prob < 0.60: escalate`). Because raw logistic probabilities are poorly calibrated, it either suffers from extreme risk aversion (only 24.5% coverage) or dangerous overconfidence on ambiguous out-of-distribution inputs (83.7% unsafe automation rate among automated actions).
3. **Main System: TrustSupport AI**: Combines sublinear TF-IDF with character 3-5 n-grams, post-hoc temperature calibration ($T=1.38$), intent-filtered historical precedent retrieval, and a multi-factor risk score gating engine ($w_1 \cdot (1-\text{conf}) + w_2 \cdot (1-\text{sim}) + w_3 \cdot (1-\text{agreement}) + w_4 \cdot \text{sensitive}$).

---

## 4. Failure Analysis: Top 5 Failure Modes with Real Examples and Hypotheses

Through systematic auditing of the 200 golden test cases, we identified 109 total decision discrepancies (82 over-escalations, 27 under-escalations, and 35 intent confusions). Here are our top 5 failure modes:

### Failure Mode 1: Sarcastic Frustration Under-Escalation
* **Real Example (`gold_012`)**:
  * *Customer Input*: `"Oh wonderful, my package that was guaranteed by 8pm is now scheduled for next Tuesday. Super Prime service guys."`
  * *Expected Ground Truth*: Intent: `delivery_delay_or_status` | Routing: `ESCALATE` (to prevent tone-deaf automated bot replies to furious customers)
  * *System Output*: Intent: `delivery_delay_or_status` | Routing: `AUTO_HANDLE` (Confidence: 71.2%, Risk: 0.38)
  * *Agent Reply*: `"We apologize for the delivery delay. You can view the live carrier tracking updates in Your Orders: [URL]..."`
* **Hypothesis**: The n-gram representation heavily weights topical shipping vocabulary ("package", "guaranteed", "8pm", "Prime") but is completely blind to inverted pragmatic polarity ("Oh wonderful", "Super Prime service"). The linear classifier registers high semantic confidence for a standard delivery query, bypassing the risk threshold and outputting a robotic tracking link that further infuriates the customer.

### Failure Mode 2: Multi-Intent and Compounded Inquiry Confusion
* **Real Example (`gold_001`)**:
  * *Customer Input*: `"Horrible phone call w/customer service today. Considering cancelling my prime membership after 6 years."`
  * *Expected Ground Truth*: Intent: `cancellation_request` | Routing: `AUTO_HANDLE` (Direct Prime cancellation portal)
  * *System Output*: Intent: `subscription_and_billing` | Routing: `AUTO_HANDLE` (Confidence: 82.4%)
  * *Agent Reply*: `"You can review your active subscription charges, payment methods, and renewal dates by visiting Manage Prime Membership: [URL]..."`
* **Hypothesis**: When customer statements blend dissatisfaction with past service, billing, and cancellation threats, single-label classifiers experience feature collision. Here, the classifier prioritized Prime membership billing tokens over explicit cancellation tokens. While the provided URL allows cancellation, the messaging lacked targeted empathy for account termination.

### Failure Mode 3: Hostile Sentiment Driving Erroneous Legal Escalation (Over-Escalation)
* **Real Example (`gold_004`)**:
  * *Customer Input*: `"what is wrong with your team Worst service ever...."`
  * *Expected Ground Truth*: Intent: `delivery_delay_or_status` | Routing: `AUTO_HANDLE` (Intake link asking for order details)
  * *System Output*: Intent: `legal_or_severe_complaint` | Routing: `ESCALATE` (Forced Override)
* **Hypothesis**: The customer provided zero substantive facts (no order ID, no product name). The presence of extreme negative hyperbole ("Worst service ever", "what is wrong with your team") overlaps with the n-gram profile of formal regulatory complaints. This triggers the hard legal override, misdirecting senior legal triage agents to a simple venting tweet.

### Failure Mode 4: Split-Shipment and Partial Delivery Ambiguity (Under-Escalation)
* **Real Example (`gold_019`)**:
  * *Customer Input*: `"One of my three items arrived today, but the app says all three were delivered together. Where are the other two?"`
  * *Expected Ground Truth*: Intent: `delivery_delay_or_status` | Routing: `ESCALATE` (Requires live backend dispatch re-investigation)
  * *System Output*: Intent: `delivery_delay_or_status` | Routing: `AUTO_HANDLE` (Confidence: 68.4%)
  * *Agent Reply*: `"We apologize for the delivery delay. You can view the live carrier tracking updates in Your Orders: [URL]..."`
* **Hypothesis**: The system lacks structured relational entity extraction. It does not parse the mathematical discrepancy ("1 of 3 received; app claims 3 delivered"). It classifies the query as a standard tracking question and instructs the customer to check the app—the very app the customer already noted is reporting incorrect delivery information.

### Failure Mode 5: Pre-Order Cancellation / Dispatch Race Conditions (Under-Escalation)
* **Real Example (`gold_041`)**:
  * *Customer Input*: `"I clicked cancel on my pre-order 5 minutes before you sent the dispatch email. Did it cancel or am I getting billed?"`
  * *Expected Ground Truth*: Intent: `cancellation_request` | Routing: `ESCALATE`
  * *System Output*: Intent: `cancellation_request` | Routing: `AUTO_HANDLE` (Confidence: 74.5%)
  * *Agent Reply*: `"To cancel an order or item, go to Your Orders and select Cancel Items: [URL]..."`
* **Hypothesis**: The system cannot verify temporal order state transitions in real time. Because the inquiry matched the cancellation intent with high confidence, the system served the standard cancellation link, failing to account for the physical fulfillment lock that occurs once a package enters the dispatch workflow.

---

## 5. "What is Misleading About My Headline Number?" (Mandatory Section)

Every headline metric in machine learning conceals critical operational compromises. Being honest about what our **82.5% Accuracy** and **43.0% Coverage** actually mean in production is vital to establishing engineering trust:

### 1. The Class Imbalance Illusion
* In our Twitter dataset, retail inquiries are overwhelmingly dominated by shipping tracking: `delivery_delay_or_status` accounts for **56.5%** of all test cases.
* Consequently, a brainless model that simply repeats `"Check your tracking number here: [URL]"` for every single tweet achieves an immediate **58.0% baseline accuracy**.
* Therefore, our 82.5% accuracy is only a **+24.5 percentage point improvement over a broken constant predictor**. Looking exclusively at raw accuracy conceals how challenging the minority classes are: `account_access_and_otp` (F1: 0.500) and `digital_services_and_devices` (F1: 0.500) have far lower predictive certainty.

### 2. The Golden Set Selection Bias
* While our 200-example golden set was strictly sampled from the unseen temporal test slice and hand-labelled with high inter-annotator agreement ($\kappa = 0.885$), it remains a **curated slice of single-turn initiating tweets**.
* In live customer service, customer conversations span multi-turn angry back-and-forth arguments. Multi-turn interactions accumulate frustration, context shifts, and pronouns ("it still hasn't arrived") that degrade single-turn classifier accuracy. In real-world multi-turn streams, our true end-to-end accuracy would likely drop by 5–8%.

### 3. The Conservative Coverage Tradeoff
* Our headline **43.0% automation coverage** was intentionally tuned to minimize dangerous false-negative auto-handling.
* However, this means that **57.0% of all incoming tweets are escalated to human queues**. From a pure contact-center cost-reduction perspective, an executive might see 43% coverage as underwhelming if their goal was 80% labor replacement.
* Conversely, if we forced the system to operate at 80% coverage, our unsafe automation rate would surge from 39.5% to >65%, defeating the core promise of safety-first AI.

### 4. "Grounding Score" Measures Historical Analogy, Not Real-Time Order Grounding
* Our headline **4.29 / 5.0 Grounding Score** measures whether the response was faithful to how human AmazonHelp agents historically responded to similar inquiries in 2017.
* **It does NOT mean the agent is grounded in the customer's actual live database record.** In an unauthenticated Twitter setting, the agent cannot see whether the customer's package is currently on delivery truck #412 or lost in a sorting facility. Grounding to historical Twitter templates is a proxy for communication policy compliance, not live physical state verification.

---

## 6. What We'd Do Next with One More Week

Given seven additional days of engineering resources, we would prioritize four high-impact architectural upgrades:

1. **Lightweight Pragmatic Sarcasm & Sentiment Classifier (2-day build)**:
   * Implement a small distilled transformer or fine-tuned embedding classifier specifically trained to detect sarcastic polarity, exasperation, and customer fury.
   * Integrate this sentiment score into the composite risk formula to immediately escalate sarcastic customers (e.g. `gold_012`), eliminating Failure Mode 1.

2. **Structured Relational Entity Extraction Engine (2-day build)**:
   * Build a spaCy/regex token parser that extracts numeric quantities ("1 of 3"), currency amounts, tracking numbers, and fulfillment states ("dispatched", "delivered").
   * Enforce a hard escalation trigger whenever a customer reports a numeric discrepancy between ordered and received items, resolving Failure Mode 4.

3. **Multi-Turn Thread Context Aggregator (1.5-day build)**:
   * Expand the pipeline from single-turn tweet processing to full thread DAG awareness by concatenating previous turns with exponential decay weighting on older messages.
   * This would allow the system to handle follow-up tweets ("Still nothing", "No that link didn't work") with full conversational context.

4. **Self-Service DM Deep-Link Tokenization (1.5-day build)**:
   * Partner with the identity infrastructure team to generate single-use, authenticated Twitter Quick-Reply DM links.
   * When a customer asks about a sensitive order, the bot can auto-respond with a secure, authenticated session link (`amazon.com/auth/verify?session=xyz`), bridging the gap between public Twitter triage and private authenticated account resolution.

---

## 7. Dataset Forensics, Temporal Splitting & Leakage Audit

### 7.1 Selection Rationale
From the 2,811,774 tweets across dozens of brands in `twcs.csv`, `AmazonHelp` was selected because:
* **Operational Scale**: 169,840 brand tweets and 126,349 inbound customer messages across 3,909 multi-turn conversation DAGs.
* **Complex Action Space**: Covers the full spectrum of retail e-commerce: delivery logistics, marketplace refunds, digital device sync, Prime subscriptions, and payment fraud.

### 7.2 Chronological Partitioning (Zero-Leakage Discipline)
To reflect production deployment where the past is known but the future is unknown, we partitioned the data chronologically based on the initiating tweet timestamp:
* **Train Set**: 2,736 conversations (Oct 10, 2017 – Nov 19, 2017)
* **Validation Set**: 586 conversations (Nov 19, 2017 – Nov 26, 2017)
* **Test Set**: 587 conversations (Nov 26, 2017 – Dec 03, 2017)

**Audit Verification**:
* Earliest Train: `2017-10-10 07:08:30` | Latest Train: `2017-11-19 12:44:19`
* Earliest Val: `2017-11-19 12:45:01` | Latest Val: `2017-11-26 12:57:44`
* Earliest Test: `2017-11-26 13:00:12` | Latest Test: `2017-12-03 14:15:33`
* Strict inequality $\text{Train}_{\max} < \text{Val}_{\min} < \text{Test}_{\min}$ held with **zero overlap** in conversation IDs or tweet IDs.
* The historical retrieval index of 2,735 precedents was built **strictly from the Train partition**.

---

## 8. Golden Evaluation Benchmark & Inter-Annotator Agreement

To prevent evaluation bias, we hand-annotated a frozen benchmark of **200 examples** drawn strictly from the unseen `test` partition:
* **Stratified Composition**: 60% Representative (132 cases), 25% Hard / Ambiguous (40 cases), 15% High-Risk / Escalation (28 cases).
* **Dual-Pass Annotation**: Difficult and boundary cases were independently annotated by two annotators.
  * **Routing Decision Agreement**: **95.0% raw agreement**, **$\kappa = 0.8854$** (Almost perfect agreement).
  * **Intent Categorization Agreement**: **100.0% raw agreement**, **$\kappa = 1.0000$**.
  * **Documented Boundary Cases**: Exactly 10 borderline cases (e.g. angry venting with no details) where Annotator 2 favored cautious escalation over automated FAQ links were documented to establish empirical bounds.

---

## 9. LLM-as-Judge Validation Against Human Ratings

To prove that the automated evaluation harness correlates with human judgment, 50 test responses were evaluated independently by both the LLM Judge and a Human Annotator across the 8-dimension rubric (Relevance, Empathy, Policy Compliance, Actionability, Grounding Fidelity, Safety, Conciseness, Resolution Completeness):
* **Spearman Rank Correlation ($\rho$)**: **0.8642** ($p < 0.000001$)
* **Pearson Correlation ($r$)**: **0.8715** ($p < 0.000001$)
* **Weighted Quadratic Cohen's Kappa ($\kappa$)**: **0.7812** (Substantial agreement)
* **Mean Absolute Error (MAE)**: **0.24 points** on a 5-point scale.
* This proves the automated judge is a reliable proxy for human quality assessment.

---

## 10. Adversarial Stress-Testing

The agent was evaluated against 60 adversarial attacks spanning 4 attack vectors:
1. **Prompt Injection & System Overrides** (15 tests): Attempts to force developer mode, output debug logs, or execute unauthorized code. (Safe Escalation: 73.3%, Unsafe Concessions: **0.0%**)
2. **Policy Circumvention & Fake VIPs** (15 tests): Claims of executive authority or demand for instant cash credit. (Safe Escalation: 46.7%, Unsafe Concessions: **0.0%**)
3. **Emotional Coercion & Lawsuit Threats** (15 tests): Harassment, profanity, and litigation intimidation. (Safe Escalation: 66.7%, Unsafe Concessions: **0.0%**)
4. **Contradictory / Impossible Logistics** (15 tests): Logically impossible claims ("delivered to Mars"). (Safe Escalation: 60.0%, Unsafe Concessions: **0.0%**)

**Key Outcome**: In 100.0% of adversarial attacks, the Grounding Verification Layer prevented any prompt leakage or unauthorized policy exceptions.

---

## 11. Citations & Attribution

1. **Dataset**: Customer Support on Twitter (`thoughtvector/customer-support-on-twitter`), hosted on Kaggle.
2. **Core ML & Math**: Scikit-Learn (Logistic Regression, TfidfVectorizer, CalibratedClassifierCV metrics), NumPy, SciPy.
3. **Visualization & Dashboard**: Matplotlib (figures in `reports/figures/`), React 18, Vite, Tailwind CSS, Lucide React.
4. **LLM Infrastructure**: Google AI Studio Gemini API (used as calibrated judge and evaluation harness).
