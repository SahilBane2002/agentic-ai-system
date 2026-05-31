"use client";

import { useState } from "react";
import { runWorkflow, RunResult } from "@/lib/api";
import WorkflowResult from "@/components/WorkflowResult";

const EXAMPLES = [
  "Research the latest trends in AI agent frameworks",
  "Find a free slot on my calendar next week and draft a meeting invite",
  "Classify my inbox and draft a reply to the most recent email",
];

export default function Home() {
  const [goal, setGoal] = useState("");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const isResearch = goal.toLowerCase().includes("research") ||
    goal.toLowerCase().includes("find") ||
    goal.toLowerCase().includes("search");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!goal.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const context = isResearch && query ? { query } : {};
      const data = await runWorkflow(goal.trim(), context);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* Hero */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">
          What should the agent do?
        </h1>
        <p className="mt-2 text-gray-500 text-sm">
          Describe your goal in plain English — the system routes it to the right agent and executes a plan.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        <textarea
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="e.g. Research competitor pricing for AI APIs"
          rows={3}
          className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100 resize-none"
        />

        {isResearch && (
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search query (optional, defaults to your goal)"
            className="w-full rounded-xl border border-gray-200 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 shadow-sm focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-100"
          />
        )}

        <button
          type="submit"
          disabled={loading || !goal.trim()}
          className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? (
            <>
              <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Running…
            </>
          ) : (
            <>
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Run Agent
            </>
          )}
        </button>
      </form>

      {/* Examples */}
      {!result && !loading && (
        <div className="mt-6">
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-3">Try an example</p>
          <div className="flex flex-col gap-2">
            {EXAMPLES.map((ex) => (
              <button
                key={ex}
                onClick={() => setGoal(ex)}
                className="text-left text-sm text-gray-600 hover:text-indigo-600 hover:bg-indigo-50 px-3 py-2 rounded-lg transition-colors border border-transparent hover:border-indigo-100"
              >
                {ex}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Result */}
      {result && <WorkflowResult result={result} />}
    </div>
  );
}
