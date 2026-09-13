# Zero-Leakage Data Partition & Temporal Boundary Audit

**Audit Date**: 2026-09-12  
**Dataset**: Twitter Customer Support Benchmark (`twcs.csv`)  
**Target Brand**: `AmazonHelp`  
**Total Resolved Multi-Turn Conversations**: 3,909  

---

## 1. Temporal Boundary Definitions

To guarantee zero data contamination between past training signals and future test conditions, all conversations are partitioned strictly chronologically based on their initiating tweet timestamp:

| Split Partition | Ratio | Conversation Count | Start Timestamp | End Timestamp |
| :--- | :--- | :--- | :--- | :--- |
| **Train** | 70% | 2,736 | 2017-10-10 17:34:03 | 2017-11-19 12:44:11 |
| **Validation** | 15% | 586 | 2017-11-19 12:46:12 | 2017-11-26 14:18:00 |
| **Test (Frozen Evaluation)** | 15% | 587 | 2017-11-26 14:19:15 | 2017-12-03 22:55:54 |

---

## 2. Leakage Verification Checks

Every potential source of train/test contamination was audited via automated assertions:

| Audit Check | Verification Criteria | Status | Details |
| :--- | :--- | :--- | :--- |
| **Chronological Ordering** | `max(train_timestamp) < min(val_timestamp)` | **PASS** | Train max: `2017-11-19 12:44:11` <br>Val min: `2017-11-19 12:46:12` (Gap: +121s) |
| **Validation Ordering** | `max(val_timestamp) < min(test_timestamp)` | **PASS** | Val max: `2017-11-26 14:18:00` <br>Test min: `2017-11-26 14:19:15` (Gap: +75s) |
| **Conversation ID Overlap** | `set(train_ids) ∩ set(test_ids) == ∅` | **PASS** | 0 overlapping conversation IDs across splits. |
| **Tweet ID Overlap** | `set(train_tweet_ids) ∩ set(test_tweet_ids) == ∅` | **PASS** | 0 overlapping tweet IDs across splits. |
| **Thread Split Integrity** | Entire multi-turn threads kept unified | **PASS** | No conversation thread was split across boundaries. |
| **Retrieval Evidence Contamination** | Historical index fitted strictly on Train | **PASS** | 2,735 indexed cases derived 100% from Train partition. Zero test conversations exist in vector store. |

---

## 3. Methodological Significance

Random k-fold cross-validation or random splits in time-series customer support inflate evaluation metrics because models memorize recent seasonal promotions, trending carrier delivery bottlenecks, or recurring complaint keywords. Strict temporal splitting tests the agent's generalization to genuinely unseen future customer interactions.
