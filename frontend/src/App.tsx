import React, { useState } from "react";
import { CrowdHeatmap } from "./components/CrowdHeatmap";
import { FanAssistant } from "./components/FanAssistant";
import { SustainabilityDashboard } from "./components/SustainabilityDashboard";
import { TransportPanel } from "./components/TransportPanel";
import { WayfindingPanel } from "./components/WayfindingPanel";
import { useStadium } from "./hooks/useStadium";

type Tab = "assistant" | "crowd" | "wayfinding" | "egress" | "sustainability";

export const App: React.FC = () => {
  const stadium = useStadium();
  const { state, clearError } = stadium;
  const [activeTab, setActiveTab] = useState<Tab>("assistant");
  const [theme, setTheme] = useState<"light" | "dark">("light");

  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);
    document.documentElement.setAttribute("data-theme", nextTheme);
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      {/* ── Skip to Main Content link (accessibility) ── */}
      <a className="skip-link" href="#main">
        Skip to main content
      </a >

      {/* ── Header Landmark ── */}
      <header className="app-header">
        <div className="brand">
          <h1>StadiumIQ</h1>
          <span className="badge-fifa">FIFA 2026</span>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <button
            onClick={toggleTheme}
            className="btn"
            style={{ padding: "6px 12px", backgroundColor: "var(--surface-border)" }}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
            type="button"
          >
            {theme === "light" ? "🌙 Dark" : "☀️ Light"}
          </button>
        </div>
      </header>

      {/* ── Main Landmark ── */}
      <main id="main">
        {/* ARIA Live region for high-priority alerts / errors */}
        {state.error && (
          <div className="alert-region" role="alert" aria-live="assertive">
            <span className="visually-hidden">Error: </span>
            {state.error}
            <button
              onClick={clearError}
              style={{
                float: "right",
                background: "none",
                border: "none",
                color: "inherit",
                cursor: "pointer",
                fontWeight: "bold",
              }}
              aria-label="Close error alert"
              type="button"
            >
              ×
            </button>
          </div>
        )}

        {/* ARIA Live region for polite status updates (visually hidden) */}
        <div className="visually-hidden" role="status" aria-live="polite">
          {state.status}
        </div>

        {/* Semantic tab selectors */}
        <nav className="nav-tabs" aria-label="Stadium Operations Tabs">
          <button
            className={`tab-btn ${activeTab === "assistant" ? "active" : ""}`}
            onClick={() => setActiveTab("assistant")}
            aria-selected={activeTab === "assistant"}
            role="tab"
            type="button"
          >
            💬 Assistant
          </button>
          <button
            className={`tab-btn ${activeTab === "crowd" ? "active" : ""}`}
            onClick={() => setActiveTab("crowd")}
            aria-selected={activeTab === "crowd"}
            role="tab"
            type="button"
          >
            📊 Crowd Density
          </button>
          <button
            className={`tab-btn ${activeTab === "wayfinding" ? "active" : ""}`}
            onClick={() => setActiveTab("wayfinding")}
            aria-selected={activeTab === "wayfinding"}
            role="tab"
            type="button"
          >
            🗺️ Wayfinding
          </button>
          <button
            className={`tab-btn ${activeTab === "egress" ? "active" : ""}`}
            onClick={() => setActiveTab("egress")}
            aria-selected={activeTab === "egress"}
            role="tab"
            type="button"
          >
            🚇 Egress & Transit
          </button>
          <button
            className={`tab-btn ${activeTab === "sustainability" ? "active" : ""}`}
            onClick={() => setActiveTab("sustainability")}
            aria-selected={activeTab === "sustainability"}
            role="tab"
            type="button"
          >
            🌱 Sustainability
          </button>
        </nav>

        {/* Panel sections layout mapping */}
        <div className="panel-grid">
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {activeTab === "assistant" && (
              <section aria-labelledby="assistant-sec">
                <span id="assistant-sec" className="visually-hidden">
                  Fan assistant panel
                </span>
                <FanAssistant stadium={stadium} />
              </section>
            )}

            {activeTab === "crowd" && (
              <section aria-labelledby="crowd-sec">
                <span id="crowd-sec" className="visually-hidden">
                  Crowd density panel
                </span>
                <CrowdHeatmap stadium={stadium} />
              </section>
            )}

            {activeTab === "wayfinding" && (
              <section aria-labelledby="wayfinding-sec">
                <span id="wayfinding-sec" className="visually-hidden">
                  Accessible wayfinding panel
                </span>
                <WayfindingPanel stadium={stadium} />
              </section>
            )}

            {activeTab === "egress" && (
              <section aria-labelledby="egress-sec">
                <span id="egress-sec" className="visually-hidden">
                  Egress and transport panel
                </span>
                <TransportPanel />
              </section>
            )}

            {activeTab === "sustainability" && (
              <section aria-labelledby="sustainability-sec">
                <span id="sustainability-sec" className="visually-hidden">
                  Sustainability metrics panel
                </span>
                <SustainabilityDashboard stadium={stadium} />
              </section>
            )}
          </div>

          {/* Quick status details sidebar */}
          <aside className="card" style={{ height: "fit-content" }} aria-label="Stadium Quick Stats">
            <h3>Stadium Operations</h3>
            <div style={{ marginTop: "16px", fontSize: "0.9rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span>Match:</span>
                <strong>USA vs England</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span>Venue:</span>
                <strong>MetLife Stadium</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span>Gate Status:</span>
                <strong style={{ color: "var(--safe)" }}>OPEN</strong>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
                <span>Device ID:</span>
                <span style={{ fontSize: "0.75rem", fontFamily: "monospace" }}>
                  {stadium.deviceId.substring(0, 12)}...
                </span>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
};
