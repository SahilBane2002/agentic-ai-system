"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getWorkflow, Workflow } from "@/lib/api";
import { AgentBadge, WorkflowStatusBadge } from "@/components/StatusBadge";
import TaskStep from "@/components/TaskStep";

export default function WorkflowDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    getWorkflow(id)
      .then(setWorkflow)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading)
    return (
      <div className="flex items-center gap-2 text-sm text-gray-500 py-12 justify-center">
        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
        Loading…
      </div>
    );

  if (error)
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">{error}</div>
    );

  if (!workflow) return null;

  const agent = workflow.name.replace("wf:", "");

  return (
    <div>
      {/* Back */}
      <Link href="/history" className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-900 mb-6 transition-colors">
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back to history
      </Link>

      {/* Header card */}
      <div className="bg-white border border-gray-200 rounded-2xl p-5 mb-4 shadow-sm">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-lg font-semibold text-gray-900 mb-2">
              {workflow.goal || "(no goal)"}
            </p>
            <div className="flex items-center gap-2">
              <AgentBadge agent={agent} />
              <WorkflowStatusBadge status={workflow.status} />
            </div>
          </div>
          <div className="text-right flex-shrink-0">
            <p className="text-xs font-mono text-gray-400">{workflow.id}</p>
            {workflow.created_at && (
              <p className="text-xs text-gray-400 mt-1">
                {new Date(workflow.created_at).toLocaleString()}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Steps */}
      <div className="bg-white border border-gray-200 rounded-2xl p-5 shadow-sm">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-4">
          Steps · {workflow.tasks.length}
        </p>
        {workflow.tasks.length === 0 ? (
          <p className="text-sm text-gray-500">No steps were executed.</p>
        ) : (
          workflow.tasks.map((task, i) => (
            <TaskStep key={task.id} task={task} index={i} />
          ))
        )}
      </div>
    </div>
  );
}
