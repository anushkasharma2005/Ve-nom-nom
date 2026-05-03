// =============================================================================
// ResultCard.jsx — Displays the full prediction + enrichment result
// =============================================================================

import ConfidenceMeter from "./ConfidenceMeter";
import StatusBadge from "./StatusBadge";

/**
 * Props:
 *   result: {
 *     prediction: { label, confidence, is_venomous, low_confidence },
 *     enrichment: { species_guess, fun_fact, iucn_status, conservation_note,
 *                   first_aid_tip, danger_level },
 *     meta: { filename }
 *   }
 */
export default function ResultCard({ result }) {
  const { prediction, enrichment } = result;
  const venomous = prediction.is_venomous;

  return (
    <div className={`result-card ${venomous ? "venomous" : "safe"}`}>
      {/* ── Header verdict ───────────────────────────────────────────── */}
      <div className="verdict-header">
        <div className={`verdict-icon ${venomous ? "icon-danger" : "icon-safe"}`}>
          {venomous ? "☠" : "✓"}
        </div>

        <div className="verdict-text">
          <h2 className="verdict-label" style={{ color: venomous ? "var(--danger)" : "var(--safe)" }}>
            {prediction.label}
          </h2>
          {enrichment?.species_guess && (
            <p className="species-name">{enrichment.species_guess}</p>
          )}
        </div>

        {/* Danger level pill */}
        {enrichment?.danger_level && (
          <span className={`danger-pill danger-${enrichment.danger_level?.toLowerCase()}`}>
            {enrichment.danger_level} Risk
          </span>
        )}
      </div>

      {/* ── Confidence meter ─────────────────────────────────────────── */}
      <ConfidenceMeter
        confidence={prediction.confidence}
        isVenomous={venomous}
        lowConfidence={prediction.low_confidence}
      />

      {/* ── Info grid ────────────────────────────────────────────────── */}
      <div className="info-grid">
        {/* Fun fact */}
        {enrichment?.fun_fact && (
          <div className="info-block">
            <span className="info-icon">💡</span>
            <div>
              <p className="info-title">Fun Fact</p>
              <p className="info-body">{enrichment.fun_fact}</p>
            </div>
          </div>
        )}

        {/* Conservation */}
        {enrichment?.conservation_note && (
          <div className="info-block">
            <span className="info-icon">🌿</span>
            <div>
              <p className="info-title">Conservation</p>
              <p className="info-body">{enrichment.conservation_note}</p>
              {enrichment.iucn_status && (
                <div style={{ marginTop: "0.5rem" }}>
                  <StatusBadge status={enrichment.iucn_status} />
                </div>
              )}
            </div>
          </div>
        )}

        {/* First aid — only if venomous */}
        {venomous && enrichment?.first_aid_tip && (
          <div className="info-block first-aid">
            <span className="info-icon">🚨</span>
            <div>
              <p className="info-title">First Aid</p>
              <p className="info-body">{enrichment.first_aid_tip}</p>
            </div>
          </div>
        )}
      </div>

      {/* ── Disclaimer ───────────────────────────────────────────────── */}
      <p className="disclaimer">
        ⚠ This tool is for educational purposes only. Do not rely on it for medical
        decisions. Always contact emergency services if bitten by a snake.
      </p>
    </div>
  );
}
