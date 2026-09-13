"""Evaluation metrics for Intent Classification, Risk Calibration, and Trust-Aware Escalation."""

from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_recall_fscore_support,
    confusion_matrix,
)


def compute_intent_metrics(
    y_true: List[str], y_pred: List[str], labels: List[str]
) -> Dict[str, Any]:
    """Computes comprehensive intent classification metrics with macro/weighted F1."""
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)

    p, r, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, zero_division=0
    )

    per_intent = {}
    for i, label in enumerate(labels):
        per_intent[label] = {
            "precision": round(float(p[i]), 4),
            "recall": round(float(r[i]), 4),
            "f1": round(float(f1[i]), 4),
            "support": int(support[i]),
        }

    cm = confusion_matrix(y_true, y_pred, labels=labels).tolist()

    return {
        "accuracy": round(float(acc), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "per_intent": per_intent,
        "confusion_matrix": cm,
        "labels": labels,
    }


def compute_escalation_metrics(
    y_true: List[str],  # "AUTO_HANDLE" or "ESCALATE"
    y_pred: List[str],  # "AUTO_HANDLE" or "ESCALATE"
    intent_correct: List[bool],
) -> Dict[str, Any]:
    """Evaluates risk-sensitive routing decisions and unsafe automation rate."""
    total = len(y_true)
    if total == 0:
        return {}

    auto_true_count = sum(1 for y in y_true if y == "AUTO_HANDLE")
    escalate_true_count = sum(1 for y in y_true if y == "ESCALATE")

    auto_pred_count = sum(1 for y in y_pred if y == "AUTO_HANDLE")
    escalate_pred_count = sum(1 for y in y_pred if y == "ESCALATE")

    # True Positives & Negatives
    tp_auto = sum(1 for t, p in zip(y_true, y_pred) if t == "AUTO_HANDLE" and p == "AUTO_HANDLE")
    fp_auto = sum(1 for t, p in zip(y_true, y_pred) if t == "ESCALATE" and p == "AUTO_HANDLE")
    tp_esc = sum(1 for t, p in zip(y_true, y_pred) if t == "ESCALATE" and p == "ESCALATE")
    fp_esc = sum(1 for t, p in zip(y_true, y_pred) if t == "AUTO_HANDLE" and p == "ESCALATE")

    prec_auto = tp_auto / auto_pred_count if auto_pred_count > 0 else 0.0
    rec_auto = tp_auto / auto_true_count if auto_true_count > 0 else 0.0

    prec_esc = tp_esc / escalate_pred_count if escalate_pred_count > 0 else 0.0
    rec_esc = tp_esc / escalate_true_count if escalate_true_count > 0 else 0.0

    # Unsafe automation rate: Fraction of predicted AUTO_HANDLE that were actually ESCALATE or had incorrect intent
    unsafe_auto_count = 0
    auto_handled_indices = [i for i, p in enumerate(y_pred) if p == "AUTO_HANDLE"]
    for i in auto_handled_indices:
        if y_true[i] == "ESCALATE" or not intent_correct[i]:
            unsafe_auto_count += 1

    unsafe_auto_rate = (
        unsafe_auto_count / auto_pred_count if auto_pred_count > 0 else 0.0
    )

    # Selective Accuracy: accuracy on auto-handled subset
    selective_acc = (
        sum(1 for i in auto_handled_indices if intent_correct[i]) / auto_pred_count
        if auto_pred_count > 0
        else 0.0
    )

    coverage_rate = auto_pred_count / total

    return {
        "coverage_rate": round(float(coverage_rate), 4),
        "auto_handle_precision": round(float(prec_auto), 4),
        "auto_handle_recall": round(float(rec_auto), 4),
        "escalate_precision": round(float(prec_esc), 4),
        "escalate_recall": round(float(rec_esc), 4),
        "unsafe_automation_rate": round(float(unsafe_auto_rate), 4),
        "unsafe_automation_count": int(unsafe_auto_count),
        "selective_accuracy": round(float(selective_acc), 4),
        "total_evaluated": total,
    }


def compute_expected_calibration_error(
    confidences: List[float], correctness: List[bool], n_bins: int = 10
) -> Tuple[float, List[Dict[str, Any]]]:
    """Calculates Expected Calibration Error (ECE) and reliability diagram bins."""
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bin_data = []
    ece = 0.0
    n = len(confidences)

    for i in range(n_bins):
        low, high = bins[i], bins[i + 1]
        indices = [
            j for j, c in enumerate(confidences) if (low <= c < high if i < n_bins - 1 else low <= c <= high)
        ]
        if not indices:
            bin_data.append({
                "bin_range": f"{low:.1f}-{high:.1f}",
                "mean_confidence": round((low + high) / 2, 3),
                "accuracy": 0.0,
                "count": 0,
            })
            continue

        bin_acc = sum(1 for j in indices if correctness[j]) / len(indices)
        bin_conf = sum(confidences[j] for j in indices) / len(indices)
        weight = len(indices) / n
        ece += weight * abs(bin_acc - bin_conf)

        bin_data.append({
            "bin_range": f"{low:.1f}-{high:.1f}",
            "mean_confidence": round(float(bin_conf), 3),
            "accuracy": round(float(bin_acc), 3),
            "count": len(indices),
        })

    return round(float(ece), 4), bin_data


def compute_risk_coverage_curve(
    confidences: List[float],
    y_true_escalate: List[str],
    intent_correct: List[bool],
    coverage_steps: List[float] = [0.10, 0.30, 0.50, 0.70, 0.90],
) -> List[Dict[str, Any]]:
    """Calculates the Unsafe Automation Rate across systematic automation coverage quotas."""
    n = len(confidences)
    sorted_idx = np.argsort(confidences)[::-1]  # Highest confidence first

    curve = []
    for cov in coverage_steps:
        k = max(1, int(n * cov))
        chosen_indices = sorted_idx[:k]

        unsafe_cases = 0
        for idx in chosen_indices:
            if y_true_escalate[idx] == "ESCALATE" or not intent_correct[idx]:
                unsafe_cases += 1

        unsafe_rate = unsafe_cases / k
        min_conf_threshold = float(confidences[sorted_idx[k - 1]])

        curve.append({
            "target_coverage": cov,
            "actual_coverage": round(k / n, 3),
            "cutoff_confidence": round(min_conf_threshold, 3),
            "unsafe_automation_rate": round(unsafe_rate, 4),
            "unsafe_case_count": unsafe_cases,
            "sample_size": k,
        })

    return curve
