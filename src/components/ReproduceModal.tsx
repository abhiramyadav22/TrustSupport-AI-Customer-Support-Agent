import React, { useState } from "react";
import { Terminal, Copy, Check, X, CheckCircle2, Play, ShieldAlert, FileCode } from "lucide-react";

interface ReproduceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ReproduceModal: React.FC<ReproduceModalProps> = ({ isOpen, onClose }) => {
  const [copiedScript, setCopiedScript] = useState(false);
  const [copiedCli, setCopiedCli] = useState(false);

  if (!isOpen) return null;

  const scriptCommand = "chmod +x reproduce.sh && ./reproduce.sh";
  const cliCommand = "python3 scripts/run_agent.py --text 'Where is my order #402-9812? It was delayed 3 days.'";

  const handleCopy = (text: string, isScript: boolean) => {
    navigator.clipboard.writeText(text);
    if (isScript) {
      setCopiedScript(true);
      setTimeout(() => setCopiedScript(false), 2000);
    } else {
      setCopiedCli(true);
      setTimeout(() => setCopiedCli(false), 2000);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-slate-950/70 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 relative max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-3 border-b border-slate-200 mb-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center">
              <Terminal className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">
                1-Click Reproduction Quickstart
              </h3>
              <p className="text-xs text-slate-500">
                Execute end-to-end evaluation & verification in &lt; 2 minutes
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          {/* Main 1-Click Script */}
          <div className="space-y-1.5">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center justify-between">
              <span>Full Benchmark & Report Reproduction</span>
              <span className="text-[11px] font-mono text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Runtime ~85s
              </span>
            </label>
            <div className="relative flex items-center bg-slate-900 rounded-xl p-3 border border-slate-800 text-xs font-mono text-slate-200">
              <span className="text-slate-500 select-none mr-2">$</span>
              <span className="flex-1 overflow-x-auto select-all">{scriptCommand}</span>
              <button
                onClick={() => handleCopy(scriptCommand, true)}
                className="ml-2 p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer shrink-0"
              >
                {copiedScript ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-[11px] text-slate-500">
              Trains intent classifier, constructs precedent index, runs full 200-test evaluation harness, verifies temporal split leakage, and generates all 5 figures in <code className="text-slate-700">reports/figures/</code>.
            </p>
          </div>

          {/* Interactive Single-Query CLI */}
          <div className="space-y-1.5 pt-2 border-t border-slate-100">
            <label className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center justify-between">
              <span>Interactive Command-Line Agent Testing</span>
              <span className="text-[11px] font-mono text-slate-500">CLI Mode</span>
            </label>
            <div className="relative flex items-center bg-slate-900 rounded-xl p-3 border border-slate-800 text-xs font-mono text-slate-200">
              <span className="text-slate-500 select-none mr-2">$</span>
              <span className="flex-1 overflow-x-auto select-all">{cliCommand}</span>
              <button
                onClick={() => handleCopy(cliCommand, false)}
                className="ml-2 p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition cursor-pointer shrink-0"
              >
                {copiedCli ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-[11px] text-slate-500">
              Executes the full calibrated pipeline in Python terminal and outputs structured JSON decision, risk score, retrieved precedents, and grounded reply.
            </p>
          </div>

          {/* Deliverables Checklist */}
          <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs space-y-2">
            <div className="font-semibold text-slate-800">
              Verified Deliverables Checklist:
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-[11px] text-slate-600">
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Runnable Pipeline (`scripts/evaluate.py`)</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>200 Golden Set (`golden_set.jsonl`)</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Evaluation Harness with 3 Baselines</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Final 6-Page Technical Report</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>Decision Log (14 non-obvious choices)</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                <span>60-Attack Adversarial Stress Suite</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
