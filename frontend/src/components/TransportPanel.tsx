import React from "react";

export const TransportPanel: React.FC = () => {
  return (
    <div className="card">
      <h2>Egress Transit Operations</h2>
      <p style={{ color: "var(--text-muted)", marginBottom: "16px" }}>
        Live departures and accessible transportation channels for post-match transit.
      </p>

      <div className="table-container">
        <table>
          <caption className="visually-hidden">Live departures from stadium transit hub</caption>
          <thead>
            <tr>
              <th scope="col">Mode</th>
              <th scope="col">Destination</th>
              <th scope="col">Frequency</th>
              <th scope="col">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">🚇 Metro (Line 1)</th>
              <td>Downtown Central</td>
              <td>Every 3 mins</td>
              <td><span style={{ color: "var(--safe)" }}>ON TIME</span></td>
            </tr>
            <tr>
              <th scope="row">🚌 Shuttle Bus</th>
              <td>West Parking lot</td>
              <td>Every 5 mins</td>
              <td><span style={{ color: "var(--safe)" }}>ON TIME</span></td>
            </tr>
            <tr>
              <th scope="row">🚐 Accessible Shuttle</th>
              <td>Special Needs Lot</td>
              <td>On Request</td>
              <td><span style={{ color: "var(--caution)" }}>10 MIN DELAY</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div
        style={{
          marginTop: "20px",
          padding: "16px",
          backgroundColor: "var(--primary-light)",
          borderRadius: "8px",
          border: "1px solid var(--surface-border)",
        }}
      >
        <h4 style={{ color: "var(--primary)" }}>Egress Crowd Warning</h4>
        <p style={{ fontSize: "0.85rem", marginTop: "4px" }}>
          North Concourse is congested. Please use A* Accessible routes pointing to East Gate or West
          Gate for faster boarding.
        </p>
      </div>
    </div>
  );
};
