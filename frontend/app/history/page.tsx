"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { listWorkflows, Workflow } from "@/lib/api";
import { AgentBadge, WorkflowStatusBadge } from "@/components/StatusBadge";

function timeAgo(iso: string | null) {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

function agentFromName(name: string) {
  return name.replace("wf:", "");
}

export default function HistoryPage() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listWorkflows(50)
      .then(setWorkflows)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Workflow History</h1>
        <p className="text-sm text-gray-500 mt-1">All past agent runs, newest first.</p>
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-gray-500 py-12 justify-center">
          <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
          </svg>
          Loading…
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{error}</div>
      )}

      {!loading && !error && workflows.length === 0 && (
        <div className="text-center py-16">
          <p className="text-gray-400 text-sm">No workflows yet.</p>
          <Link href="/" className="mt-3 inline-block text-sm text-indigo-600 hover:text-indigo-800">
            Run your first agent →
          </Link>
        </div>
      )}

      {!loading && workflows.length > 0 && (
        <div className="space-y-2">
          {workflows.map((wf) => (
            <Link
              key={wf.id}
              href={`/workflows/${wf.id}`}
              className="block bg-white border border-gray-200 rounded-xl px-4 py-3.5 hover:border-indigo-200 hover:shadow-sm transition-all"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {wf.goal || "(no goal)"}
                  </p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <AgentBadge agent={agentFromName(wf.name)} />
                    <WorkflowStatusBadge status={wf.status} />
                    <span className="text-xs text-gray-400">
                      {wf.tasks.length} step{wf.tasks.length !== 1 ? "s" : ""}
                    </span>
                  </div>
                </div>
                <div className="text-xs text-gray-400 whitespace-nowrap flex-shrink-0 mt-0.5">
                  {timeAgo(wf.created_at)}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
