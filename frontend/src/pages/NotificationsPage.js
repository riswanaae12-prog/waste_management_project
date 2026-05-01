import React from "react";
export default function NotificationsPage() {
  return (
    <div style={{ padding: 24 }}>
      <h2>All Notifications</h2>
      <div style={{ background: "#fff", padding: 16, borderRadius: 8 }}>
        <ul>
          <li>[2026-01-29 10:00] BIN 4 reached 95% (Technopark)</li>
          <li>[2026-01-29 09:15] BIN 2 decreased to 10% (East Fort)</li>
        </ul>
      </div>
    </div>
  );
}