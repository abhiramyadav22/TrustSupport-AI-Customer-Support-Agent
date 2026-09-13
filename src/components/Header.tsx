import React from "react";
import { ShieldCheck, BarChart3, BrainCircuit, UserCheck, Flame, FileText, CheckCircle2, Download, Terminal } from "lucide-react";

interface HeaderProps {
  activeTab: "simulator" | "benchmark" | "golden" | "adversarial" | "reports";
  setActiveTab: (tab: "simulator" | "benchmark" | "golden" | "adversarial" | "reports") => void;
  onOpenReproduceModal?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, onOpenReproduceModal }) => {
  const navItems = [
    { id: "simulator" as const, label: "Live Simulator", icon: BrainCircuit, badge: "Interactive" },
    { id: "benchmark" as const, label: "Central Results", icon: BarChart3, badge: "3 Systems" },
    { id: "golden" as const, label: "Golden Set", icon: UserCheck, badge: "200 Cases" },
    { id: "adversarial" as const, label: "Attack Suite", icon: Flame, badge: "60 Tests" },
    { id: "reports" as const, label: "Forensic Reports", icon: FileText, badge: "6 Pages" },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and System Status */}
          <div className="flex items-center space-x-3.5">
            <div className="h-10 w-10 rounded-xl bg-slate-900 text-white flex items-center justify-center shadow-xs border border-slate-800">
              <ShieldCheck className="h-5 w-5 text-indigo-400" />
            </div>
            <div>
              <div className="flex items-center space-x-2.5">
                <span className="text-base font-bold tracking-tight text-slate-900">TrustSupport AI</span>
                <span className="inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded-md bg-slate-100 text-slate-700 border border-slate-300">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mr-1.5 animate-pulse"></span>
                  AmazonHelp Benchmark
                </span>
                <span className="hidden md:inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200">
                  <CheckCircle2 className="w-3 h-3 mr-1 text-emerald-600" />
                  Zero-Leakage Audited
                </span>
              </div>
              <p className="text-xs text-slate-500 hidden sm:block">
                Calibrated Intent Classifier &bull; Intent-Filtered Historical Retrieval &bull; Multi-Factor Escalation
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center space-x-2">
            {onOpenReproduceModal && (
              <button
                id="btn-reproduce-quickstart"
                onClick={onOpenReproduceModal}
                className="inline-flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-lg text-slate-700 bg-slate-100 hover:bg-slate-200 transition border border-slate-300 cursor-pointer"
              >
                <Terminal className="w-3.5 h-3.5 text-slate-600" />
                <span className="hidden sm:inline">Reproduce in &lt; 2m</span>
                <span className="sm:hidden">CLI</span>
              </button>
            )}
          </div>
        </div>

        {/* Navigation Tabs Bar */}
        <nav className="flex space-x-1 sm:space-x-2 border-t border-slate-100 py-1.5 overflow-x-auto scrollbar-none">
          {navItems.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                id={`nav-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className={`relative flex items-center space-x-2 px-3.5 py-2 text-xs font-medium rounded-lg transition-all whitespace-nowrap cursor-pointer ${
                  isActive
                    ? "bg-slate-900 text-white shadow-xs font-semibold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`}
              >
                <Icon className={`h-4 w-4 ${isActive ? "text-indigo-400" : "text-slate-400"}`} />
                <span>{tab.label}</span>
                <span
                  className={`text-[10px] px-1.5 py-0.2 rounded-md font-mono ${
                    isActive ? "bg-slate-800 text-slate-300" : "bg-slate-200/70 text-slate-600"
                  }`}
                >
                  {tab.badge}
                </span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
