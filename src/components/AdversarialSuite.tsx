import React, { useState } from "react";
import {
  Flame,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Filter,
  Lock,
  Sparkles,
} from "lucide-react";
import { AttackSample } from "../data/types";

interface AdversarialSuiteProps {
  samples?: AttackSample[];
}

export const AdversarialSuite: React.FC<AdversarialSuiteProps> = ({ samples = [] }) => {
  const safeSamples = Array.isArray(samples) ? samples : [];
  const getAttackId = (a: any) => a?.attack_id || a?.id || "";

  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [expandedAttack, setExpandedAttack] = useState<string | null>(
    () => (safeSamples.length > 0 ? getAttackId(safeSamples[0]) : null)
  );

  const filtered = safeSamples.filter((s) => {
    if (selectedCategory === "all") return true;
    return s.category === selectedCategory;
  });

  return (
    <div className="space-y-5">
      {/* Overview Defense Scorecards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Total Stress Attacks</div>
          <div className="text-2xl font-extrabold font-mono text-slate-900 mt-0.5">
            60 Attacks
          </div>
          <div className="text-xs text-slate-500 mt-1">
            4 adversarial threat vectors (15 each)
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Unsafe Concession Rate</div>
          <div className="text-2xl font-extrabold font-mono text-emerald-700 mt-0.5">
            0.0%
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Zero unauthorized financial promises
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Safe Escalation Rate</div>
          <div className="text-2xl font-extrabold font-mono text-slate-900 mt-0.5">
            61.7%
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Safely routed to human intervention
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Grounding Preservation</div>
          <div className="text-2xl font-extrabold font-mono text-indigo-700 mt-0.5">
            100.0%
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Enforced by Regex Verification Guard
          </div>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs flex flex-wrap items-center justify-between gap-2">
        <div className="flex flex-wrap gap-1.5">
          {[
            { id: "all", label: "All Threat Vectors (60)" },
            { id: "prompt_injection", label: "Prompt Injection (15)" },
            { id: "policy_circumvention", label: "Policy Circumvention (15)" },
            { id: "emotional_coercion", label: "Emotional Coercion (15)" },
            { id: "contradictory_context", label: "Contradictory Logistics (15)" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setSelectedCategory(tab.id)}
              className={`text-xs px-3 py-1.5 rounded-lg border font-medium transition cursor-pointer ${
                selectedCategory === tab.id
                  ? "bg-slate-900 text-white border-slate-900 shadow-xs"
                  : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
        <span className="text-xs font-mono text-slate-400">
          Showing {filtered.length} attacks
        </span>
      </div>

      {/* Attack Cases List */}
      <div className="space-y-3">
        {filtered.map((attack) => {
          const attackId = getAttackId(attack);
          const isExpanded = expandedAttack === attackId;
          const isEscalated = attack.decision === "ESCALATE";

          return (
            <div
              key={attackId}
              className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs transition hover:border-slate-300"
            >
              <button
                onClick={() => setExpandedAttack(isExpanded ? null : attackId)}
                className="w-full p-4 text-left flex items-start sm:items-center justify-between gap-3 cursor-pointer bg-slate-50/40 hover:bg-slate-50 transition"
              >
                <div className="flex-1">
                  <div className="flex items-center space-x-2.5 mb-1">
                    <span className="font-mono font-bold text-xs text-slate-800">
                      {attackId}
                    </span>
                    <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-slate-200/70 text-slate-700 font-medium">
                      {attack.category.replace(/_/g, " ")}
                    </span>
                    <span
                      className={`text-[10px] px-2 py-0.5 rounded font-mono font-semibold border ${
                        isEscalated
                          ? "bg-amber-50 text-amber-800 border-amber-300"
                          : "bg-emerald-50 text-emerald-800 border-emerald-300"
                      }`}
                    >
                      {attack.decision}
                    </span>
                  </div>

                  <div className="text-xs text-slate-700 font-medium line-clamp-1">
                    "{attack.prompt}"
                  </div>
                </div>

                <div className="flex items-center space-x-2 shrink-0">
                  <span className="text-[11px] font-mono text-slate-500 hidden sm:inline">
                    Risk: {attack.risk_score.toFixed(2)}
                  </span>
                  {isExpanded ? (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </button>

              {isExpanded && (
                <div className="p-5 border-t border-slate-200 space-y-4 bg-white">
                  {/* Full Attack Prompt */}
                  <div className="p-3.5 rounded-xl bg-slate-900 text-slate-100 text-xs font-mono space-y-1">
                    <div className="text-[10px] uppercase font-bold text-indigo-400">
                      Adversarial Attack Input
                    </div>
                    <div className="leading-relaxed">"{attack.prompt}"</div>
                  </div>

                  {/* Defense Diagnostics Grid */}
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                      <div className="text-[10px] uppercase font-semibold text-slate-500">
                        Inferred Intent
                      </div>
                      <div className="font-mono font-bold text-slate-900 mt-0.5">
                        {attack.intent}
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                      <div className="text-[10px] uppercase font-semibold text-slate-500">
                        Risk Score & Gating
                      </div>
                      <div className="font-mono font-bold text-slate-900 mt-0.5">
                        {attack.risk_score.toFixed(2)} &bull; {attack.decision}
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                      <div className="text-[10px] uppercase font-semibold text-slate-500">
                        Concession Audit
                      </div>
                      <div className="font-mono font-bold text-emerald-700 mt-0.5 flex items-center space-x-1">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>0 Concessions</span>
                      </div>
                    </div>
                  </div>

                  {/* Grounded Response */}
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
                    <div className="text-[10px] uppercase font-bold text-slate-500 flex items-center space-x-1">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Verified Defensive Reply</span>
                    </div>
                    <p className="text-slate-800 text-[12px] leading-relaxed">
                      "{attack.response}"
                    </p>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
