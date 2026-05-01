// ...existing code...
import React from "react";
import "leaflet/dist/leaflet.css";
import { MapContainer, TileLayer, CircleMarker, Marker, Popup, Tooltip } from "react-leaflet";

function MapView({ bins = [], trucks = [], collectBin }) {
  const center = bins.length ? [bins[0].lat, bins[0].lon] : [28.6145, 77.2095];

  const colorFor = (status) => {
    if (!status) return "#888";
    if (status === "FULL") return "#e84118";
    if (status === "HALF") return "#f39c12";
    if (status === "COLLECTED") return "#44bd32";
    return "#888";
  };

  return (
    <MapContainer center={center} zoom={13} style={{ height: "420px", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {bins.map(b => (
        <CircleMarker
          key={b.bin_id}
          center={[b.lat, b.lon]}
          radius={10}
          pathOptions={{ color: colorFor(b.status), fillColor: colorFor(b.status), fillOpacity: 0.85 }}
        >
          <Popup>
            <div style={{ minWidth: 180, fontFamily: "Segoe UI, Arial" }}>
              <strong style={{ fontSize: 14 }}>{b.bin_id}</strong>
              <div style={{ marginTop: 6 }}>
                <div style={{ fontSize: 13 }}>Level: <strong>{b.level}%</strong></div>
                <div style={{ fontSize: 13 }}>Status: <span style={{ color: colorFor(b.status), fontWeight: 700 }}>{b.status}</span></div>
                <div style={{ fontSize: 12, color: "#666", marginTop: 6 }}>Lat: {b.lat.toFixed(4)}, Lon: {b.lon.toFixed(4)}</div>
                <div style={{ marginTop: 8 }}>
                  <button
                    onClick={() => collectBin && collectBin(b.bin_id)}
                    style={{ padding: "6px 10px", background: "#273c75", color: "#fff", border: "none", borderRadius: 6, cursor: "pointer" }}
                  >
                    Collect
                  </button>
                </div>
              </div>
            </div>
          </Popup>
          <Tooltip direction="top" offset={[0, -12]} opacity={1} permanent>
            <span style={{ fontSize: 12, fontWeight: 700 }}>{b.bin_id} — {b.level}%</span>
          </Tooltip>
        </CircleMarker>
      ))}

      {trucks.map(t => (
        <Marker key={t.truck_id} position={[t.lat, t.lon]}>
          <Popup>
            <div style={{ fontFamily: "Segoe UI, Arial" }}>
              <strong>Truck: {t.name}</strong><br />
              <small>{t.phone}</small>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}

export default MapView;
// ...existing code...