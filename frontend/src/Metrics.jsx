import React, { useEffect, useState } from "react";

// const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


const API_BASE = import.meta.env.VITE_API_BASE_URL ?? window.location.origin;

// if (import.meta.env.MODE === "production" && !import.meta.env.VITE_API_BASE_URL) {
  // Helpful runtime warning if you forgot to set the build-time env for production.
  // This will show in the browser console of deployed app.
//   console.warn("VITE_API_BASE_URL is not set. Falling back to window.location.origin:", API_BASE);
// } else {
  // Helpful in dev to confirm which API URL is used
//   console.log("API_BASE =", API_BASE);
// }

export default function Metrics() {
  const [metrics, setMetrics] = useState(null);

  const fetchMetrics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/metrics`);
      if (!res.ok) throw new Error("Metrics fetch failed");
      setMetrics(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchMetrics();
    const id = setInterval(fetchMetrics, 15000);
    return () => clearInterval(id);
  }, []);

  if (!metrics)
    return <div className="text-gray-500 animate-pulse">Loading metrics…</div>;

  return (
    <div className="space-y-4">
      {/* Cards */}
     <div className="grid grid-cols-4 gap-4">
  {[
    { label: "Total Tasks", value: metrics.total_tasks },
    { label: "Running", value: metrics.tasks_running },
    { label: "Failed", value: metrics.tasks_failed },
    { label: "Done", value: metrics.tasks_done },
  ].map((item) => (

          <div
            key={item.label}
            className="p-4 rounded-lg border bg-gray-50 shadow-sm text-center"
          >
            <div className="text-sm text-gray-500">{item.label}</div>
            <div className="text-2xl font-bold mt-1">{item.value}</div>
          </div>
        ))}
      </div>

      <div>
        <h3 className="font-semibold text-gray-700 mb-2">
          Status Breakdown
        </h3>
        <pre className="bg-gray-100 p-3 rounded-lg text-sm text-gray-700 overflow-auto">
          {JSON.stringify(metrics.tasks_by_status, null, 2)}
        </pre>
      </div>

      <div className="text-gray-700">
        Avg Execution (s):{" "}
        <span className="font-semibold">
          {metrics.avg_execution_seconds.toFixed(2)}
        </span>
      </div>
    </div>
  );
}
