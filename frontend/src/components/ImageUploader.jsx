// =============================================================================
// ImageUploader.jsx — Drag-and-drop / click-to-upload image input
// =============================================================================

import { useRef, useState, useCallback } from "react";
import config from "../config";

/**
 * Props:
 *   onFile(file: File)  — called when a valid image is selected
 *   disabled: bool      — disables interaction while loading
 */
export default function ImageUploader({ onFile, disabled }) {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState("");

  // -------------------------------------------------------------------------
  // Validation
  // -------------------------------------------------------------------------

  const validate = useCallback((file) => {
    if (!config.ALLOWED_TYPES.includes(file.type)) {
      setError(`Unsupported file type. Please upload a JPG, PNG, or WebP image.`);
      return false;
    }
    if (file.size > config.MAX_FILE_SIZE_MB * 1024 * 1024) {
      setError(`File is too large. Maximum size is ${config.MAX_FILE_SIZE_MB} MB.`);
      return false;
    }
    setError("");
    return true;
  }, []);

  // -------------------------------------------------------------------------
  // Handlers
  // -------------------------------------------------------------------------

  const handleFile = useCallback(
    (file) => {
      if (file && validate(file)) onFile(file);
    },
    [onFile, validate]
  );

  const handleInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    // Reset so the same file can be re-selected
    e.target.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (disabled) return;
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    if (!disabled) setDragOver(true);
  };

  const handleDragLeave = () => setDragOver(false);

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleKeyDown = (e) => {
    if ((e.key === "Enter" || e.key === " ") && !disabled) inputRef.current?.click();
  };

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  return (
    <div className="uploader-wrapper">
      {/* Hidden native file input */}
      <input
        ref={inputRef}
        type="file"
        accept={config.ALLOWED_EXTENSIONS.join(",")}
        onChange={handleInputChange}
        style={{ display: "none" }}
        aria-hidden="true"
      />

      {/* Drop zone */}
      <div
        className={`drop-zone ${dragOver ? "drag-over" : ""} ${disabled ? "disabled" : ""}`}
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onKeyDown={handleKeyDown}
        role="button"
        tabIndex={disabled ? -1 : 0}
        aria-label="Upload snake image"
      >
        {/* Snake SVG icon */}
        <div className="upload-icon">
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M10 48 C10 48, 8 35, 20 32 C32 29, 38 38, 46 30 C54 22, 52 10, 44 10
                 C36 10, 32 18, 36 24 C40 30, 50 28, 52 36"
              stroke="currentColor"
              strokeWidth="3"
              strokeLinecap="round"
              fill="none"
            />
            <circle cx="44" cy="10" r="3" fill="currentColor" />
            {/* Tongue */}
            <path d="M44 7 L42 4 M44 7 L46 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        </div>

        <p className="upload-title">
          {dragOver ? "Drop it here!" : "Drop a snake photo here"}
        </p>
        <p className="upload-sub">or click to browse</p>
        <p className="upload-hint">JPG, PNG, WebP · max {config.MAX_FILE_SIZE_MB} MB</p>
      </div>

      {/* Validation error */}
      {error && (
        <p className="upload-error" role="alert">
          ⚠ {error}
        </p>
      )}
    </div>
  );
}
