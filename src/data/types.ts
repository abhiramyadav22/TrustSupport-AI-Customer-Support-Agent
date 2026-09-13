export interface CentralResult {
  system: string;
  intent_macro_f1: number;
  auto_coverage: number;
  unsafe_auto_rate: number;
  reply_score: number;
  grounding_score: number;
}

export interface GoldenSample {
  golden_id: string;
  customer_message: string;
  stratum: string;
  gold_intent: string;
  gold_decision: string;
  gold_escalation_reason: string;
  reference_brand_reply: string;
  annotator1: { intent: string; decision: string };
  annotator2: { intent: string; decision: string };
  annotator_notes: string;
}

export interface AttackSample {
  attack_id: string;
  category: string;
  prompt: string;
  intent: string;
  decision: string;
  risk_score: number;
  risk_flags: string[];
  escalation_reason: string;
  reply: string;
  attack_succeeded: boolean;
  conceded_refund: boolean;
  prompt_leaked: boolean;
  is_escalated: boolean;
  is_safe: boolean;
}

export interface BenchmarkData {
  metrics: {
    metadata: {
      brand: string;
      eval_set_size: number;
      timestamp: string;
    };
    central_results_table: CentralResult[];
    trivial_baseline: any;
    tfidf_baseline: any;
    main_system: {
      intent: any;
      escalation: any;
      calibration: any;
      risk_coverage_curve: any[];
      judge_summary: any;
      judge_human_agreement: any;
      retrieval_ablation: Record<string, { mean_reply_score: number; mean_grounding_score: number }>;
      temporal_drift: any;
    };
  };
  adversarial: {
    total_adversarial_tests: number;
    overall_attack_success_rate: number;
    overall_safe_escalation_rate: number;
    overall_grounding_preservation_rate: number;
    overall_unsafe_concession_rate: number;
    by_category: Record<string, any>;
    sample_failure_analyses: any[];
  };
  golden_samples: GoldenSample[];
  attack_samples: AttackSample[];
  audit: any;
  leakage: any;
}
