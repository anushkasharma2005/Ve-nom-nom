// =============================================================================
// config.js — Frontend configuration
// Change API_BASE_URL to your deployed backend URL when deploying.
// =============================================================================

const config = {
  // In development, Vite proxies /api → localhost:7860 (see vite.config.js)
  // In production on HF Spaces, frontend is served from same origin as backend
  API_BASE_URL: import.meta.env.VITE_API_URL || "",

  // Endpoints
  ENDPOINTS: {
    health:  "/health",
    predict: "/predict",
  },

  // Upload constraints (should mirror backend/config.py)
  MAX_FILE_SIZE_MB:    10,
  ALLOWED_TYPES:       ["image/jpeg", "image/png", "image/webp"],
  ALLOWED_EXTENSIONS:  [".jpg", ".jpeg", ".png", ".webp"],

  // UI thresholds
  LOW_CONFIDENCE_THRESHOLD: 0.65,  // Show warning below this

  // IUCN badge colours
  IUCN_COLORS: {
    LC:  "#4ade80",  // Least Concern — green
    NT:  "#a3e635",  // Near Threatened — yellow-green
    VU:  "#facc15",  // Vulnerable — yellow
    EN:  "#fb923c",  // Endangered — orange
    CR:  "#f87171",  // Critically Endangered — red
    EW:  "#c084fc",  // Extinct in Wild — purple
    EX:  "#94a3b8",  // Extinct — grey
    DD:  "#64748b",  // Data Deficient — slate
    NE:  "#475569",  // Not Evaluated — slate dark
  },

  IUCN_LABELS: {
    LC: "Least Concern",
    NT: "Near Threatened",
    VU: "Vulnerable",
    EN: "Endangered",
    CR: "Critically Endangered",
    EW: "Extinct in Wild",
    EX: "Extinct",
    DD: "Data Deficient",
    NE: "Not Evaluated",
  },
};

export default config;
