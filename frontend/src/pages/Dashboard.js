import React, { useState, useEffect } from "react";

const bins = [
  { id: 1, location: "Main Street", status: "Empty", lat: 28.6139, lng: 77.2090 },
  { id: 2, location: "Park Area", status: "Half-Full", lat: 28.6145, lng: 77.2085 },
  { id: 3, location: "Bus Stand", status: "Full", lat: 28.6150, lng: 77.2100 }
];

const truckDriver = { name: "Ravi", phone: "9876543210", location: "Sector 5" };

const publicOpinions = [
  { user: "Amit", opinion: "Bins are emptied regularly." },
  { user: "Priya", opinion: "Need more bins in my area." }
];

function Dashboard() {
  const [binStatuses, setBinStatuses] = useState(bins);

  // Simulate live bin status update
  useEffect(() => {
    const interval = setInterval(() => {
      setBinStatuses(bs =>
        bs.map(bin =>
          bin.id === 2
            ? { ...bin, status: bin.status === "Half-Full" ? "Full" : "Half-Full" }
            : bin
        )
      );
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "2rem", background: "#f5f6fa", minHeight: "100vh" }}>
      <h1 style={{ color: "#273c75", marginBottom: "1.5rem" }}>Smart Bin Dashboard</h1>
      <section style={{ marginBottom: "2rem" }}>
        <h2>Status of Smart Bins</h2>
        <div style={{ display: "flex", gap: "2rem" }}>
          {binStatuses.map(bin => (
            <div key={bin.id} style={{
              background: "#fff", padding: "1rem", borderRadius: "8px", boxShadow: "0 2px 8px rgba(44,62,80,0.1)", minWidth: "150px"
            }}>
              <strong>{bin.location}</strong>
              <div>Status: <span style={{
                color: bin.status === "Full" ? "#e84118" : bin.status === "Half-Full" ? "#fbc531" : "#44bd32"
              }}>{bin.status}</span></div>
            </div>
          ))}
        </div>
      </section>
      <section style={{ marginBottom: "2rem" }}>
        <h2>Bin Locations (Live Map)</h2>
        <div style={{
          width: "100%", height: "300px", background: "#dcdde1", borderRadius: "8px", position: "relative", marginBottom: "1rem"
        }}>
          {binStatuses.map(bin => (
            <div key={bin.id} style={{
              position: "absolute",
              left: `${30 + bin.id * 80}px`,
              top: `${100 + bin.id * 30}px`,
              background: "#273c75",
              color: "#fff",
              padding: "5px 10px",
              borderRadius: "5px"
            }}>
              {bin.location}
            </div>
          ))}
        </div>
      </section>
      <section style={{ marginBottom: "2rem" }}>
        <h2>Historical Data</h2>
        <ul>
          <li>Main Street: Fills every 2 days, mostly organic waste, last collected 1 day ago.</li>
          <li>Park Area: Fills every 3 days, mixed waste, last collected 2 days ago.</li>
          <li>Bus Stand: Fills daily, plastic waste, last collected today.</li>
        </ul>
      </section>
      <section style={{ marginBottom: "2rem" }}>
        <h2>Live Bin Status Updates</h2>
        <div>Bin status for Park Area changes every 5 seconds (simulated).</div>
      </section>
      <section style={{ marginBottom: "2rem" }}>
        <h2>Nearest Truck Driver</h2>
        <div style={{
          background: "#fff", padding: "1rem", borderRadius: "8px", boxShadow: "0 2px 8px rgba(44,62,80,0.1)", minWidth: "200px"
        }}>
          <strong>Name:</strong> {truckDriver.name}<br />
          <strong>Phone:</strong> {truckDriver.phone}<br />
          <strong>Location:</strong> {truckDriver.location}
        </div>
      </section>
      <section>
        <h2>Public Opinion (from Flutter app)</h2>
        <ul>
          {publicOpinions.map((op, idx) => (
            <li key={idx}><strong>{op.user}:</strong> {op.opinion}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default Dashboard;