import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { Link } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Logo from "./Logo"; // use same logo component as admin login

/* Helper to create leaflet icons */
function makeIcon(url, size = [28, 38]) {
  return new L.Icon({
    iconUrl: url,
    iconSize: size,
    iconAnchor: [Math.round(size[0] / 2), size[1]],
    popupAnchor: [0, -size[1] + 8],
    shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
    shadowSize: [41, 41],
    shadowAnchor: [12, 41],
  });
}

const ICONS = {
  green: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
  yellow: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png",
  red: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
  truck: "https://cdn-icons-png.flaticon.com/512/1995/1995574.png",
};

const binIconMap = {
  Empty: makeIcon(ICONS.green),
  "Half-Full": makeIcon(ICONS.yellow),
  Full: makeIcon(ICONS.red),
};
const truckIcon = makeIcon(ICONS.truck, [36, 36]);

const initialBins = [
  { id: "1 - Thampanoor", name: "Thampanoor", lat: 8.4821, lng: 76.9470, level: 19, status: "Empty" },
  { id: "2 - East Fort", name: "East Fort (Padmanabhaswamy)", lat: 8.4868, lng: 76.9476, level: 10, status: "Empty" },
  { id: "3 - Kowdiar", name: "Kowdiar", lat: 8.5046, lng: 76.9643, level: 45, status: "Half-Full" },
  { id: "4 - Technopark", name: "Technopark (Kazhakuttam)", lat: 8.5628, lng: 76.8756, level: 92, status: "Full" },
  { id: "5 - Kovalam", name: "Kovalam Beach", lat: 8.4116, lng: 76.9780, level: 26, status: "Empty" },
  { id: "6 - Vellayambalam", name: "Vellayambalam", lat: 8.4968, lng: 76.9500, level: 34, status: "Empty" },
];

function createTrucksFromBins(bins) {
  return bins.map((b, i) => ({
    id: `T${i + 1}`,
    name: `${i + 1} - ${b.name}`,
    lat: b.lat + (Math.random() * 0.002 - 0.001),
    lng: b.lng + (Math.random() * 0.002 - 0.001),
    status: "Available",
    assignedBin: b.id,
  }));
}

export default function Dashboard({ onLogout, user }) {
  const center = [8.4868, 76.9476]; // Trivandrum center
  const [bins, setBins] = useState(initialBins);
  const [trucks, setTrucks] = useState(() => createTrucksFromBins(initialBins));

  useEffect(() => {
    const iv = setInterval(() => {
      setBins(bs =>
        bs.map(b => {
          const delta = Math.round((Math.random() - 0.45) * 18);
          const level = Math.max(0, Math.min(100, b.level + delta));
          const status = level > 80 ? "Full" : level > 40 ? "Half-Full" : "Empty";
          return { ...b, level, status };
        })
      );
      setTrucks(ts =>
        ts.map(t => ({
          ...t,
          lat: t.lat + (Math.random() - 0.5) * 0.0012,
          lng: t.lng + (Math.random() - 0.5) * 0.0012,
        }))
      );
    }, 4500);
    return () => clearInterval(iv);
  }, []);

  const totalBins = bins.length;
  const fullCount = bins.filter(b => b.status === "Full").length;
  const collected = 0;
  const avgLevel = Math.round(bins.reduce((s, b) => s + b.level, 0) / Math.max(1, bins.length));

  function nearestTruckForBin(bin) {
    let best = Infinity, pick = null;
    for (const tr of trucks) {
      const d2 = (tr.lat - bin.lat) ** 2 + (tr.lng - bin.lng) ** 2;
      if (d2 < best) { best = d2; pick = tr; }
    }
    return pick;
  }

  const greenBtnStyle = {
    background: "#1e6b37",
    color: "#fff",
    padding: "10px 16px",
    borderRadius: 8,
    textDecoration: "none",
    display: "inline-block",
    marginRight: 10
  };

  const logoutStyle = {
    background: "#e53935", // red
    color: "#fff",
    border: "none",
    padding: "8px 12px",
    borderRadius: 8,
    cursor: "pointer"
  };

  return (
    <div style={{ fontFamily: "Segoe UI, Arial, sans-serif", background: "#f3fbf5", minHeight: "100vh" }}>
      <header style={{ padding: 18, display: "flex", alignItems: "center", gap: 12 }}>
        {/* use same Logo as admin screen */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Logo size={48} />
          <div>
            <div style={{ fontSize: 20, fontWeight: 700, color: "#18462b" }}>Smart Waste Dashboard</div>
            <div style={{ fontSize: 12, color: "#467555" }}>Real-time waste monitoring & collection management — Trivandrum</div>
          </div>
        </div>

        <div style={{ marginLeft: "auto", display: "flex", gap: 10 }}>
          <Link to="/profile" style={{ ...greenBtnStyle, padding: "8px 12px", background: "#2f8a4a" }}>Profile</Link>
          <button onClick={onLogout} style={logoutStyle}>Logout</button>
        </div>
      </header>

      <div style={{ margin: "18px auto", maxWidth: 1100 }}>
        <div style={{ background: "linear-gradient(90deg,#e8f8ec,#d7f0df)", padding: 26, borderRadius: 12, boxShadow: "0 6px 20px rgba(30,100,50,0.06)", textAlign: "center" }}>
          <h1 style={{ margin: 0, color: "#1e6b37", fontSize: 28 }}>Healthy Streets, Smarter Waste</h1>
          <p style={{ marginTop: 6, color: "#3b6b4b" }}>Monitor bins, optimize routes, and reduce overflow — live view for Trivandrum</p>
        </div>

        <div style={{ display: "flex", justifyContent: "center", gap: 12, marginTop: 18 }}>
          {[
            { title: "Total Bins", value: totalBins },
            { title: "Full", value: fullCount },
            { title: "Collected", value: collected },
            { title: "Avg Level", value: `${avgLevel}%` },
          ].map((w, i) => (
            <div key={i} style={{ background: "#ffffff", borderRadius: 8, padding: 14, width: 180, textAlign: "center", boxShadow: "0 6px 18px rgba(30,100,50,0.06)" }}>
              <div style={{ fontSize: 12, color: "#2f6b3f" }}>{w.title}</div>
              <div style={{ fontSize: 20, fontWeight: 700, marginTop: 6, color: "#154724" }}>{w.value}</div>
            </div>
          ))}
        </div>

        <div style={{ display: "flex", gap: 18, marginTop: 18 }}>
          <div style={{ flex: 1 }}>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
              {bins.map(b => (
                <div key={b.id} style={{ background: "#fff", padding: 12, borderRadius: 10, minWidth: 160, boxShadow: "0 6px 16px rgba(30,100,50,0.04)" }}>
                  <div style={{ fontSize: 13, fontWeight: 700 }}>{b.id}</div>
                  <div style={{ marginTop: 6, color: "#666", fontSize: 13 }}>{b.name}</div>
                  <div style={{ marginTop: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ fontSize: 12, color: "#444" }}>Status: <strong style={{ color: b.status === "Full" ? "#e84118" : b.status === "Half-Full" ? "#f39c12" : "#44bd32" }}>{b.status}</strong></div>
                    <div style={{ fontSize: 12, color: "#444" }}>Level: <strong>{b.level}%</strong></div>
                  </div>
                </div>
              ))}
            </div>

            <h3 style={{ color: "#1b4f31", marginBottom: 8 }}>Bin Locations (Live Map)</h3>
            <div style={{ height: 360, borderRadius: 12, overflow: "hidden", boxShadow: "0 8px 20px rgba(30,100,50,0.06)" }}>
              <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
                {bins.map(bin => (
                  <Marker key={bin.id} position={[bin.lat, bin.lng]} icon={binIconMap[bin.status] || binIconMap.Empty}>
                    <Popup>
                      <div style={{ minWidth: 220 }}>
                        <strong>{bin.name}</strong>
                        <div style={{ marginTop: 6 }}>Bin ID: <strong>{bin.id}</strong></div>
                        <div>Level: <strong>{bin.level}%</strong></div>
                        <div>Status: <strong style={{ color: bin.status === "Full" ? "#e84118" : bin.status === "Half-Full" ? "#f39c12" : "#44bd32" }}>{bin.status}</strong></div>
                        <div style={{ marginTop: 8 }}>
                          Nearest Truck:
                          <div style={{ marginTop: 4, fontWeight: 700 }}>{nearestTruckForBin(bin)?.name || "—"}</div>
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {trucks.map(tr => (
                  <Marker key={tr.id} position={[tr.lat, tr.lng]} icon={truckIcon}>
                    <Popup>
                      <div style={{ minWidth: 180 }}>
                        <strong>{tr.name}</strong>
                        <div style={{ marginTop: 6 }}>Status: <strong>{tr.status}</strong></div>
                        <div>Assigned: <strong>{tr.assignedBin}</strong></div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>

            {/* Action widgets under the map */}
            <div style={{ marginTop: 12 }}>
              <Link to="/notifications" style={greenBtnStyle}>All Notifications</Link>
              <Link to="/history" style={greenBtnStyle}>History</Link>
              <Link to="/suggestions" style={greenBtnStyle}>Suggestions / Complaints</Link>
              <Link to="/drivers" style={greenBtnStyle}>Drivers Details</Link>
            </div>
          </div>

          <aside style={{ width: 320 }}>
            <div style={{ background: "#fff", padding: 14, borderRadius: 10, boxShadow: "0 6px 18px rgba(30,100,50,0.04)", marginBottom: 12 }}>
              <h4 style={{ margin: "6px 0", color: "#18462b" }}>Drivers (summary)</h4>
              {trucks.map(t => (
                <div key={t.id} style={{ padding: 10, borderRadius: 8, marginBottom: 8, background: "#f7fff7" }}>
                  <div style={{ fontWeight: 700 }}>{t.name}</div>
                  <div style={{ fontSize: 13, color: "#556" }}>ID: {t.id}</div>
                  <div style={{ fontSize: 13, color: "#556" }}>Assigned: {t.assignedBin}</div>
                  <div style={{ fontSize: 12, color: "#444", marginTop: 6 }}>Location: {t.lat.toFixed(4)}, {t.lng.toFixed(4)}</div>
                </div>
              ))}
            </div>

            <div style={{ background: "#fff", padding: 12, borderRadius: 10, boxShadow: "0 6px 18px rgba(30,100,50,0.04)" }}>
              <h4 style={{ margin: "6px 0", color: "#18462b" }}>Historical Snapshot</h4>
              <ul style={{ paddingLeft: 18, color: "#444" }}>
                <li>Thampanoor: fills ~2 days — mixed waste</li>
                <li>East Fort: fills ~3 days — organics</li>
                <li>Technopark: fills ~1 day — high plastic</li>
              </ul>
            </div>
          </aside>
        </div>
      </div>

      <div style={{ textAlign: "center", color: "#556", paddingBottom: 28 }}>Live data is simulated for demo purposes.</div>
    </div>
  );
}