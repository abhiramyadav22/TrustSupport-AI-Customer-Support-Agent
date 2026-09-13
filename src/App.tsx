import React, { useState } from "react";
import benchmarkDataRaw from "./data/benchmarkData.json";
import { BenchmarkData } from "./data/types";
import { Header } from "./components/Header";
import { LiveSimulator } from "./components/LiveSimulator";
import { BenchmarkDashboard } from "./components/BenchmarkDashboard";
import { GoldenSetExplorer } from "./components/GoldenSetExplorer";
import { AdversarialSuite } from "./components/AdversarialSuite";
import { ForensicReports } from "./components/ForensicReports";
import { ReproduceModal } from "./components/ReproduceModal";
import { ShieldCheck, Terminal, Github, CheckCircle2, Heart } from "lucide-react";

const benchmarkData = benchmarkDataRaw as unknown as BenchmarkData;

export default function App() {
  const [activeTab, setActiveTab] = useState<"simulator" | "benchmark" | "golden" | "adversarial" | "reports">("simulator");
  const [isReproduceModalOpen, setIsReproduceModalOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans antialiased flex flex-col selection:bg-indigo-100 selection:text-indigo-900">
      {/* Enterprise Header with Telemetry & Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenReproduceModal={() => setIsReproduceModalOpen(true)}
      />

      {/* Main View Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {activeTab === "simulator" && <LiveSimulator />}

        {activeTab === "benchmark" && (
          <BenchmarkDashboard benchmarkData={benchmarkData} />
        )}

        {activeTab === "golden" && (
          <GoldenSetExplorer samples={benchmarkData.golden_samples} />
        )}

        {activeTab === "adversarial" && (
          <AdversarialSuite samples={benchmarkData.attack_samples} />
        )}

        {activeTab === "reports" && <ForensicReports />}
      </main>

      {/* Enterprise Production Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <div className="flex items-center space-x-2">
            <div className="h-6 w-6 rounded-md bg-slate-900 text-white flex items-center justify-center">
              <ShieldCheck className="h-3.5 w-3.5 text-indigo-400" />
            </div>
            <span className="font-semibold text-slate-800">TrustSupport AI</span>
            <span>&bull;</span>
            <span>Hiver SDE Intern Take-Home Evaluation Suite</span>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4 text-[11px]">
            <span className="font-mono bg-slate-100 px-2 py-0.5 rounded text-slate-600">
              Dataset: Kaggle TWCS (2.81M)
            </span>
            <span className="font-mono bg-emerald-50 text-emerald-800 px-2 py-0.5 rounded border border-emerald-200">
              Split: Strict Temporal (0% Leakage)
            </span>
            <button
              onClick={() => setIsReproduceModalOpen(true)}
              className="text-slate-600 hover:text-slate-900 transition underline cursor-pointer font-medium"
            >
              reproduce.sh CLI
            </button>
            <span className="text-slate-400">&bull;</span>
            <span className="text-slate-700 font-mono">abhiramyadav002@gmail.com</span>
          </div>
        </div>
      </footer>

      {/* 1-Click Reproduction Quickstart Modal */}
      <ReproduceModal
        isOpen={isReproduceModalOpen}
        onClose={() => setIsReproduceModalOpen(false)}
      />
    </div>
  );
}
