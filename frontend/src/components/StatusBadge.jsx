// =============================================================================
// StatusBadge.jsx — IUCN conservation status badge
// =============================================================================

import config from "../config";

/**
 * Props:
 *   status: string  e.g. "VU", "LC", "EN"
 */
export default function StatusBadge({ status }) {
  const code  = (status || "NE").toUpperCase();
  const color = config.IUCN_COLORS[code]  || config.IUCN_COLORS.NE;
  const label = config.IUCN_LABELS[code] || "Unknown";

  return (
    <span
      className="iucn-badge"
      style={{ "--badge-color": color }}
      title={`IUCN Red List: ${label}`}
    >
      <span className="iucn-dot" />
      <span className="iucn-code">{code}</span>
      <span className="iucn-label">{label}</span>
    </span>
  );
}
