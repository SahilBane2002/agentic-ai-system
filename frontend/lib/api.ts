const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

function headers() {
  const h: Record<string, string> = { "Content-Type": "application/json" };
  if (API_KEY) h["X-API-Key"] = API_KEY;
  return h;
}

async function handle(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

export type TaskState = "pending" | "running" | "done" | "error" | "skipped";

export interface Task {
  id: string;
  type: string;
  state: TaskState;
  payload: Record<string, unknown>;
  result: unknown;
}

export interface Workflow {
  id: string;
  name: string;
  status: string;
  goal: string;
  created_at: string | null;
  tasks: Task[];
}

export interface RunResult {
  route: { agent: string; plan: { type: string; payload: Record<string, unknown> }[] };
  workflow: Workflow;
  final: Record<string, unknown>;
}

export async function runWorkflow(
  goal: string,
  context: Record<string, unknown> = {}
): Promise<RunResult> {
  const res = await fetch(`${API_URL}/workflows/run`, {
    method: "POST",
    headers: headers(),
    body: JSON.stringify({ goal, context }),
  });
  return handle(res);
}

export async function listWorkflows(limit = 20, offset = 0): Promise<Workflow[]> {
  const res = await fetch(`${API_URL}/workflows?limit=${limit}&offset=${offset}`, {
    headers: headers(),
  });
  return handle(res);
}

export async function getWorkflow(id: string): Promise<Workflow> {
  const res = await fetch(`${API_URL}/workflows/${id}`, { headers: headers() });
  return handle(res);
}
