import { RunResult } from "@/lib/api";
import { AgentBadge, WorkflowStatusBadge } from "./StatusBadge";
import TaskStep from "./TaskStep";

function FinalOutput({ agent, final }: { agent: string; final: Record<string, unknown> }) {
  if (agent === "research" && final.summary) {
    return (
      <div className="mt-4 p-4 bg-indigo-50 border border-indigo-100 rounded-xl">
        <p className="text-xs font-medium text-indigo-500 uppercase tracking-wide mb-2">Summary</p>
        <p className="text-sm text-gray-800 leading-relaxed">{String(final.summary)}</p>
      </div>
    );
  }
  if (agent === "calendar" && Array.isArray(final.proposed_times) && final.proposed_times.length > 0) {
    return (
      <div className="mt-4 p-4 bg-cyan-50 border border-cyan-100 rounded-xl">
        <p className="text-xs font-medium text-cyan-600 uppercase tracking-wide mb-2">Proposed Times</p>
        <ul className="space-y-1">
          {(final.proposed_times as { start: string; end: string }[]).map((slot, i) => (
            <li key={i} className="text-sm text-gray-800">
              {new Date(slot.start).toLocaleString()} → {new Date(slot.end).toLocaleString()}
            </li>
          ))}
        </ul>
      </div>
    );
  }
  if (agent === "communication") {
    return (
      <div className="mt-4 p-4 bg-orange-50 border border-orange-100 rounded-xl">
        <p className="text-xs font-medium text-orange-600 uppercase tracking-wide mb-2">Result</p>
        <p className="text-sm text-gray-800">Inbox classified and email drafted.</p>
      </div>
    );
  }
  return null;
}

export default function WorkflowResult({ result }: { result: RunResult }) {
  const { route, workflow, final } = result;

  return (
    <div className="mt-6 border border-gray-200 rounded-2xl overflow-hidden bg-white shadow-sm">
      {/* Header */}
      <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AgentBadge agent={route.agent} />
          <WorkflowStatusBadge status={workflow.status} />
        </div>
        <span className="text-xs text-gray-400 font-mono">{workflow.id.slice(0, 8)}</span>
      </div>

      {/* Steps */}
      <div className="px-5 pt-4">
        {workflow.tasks.length === 0 ? (
          <p className="text-sm text-gray-500 pb-4">No steps — goal could not be routed.</p>
        ) : (
          workflow.tasks.map((task, i) => <TaskStep key={task.id} task={task} index={i} />)
        )}
      </div>

      {/* Final output */}
      {Object.keys(final).length > 0 && (
        <div className="px-5 pb-5">
          <FinalOutput agent={route.agent} final={final} />
        </div>
      )}
    </div>
  );
}
