import React, { useEffect, useState } from "react";
import { collection, getDocs } from "firebase/firestore";
import { db } from "../firebase"; // adjust path

export default function SuggestionsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchItems = async () => {
    setLoading(true);
    try {
      const snapshot = await getDocs(collection(db, "issues"));

      const data = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));

      setItems(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchItems();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h2>Suggestions & Complaints</h2>

      <div style={{ background: "#fff", padding: 16, borderRadius: 8 }}>
        {loading ? <p>Loading...</p> : (
          items.length === 0 ? <p>No issues found</p> : (
            <ul>
              {items.map(i => (
                <li key={i.id} style={{ marginBottom: 10 }}>
                  <strong>{i.issueType}</strong> — {i.userId}
                  <div>{i.description}</div>
                  <small>
                    {new Date(i.createdAt).toLocaleString()}
                  </small>
                </li>
              ))}
            </ul>
          )
        )}
      </div>
    </div>
  );
}