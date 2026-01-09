import React from "react";
import Metrics from "./Metrics";
import Workers from "./Workers";
import ScheduleForm from "./ScheduleForm";
import TaskTable from "./TaskTable";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 flex flex-col">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 to-blue-500 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold tracking-wide">
              PyTaskFlow 
            </h1>
            <p className="text-sm font-medium opacity-90">
              Distributed Task Scheduler
            </p>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-8 grow space-y-8">
        {/* Row 1: Metrics + Workers */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* System Metrics */}
          <div className="lg:col-span-2 bg-slate-100 rounded-xl p-6 shadow-sm border border-slate-200">
  <h2 className="text-lg font-semibold mb-4 text-slate-800">
    System Metrics
  </h2>
  <Metrics />
</div>


          {/* Worker Status */}
          <div className="bg-indigo-50 rounded-xl p-6 shadow-sm border border-indigo-100">
            <h2 className="text-lg font-semibold mb-4 text-indigo-700">
              Worker Status
            </h2>
            <Workers />
          </div>
        </div>

        {/* Schedule form */}
        <div className="bg-emerald-50 rounded-xl p-6 shadow-sm border border-emerald-100">
          <h2 className="text-lg font-semibold mb-4 text-emerald-700">
            Schedule a New Task
          </h2>
          <ScheduleForm />
        </div>

        {/* Recent Tasks */}
        <div className="bg-blue-50 rounded-xl p-6 shadow-sm border border-blue-100">
          <h2 className="text-lg font-semibold mb-4 text-blue-700">
            Recent Tasks
          </h2>
          <TaskTable />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-blue-600 to-blue-500 text-white">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center">
          <p className="text-sm font-semibold tracking-wide">
            © 2026 PyTaskFlow
          </p>
          <p className="text-xs opacity-90 mt-1">
            Distributed Task Scheduler • Python • FastAPI • gRPC • React • Docker
          </p>
          <p className="text-xs opacity-80 mt-2">
            Developed by <span className="font-medium">Shrinedhi M R</span>
          </p>
        </div>
      </footer>
    </div>
  );
}
