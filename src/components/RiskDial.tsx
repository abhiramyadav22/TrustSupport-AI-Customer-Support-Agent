import React from "react";
import { ShieldAlert, ShieldCheck, HelpCircle, Sliders } from "lucide-react";

interface RiskDialProps {
  riskScore: number;
  confidence: number;
  similarity: number;
  sensitiveTriggered: boolean;
  threshold?: number;
  onThresholdChange?: (val: number) => void;
}

export const RiskDial: React.FC<RiskDialProps> = ({
  riskScore = 0,
  confidence = 0,
  similarity = 0,
  sensitiveTriggered = false,
  threshold = 0.46,
  onThresholdChange,
}) => {
  const safeRisk = typeof riskScore === "number" && !isNaN(riskScore) ? riskScore : 0;
  const safeConfidence = typeof confidence === "number" && !isNaN(confidence) ? confidence : 0;
  const safeSimilarity = typeof similarity === "number" && !isNaN(similarity) ? similarity : 0;

  // SVG semi-circle parameters
  const radius = 70;
  const strokeWidth = 12;
  const cx = 90;
  const cy = 85;

  // Clamped risk score for dial calculation
  const clampedRisk = Math.max(0, Math.min(1, safeRisk));
  const isEscalated = clampedRisk > threshold;

  // Calculate needle angle (-90deg at 0 to +90deg at 1.0)
  const angleDeg = -90 + clampedRisk * 180;
  const angleRad = (angleDeg * Math.PI) / 180;
  const needleLength = 55;
  const needleX = cx + needleLength * Math.cos(angleRad);
  const needleY = cy + needleLength * Math.sin(angleRad);

  // Threshold marker angle
  const threshAngleDeg = -90 + threshold * 180;
  const threshAngleRad = (threshAngleDeg * Math.PI) / 180;
  const threshX = cx + (radius + 2) * Math.cos(threshAngleRad);
  const threshY = cy + (radius + 2) * Math.sin(threshAngleRad);

  // Risk component terms
  const termUncertainty = 0.4 * (1 - safeConfidence);
  const termRetrieval = 0.3 * (1 - safeSimilarity);
  const termAgreement = 0.0; // 0.20 * (1 - 1.0) when precedents agree
  const termSensitive = sensitiveTriggered ? 0.3 : 0.0;

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center space-x-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-900">
              Escalation Risk Engine
            </h4>
            <span
              className={`text-[10px] px-2 py-0.5 rounded-full font-semibold border ${
                isEscalated
                  ? "bg-amber-50 text-amber-800 border-amber-300"
                  : "bg-emerald-50 text-emerald-800 border-emerald-300"
              }`}
            >
              {isEscalated ? "ESCALATE TRIGGERED" : "AUTO-HANDLE PERMITTED"}
            </span>
          </div>
          <span className="text-xs font-mono text-slate-500">Threshold: {threshold.toFixed(2)}</span>
        </div>

        {/* Dial & Score Container */}
        <div className="flex flex-col items-center justify-center my-3 relative">
          <svg width="180" height="100" className="overflow-visible">
            <defs>
              <linearGradient id="riskDialGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="45%" stopColor="#3b82f6" />
                <stop offset="60%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#ef4444" />
              </linearGradient>
            </defs>

            {/* Background Arc */}
            <path
              d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
              fill="none"
              stroke="#e2e8f0"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
            />

            {/* Active Colored Arc */}
            <path
              d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
              fill="none"
              stroke="url(#riskDialGradient)"
              strokeWidth={strokeWidth}
              strokeLinecap="round"
              strokeDasharray="220"
              strokeDashoffset={220 * (1 - clampedRisk)}
              className="transition-all duration-500 ease-out"
            />

            {/* Threshold Marker Pin */}
            <circle cx={threshX} cy={threshY} r="3.5" fill="#0f172a" stroke="#ffffff" strokeWidth="1.5" />

            {/* Pivot Center */}
            <circle cx={cx} cy={cy} r="5" fill="#1e293b" />

            {/* Needle */}
            <line
              x1={cx}
              y1={cy}
              x2={needleX}
              y2={needleY}
              stroke="#0f172a"
              strokeWidth="2.5"
              strokeLinecap="round"
              className="transition-all duration-500 ease-out"
            />
          </svg>

          {/* Value Display */}
          <div className="text-center mt-1">
            <div className="text-2xl font-extrabold font-mono text-slate-900 tracking-tight">
              {clampedRisk.toFixed(2)}
            </div>
            <div className="text-[11px] text-slate-500 font-medium">
              Composite Risk Score (0.00 – 1.00)
            </div>
          </div>
        </div>

        {/* Formula Decomposition Breakdown */}
        <div className="space-y-2 mt-2 pt-2 border-t border-slate-100">
          <div className="text-[11px] font-semibold text-slate-700 flex items-center justify-between">
            <span>Risk Factor Breakdown</span>
            <span className="text-slate-400 font-mono text-[10px]">Formula: Σ wᵢ·fᵢ</span>
          </div>

          <div className="space-y-1.5 text-xs">
            {/* Uncertainty */}
            <div>
              <div className="flex justify-between text-[11px] text-slate-600 mb-0.5">
                <span>Intent Uncertainty (40%)</span>
                <span className="font-mono">+{termUncertainty.toFixed(2)}</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-indigo-600 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (termUncertainty / 0.4) * 100)}%` }}
                ></div>
              </div>
            </div>

            {/* Retrieval Distance */}
            <div>
              <div className="flex justify-between text-[11px] text-slate-600 mb-0.5">
                <span>Retrieval Distance (30%)</span>
                <span className="font-mono">+{termRetrieval.toFixed(2)}</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-blue-600 h-1.5 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (termRetrieval / 0.3) * 100)}%` }}
                ></div>
              </div>
            </div>

            {/* Sensitive Override */}
            {sensitiveTriggered && (
              <div>
                <div className="flex justify-between text-[11px] text-amber-700 font-semibold mb-0.5">
                  <span>Sensitive Keyword / Legal Override</span>
                  <span className="font-mono">+0.30</span>
                </div>
                <div className="w-full bg-amber-100 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-amber-600 h-1.5 rounded-full w-full"></div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Interactive Threshold Slider (Optional Tuner) */}
      {onThresholdChange && (
        <div className="mt-4 pt-3 border-t border-slate-100">
          <div className="flex items-center justify-between text-[11px] text-slate-600 mb-1">
            <span className="flex items-center space-x-1 font-medium">
              <Sliders className="w-3 h-3 text-slate-400" />
              <span>Tune Risk Threshold</span>
            </span>
            <span className="font-mono font-bold text-slate-900">{threshold.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0.20"
            max="0.80"
            step="0.02"
            value={threshold}
            onChange={(e) => onThresholdChange(parseFloat(e.target.value))}
            className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-slate-900"
          />
          <div className="flex justify-between text-[10px] text-slate-400 mt-0.5 font-mono">
            <span>Conservative (0.20)</span>
            <span>Default (0.46)</span>
            <span>Permissive (0.80)</span>
          </div>
        </div>
      )}
    </div>
  );
};
