import React, { useEffect, useState } from "react";

// const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";



const API_BASE = import.meta.env.VITE_API_BASE_URL ?? window.location.origin;

if (import.meta.env.MODE === "production" && !import.meta.env.VITE_API_BASE_URL) {
  // Helpful runtime warning if you forgot to set the build-time env for production.
  // This will show in the browser console of deployed app.
  console.warn("VITE_API_BASE_URL is not set. Falling back to window.location.origin:", API_BASE);
} else {
  // Helpful in dev to confirm which API URL is used
  console.log("API_BASE =", API_BASE);
}



export default function Workers() {
  const [workers, setWorkers] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const es = new EventSource(`${API_BASE}/api/events`);

    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);

    es.addEventListener("workers", (ev) => {
      try {
        const payload = JSON.parse(ev.data);
        setWorkers(payload.workers || []);
      } catch (err) {
        console.error("SSE parse error", err);
      }
    });

    (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/workers`);
        if (res.ok) setWorkers(await res.json());
      } catch {}
    })();

    return () => es.close();
  }, []);

  return (
    <div>
      <div
        className={`text-sm mb-3 font-medium ${
          connected ? "text-green-600" : "text-red-600"
        }`}
      >
        SSE Status: {connected ? "Connected" : "Disconnected"}
      </div>

      <div className="space-y-3">
        {workers.map((w) => (
          <div
            key={w.id}
            className="p-3 rounded-lg border bg-gray-50 shadow-sm hover:shadow-md transition"
          >
            <div className="font-medium text-gray-800">{w.hostname}</div>
            <div className="text-sm">
              Status:{" "}
              <span
                className={
                  w.status === "alive" ? "text-green-600" : "text-red-600"
                }
              >
                {w.status}
              </span>
            </div>
            <div className="text-xs text-gray-500">
              Last heartbeat: {w.last_heartbeat}
            </div>
          </div>
        ))}

        {workers.length === 0 && (
          <div className="text-gray-500 text-sm">No workers connected</div>
        )}
      </div>
    </div>
  );
}
