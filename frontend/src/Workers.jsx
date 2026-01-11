import React, { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? window.location.origin;

// if (import.meta.env.MODE === "production" && !import.meta.env.VITE_API_BASE_URL) {
//   console.warn(
//     "VITE_API_BASE_URL is not set. Falling back to window.location.origin:",
//     API_BASE
//   );
// } else {
//   console.log("API_BASE =", API_BASE);
// }

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
      {/* SSE status */}
      {/* Show warning ONLY when disconnected */}
{!connected && (
  <div className="text-sm mb-3 font-medium text-red-600">
    ⚠ Live updates disconnected
  </div>
)}


      <div className="space-y-3">
        {workers.map((w, index) => {
          // 🔒 SAFE ID HANDLING (real-world correct)
          const sourceId = w.hostname ?? w.id ?? "";
          const shortId = String(sourceId).slice(-6);

          return (
            <div
              key={String(sourceId) || index}
              className="p-3 rounded-lg border bg-white shadow-sm hover:shadow-md transition"
            >
              {/* Display name */}
              <div className="font-semibold text-gray-800">
                Worker {index + 1}
              </div>

              {/* ID (secondary) */}
              <div className="text-xs text-gray-500">
                ID: {shortId || "unknown"}
              </div>

              {/* Status */}
              <div className="text-sm mt-1">
                Status:{" "}
                <span
                  className={
                    w.status === "alive"
                      ? "text-green-600 font-medium"
                      : "text-red-600 font-medium"
                  }
                >
                  {w.status}
                </span>
              </div>

              {/* Heartbeat */}
              <div className="text-xs text-gray-500 mt-1">
                Last heartbeat: {w.last_heartbeat}
              </div>
            </div>
          );
        })}

        {workers.length === 0 && (
          <div className="text-gray-500 text-sm">
            No workers connected
          </div>
        )}
      </div>
    </div>
  );
}
