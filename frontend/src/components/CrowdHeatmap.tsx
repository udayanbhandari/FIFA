import React, { useState } from "react";
import { useStadium } from "../hooks/useStadium";
import { formatDensity, formatZoneName } from "../lib/format";
import { EventPhase } from "../lib/types";

interface Props {
  stadium: ReturnType<typeof useStadium>;
}

export const CrowdHeatmap: React.FC<Props> = ({ stadium }) => {
  const { state, checkZoneDensity } = stadium;
  const [selectedZone, setSelectedZone] = useState("concourse_north");
  const [phase, setPhase] = useState<EventPhase>("pre_match");

  const handleCheck = () => {
    checkZoneDensity(selectedZone, phase);
  };

  const zones = [
    "concourse_north",
    "concourse_south",
    "concourse_east",
    "concourse_west",
    "vomitory_1",
    "vomitory_2",
    "transit_hub",
  ];

  return (
    <div className="card">
      <h2>Real-Time Crowd Density Map</h2>
      <div className="grid-2col" style={{ marginBottom: "20px" }}>
        <div className="form-group">
          <label htmlFor="zone-select">Select Stadium Zone</label>
          <select
            id="zone-select"
            value={selectedZone}
            onChange={(e) => setSelectedZone(e.target.value)}
          >
            {zones.map((z) => (
              <option key={z} value={z}>
                {formatZoneName(z)}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="phase-select">Event Phase</label>
          <select
            id="phase-select"
            value={phase}
            onChange={(e) => setPhase(e.target.value as EventPhase)}
          >
            <option value="pre_match">Pre-Match Ingress</option>
            <option value="kickoff">Match Play (Seated)</option>
            <option value="halftime">Halftime Rush</option>
            <option value="full_time">Full Time</option>
            <option value="post_match">Post-Match Egress</option>
          </select>
        </div>
      </div>

      <button
        onClick={handleCheck}
        className="btn btn-primary"
        style={{ width: "100%", marginBottom: "24px" }}
      >
        Update Crowd Estimation
      </button>

      {/* Main Heatmap Visual representation */}
      <div
        className="heatmap"
        role="img"
        aria-label="Stadium zone density heatmap representation showing occupancy levels"
      >
        {zones.map((z) => {
          let safety = "safe";
          if (z === selectedZone && state.density) {
            safety = state.density.safety_status;
          } else if (z === "vomitory_1") {
            safety = "critical";
          }
          return (
            <button
              key={z}
              className={`heatmap-zone ${safety}`}
              onClick={() => setSelectedZone(z)}
              type="button"
            >
              <div style={{ fontWeight: "bold" }}>{formatZoneName(z)}</div>
              <div style={{ fontSize: "0.8rem" }}>
                {z === selectedZone && state.density
                  ? formatDensity(state.density.current_density)
                  : "Click to check"}
              </div>
            </button>
          );
        })}
      </div>

      {/* Accessible Text Equivalent Data Grid */}
      <div className="table-container" style={{ marginTop: "24px" }}>
        <table>
          <caption className="visually-hidden">Current stadium crowd density statistics</caption>
          <thead>
            <tr>
              <th scope="col">Zone</th>
              <th scope="col">Status</th>
              <th scope="col">Density</th>
              <th scope="col">Utilization</th>
            </tr>
          </thead>
          <tbody>
            {state.density && state.density.zone_id === selectedZone && (
              <tr>
                <th scope="row">{formatZoneName(state.density.zone_id)}</th>
                <td>
                  <span className={`indicator-text ${state.density.safety_status}`}>
                    {state.density.safety_status.toUpperCase()}
                  </span>
                </td>
                <td>{formatDensity(state.density.current_density)}</td>
                <td>{state.density.utilization_pct}%</td>
              </tr>
            )}
            <tr>
              <th scope="row">Vomitory 1</th>
              <td>
                <span className="indicator-text critical" style={{ color: "var(--danger)" }}>
                  CRITICAL
                </span>
              </td>
              <td>4.8 P/m²</td>
              <td>96.0%</td>
            </tr>
            <tr>
              <th scope="row">Transit Hub</th>
              <td>
                <span className="indicator-text safe" style={{ color: "var(--safe)" }}>
                  SAFE
                </span>
              </td>
              <td>1.2 P/m²</td>
              <td>24.0%</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Hotspot alerts panel */}
      {state.alerts.length > 0 && (
        <div style={{ marginTop: "24px" }}>
          <h3>Safety Hotspot Warnings</h3>
          <ul style={{ paddingLeft: "20px", marginTop: "8px" }}>
            {state.alerts
              .filter((a) => a.risk_level === "critical" || a.risk_level === "high")
              .map((alert, i) => (
                <li key={i} style={{ marginBottom: "12px", color: "var(--danger)" }}>
                  <strong>{formatZoneName(alert.zone_id)}:</strong> {alert.recommended_action}
                </li>
              ))}
          </ul>
        </div>
      )}
    </div>
  );
};
