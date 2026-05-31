import { TaskState } from "@/lib/api";

const stateStyles: Record<string, string> = {
  done: "bg-green-100 text-green-700",
  error: "bg-red-100 text-red-700",
  running: "bg-blue-100 text-blue-700",
  skipped: "bg-gray-100 text-gray-500",
  pending: "bg-yellow-100 text-yellow-700",
};

const agentStyles: Record<string, string> = {
  research: "bg-violet-100 text-violet-700",
  calendar: "bg-cyan-100 text-cyan-700",
  communication: "bg-orange-100 text-orange-700",
  unknown: "bg-gray-100 text-gray-500",
};

export function TaskStateBadge({ state }: { state: TaskState }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${stateStyles[state] ?? "bg-gray-100 text-gray-500"}`}>
      {state}
    </span>
  );
}

export function AgentBadge({ agent }: { agent: string }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${agentStyles[agent] ?? "bg-gray-100 text-gray-500"}`}>
      {agent}
    </span>
  );
}

export function WorkflowStatusBadge({ status }: { status: string }) {
  const style = status === "done" ? stateStyles.done : status === "error" ? stateStyles.error : stateStyles.running;
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${style}`}>
      {status}
    </span>
  );
}
