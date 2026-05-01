import React from "react";
export default function HistoryPage() {
  return (
    <div style={{ padding: 24 }}>
      <h2>History</h2>
      <div style={{ background: "#fff", padding: 16, borderRadius: 8 }}>
        <p>Historical bin fill/collection records (demo).</p>
        <ul>
          <li>Thampanoor — collected 2026-01-28</li>
          <li>East Fort — collected 2026-01-27</li>
          <li>Technopark — collected 2026-01-29</li>
        </ul>
      </div>
    </div>
  );
}