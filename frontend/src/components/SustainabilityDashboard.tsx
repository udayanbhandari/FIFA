import React, { useState } from "react";
import { useStadium } from "../hooks/useStadium";
import { formatCO2 } from "../lib/format";

interface Props {
  stadium: ReturnType<typeof useStadium>;
}

export const SustainabilityDashboard: React.FC<Props> = ({ stadium }) => {
  const { state, calculateSustainability } = stadium;
  const [attendance, setAttendance] = useState(45000);
  const [energy, setEnergy] = useState(210000);
  const [waste, setWaste] = useState(12000);
  const [water, setWater] = useState(380000);

  const handleCalculate = (e: React.FormEvent) => {
    e.preventDefault();
    calculateSustainability({
      attendance,
      transport_mix: {
        metro: 0.45,
        bus: 0.15,
        rideshare: 0.25,
        walk: 0.1,
        accessible_shuttle: 0.05,
      },
      energy_kwh: energy,
      waste_kg: waste,
      water_liters: water,
    });
  };

  return (
    <div className="card">
      <h2>Sustainability & Footprint Tracker</h2>
      <form onSubmit={handleCalculate} aria-labelledby="sustainability-title">
        <span id="sustainability-title" className="visually-hidden">
          Sustainability footprint inputs
        </span>

        <div className="grid-2col">
          <div className="form-group">
            <label htmlFor="attendance-input">Attendance</label>
            <input
              id="attendance-input"
              type="number"
              value={attendance}
              onChange={(e) => setAttendance(Number(e.target.value))}
              min={0}
              max={110000}
            />
          </div>

          <div className="form-group">
            <label htmlFor="energy-input">Energy Usage (kWh)</label>
            <input
              id="energy-input"
              type="number"
              value={energy}
              onChange={(e) => setEnergy(Number(e.target.value))}
              min={0}
              max={1000000}
            />
          </div>
        </div>

        <div className="grid-2col">
          <div className="form-group">
            <label htmlFor="waste-input">Waste Generated (kg)</label>
            <input
              id="waste-input"
              type="number"
              value={waste}
              onChange={(e) => setWaste(Number(e.target.value))}
              min={0}
              max={100000}
            />
          </div>

          <div className="form-group">
            <label htmlFor="water-input">Water Usage (Liters)</label>
            <input
              id="water-input"
              type="number"
              value={water}
              onChange={(e) => setWater(Number(e.target.value))}
              min={0}
              max={5000000}
            />
          </div>
        </div>

        <button type="submit" className="btn btn-primary" style={{ width: "100%" }}>
          Calculate Match Day Footprint
        </button>
      </form>

      {state.footprint && (
        <div style={{ marginTop: "24px" }}>
          <h3>Spectator & Venue Footprint</h3>
          <div
            style={{
              fontSize: "1.8rem",
              fontWeight: 800,
              color: "var(--primary)",
              margin: "12px 0",
            }}
          >
            {formatCO2(state.footprint.total_kg_co2e)}
          </div>

          <div className="table-container">
            <table>
              <caption className="visually-hidden">Match day carbon footprint breakdown</caption>
              <thead>
                <tr>
                  <th scope="col">Source</th>
                  <th scope="col">Emissions</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <th scope="row">Transport</th>
                  <td>{formatCO2(state.footprint.transport_kg_co2e)}</td>
                </tr>
                <tr>
                  <th scope="row">Energy</th>
                  <td>{formatCO2(state.footprint.energy_kg_co2e)}</td>
                </tr>
                <tr>
                  <th scope="row">Waste</th>
                  <td>{formatCO2(state.footprint.waste_kg_co2e)}</td>
                </tr>
                <tr>
                  <th scope="row">Water</th>
                  <td>{formatCO2(state.footprint.water_kg_co2e)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      {state.comparison && (
        <div
          style={{
            marginTop: "24px",
            padding: "16px",
            borderRadius: "8px",
            backgroundColor: state.comparison.on_target
              ? "hsla(140, 60%, 30%, 0.1)"
              : "hsla(354, 70%, 42%, 0.1)",
            borderLeft: `4px solid ${state.comparison.on_target ? "var(--safe)" : "var(--danger)"}`,
          }}
        >
          <h4>
            FIFA Target Comparison:{" "}
            <span
              style={{
                color: state.comparison.on_target ? "var(--safe)" : "var(--danger)",
                fontWeight: "bold",
              }}
            >
              {state.comparison.on_target ? "ON TARGET (🟢)" : "EXCEEDED LIMIT (🔴)"}
            </span>
          </h4>
          <p style={{ marginTop: "8px", fontSize: "0.9rem" }}>
            {state.comparison.on_target
              ? "Operation matches green strategy metrics."
              : "Action required. Emitting higher than carbon-neutral allocation."}
          </p>
          <ul style={{ marginTop: "12px", paddingLeft: "20px" }}>
            {state.comparison.recommendations.map((rec, i) => (
              <li key={i} style={{ fontSize: "0.85rem", marginBottom: "4px" }}>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
