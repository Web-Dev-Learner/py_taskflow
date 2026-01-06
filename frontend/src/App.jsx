import React from "react";
import Metrics from "./Metrics";
import Workers from "./Workers";
import ScheduleForm from "./ScheduleForm";
import TaskTable from "./TaskTable";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 flex flex-col">
      {/* Header */}
      <header className="bg-blue-600 text-white py-4 shadow-md">
        <div className="container mx-auto px-6 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-wide">
              PyTaskFlow Dashboard
            </h1>
            <p className="text-base font-semibold opacity-95">
              Distributed Task Scheduler
            </p>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="container mx-auto px-6 py-6 grow space-y-6">
        {/* Row 1: Metrics + Workers */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl p-5 shadow-sm border">
            <h2 className="text-lg font-semibold mb-3 text-gray-700">
              System Metrics
            </h2>
            <Metrics />
          </div>

          <div className="bg-white rounded-xl p-5 shadow-sm border">
            <h2 className="text-lg font-semibold mb-3 text-gray-700">
              Worker Status
            </h2>
            <Workers />
          </div>
        </div>

        {/* Row 2: Schedule form */}
        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <h2 className="text-lg font-semibold mb-3 text-gray-700">
            Schedule a New Task
          </h2>
          <ScheduleForm />
        </div>

        {/* Row 3: Task table */}
        <div className="bg-white rounded-xl p-5 shadow-sm border">
          <h2 className="text-lg font-semibold mb-3 text-gray-700">
            Recent Tasks
          </h2>
          <TaskTable />
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-sm text-gray-500 border-t">
        <p className="font-medium">
          © 2026 PyTaskFlow
        </p>
        <p className="text-xs mt-1">
          Distributed Task Scheduler • Python • FastAPI • gRPC • React • Docker
        </p>
      </footer>
    </div>
  );
}
