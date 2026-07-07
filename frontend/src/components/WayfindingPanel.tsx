import React, { useState } from "react";
import { useStadium } from "../hooks/useStadium";
import { formatDuration, formatZoneName } from "../lib/format";
import { AccessibilityNeed } from "../lib/types";

interface Props {
  stadium: ReturnType<typeof useStadium>;
}

export const WayfindingPanel: React.FC<Props> = ({ stadium }) => {
  const { state, findRoute, findNearest } = stadium;
  const [origin, setOrigin] = useState("gate_north");
  const [destination, setDestination] = useState("seating_1");
  const [need, setNeed] = useState<AccessibilityNeed>("none");

  const handleFindRoute = (e: React.FormEvent) => {
    e.preventDefault();
    findRoute(origin, destination, need);
  };

  const handleNearestRestroom = () => {
    findNearest(origin, "restroom", need);
  };

  const handleNearestMedical = () => {
    findNearest(origin, "medical", need);
  };

  const zones = [
    "gate_north",
    "gate_south",
    "gate_east",
    "gate_west",
    "concourse_north",
    "concourse_south",
    "vomitory_1",
    "vomitory_2",
    "seating_1",
    "seating_5",
    "transit_hub",
  ];

  return (
    <div className="card">
      <h2>Accessible Wayfinding</h2>
      <form onSubmit={handleFindRoute} aria-labelledby="wayfinding-title">
        <span id="wayfinding-title" className="visually-hidden">
          Wayfinding Routing parameters
        </span>

        <fieldset>
          <legend>Accessibility Profile</legend>
          <div className="grid-2col">
            <label style={{ display: "flex", gap: "8px", fontWeight: "normal" }}>
              <input
                type="radio"
                name="need"
                checked={need === "none"}
                onChange={() => setNeed("none")}
                style={{ width: "auto" }}
              />
              Standard Route (Use Stairs/Escalators)
            </label>
            <label style={{ display: "flex", gap: "8px", fontWeight: "normal" }}>
              <input
                type="radio"
                name="need"
                checked={need === "wheelchair"}
                onChange={() => setNeed("wheelchair")}
                style={{ width: "auto" }}
              />
              Wheelchair Accessible (Ramps/Elevators)
            </label>
            <label style={{ display: "flex", gap: "8px", fontWeight: "normal" }}>
              <input
                type="radio"
                name="need"
                checked={need === "visual"}
                onChange={() => setNeed("visual")}
                style={{ width: "auto" }}
              />
              Tactile Markers (Visually Impaired)
            </label>
          </div>
        </fieldset>

        <div className="grid-2col">
          <div className="form-group">
            <label htmlFor="origin-select">Start Location</label>
            <select id="origin-select" value={origin} onChange={(e) => setOrigin(e.target.value)}>
              {zones.map((z) => (
                <option key={z} value={z}>
                  {formatZoneName(z)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="destination-select">Destination</label>
            <select
              id="destination-select"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
            >
              {zones.map((z) => (
                <option key={z} value={z}>
                  {formatZoneName(z)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
          Find Accessible Route
        </button>
      </form>

      <div style={{ marginTop: "24px", display: "flex", gap: "12px" }}>
        <button
          onClick={handleNearestRestroom}
          className="btn"
          style={{ flexGrow: 1, backgroundColor: "var(--surface-border)" }}
          type="button"
        >
          🚻 Find Nearest Restroom
        </button>
        <button
          onClick={handleNearestMedical}
          className="btn"
          style={{ flexGrow: 1, backgroundColor: "var(--surface-border)" }}
          type="button"
        >
          🏥 Find Nearest Medical
        </button>
      </div>

      {/* Render Steps */}
      {state.route && (
        <div style={{ marginTop: "24px" }}>
          <h3>Navigation Steps</h3>
          <div style={{ margin: "8px 0", color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Total Distance: {state.route.total_distance_meters}m | Estimated Time:{" "}
            {formatDuration(state.route.estimated_minutes)} | Accessible rating:{" "}
            {state.route.accessibility_score * 100}%
          </div>
          <ol style={{ paddingLeft: "20px", marginTop: "12px" }}>
            {state.route.steps.map((step, i) => (
              <li key={i} style={{ marginBottom: "12px" }}>
                <div>{step.instruction}</div>
                <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  {step.distance_meters}m{" "}
                  {step.accessibility_features.length > 0 &&
                    `| Features: ${step.accessibility_features.join(", ")}`}
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}

      {/* Render Nearest Facility */}
      {state.nearest && (
        <div style={{ marginTop: "24px" }}>
          <h3>Facility Target: {formatZoneName(state.nearest.zoneId)}</h3>
          <div style={{ margin: "8px 0", color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Walking distance: {state.nearest.route.total_distance_meters}m | Estimated:{" "}
            {formatDuration(state.nearest.route.estimated_minutes)}
          </div>
          <ol style={{ paddingLeft: "20px", marginTop: "12px" }}>
            {state.nearest.route.steps.map((step, i) => (
              <li key={i} style={{ marginBottom: "12px" }}>
                <div>{step.instruction}</div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
};
