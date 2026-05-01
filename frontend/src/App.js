import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import Profile from "./pages/Profile";
import HistoryPage from "./pages/HistoryPage";
import NotificationsPage from "./pages/NotificationsPage";
import SuggestionsPage from "./pages/SuggestionsPage";
import DriversPage from "./pages/DriversPage";

function App() {
  const [auth, setAuth] = useState(null);

  const handleLogin = (user) => {
    setAuth(user || { username: "admin", name: "Admin User" });
  };

  const handleLogout = () => setAuth(null);

  if (!auth) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard onLogout={handleLogout} user={auth} />} />
        <Route path="/profile" element={<Profile user={auth} />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/suggestions" element={<SuggestionsPage />} />
        <Route path="/drivers" element={<DriversPage />} />
      </Routes>
    </Router>
  );
}

export default App;