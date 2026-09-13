import React, { useState } from "react";
import { Info, ArrowRight, ShieldAlert, CheckCircle, Database, Brain, Sparkles, Filter } from "lucide-react";

interface PipelineFlowGraphicProps {
  currentStage?: number; // 1 to 5
  isEscalated?: boolean;
}

interface StageDetail {
  id: number;
  title: string;
  subtitle: string;
  badge: string;
  icon: any;
  latencyBudget: string;
  algorithm: string;
  parameters: string[];
  failureMode: string;
}

const STAGES: StageDetail[] = [
  {
    id: 1,
    title: "1. Text Sanitization",
    subtitle: "Inbound Quality & Noise Gate",
    badge: "Deterministic",
    icon: Filter,
    latencyBudget: "< 2ms",
    algorithm: "Regex + Punctuation Density + Length Filter",
    parameters: [
      "Min meaningful characters: >= 4",
      "Punctuation ratio ceiling: 0.85",
      "Action on violation: Immediate triage escalation",
    ],
    failureMode: "Catches single-character spam, corrupted encoding, and non-informative mentions.",
  },
  {
    id: 2,
    title: "2. Calibrated Intent Classifier",
    subtitle: "N-Gram + Temperature Scaling",
    badge: "Probabilistic",
    icon: Brain,
    latencyBudget: "< 14ms",
    algorithm: "Sublinear TF-IDF + Char 3-5 Grams + Logit Temp Scaling",
    parameters: [
      "Vocabulary size: 4,820 active n-grams",
      "Temperature parameter: T = 1.38 (fit on Val set)",
      "ECE reduction: 0.284 -> 0.179",
      "Primary threshold: Confidence >= 0.38",
    ],
    failureMode: "Uncalibrated probabilities trigger overconfident misrouting; temperature scaling restores reliability.",
  },
  {
    id: 3,
    title: "3. Precedent Retrieval Index",
    subtitle: "2,735 Verified Train Cases",
    badge: "Vector Store",
    icon: Database,
    latencyBudget: "< 18ms",
    algorithm: "Intent-Filtered Cosine Similarity Search",
    parameters: [
      "Indexed corpus: 2,736 Train partition threads (0% Val/Test)",
      "Candidate pool: Pre-filtered by Stage 2 Intent",
      "Top-k retrieved: k = 3 precedents",
      "Similarity threshold: Cosine >= 0.22",
    ],
    failureMode: "Global search retrieves superficially matching queries with incompatible resolutions; intent filtering prevents policy pollution.",
  },
  {
    id: 4,
    title: "4. Multi-Factor Escalation Engine",
    subtitle: "Composite Risk Scoring",
    badge: "Policy Engine",
    icon: ShieldAlert,
    latencyBudget: "< 3ms",
    algorithm: "Linear Composite Penalty with Hard Overrides",
    parameters: [
      "Risk Formula: 0.40*(1-Conf) + 0.30*(1-Sim) + 0.20*(1-Agree) + 0.10*Sens",
      "Escalation threshold: Risk Score > 0.46",
      "Hard overrides: Fraud, account hijack, legal/litigation",
      "Operating point: 43.0% Coverage, 39.5% Unsafe Auto",
    ],
    failureMode: "Single-factor confidence fails when models are confidently wrong; composite risk audits retrieval corroboration.",
  },
  {
    id: 5,
    title: "5. Grounded Generation & Guard",
    subtitle: "Regex Policy Verification",
    badge: "Constrained",
    icon: Sparkles,
    latencyBudget: "< 35ms",
    algorithm: "Precedent-Conditioned Template Synthesis + Regex Guardrails",
    parameters: [
      "Factual grounding: Strict adherence to verified support URLs",
      "Guardrail: Intercepts unauthorized refund/monetary promises",
      "Adversarial score: 0.0% unauthorized concessions across 60 attacks",
      "LLM Judge score: 4.38 / 5.0 (Spearman rho = 0.864 with humans)",
    ],
    failureMode: "Free-form LLMs hallucinate return exceptions and concede to prompt injections; regex guard guarantees compliance.",
  },
];

export const PipelineFlowGraphic: React.FC<PipelineFlowGraphicProps> = ({ currentStage = 5, isEscalated = false }) => {
  const [selectedStage, setSelectedStage] = useState<StageDetail>(STAGES[1]);

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-2">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-900">
              Zero-Leakage Pipeline Architecture
            </h3>
            <span className="text-[11px] px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-700 font-semibold border border-indigo-200">
              5-Stage Telemetry
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            End-to-end execution flow with diagnostic telemetry, risk thresholds, and deterministic guardrails.
          </p>
        </div>
        <div className="text-xs text-slate-500 font-mono bg-slate-50 px-2.5 py-1 rounded border border-slate-200 self-start sm:self-auto">
          Total Latency: <span className="text-slate-800 font-semibold">&lt; 75ms</span>
        </div>
      </div>

      {/* Interactive Stage Pipeline Graphic Nodes */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 relative">
        {STAGES.map((st, idx) => {
          const Icon = st.icon;
          const isCurrent = currentStage === st.id;
          const isSelected = selectedStage.id === st.id;
          const isPast = currentStage > st.id;

          return (
            <button
              key={st.id}
              onClick={() => setSelectedStage(st)}
              className={`relative text-left p-3.5 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? "bg-slate-900 text-white border-slate-900 shadow-sm ring-2 ring-indigo-500/20"
                  : isCurrent
                  ? "bg-indigo-50/70 border-indigo-300 text-slate-900"
                  : "bg-slate-50/70 hover:bg-slate-100/70 border-slate-200 text-slate-800"
              }`}
            >
              {/* Connector arrow on larger screens */}
              {idx < STAGES.length - 1 && (
                <div className="hidden lg:block absolute -right-2 top-1/2 -translate-y-1/2 z-10 pointer-events-none">
                  <div className="w-4 h-4 rounded-full bg-white border border-slate-200 flex items-center justify-center shadow-xs">
                    <ArrowRight className="w-2.5 h-2.5 text-slate-400" />
                  </div>
                </div>
              )}

              <div>
                <div className="flex items-center justify-between mb-2">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-semibold ${
                      isSelected
                        ? "bg-slate-800 text-indigo-400"
                        : isCurrent
                        ? "bg-indigo-600 text-white"
                        : "bg-slate-200 text-slate-700"
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                      isSelected
                        ? "bg-slate-800 text-slate-300"
                        : "bg-slate-200/80 text-slate-600"
                    }`}
                  >
                    {st.latencyBudget}
                  </span>
                </div>

                <div className="text-xs font-bold leading-tight">{st.title}</div>
                <div
                  className={`text-[11px] mt-0.5 line-clamp-1 ${
                    isSelected ? "text-slate-400" : "text-slate-500"
                  }`}
                >
                  {st.subtitle}
                </div>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-200/40 flex items-center justify-between text-[10px]">
                <span className={isSelected ? "text-indigo-300 font-mono" : "text-slate-500 font-mono"}>
                  {st.badge}
                </span>
                {isSelected && (
                  <span className="text-indigo-400 font-medium">Selected &bull;</span>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* Detailed Inspection Drawer for Selected Stage */}
      <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200">
        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 font-mono">
                Stage {selectedStage.id} Specifications
              </span>
              <span className="text-xs text-slate-400">&bull;</span>
              <span className="text-xs font-semibold text-slate-800">{selectedStage.title}</span>
            </div>
            <p className="text-xs text-slate-600 mt-1 font-mono">
              Algorithm: <span className="text-slate-900 font-medium">{selectedStage.algorithm}</span>
            </p>

            <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
              {selectedStage.parameters.map((param, pIdx) => (
                <div
                  key={pIdx}
                  className="flex items-center space-x-2 text-xs text-slate-700 bg-white px-2.5 py-1.5 rounded-lg border border-slate-200"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0"></span>
                  <span className="font-mono text-[11px]">{param}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="md:w-72 shrink-0 bg-white p-3 rounded-lg border border-slate-200 text-xs">
            <div className="flex items-center space-x-1.5 text-slate-700 font-semibold mb-1">
              <Info className="w-3.5 h-3.5 text-slate-500" />
              <span>Safety Rationale</span>
            </div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              {selectedStage.failureMode}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
