import React from 'react';

export default function Logo({ size = 64 }) {
  const s = size;
  return (
    <svg width={s} height={s} viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" aria-hidden>
      <defs>
        <linearGradient id="lg_shared" x1="0" x2="1" y1="0" y2="1">
          <stop offset="0%" stopColor="#66bb6a" />
          <stop offset="100%" stopColor="#2e7d32" />
        </linearGradient>
      </defs>
      <circle cx="32" cy="32" r="30" fill="url(#lg_shared)" />
      <path d="M18 38c7-9 21-13 28-6-7 7-9 20-21 20-7 0-9-6-7-14z" fill="#e8f5e9" />
    </svg>
  );
}
