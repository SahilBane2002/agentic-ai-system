import Link from "next/link";

export default function Header() {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto max-w-4xl px-6 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span className="font-semibold text-gray-900 text-lg">Agentic AI</span>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link href="/" className="text-gray-600 hover:text-gray-900 transition-colors">
            Run
          </Link>
          <Link href="/history" className="text-gray-600 hover:text-gray-900 transition-colors">
            History
          </Link>
        </nav>
      </div>
    </header>
  );
}
