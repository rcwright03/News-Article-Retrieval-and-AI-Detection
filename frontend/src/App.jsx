import React, { useEffect, useState } from "react";
import api from "./api";

export default function App() {
  const [q, setQ] = useState("news");
  const [items, setItems] = useState([]);
  const [error, setError] = useState("");

  const runSearch = async () => {
    try {
      setError("");
      const res = await api.get("/search", { params: { q } });
      setItems(res.data.items || []);
    } catch (e) {
      setError(e?.response?.data?.detail || e?.message || "Could not fetch results");
      setItems([]);
    }
  };

  useEffect(() => { runSearch(); }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 to-slate-800 text-slate-100 p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        <h1 className="text-4xl font-bold text-center text-amber-300">IR News Search</h1>

        <form onSubmit={(e) => { e.preventDefault(); runSearch(); }} className="flex justify-center gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search trending topics…"
            className="px-4 py-2 rounded-md w-full max-w-xl text-slate-900 outline-none"
          />
          <button className="px-5 py-2 rounded-md bg-blue-600 hover:bg-blue-700 transition">
            Search
          </button>
        </form>

        {error && <p className="text-center text-red-400">{error}</p>}

        <div className="grid md:grid-cols-2 gap-6">
          <div className="bg-slate-800/60 backdrop-blur rounded-xl p-5 shadow">
            <h3 className="text-xl font-semibold text-amber-300 mb-3">Results</h3>
            <ul className="space-y-3">
              {items.map(it => (
                <li key={it.id} className="p-3 rounded-lg bg-slate-700/70 hover:bg-slate-700 transition">
                  <strong className="block text-lg">{it.title}</strong>
                  <p className="text-slate-300 text-sm">{it.snippet}</p>
                </li>
              ))}
              {items.length === 0 && <li className="text-slate-400">No results.</li>}
            </ul>
          </div>

          <div className="bg-slate-800/60 backdrop-blur rounded-xl p-5 shadow">
            <h3 className="text-xl font-semibold text-amber-300 mb-3">Article</h3>
            <p className="text-slate-300">Select a result (detail view coming next).</p>
          </div>
        </div>
      </div>
    </div>
  );}
