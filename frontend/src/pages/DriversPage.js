import React, { useEffect, useState } from "react";
import { collection, getDocs, updateDoc, doc } from "firebase/firestore";
import { db } from "../firebase"; // adjust path if needed

export default function DriversPage() {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDrivers = async () => {
    setLoading(true);
    try {
      const snapshot = await getDocs(collection(db, "drivers"));

      const driverList = snapshot.docs
        .map(doc => ({ id: doc.id, ...doc.data() }))
        .filter(user => user.userType === "driver");

      setDrivers(driverList);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchDrivers();
  }, []);

  // ✅ Approve Driver
  const approve = async (id) => {
    try {
      await updateDoc(doc(db, "drivers", id), {
        status: "approved"
      });
      fetchDrivers();
    } catch (e) {
      console.error(e);
    }
  };

  // ❌ Reject Driver
  const reject = async (id) => {
    try {
      await updateDoc(doc(db, "drivers", id), {
        status: "rejected"
      });
      fetchDrivers();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <h2>Drivers Details</h2>

      {loading ? <p>Loading...</p> : (
        <div style={{ background: "#fff", padding: 16, borderRadius: 8 }}>
          {drivers.length === 0 ? <p>No drivers found</p> : (
            <ul>
              {drivers.map(d => (
                <li key={d.id} style={{ marginBottom: 10 }}>
                  <strong>{d.name}</strong> — {d.phone} — {d.status || "pending"}

                  <div style={{ marginTop: 6 }}>
                    <button onClick={() => approve(d.id)} style={{ marginRight: 8 }}>
                      Approve
                    </button>
                    <button onClick={() => reject(d.id)}>
                      Reject
                    </button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}