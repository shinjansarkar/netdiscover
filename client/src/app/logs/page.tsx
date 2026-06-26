"use client";

import { useState, useEffect } from "react";
import { useLogs, useDashboard } from "@/hooks/useApi";
import { Terminal, RefreshCw, Square } from "lucide-react";

import Loader from "@/components/Loader";

export default function Logs() {
  const [isStopped, setIsStopped] = useState(false);
  const [sarcasticMessage, setSarcasticMessage] = useState<string | null>(null);
  
  const { data: dashboardData } = useDashboard({ refreshInterval: 2000 });
  const [prevTotal, setPrevTotal] = useState(0);
  const [prevActive, setPrevActive] = useState(0);

  useEffect(() => {
    const currentTotal = dashboardData?.stats?.total_scans || 0;
    const currentActive = dashboardData?.stats?.active_scans || 0;

    if (currentTotal > prevTotal || currentActive > prevActive) {
      setIsStopped(false);
      setSarcasticMessage(null);
    }
    
    setPrevTotal(currentTotal);
    setPrevActive(currentActive);
  }, [dashboardData?.stats?.total_scans, dashboardData?.stats?.active_scans, prevTotal, prevActive]);

  const { data: logs, error, isLoading, mutate } = useLogs({
    refreshInterval: isStopped ? 0 : 2000
  });

  const handleStop = () => {
    setIsStopped(true);
    setSarcasticMessage("Terminal paused. Ah yes, because ignoring the logs makes the errors magically disappear. Brilliant strategy.");
  };

  const handleRefresh = () => {
    setIsStopped(false);
    setSarcasticMessage(null);
    mutate();
  };

  if (isLoading && !logs) return <Loader text="Loading System Logs..." />;
  if (error) return <div className="p-8 text-red-600 text-xl font-bold bg-black inline-block p-4">Error loading logs</div>;

  return (
    <div className="space-y-8 max-w-6xl mx-auto p-4">
      <header className="mb-8">
        <h1 className="text-5xl font-black uppercase tracking-tighter mb-2">System Logs</h1>
        <p className="text-xl font-mono bg-white inline-block px-2 brutal-border">Backend events and error tracing</p>
      </header>

      <div className="brutal-border brutal-shadow p-0 overflow-hidden bg-brutal-black text-brutal-white">
        <div className="p-4 border-b-[3px] border-brutal-black bg-brutal-white text-brutal-black font-bold uppercase flex justify-between items-center">
          <div className="flex gap-2 items-center">
            <Terminal size={24} />
            <span>Terminal Output</span>
            {isStopped && <span className="ml-4 text-red-500 bg-black px-2 py-1 text-xs">[ STOPPED ]</span>}
          </div>
          <div className="flex gap-2">
            <button onClick={handleRefresh} className="flex items-center gap-2 brutal-btn bg-brutal-accent2 hover:bg-[#CCFF00] text-black text-xs px-3 py-1">
              <RefreshCw size={14} /> Refresh
            </button>
            {!isStopped && (
              <button onClick={handleStop} className="flex items-center gap-2 brutal-btn bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1">
                <Square size={14} /> Stop
              </button>
            )}
          </div>
        </div>
        <div className="p-6 h-[600px] overflow-y-auto space-y-2">
          {isStopped ? (
            <div className="font-mono text-gray-500">Logs cleared. Terminal stopped.</div>
          ) : logs?.length === 0 ? (
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
          
          {sarcasticMessage && (
            <div className="mt-4 p-4 border-l-4 border-red-500 text-red-500 bg-red-500/10 font-bold inline-block animate-pulse">
              <span className="opacity-80 mr-2">[SYSTEM SARCASM]</span> {sarcasticMessage}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
