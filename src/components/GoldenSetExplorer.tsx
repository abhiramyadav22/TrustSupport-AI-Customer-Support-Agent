import React, { useState } from "react";
import {
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  FileText,
  UserCheck,
  ChevronRight,
  X,
  Scale,
  Sparkles,
} from "lucide-react";
import { GoldenSample } from "../data/types";

interface GoldenSetExplorerProps {
  samples?: GoldenSample[];
}

export const GoldenSetExplorer: React.FC<GoldenSetExplorerProps> = ({ samples = [] }) => {
  const safeSamples = Array.isArray(samples) ? samples : [];

  const getCaseId = (s: any) => s?.golden_id || s?.id || "";
  const getCaseText = (s: any) => s?.customer_message || s?.text || "";
  const getCaseIntent = (s: any) => s?.gold_intent || s?.intent || "";
  const getCaseDecision = (s: any) => s?.gold_decision || s?.decision || "";
  const getCaseStratum = (s: any) => s?.stratum || "";
  const getCaseReason = (s: any) => s?.gold_escalation_reason || s?.escalation_reason || "";
  const getBrandReply = (s: any) => s?.reference_brand_reply || s?.brand_reply || "";

  const [searchTerm, setSearchTerm] = useState("");
  const [stratumFilter, setStratumFilter] = useState<string>("all");
  const [decisionFilter, setDecisionFilter] = useState<string>("all");
  const [selectedCase, setSelectedCase] = useState<GoldenSample | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 15;

  const filteredSamples = safeSamples.filter((s) => {
    const stratum = getCaseStratum(s);
    const decision = getCaseDecision(s);
    if (stratumFilter !== "all" && stratum !== stratumFilter) return false;
    if (decisionFilter !== "all" && decision !== decisionFilter) return false;
    if (searchTerm.trim()) {
      const q = searchTerm.toLowerCase();
      const matchId = getCaseId(s).toLowerCase().includes(q);
      const matchText = getCaseText(s).toLowerCase().includes(q);
      const matchIntent = getCaseIntent(s).toLowerCase().includes(q);
      return matchId || matchText || matchIntent;
    }
    return true;
  });

  const totalPages = Math.ceil(filteredSamples.length / pageSize);
  const paginatedSamples = filteredSamples.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  return (
    <div className="space-y-5">
      {/* Overview Metric Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Benchmark Size</div>
          <div className="text-2xl font-extrabold font-mono text-slate-900 mt-0.5">
            200 Cases
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Hand-labelled from unseen test split
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Stratification Architecture</div>
          <div className="text-sm font-bold text-slate-800 mt-0.5">
            60% / 20% / 14%
          </div>
          <div className="text-xs text-slate-500 mt-1">
            132 Rep &bull; 40 Ambiguous &bull; 28 High-Risk
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Inter-Annotator Agreement</div>
          <div className="text-2xl font-extrabold font-mono text-indigo-700 mt-0.5">
            κ = 0.8854
          </div>
          <div className="text-xs text-slate-500 mt-1">
            95.0% raw decision agreement
          </div>
        </div>

        <div className="p-4 rounded-xl bg-white border border-slate-200 shadow-xs">
          <div className="text-xs text-slate-500 font-medium">Target Decision Split</div>
          <div className="text-sm font-bold font-mono text-slate-800 mt-0.5">
            141 Auto / 59 Escalate
          </div>
          <div className="text-xs text-slate-500 mt-1">
            70.5% automated resolution target
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => {
              setSearchTerm(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="Search by case ID, intent, or text keywords..."
            className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition font-sans text-slate-900 placeholder:text-slate-400 bg-slate-50/50"
          />
        </div>

        {/* Stratum Filter Buttons */}
        <div className="flex flex-wrap items-center gap-1.5">
          {[
            { id: "all", label: "All (200)" },
            { id: "representative", label: "Representative (132)" },
            { id: "hard_ambiguous", label: "Hard / Ambiguous (40)" },
            { id: "high_risk_escalation", label: "High-Risk (28)" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => {
                setStratumFilter(tab.id);
                setCurrentPage(1);
              }}
              className={`text-xs px-2.5 py-1 rounded-lg border font-medium transition cursor-pointer ${
                stratumFilter === tab.id
                  ? "bg-slate-900 text-white border-slate-900 shadow-xs"
                  : "bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Samples Table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden shadow-xs">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-600 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4 w-28">Case ID</th>
                <th className="py-3 px-4 w-36">Stratum</th>
                <th className="py-3 px-4 w-44">Operational Intent</th>
                <th className="py-3 px-4">Customer Inquiry</th>
                <th className="py-3 px-4 w-32">Ground Truth</th>
                <th className="py-3 px-4 w-20 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-800">
              {paginatedSamples.map((sample) => {
                const caseId = getCaseId(sample);
                const caseText = getCaseText(sample);
                const caseIntent = getCaseIntent(sample);
                const caseDecision = getCaseDecision(sample);
                const caseStratum = getCaseStratum(sample);
                const isEscalate = caseDecision === "ESCALATE";

                return (
                  <tr
                    key={caseId}
                    onClick={() => setSelectedCase(sample)}
                    className="hover:bg-slate-50/80 transition cursor-pointer"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-slate-800">
                      {caseId}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-mono font-medium ${
                          caseStratum === "high_risk_escalation"
                            ? "bg-red-50 text-red-700 border border-red-200"
                            : caseStratum === "hard_ambiguous"
                            ? "bg-amber-50 text-amber-700 border border-amber-200"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {caseStratum.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-slate-700">
                      {caseIntent}
                    </td>
                    <td className="py-3 px-4 text-slate-600 max-w-md truncate">
                      "{caseText}"
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded font-semibold font-mono border ${
                          isEscalate
                            ? "bg-amber-50 text-amber-800 border-amber-300"
                            : "bg-emerald-50 text-emerald-800 border-emerald-300"
                        }`}
                      >
                        {caseDecision}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <ChevronRight className="w-4 h-4 text-slate-400 inline" />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="p-3 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <div>
            Showing <strong>{(currentPage - 1) * pageSize + 1}</strong> to{" "}
            <strong>{Math.min(currentPage * pageSize, filteredSamples.length)}</strong> of{" "}
            <strong>{filteredSamples.length}</strong> matching cases
          </div>
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-2.5 py-1 rounded bg-white border border-slate-300 disabled:opacity-40 cursor-pointer font-medium"
            >
              Previous
            </button>
            <span className="px-2 font-mono">
              {currentPage} / {totalPages || 1}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage >= totalPages}
              className="px-2.5 py-1 rounded bg-white border border-slate-300 disabled:opacity-40 cursor-pointer font-medium"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Detailed Case Inspection Drawer Modal */}
      {selectedCase && (
        <div
          className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6"
          onClick={() => setSelectedCase(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 relative max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-4">
              <div className="flex items-center space-x-2">
                <span className="font-mono font-bold text-base text-slate-900">
                  {getCaseId(selectedCase)}
                </span>
                <span className="text-xs px-2 py-0.5 rounded font-mono bg-slate-100 text-slate-700">
                  {getCaseStratum(selectedCase)}
                </span>
              </div>
              <button
                onClick={() => setSelectedCase(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              {/* Customer Input */}
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Customer Tweet Text (Test Split)
                </div>
                <div className="text-sm font-medium text-slate-900">
                  "{getCaseText(selectedCase)}"
                </div>
              </div>

              {/* Label Specifications */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-[10px] uppercase font-semibold text-slate-500">
                    Hand-Labelled Intent
                  </div>
                  <div className="text-sm font-mono font-bold text-indigo-700 mt-0.5">
                    {getCaseIntent(selectedCase)}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-[10px] uppercase font-semibold text-slate-500">
                    Ground Truth Routing Decision
                  </div>
                  <div className="text-sm font-mono font-bold text-slate-900 mt-0.5">
                    {getCaseDecision(selectedCase)}
                  </div>
                </div>
              </div>

              {/* Ground Truth Escalation Reason if present */}
              {getCaseReason(selectedCase) && (
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                  <span className="font-semibold text-slate-700">Ground Truth Rationale: </span>
                  <span className="text-slate-600">{getCaseReason(selectedCase)}</span>
                </div>
              )}

              {/* Reference Historical Brand Reply if present */}
              {getBrandReply(selectedCase) && (
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs">
                  <span className="font-semibold text-slate-700">Historical Amazon Agent Reply: </span>
                  <span className="text-slate-600 italic">"{getBrandReply(selectedCase)}"</span>
                </div>
              )}

              {/* Annotator Consensus Section */}
              <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-1">
                <div className="flex items-center space-x-1 text-slate-700 font-semibold">
                  <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
                  <span>Dual Annotator Agreement Audit</span>
                </div>
                <p className="text-slate-600 text-[11px] leading-relaxed">
                  Both independent annotators evaluated this case for intent categorizability and customer liability risk. Inter-annotator kappa achieved κ = 0.8854 across all routing decisions.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
