"use client";

import { useState } from "react";
import { Play } from "lucide-react";
import useSWR from 'swr';
import { useReportContent, apiFetch, fetcher } from "@/hooks/useApi";
import ScanResultsDashboard from "@/components/ScanResultsDashboard";

export default function NewScan() {
  const [target, setTarget] = useState("");
  const [portRange, setPortRange] = useState("top100");
  const [discoveryMethod, setDiscoveryMethod] = useState("ICMP");
  const [threads, setThreads] = useState(150);

  const [activeScanId, setActiveScanId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  // Poll scan status
  const { data: scanStatus } = useSWR(
    activeScanId ? `/scan/status/${activeScanId}` : null,
    fetcher,
    { refreshInterval: 1000 }
  );

  // Poll logs
  const { data: logsData } = useSWR(
    activeScanId ? `/logs?limit=20` : null,
    fetcher,
    { refreshInterval: 1000 }
  );

  const handleLaunch = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg("");
    setActiveScanId(null);

    try {
      const data = await apiFetch("/scan/launch", {
        method: "POST",
        body: JSON.stringify({ subnet: target, port_range: portRange, discovery_method: discoveryMethod, threads: threads })
      });
      if (data.status === "success") {
        setActiveScanId(data.scan_id);
      } else {
        setErrorMsg(`Error: ${data.message}`);
      }
    } catch (err) {
      setErrorMsg(`Error: Failed to connect to backend`);
    }
  };

  const progress = scanStatus?.progress || 0;
  const isCompleted = scanStatus?.status === 'COMPLETED' || scanStatus?.status === 'FAILED';

  const { data: reportData } = useReportContent(isCompleted ? activeScanId : null);
  const report = reportData?.content;
  const hosts = report?.hosts || [];

  return (
    <div className="space-y-8 max-w-[1600px] w-full mx-auto p-4">
      <header className="mb-8">
        <h1 className="text-5xl font-black uppercase tracking-tighter mb-2">New Scan</h1>
        <p className="text-xl font-mono bg-brutal-accent1 text-brutal-black inline-block px-2 brutal-border font-bold">Configure and launch discovery</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Configuration Form */}
        <div className="brutal-card p-6 h-fit bg-brutal-white text-brutal-black">
          <h2 className="text-2xl font-black uppercase mb-6 flex items-center gap-2">
            <span className="text-brutal-black">⚙️</span> Configuration
          </h2>
          <form onSubmit={handleLaunch} className="space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-bold uppercase text-gray-700">Subnet Range</label>
              <input
                type="text"
                placeholder="192.168.29.1/24"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                required
                className="w-full p-3 font-mono text-brutal-black bg-white border-2 border-brutal-black focus:border-brutal-accent1 focus:outline-none transition-colors"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-bold uppercase text-gray-700">Port Range</label>
              <div className="flex gap-2">
                {['Common', 'Top 100', 'Top 1000', 'Custom'].map((p) => {
                  const val = p.replace(' ', '').toLowerCase();
                  return (
                    <button
                      key={p}
                      type="button"
                      onClick={() => setPortRange(val)}
                      className={`flex-1 p-2 font-bold uppercase text-xs border-2 transition-colors ${portRange === val ? 'bg-brutal-accent1 border-brutal-black text-brutal-black' : 'bg-white border-brutal-black text-gray-600 hover:bg-gray-100'}`}
                    >
                      {p}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-bold uppercase text-gray-700">Discovery Method</label>
              <select
                value={discoveryMethod}
                onChange={(e) => setDiscoveryMethod(e.target.value)}
                className="w-full p-3 font-mono text-brutal-black bg-white border-2 border-brutal-black focus:border-brutal-accent1 focus:outline-none appearance-none cursor-pointer"
              >
                <option value="ICMP">ICMP Echo Request</option>
                <option value="ARP">ARP Broadcast</option>
                <option value="TCP_SYN">TCP SYN (Stealth)</option>
              </select>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm font-bold uppercase text-gray-700">
                <label>Max Concurrent Threads</label>
                <span className="text-brutal-black font-black">{threads}</span>
              </div>
              <input
                type="range"
                min="10" max="500"
                value={threads}
                onChange={(e) => setThreads(parseInt(e.target.value))}
                className="w-full accent-brutal-black"
              />
            </div>

            <div className="flex gap-4 pt-4">
              <button type="submit" className="flex-1 bg-brutal-accent1 hover:bg-opacity-90 text-brutal-black font-black uppercase tracking-wider p-4 flex items-center justify-center gap-2 border-2 border-brutal-black transition-opacity cursor-pointer">
                <Play size={20} fill="currentColor" /> Start Scan
              </button>
              <button type="button" onClick={() => { setTarget(''); setActiveScanId(null); }} className="px-6 py-4 border-2 border-brutal-black hover:bg-gray-100 text-brutal-black font-bold uppercase text-sm transition-colors cursor-pointer">
                Reset
              </button>
            </div>

            {errorMsg && (
              <div className="p-3 bg-red-500 text-white font-mono text-sm font-bold mt-4 brutal-border">
                {errorMsg}
              </div>
            )}
          </form>
        </div>

        {/* Status and Logs Area */}
        <div className="space-y-6">
          {activeScanId ? (
            <>
              {/* Progress Card */}
              <div className="brutal-border brutal-shadow p-6 bg-[#151515] text-white relative overflow-hidden">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex items-center gap-2 uppercase font-bold text-sm">
                    <div className={`w-3 h-3 rounded-full ${isCompleted ? 'bg-brutal-accent1' : 'bg-brutal-accent2 animate-pulse'}`}></div>
                    <span className={isCompleted ? "text-brutal-accent1" : "text-gray-400"}>{scanStatus?.status || "INITIALIZING..."}</span>
                  </div>
                  <div className="text-4xl font-black font-mono">{progress}%</div>
                </div>

                <div className="grid grid-cols-2 gap-y-6 gap-x-4 mb-2">
                  <div>
                    <div className="text-xs font-bold text-gray-500 uppercase mb-1">Scanning IP</div>
                    <div className="font-mono text-sm">{scanStatus?.current_ip || "Waiting..."}</div>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-500 uppercase mb-1">Target Port</div>
                    <div className="font-mono text-sm">{scanStatus?.target_port || "Waiting..."}</div>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-500 uppercase mb-1">Elapsed</div>
                    <div className="font-mono text-sm text-gray-300">{scanStatus?.elapsed || "00:00:00"}</div>
                  </div>
                  <div>
                    <div className="text-xs font-bold text-gray-500 uppercase mb-1">Remaining</div>
                    <div className="font-mono text-sm text-gray-300">{scanStatus?.remaining || "~ 00:00:00"}</div>
                  </div>
                </div>
              </div>

              {/* Engine Log Card */}
              <div className="brutal-border brutal-shadow p-0 bg-[#111] overflow-hidden flex flex-col h-[400px]">
                <div className="flex items-center gap-2 p-3 bg-[#1a1a1a] border-b-2 border-[#333]">
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  </div>
                  <div className="text-xs font-bold uppercase text-gray-500 ml-4 font-mono flex items-center gap-2">
                    <span>&gt;_</span> ENGINE LOG
                  </div>
                </div>
                <div className="p-4 overflow-y-auto flex-1 space-y-1 font-mono text-xs">
                  {logsData?.map((log: any, idx: number) => {
                    let colorClass = "text-gray-300";
                    if (log.level === 'ERROR' || log.level === 'CRITICAL') colorClass = "text-red-500";
                    if (log.level === 'INFO') colorClass = "text-brutal-accent1";
                    if (log.level === 'WARNING') colorClass = "text-yellow-400";

                    return (
                      <div key={idx} className={`${colorClass} break-all`}>
                        [{log.level}] {log.message}
                      </div>
                    );
                  })}
                  {!isCompleted && (
                    <div className="animate-pulse text-gray-500 mt-2">_</div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="h-full flex flex-col items-center justify-center p-12 border-4 border-dashed border-[#333] text-gray-500 min-h-[400px]">
              <div className="text-6xl mb-4 opacity-50">📡</div>
              <h3 className="text-xl font-bold uppercase tracking-widest text-center">Ready to Scan</h3>
              <p className="text-sm font-mono mt-2 text-center max-w-xs">Configure your scan parameters on the left and hit launch to begin discovering hosts.</p>
            </div>
          )}
        </div>
      </div>

      {/* Render the full interactive results dashboard if the scan is completed */}
      {isCompleted && report && (
        <div className="mt-12 pt-12 border-t-4 border-brutal-black border-dashed">
          <h2 className="text-4xl font-black uppercase mb-8 flex items-center gap-3">
            <span className="bg-[#CCFF00] text-brutal-black px-4 py-2 border-2 border-brutal-black brutal-shadow">Scan Results Dashboard</span>
          </h2>
          <ScanResultsDashboard report={report} hosts={hosts} />
        </div>
      )}
    </div>
  );
}
