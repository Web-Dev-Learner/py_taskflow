import React, { useState } from "react";
import axios from "axios";

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


export default function ScheduleForm() {
  const [command, setCommand] = useState("echo 'Hello from UI'");
  const [scheduledAt, setScheduledAt] = useState(
    new Date().toISOString().slice(0, 16)
  );
  const [msg, setMsg] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMsg(null);

    try {
      const iso = new Date(scheduledAt).toISOString();
      const res = await axios.post(`${API_BASE}/api/schedule`, {
        command,
        scheduled_at: iso,
      });

      setMsg({
        type: "success",
        text: `✅ Scheduled task id ${res.data.id}`,
      });
    } catch {
      setMsg({
        type: "error",
        text: "Failed to schedule task. Check backend connection.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={submit}
      className="space-y-4 max-w-2xl bg-gray-50 p-6 rounded-lg border shadow-sm"
    >
      <div>
        <label className="block text-sm font-medium mb-1">Command</label>
        <input
          className="w-full border p-2 rounded focus:ring focus:ring-blue-200"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Schedule</label>
        <input
          type="datetime-local"
          className="w-full border p-2 rounded focus:ring focus:ring-blue-200"
          value={scheduledAt}
          onChange={(e) => setScheduledAt(e.target.value)}
        />
      </div>

      <button
        disabled={loading}
        className="px-5 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Scheduling..." : "Schedule Task"}
      </button>

      {msg && (
        <div
          className={`mt-2 text-sm ${
            msg.type === "success" ? "text-green-600" : "text-red-600"
          }`}
        >
          {msg.text}
        </div>
      )}
    </form>
  );
}
