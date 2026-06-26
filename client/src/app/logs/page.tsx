"use client";

import { useLogs } from "@/hooks/useApi";
import { Terminal } from "lucide-react";

import Loader from "@/components/Loader";

export default function Logs() {
  const { data: logs, error, isLoading } = useLogs();

  if (isLoading) return <Loader text="Loading System Logs..." />;
  if (error) return <div className="p-8 text-red-600 text-xl font-bold bg-black inline-block p-4">Error loading logs</div>;

  return (
    <div className="space-y-8 max-w-6xl mx-auto p-4">
      <header className="mb-8">
        <h1 className="text-5xl font-black uppercase tracking-tighter mb-2">System Logs</h1>
        <p className="text-xl font-mono bg-white inline-block px-2 brutal-border">Backend events and error tracing</p>
      </header>

      <div className="brutal-border brutal-shadow p-0 overflow-hidden bg-brutal-black text-brutal-white">
        <div className="p-4 border-b-[3px] border-brutal-black bg-brutal-white text-brutal-black font-bold uppercase flex gap-2 items-center">
          <Terminal size={24} />
          <span>Terminal Output</span>
        </div>
        <div className="p-6 h-[600px] overflow-y-auto space-y-2">
          {logs?.length === 0 ? (
            <div className="font-mono text-gray-500">No logs available.</div>
          ) : (
            logs?.map((log: any, idx: number) => {
              let colorClass = "text-brutal-white"; // INFO
              if (log.level === "ERROR" || log.level === "CRITICAL") colorClass = "text-brutal-accent2";
              if (log.level === "WARNING") colorClass = "text-brutal-accent1";
              
              return (
                <div key={idx} className={`font-mono text-sm ${colorClass} break-all hover:bg-white/10 p-1`}>
                  <span className="opacity-50 mr-4">[{new Date(log.timestamp).toISOString()}]</span>
                  <span className="font-bold mr-4 w-16 inline-block">[{log.level}]</span>
                  <span>{log.message}</span>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
