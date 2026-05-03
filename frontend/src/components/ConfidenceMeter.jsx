// =============================================================================
// ConfidenceMeter.jsx — Animated confidence score bar
// =============================================================================

import { useEffect, useRef } from "react";

/**
 * Props:
 *   confidence: number  0–1
 *   isVenomous: bool
 *   lowConfidence: bool
 */
export default function ConfidenceMeter({ confidence, isVenomous, lowConfidence }) {
  const barRef = useRef(null);
  const pct = Math.round(confidence * 100);

  useEffect(() => {
    // Animate bar width on mount
    if (barRef.current) {
      barRef.current.style.width = "0%";
      requestAnimationFrame(() => {
        setTimeout(() => {
          if (barRef.current) barRef.current.style.width = `${pct}%`;
        }, 50);
      });
    }
  }, [pct]);

  const barColor = isVenomous
    ? "var(--danger)"
    : "var(--safe)";

  return (
    <div className="confidence-meter">
      <div className="confidence-header">
        <span className="confidence-label">Model Confidence</span>
        <span className="confidence-pct" style={{ color: barColor }}>
          {pct}%
        </span>
      </div>

      <div className="confidence-track">
        <div
          ref={barRef}
          className="confidence-bar"
          style={{
            backgroundColor: barColor,
            transition: "width 0.9s cubic-bezier(0.34, 1.56, 0.64, 1)",
          }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>

      {/* Low-confidence warning */}
      {lowConfidence && (
        <p className="confidence-warning">
          ⚠ Low confidence — result may not be reliable. Please consult an expert.
        </p>
      )}
    </div>
  );
}
