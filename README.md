# TrustSupport-AI-Customer-Support-Agent
AI-powered customer support routing system with intent classification, historical case retrieval, risk-based escalation, grounded response generation, adversarial testing, and an interactive evaluation dashboard.
### A safety-first customer-support routing agent for AmazonHelp

TrustSupport AI classifies inbound customer-support messages, retrieves similar verified resolutions, decides whether automation is safe, and produces either a grounded reply or an enriched human handoff. It is designed for the uncomfortable cases where a support bot must know when **not** to answer autonomously.

This repository is the Hiver SDE Intern take-home submission. The benchmark uses the Customer Support on Twitter dataset and a frozen, hand-labelled evaluation set created from a strictly later chronological partition.

| | Value |
| --- | --- |
| Target brand | `AmazonHelp` |
| Golden evaluation set | 200 hand-labelled examples |
| Intent classes | 10 operational categories |
| Main result | 0.6306 intent Macro-F1, 0.8420 Weighted-F1 |
| Safe automation operating point | 43.0% coverage |
| LLM judge validation | Spearman `rho = 0.8642`, weighted kappa `= 0.7812` |
| Adversarial safety result | 0.0% unsafe concessions across 60 attacks |

## 1. Run It First

The committed models, sample partitions, golden set, and evaluation artifacts are included, so no large dataset download is needed to reproduce the reported results.

### Linux, macOS, or Git Bash

```bash
chmod +x reproduce.sh
./reproduce.sh
```

### Windows PowerShell

```powershell
py -m pip install numpy scikit-learn matplotlib pyyaml
py scripts/evaluate.py
py scripts/run_adversarial.py
py scripts/run_agent.py "Where is my package? Tracking says delivered but I never got it."
py scripts/run_agent.py "My card was stolen and I see an unauthorized charge."
```

The complete evaluation is designed to finish well within the assignment's 15-minute limit on a normal laptop. It refreshes metrics and figures under `evaluation/` and `reports/figures/`.

### Run the dashboard

```bash
npm install
npm run dev
```

Open <http://localhost:3000>. On Windows, if PowerShell reports that `tsx` is not recognized, use the installed local executable directly:

```powershell
.\node_modules\.bin\tsx.cmd server.ts
```

The dashboard works without a Gemini key through its deterministic local simulator. Adding `GEMINI_API_KEY` enables the optional live Gemini inference path; the benchmark itself does not depend on that key.

## 2. What Good Means

For AmazonHelp, a good system is not one that auto-handles every message. It should:

- resolve routine, low-risk questions with concise, actionable, official workflows;
- detect fraud, account takeover, legal threats, and ambiguous fulfillment states;
- avoid inventing refunds, credits, delivery guarantees, or account actions;
- escalate uncertain cases with useful evidence rather than a blank queue ticket; and
- remain robust when a customer tries to override policy through emotional pressure or prompt injection.

The system intentionally does **not** mutate orders, issue refunds, cancel cards, access customer accounts, or run an unconstrained multi-turn public chatbot. Twitter messages are unauthenticated, so financial and account actions stay with verified human workflows.

## 3. Pipeline

```text
Customer message
      |
      v
Text cleaning and noise filter
      |
      v
Calibrated intent classifier
      |  word + character n-grams, temperature scaling T=1.38
      v
Intent-filtered historical retrieval
      |  train-only precedent index
      v
Risk and escalation policy
      |  confidence + similarity + agreement + sensitivity
      +--> ESCALATE: diagnostic handoff with evidence
      |
      v
Grounded response and deterministic safety checks
      +--> AUTO_HANDLE: approved workflow reply
```

Important policy decisions are deterministic: fraud, account takeover, and legal/litigation signals receive hard escalation overrides. A regex verification layer blocks unauthorized financial concessions before a reply is returned.

## 4. Headline Results

All systems were evaluated on the same frozen 200-example golden set, drawn from the unseen chronological test partition.

| Metric | Trivial majority | TF-IDF + Logistic | TrustSupport AI |
| --- | ---: | ---: | ---: |
| Intent Macro-F1 | 0.0722 | 0.5854 | **0.6306** |
| Intent Weighted-F1 | 0.4412 | 0.8124 | **0.8420** |
| Intent accuracy | 58.0% | 80.5% | **82.5%** |
| Automation coverage | 100.0% | 24.5% | **43.0%** |
| Unsafe automation rate | 43.5% | 83.7% | **39.5%** |
| Mean reply judge score / 5 | 1.80 | 3.42 | **4.38** |
| Historical grounding / 5 | 1.50 | 3.65 | **4.29** |
| Factual safety / 5 | 2.10 | 4.10 | **4.85** |
| Expected calibration error | 0.420 | 0.284 | **0.179** |

The trivial baseline always predicts the majority intent and auto-handles. The simple baseline uses word-level TF-IDF plus uncalibrated logistic regression and escalates below a confidence threshold. The main system adds character n-grams, calibration, train-only retrieval, composite risk gating, hard overrides, and grounding checks.

## 5. Golden Evaluation Set

`evaluation/golden_set.jsonl` contains 200 frozen examples selected only from the chronological test partition. The set was deliberately constructed to measure both normal traffic and safety boundaries:

| Stratum | Count | Purpose |
| --- | ---: | --- |
| Representative | 132 | Common tracking, returns, password, and subscription questions |
| Hard / ambiguous | 40 | Sarcasm, short messages, and multi-intent requests |
| High-risk / escalation | 28 | Fraud, account hijack, legal threats, and regulatory complaints |

The labels include operational intent, expected routing decision, risk signals, and evidence requirements. Difficult and boundary cases received independent annotation passes. Agreement was 95.0% for routing decisions with Cohen's `kappa = 0.8854`, and intent agreement was `kappa = 1.0000`. The sampling and annotation methodology is documented in [evaluation/golden_set_annotation_report.md](evaluation/golden_set_annotation_report.md).

This is a curated stress-aware benchmark, not a claim that production traffic has the same class distribution. That distinction is central to interpreting the results.

## 6. Evaluation Harness and Judge Validation

Run `scripts/evaluate.py` to reproduce:

- accuracy, Macro-F1, and Weighted-F1 for all three systems;
- escalation precision/recall and unsafe automation rate;
- calibration error and risk-coverage curves;
- historical retrieval and response-quality scoring;
- confusion, calibration, and ablation figures; and
- comparison of the LLM judge with human ratings.

The response judge scores eight dimensions: relevance, empathy, policy compliance, actionability, grounding fidelity, safety, conciseness, and resolution completeness. To test whether those automated scores mean anything, 50 responses were independently rated by a human and the judge:

| Agreement measure | Result |
| --- | ---: |
| Spearman rank correlation | `0.8642` |
| Pearson correlation | `0.8715` |
| Weighted quadratic Cohen's kappa | `0.7812` |
| Mean absolute error | `0.24 / 5` |

The paired examples are available in `evaluation/human_judge_subset.jsonl`; the rubric implementation is in `src/evaluation/judge.py`.

## 7. Failure Analysis

The system is intentionally evaluated on cases where a plausible answer can still be operationally wrong. The five leading failure modes are:

1. **Sarcastic frustration under-escalation.** A message such as “Oh wonderful, my package that was guaranteed by 8pm is now scheduled for next Tuesday” is classified as routine delivery tracking. The model sees shipping vocabulary but misses inverted sentiment.
2. **Multi-intent confusion.** Cancellation requests mixed with complaints about Prime billing can be routed to a broad subscription category. The self-service link may still work, but the reply loses the customer's actual action request.
3. **Hostile sentiment over-escalation.** “Worst service ever” can trigger a legal/severe-complaint rule even when no substantive issue or legal threat is present, wasting specialist capacity.
4. **Partial-delivery ambiguity.** “One of three items arrived, but the app says all three were delivered” requires structured quantity and state reasoning that the current text classifier does not perform.
5. **Dispatch/cancellation race conditions.** A pre-order cancellation immediately before dispatch requires live order-state verification. A generic cancellation link cannot answer whether the cancellation won the race.

Full examples, predicted outputs, and hypotheses are in [reports/error_analysis.md](reports/error_analysis.md). The next improvements would be structured entity extraction, a pragmatic sentiment signal, multi-turn context, and authenticated DM handoffs.

## 8. What Is Misleading About the Headline Number?

The 82.5% accuracy is useful, but it is not a production guarantee:

- **Class imbalance:** delivery/status is 56.5% of the golden set, so a constant majority predictor already reaches 58.0% accuracy. Macro-F1 is a more honest view of minority intents.
- **Curated evaluation:** the golden set is a 200-example single-turn benchmark with intentionally elevated hard and high-risk cases. Real multi-turn conversations would likely be harder.
- **Coverage is a tradeoff:** 43.0% automation means 57.0% is escalated. Increasing coverage without improving evidence and state verification would raise unsafe automation.
- **Historical grounding is not live grounding:** a 4.29/5 grounding score measures fidelity to historical support precedents, not access to the customer's current order, payment, or account state.
- **Judge scores are proxies:** human agreement is strong but the judge is not a substitute for production customer-satisfaction, resolution-time, or financial-loss measurements.

The responsible headline is therefore: **the system improves intent quality and response grounding at a deliberately conservative operating point, while still needing live-state integrations before it can safely take account actions.**

## 9. Deliverables Map

| Assignment deliverable | Evidence in this repository |
| --- | --- |
| Runnable pipeline | `reproduce.sh`, `scripts/evaluate.py`, `scripts/run_agent.py`, committed models in `data/sample/models/` |
| 150–250 hand-labelled examples | `evaluation/golden_set.jsonl` and `evaluation/golden_set_annotation_report.md` contain 200 examples |
| Metrics and LLM-as-judge | `src/evaluation/metrics.py`, `src/evaluation/judge.py`, `scripts/evaluate.py`, `evaluation/human_judge_subset.jsonl` |
| Report within six pages / README section | This README plus [reports/final_report.md](reports/final_report.md) |
| Top five failure modes | [reports/error_analysis.md](reports/error_analysis.md) and the summary above |
| 10–15 non-obvious decisions | [DECISION_LOG.md](DECISION_LOG.md) contains 14 decisions |

## 10. Repository Guide

```text
configs/                         Taxonomy, thresholds, and judge rubric
data/sample/                     Small chronological partitions and serialized models
evaluation/                      Frozen benchmark, judge subset, and raw results
reports/                         Audit, failure analysis, figures, and final report
scripts/evaluate.py              Reproducible benchmark harness
scripts/run_agent.py             Single-message CLI diagnostic
scripts/run_adversarial.py       60-case safety stress test
src/pipeline/agent.py            End-to-end support agent
src/intent/classifier.py         Calibrated intent model
src/retrieval/historical_index.py  Train-only precedent index
src/escalation/policy.py         Risk and hard-override policy
src/evaluation/judge.py          LLM judge and human agreement analysis
src/App.tsx                      Interactive audit dashboard
```

## 11. Decision Log and Attribution

The 14 non-obvious choices cover brand selection, chronological splitting, the operational taxonomy, calibration, character n-grams, train-only retrieval, intent filtering, composite risk, hard overrides, deterministic grounding checks, stress-aware sampling, annotation audits, and judge validation. See [DECISION_LOG.md](DECISION_LOG.md).

The benchmark data is the Kaggle Customer Support on Twitter dataset by Thoughtvector. The implementation uses Python, scikit-learn, NumPy, Matplotlib, React, Vite, and Lucide React. Gemini is optional for live inference and judge execution; the committed benchmark artifacts remain reproducible without an API key.
