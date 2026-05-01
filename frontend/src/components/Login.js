import React, { useState } from "react";
import './Login.css';
import Logo from './Logo';

function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = (e) => {
  e.preventDefault();

  if (username === "admin" && password === "admin") {
    localStorage.setItem("admin", "true");
    onLogin({ username: "admin" });
  } else {
    alert("Invalid username or password");
  }
};

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-card">
          <div className="brand">
            <div className="logo" aria-hidden>
              <Logo size={40} />
            </div>
            <div>
              <h2>Smart Waste</h2>
              <p className="subtitle">City bin monitoring & collections</p>
            </div>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <div className="form-field">
              <span className="field-icon" aria-hidden>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4z" stroke="#6b7a86" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M20 21v-1c0-2.76-2.24-5-5-5H9c-2.76 0-5 2.24-5 5v1" stroke="#6b7a86" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <input placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} />
            </div>

            <div className="form-field">
              <span className="field-icon" aria-hidden>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="11" width="18" height="11" rx="2" stroke="#6b7a86" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                  <path d="M7 11V8a5 5 0 0110 0v3" stroke="#6b7a86" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
            </div>

            <div className="actions">
              <button type="submit" className="btn-primary">Sign in</button>
            </div>
          </form>

          <div className="footer-note">By signing in you can monitor bin fill levels and schedule pickups.</div>
        </div>

        <div className="side-panel">
          <div className="illustration" aria-hidden>
            <svg viewBox="0 0 640 360" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
              <defs>
                <linearGradient id="g1" x1="0" x2="1" y1="0" y2="1">
                  <stop offset="0%" stopColor="#e8f5e9" />
                  <stop offset="100%" stopColor="#c8e6c9" />
                </linearGradient>
              </defs>
              <rect width="100%" height="100%" fill="url(#g1)" rx="12" />

              {/* bin illustration */}
              <g transform="translate(60,60)">
                <rect x="20" y="80" width="120" height="120" rx="8" fill="#2E7D32" opacity="0.95" />
                <rect x="0" y="60" width="160" height="30" rx="6" fill="#1b5e20" />
                <path d="M40 110 L55 90 L75 115 L95 85 L115 120" stroke="#c8e6c9" strokeWidth="6" strokeLinecap="round" fill="none" opacity="0.9" />
              </g>

              {/* truck */}
              <g transform="translate(260,120)">
                <rect x="0" y="30" width="220" height="70" rx="10" fill="#455a64" />
                <rect x="150" y="0" width="80" height="60" rx="6" fill="#607d8b" />
                <circle cx="50" cy="110" r="18" fill="#37474f" />
                <circle cx="170" cy="110" r="18" fill="#37474f" />
                <rect x="20" y="40" width="100" height="40" rx="6" fill="#81c784" opacity="0.9" />
              </g>

              {/* text */}
              <g transform="translate(60,300)">
                <text x="0" y="0" fontSize="28" fontWeight="800" letterSpacing="0.6" fill="#0b3d00" fontFamily="Inter, Arial, sans-serif">Cleaner Cities</text>
                <text x="0" y="34" fontSize="16" fill="#2f5a3a" fontFamily="Inter, Arial, sans-serif">Visualize bin levels, assign routes and reduce overflow.</text>
              </g>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;