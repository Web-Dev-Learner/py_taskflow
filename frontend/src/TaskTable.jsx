import React, { useEffect, useState } from "react";

// const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? window.location.origin;

// if (import.meta.env.MODE === "production" && !import.meta.env.VITE_API_BASE_URL) {
//   console.warn("VITE_API_BASE_URL is not set. Falling back to window.location.origin:", API_BASE);
// } else {
//   console.log("API_BASE =", API_BASE);
// }

export default function TaskTable() {
  const [tasks, setTasks] = useState([]);

  const fetchTasks = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/tasks`);
      if (res.ok) {
        const data = await res.json();
        setTasks(data.reverse()); // show ALL tasks newest-first
      }
    } catch (e) {
      console.error("Failed to fetch tasks", e);
    }
  };

  useEffect(() => {
    fetchTasks();
    const id = setInterval(fetchTasks, 15000);
    return () => clearInterval(id);
  }, []);

  if (!tasks.length)
    return <div className="text-gray-500 text-sm">No recent tasks.</div>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full border-collapse">
        <thead>
          <tr className="bg-gray-100 text-left text-sm text-gray-700">
            <th className="py-2 px-3 border-b">ID</th>
            <th className="py-2 px-3 border-b">Command</th>
            <th className="py-2 px-3 border-b">Status</th>
            <th className="py-2 px-3 border-b">Scheduled</th>
            <th className="py-2 px-3 border-b">Created</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((t) => (
            <tr key={t.id} className="text-sm hover:bg-gray-50">
              <td className="py-2 px-3 border-b">{t.id}</td>
              <td className="py-2 px-3 border-b">{t.command}</td>
              <td
                className={`py-2 px-3 border-b font-medium ${
                  t.status === "done"
                    ? "text-green-600"
                    : t.status === "failed"
                    ? "text-red-600"
                    : t.status === "scheduled"
                    ? "text-yellow-600"
                    : "text-blue-600"
                }`}
              >
                {t.status}
              </td>
              <td className="py-2 px-3 border-b text-gray-600">
                {new Date(t.scheduled_at).toLocaleString()}
              </td>
              <td className="py-2 px-3 border-b text-gray-600">
                {new Date(t.created_at).toLocaleString()}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
