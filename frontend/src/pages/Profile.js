import React from "react";

export default function Profile({ user }) {
  return (
    <div style={{ padding: 24, fontFamily: "Segoe UI" }}>
      <h2>Profile</h2>
      <div style={{ background: "#fff", padding: 16, borderRadius: 8, maxWidth: 480 }}>
        <div><strong>Username:</strong> {user?.username || "admin"}</div>
        <div style={{ marginTop: 8 }}><strong>Name:</strong> {user?.name || "Admin User"}</div>
        <div style={{ marginTop: 8 }}><strong>Role:</strong> {user?.role || "Administrator"}</div>
      </div>
    </div>
  );
}