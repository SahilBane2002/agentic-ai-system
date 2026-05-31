"use client";

import { useState } from "react";
import { Task } from "@/lib/api";
import { TaskStateBadge } from "./StatusBadge";

function StateIcon({ state }: { state: string }) {
  if (state === "done")
    return (
      <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
        <svg className="w-3.5 h-3.5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
        </svg>
      </div>
    );
  if (state === "error")
    return (
      <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
        <svg className="w-3.5 h-3.5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
    );
  if (state === "skipped")
    return (
      <div className="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
        <svg className="w-3.5 h-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
      </div>
    );
  return (
    <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
      <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
    </div>
  );
}

export default function TaskStep({ task, index }: { task: Task; index: number }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <StateIcon state={task.state} />
        <div className="w-px flex-1 bg-gray-200 mt-1" />
      </div>
      <div className="pb-4 flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xs text-gray-400 font-mono">{index + 1}</span>
          <span className="text-sm font-medium text-gray-800 font-mono">{task.type}</span>
          <TaskStateBadge state={task.state} />
        </div>
        {task.result !== null && task.result !== undefined && (
          <button
            onClick={() => setOpen((o) => !o)}
            className="text-xs text-indigo-600 hover:text-indigo-800 transition-colors"
          >
            {open ? "hide result" : "show result"}
          </button>
        )}
        {open && task.result !== null && task.result !== undefined && (
          <pre className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs text-gray-700 overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(task.result, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
