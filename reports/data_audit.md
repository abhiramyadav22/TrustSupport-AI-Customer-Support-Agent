# Dataset Forensics & Data Quality Audit Report

**Dataset**: `Customer Support on Twitter (Kaggle / thoughtvector)`  
**Audit Timestamp**: 2026-09-12  
**Total Analyzed Rows**: 2,811,774  

---

## 1. Executive Summary & Macro Distributions

The dataset represents customer support interactions on Twitter across major global brands. The conversation topology is characterized by customer issue initiation (`inbound = True`), followed by brand support responses (`inbound = False`), and optional follow-up resolution turns.

| Metric | Measured Value | Percentage |
| :--- | :--- | :--- |
| **Total Tweets** | 2,811,774 | 100.0% |
| **Customer Initiations (Inbound)** | 1,537,843 | 54.69% |
| **Brand Support Agent Replies (Outbound)** | 1,273,931 | 45.31% |
| **Earliest Recorded Message** | 2014-12-18 17:55:24 | - |
| **Latest Recorded Message** | 2017-12-03 22:55:54 | - |

---

## 2. Text Length & Distribution Diagnostics

Twitter character limits directly shape communication dynamics:
- Customer messages are concise, averaging **111.1 characters** (median 109.0), with 90% of messages under 179.0 characters.
- Brand support replies average **120.0 characters** (median 120.0), exhibiting greater uniformity due to macro templates, empathy framing, and standardized sign-offs (e.g., agent initials `-AB`, `^MK`).

---

## 3. Data Integrity & Missing Values Analysis

| Column | Missing Count | Missing % | Risk Assessment |
| :--- | :--- | :--- | :--- |
| `tweet_id` | 0 | 0.0% | Primary key intact across all rows. |
| `author_id` | 0 | 0.0% | Allows deterministic separation of customer vs brand. |
| `inbound` | 0 | 0.0% | Ground truth directionality verified. |
| `created_at` | 0 | 0.0% | Enables strict temporal splitting without forward leakage. |
| `text` | 0 | 0.0% | No empty text payloads. |
| `in_response_to_tweet_id` | 794,335 | 28.3% | Expected: indicates thread initiation (root customer tweets). |
| `response_tweet_id` | 1,040,629 | 37.0% | Missing when conversation terminates (final resolution turn). |

---

## 4. Top 15 Brand Volumes

```
AmazonHelp          :  169,840 tweets
AppleSupport        :  106,860 tweets
Uber_Support        :   56,270 tweets
SpotifyCares        :   43,265 tweets
Delta               :   42,253 tweets
Tesco               :   38,573 tweets
AmericanAir         :   36,764 tweets
TMobileHelp         :   34,317 tweets
comcastcares        :   33,031 tweets
British_Airways     :   29,361 tweets
SouthwestAir        :   28,977 tweets
VirginTrains        :   27,817 tweets
Ask_Spectrum        :   25,860 tweets
XboxSupport         :   24,557 tweets
sprintcare          :   22,381 tweets
```

---

## 5. Thread Reconstruction Feasibility & Pathological Cases

1. **Orphaned Replies**: ~4.2% of replies cite an `in_response_to_tweet_id` outside the captured temporal window or deleted tweets. These are safely pruned during thread reconstruction.
2. **Branching Conversations**: Multiple agents or duplicate customer follow-ups create DAG structures rather than linear lists. The reconstructor follows primary customer-brand interaction paths chronologically.
3. **Private Channel Transitions**: In customer support, sensitive actions (order lookups, account credentials) are transitioned to Direct Messages (DM). Grounding must distinguish between public self-service resolutions and mandatory DM handoffs.
