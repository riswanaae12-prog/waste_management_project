import React, { useState, useEffect, useCallback } from "react";
import MapView from "../mapView";
import { useNavigate, useLocation } from 'react-router-dom';

function TruckDashboard({ user, onLogout }) {
  const truckId = user?.truck_id;
  const [bins, setBins] = useState([]);
  const [trucks, setTrucks] = useState([]);
  const [notes, setNotes] = useState([]);
  const [hist, setHist] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [view, setView] = useState('home'); // home | notifications | history
  const navigate = useNavigate();
  const location = useLocation();

  const fetchBins = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/bins');
      setBins(await res.json());
    } catch (e) { console.error(e); }
  }

  const fetchTrucks = async () => {
    try {
      const res = await fetch('http://localhost:5000/api/trucks');
      setTrucks(await res.json());
    } catch (e) { console.error(e); }
  }

  const fetchNotes = useCallback(async () => {
    try {
      const res = await fetch(`http://localhost:5000/api/notifications?truck_id=${truckId}`);
      setNotes(await res.json());
    } catch (e) { console.error(e); }
  }, [truckId]);

  const fetchHist = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:5000/api/history?months=3');
      const data = await res.json();
      setHist(data.filter(h => h.truck_id === truckId));
    } catch (e) { console.error(e); }
  }, [truckId]);

  useEffect(() => {
    fetchBins();
    fetchTrucks();
    fetchNotes();
    const iv = setInterval(() => { fetchBins(); fetchNotes(); }, 5000);
    return () => clearInterval(iv);
  }, []);

  // derive view from router location
  useEffect(() => {
    const p = location.pathname || '';
    if (p.includes('/truck/notifications')) { fetchNotes(); setView('notifications'); }
    else if (p.includes('/truck/history')) { fetchHist(); setView('history'); }
    else setView('home');
  }, [location, fetchNotes, fetchHist]);

  const respond = async (notif_id, action) => {
    try {
      await fetch('http://localhost:5000/api/notifications/respond', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notif_id, action, truck_id: truckId })
      });
      fetchNotes();
      if (action === 'COLLECTED') fetchHist();
    } catch (e) { console.error(e); }
  }

  const collectBin = async (bin_id) => {
    try {
      await fetch('http://localhost:5000/api/collect_by_truck', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bin_id, truck_id: truckId })
      });
      fetchBins();
      fetchNotes();
    } catch (e) { console.error(e); }
  }

  const sendComplaint = async (type, contact, message) => {
    try {
      await fetch('http://localhost:5000/api/complaints', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, contact, message })
      });
      alert('Submitted');
    } catch (e) { console.error(e); alert('Submit failed'); }
  }

  const total = bins.length;
  const fullCount = bins.filter(b => b.status === 'FULL').length;
  const collectedCount = bins.filter(b => b.status === 'COLLECTED').length;
  const avgLevel = total ? Math.round(bins.reduce((s,b)=>s+(b.level||0),0)/total) : 0;

  return (
    <div style={{ padding: 20, fontFamily: 'Segoe UI, Arial' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Truck Dashboard — {user?.name} ({truckId})</h2>
        <div>
          <button onClick={onLogout} style={{ marginLeft: 8 }}>Logout</button>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8 }}>
        <button onClick={() => navigate('/truck/notifications')} style={{ padding: '6px 10px' }}>View Notifications</button>
        <button onClick={() => navigate('/truck/history')} style={{ padding: '6px 10px' }}>History</button>
      </div>

      <div style={{ display: 'flex', gap: 12 }}>
        <Stat label='Total' value={total} />
        <Stat label='Full' value={fullCount} color='#e84118' />
        <Stat label='Collected' value={collectedCount} color='#44bd32' />
        <Stat label='Avg' value={`${avgLevel}%`} />
      </div>

      <div style={{ marginTop: 12 }}>
        <MapView bins={bins} trucks={trucks} />
      </div>

      {view === 'home' && (
        <div style={{ marginTop: 12 }}>
          <h3>Bins (current data)</h3>
          {bins.map(b => (
            <div key={b.bin_id} style={{ padding: 8, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 700 }}>{b.bin_id}</div>
                <div style={{ fontSize: 12, color: '#666' }}>Status: {b.status} — Level: {b.level}%</div>
              </div>
              <div>
                <button onClick={() => collectBin(b.bin_id)} style={{ padding: '6px 10px', borderRadius: 6, border: 'none', background: '#273c75', color: '#fff' }}>Collect</button>
              </div>
            </div>
          ))}
        </div>
      )}

      {view === 'notifications' && (
        <div style={{ marginTop: 12 }}>
          <h3>Notifications for you</h3>
          {notes.length === 0 && <div>No notifications</div>}
          {notes.map(n => (
            <div key={n.notif_id} style={{ padding: 8, borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontWeight: 700 }}>{n.message}</div>
                <div style={{ fontSize: 12, color: '#666' }}>Bin: {n.bin_id} — Status: {n.status}</div>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                {n.status === 'ACK' && <button onClick={() => respond(n.notif_id, 'COLLECTED')}>Mark Collected</button>}
              </div>
            </div>
          ))}
        </div>
      )}

      {view === 'history' && (
        <div style={{ marginTop: 12 }}>
          <h3>Your Collections (last 3 months)</h3>
          {hist.length === 0 && <div>No history</div>}
          {hist.map(h => (
            <div key={h.id} style={{ padding: 8, borderBottom: '1px solid #eee' }}>
              <div style={{ fontWeight: 700 }}>{h.bin_id} — {h.level_at_collection}%</div>
              <div style={{ fontSize: 12, color: '#666' }}>At: {h.collected_at}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{ marginTop: 12 }}>
        <h3>History (your collections, last 3 months)</h3>
        <button onClick={() => { fetchHist(); setShowHistory(!showHistory); }}>{showHistory ? 'Hide' : 'Show'}</button>
        {showHistory && hist.map(h => (
          <div key={h.id} style={{ padding: 8, borderBottom: '1px solid #eee' }}>
            <div style={{ fontWeight: 700 }}>{h.bin_id} — {h.level_at_collection}%</div>
            <div style={{ fontSize: 12, color: '#666' }}>At: {h.collected_at}</div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: 12 }}>
        <h3>Send Complaint / Suggestion</h3>
        <ComplaintForm onSubmit={sendComplaint} />
      </div>
    </div>
  )
}

function Stat({ label, value, color }) {
  return (
    <div style={{ background: '#fff', padding: 12, borderRadius: 8, minWidth: 120, textAlign: 'center' }}>
      <div style={{ fontSize: 12, color: '#666' }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700, color: color || '#000' }}>{value}</div>
    </div>
  )
}

function ComplaintForm({ onSubmit }) {
  const [type, setType] = useState('complaint');
  const [contact, setContact] = useState('');
  const [msg, setMsg] = useState('');
  return (
    <div style={{ background: '#fff', padding: 12, borderRadius: 8 }}>
      <div style={{ marginBottom: 8 }}>
        <select value={type} onChange={e=>setType(e.target.value)}>
          <option value='complaint'>Complaint</option>
          <option value='suggestion'>Suggestion</option>
        </select>
      </div>
      <div style={{ marginBottom: 8 }}>
        <input placeholder='Contact (email/phone)' value={contact} onChange={e=>setContact(e.target.value)} style={{ width: 360, padding: 6 }} />
      </div>
      <div style={{ marginBottom: 8 }}>
        <textarea placeholder='Message' value={msg} onChange={e=>setMsg(e.target.value)} style={{ width: 360, height: 80, padding: 6 }} />
      </div>
      <div>
        <button onClick={() => onSubmit(type, contact, msg)}>Submit</button>
      </div>
    </div>
  )
}

export default TruckDashboard;
