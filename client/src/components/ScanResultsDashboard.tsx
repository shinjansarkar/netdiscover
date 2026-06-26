"use client";

import { useState, useEffect } from "react";
import { Server, Info, Network } from "lucide-react";

export default function ScanResultsDashboard({ report, hosts }: { report: any; hosts: any[] }) {
  const [selectedHostIp, setSelectedHostIp] = useState<string | null>(null);

  useEffect(() => {
    if (hosts.length > 0 && !selectedHostIp) {
      setSelectedHostIp(hosts[0].ip);
    }
  }, [hosts, selectedHostIp]);

  const selectedHost = hosts.find((h: any) => h.ip === selectedHostIp) || hosts[0];
  const totalOpenPorts = hosts.reduce((sum: number, host: any) => sum + host.open_ports.length, 0);

  return (
    <div className="space-y-8 mt-8">
      {/* Metadata Summary Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="brutal-card p-4 bg-white">
          <div className="text-xs uppercase font-bold text-gray-500 mb-1">Hosts Found</div>
          <div className="text-3xl font-black font-mono">{report.metadata.hosts_found}</div>
        </div>
        <div className="brutal-card p-4 bg-[#CCFF00]">
          <div className="text-xs uppercase font-bold text-gray-700 mb-1">Ports Open</div>
          <div className="text-3xl font-black font-mono">{totalOpenPorts}</div>
        </div>
        <div className="brutal-card p-4 !bg-[#FF00FF] text-black">
          <div className="text-xs uppercase font-bold text-black mb-1">Scan Type</div>
          <div className="text-xl font-black font-mono mt-2">{report.metadata.scan_type}</div>
        </div>
        <div className="brutal-card p-4 bg-white">
          <div className="text-xs uppercase font-bold text-gray-500 mb-1">Duration</div>
          <div className="text-3xl font-black font-mono">{report.metadata.duration_seconds.toFixed(2)}s</div>
        </div>
      </div>

      {/* Middle Section: Inventory & Node Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Inventory Discovery Table */}
        <div className="brutal-card p-0 overflow-hidden bg-white flex flex-col h-[500px] lg:col-span-2">
          <div className="p-4 border-b-[3px] border-brutal-black bg-brutal-black text-white font-bold uppercase flex justify-between items-center">
            <span>Inventory Discovery</span>
          </div>
          <div className="overflow-auto flex-1">
            <table className="w-full text-left border-collapse">
              <thead className="bg-[#f0f0f0] font-mono text-xs uppercase border-b-[3px] border-brutal-black sticky top-0 z-10">
                <tr>
                  <th className="p-3 border-r-[3px] border-brutal-black">IP Address</th>
                  <th className="p-3 border-r-[3px] border-brutal-black">Hostname</th>
                  <th className="p-3 border-r-[3px] border-brutal-black">Status</th>
                  <th className="p-3 border-r-[3px] border-brutal-black">MAC Address</th>
                  <th className="p-3">Response</th>
                </tr>
              </thead>
              <tbody>
                {hosts.map((host: any, idx: number) => (
                  <tr
                    key={idx}
                    onClick={() => setSelectedHostIp(host.ip)}
                    className={`font-mono text-sm border-b-[3px] border-brutal-black cursor-pointer transition-colors ${selectedHostIp === host.ip ? 'bg-brutal-accent1' : 'hover:bg-gray-100'}`}
                  >
                    <td className="p-3 border-r-[3px] border-brutal-black font-bold">{host.ip}</td>
                    <td className="p-3 border-r-[3px] border-brutal-black">{host.hostname}</td>
                    <td className="p-3 border-r-[3px] border-brutal-black">
                      <span className={`px-2 py-1 text-xs font-bold border-2 border-brutal-black ${host.status === 'ONLINE' ? 'bg-brutal-black text-white' : 'bg-red-500 text-white'}`}>
                        {host.status}
                      </span>
                    </td>
                    <td className="p-3 border-r-[3px] border-brutal-black">{host.mac}</td>
                    <td className={`p-3 font-bold ${selectedHostIp === host.ip ? 'text-brutal-black font-black' : 'text-[#10b981]'}`}>{host.response_time}</td>
                  </tr>
                ))}
                {hosts.length === 0 && (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-gray-500 font-bold uppercase">No hosts discovered</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Node Details */}
        <div className="space-y-6 h-[500px] flex flex-col">
          {selectedHost ? (
            <>
              <div className="brutal-card p-6 bg-white shrink-0">
                <div className="flex items-start gap-4">
                  <div className="p-3 border-2 border-brutal-black rounded-full bg-[#151515]">
                    <Info size={32} className="text-brutal-accent1" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xl lg:text-2xl font-black font-mono text-brutal-black truncate" title={selectedHost.ip}>{selectedHost.ip}</div>
                    <div className="text-gray-500 font-bold uppercase text-xs lg:text-sm mb-4 truncate" title={selectedHost.hostname}>{selectedHost.hostname}</div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-brutal-black p-3 border-2 border-brutal-black text-white">
                        <div className="text-xs uppercase text-gray-400 font-bold mb-1">Detected OS</div>
                        <div className="font-mono text-sm text-brutal-accent1">{selectedHost.os}</div>
                      </div>
                      <div className="bg-brutal-black p-3 border-2 border-brutal-black text-white">
                        <div className="text-xs uppercase text-gray-400 font-bold mb-1">Status</div>
                        <div className="font-mono text-sm text-white">{selectedHost.status}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="brutal-card p-0 overflow-hidden bg-white flex-1 flex flex-col">
                <div className="p-3 border-b-[3px] border-brutal-black bg-[#f0f0f0] font-bold uppercase text-sm">
                  Open Ports on Node
                </div>
                <div className="overflow-x-auto overflow-y-auto flex-1">
                  {selectedHost.open_ports.length > 0 ? (
                    <table className="w-full text-left border-collapse">
                      <thead className="bg-brutal-black text-white font-mono text-xs uppercase sticky top-0">
                        <tr>
                          <th className="p-3 border-r-[3px] border-brutal-black">Port</th>
                          <th className="p-3 border-r-[3px] border-brutal-black">Service</th>
                          <th className="p-3 border-r-[3px] border-brutal-black">Product</th>
                          <th className="p-3">Version</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedHost.open_ports.map((port: any, pIdx: number) => (
                          <tr key={pIdx} className="font-mono text-sm border-b-[3px] border-brutal-black last:border-b-0">
                            <td className="p-3 border-r-[3px] border-brutal-black font-bold">{port.port}</td>
                            <td className="p-3 border-r-[3px] border-brutal-black">{port.service}</td>
                            <td className="p-3 border-r-[3px] border-brutal-black">{port.product !== "Unknown" ? port.product : "-"}</td>
                            <td className="p-3">{port.version !== "Unknown" ? port.version : "-"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="h-full flex items-center justify-center p-6 font-mono text-gray-500 text-sm">
                      No open ports detected
                    </div>
                  )}
                </div>
              </div>
            </>
          ) : (
            <div className="brutal-card flex-1 flex items-center justify-center text-gray-500 font-bold uppercase">
              Select a host to view details
            </div>
          )}
        </div>
      </div>

      {/* Topology Visualization */}
      <div className="brutal-card p-0 overflow-hidden bg-brutal-bg h-[500px] flex flex-col relative">
        <div className="p-4 border-b-[3px] border-brutal-black bg-brutal-black text-white font-bold uppercase flex justify-between items-center z-10">
          <span className="flex items-center gap-2"><Network size={20} /> Topology Visualization</span>
        </div>
        <div className="flex-1 relative w-full h-full bg-[#151515] overflow-hidden">
          {hosts.length === 0 ? (
            <div className="text-white font-mono flex items-center justify-center h-full text-xl">No hosts available for topology mapping.</div>
          ) : (
            <svg width="100%" height="100%" className="absolute inset-0">
              <g style={{ transform: 'translate(50%, 50%)' }}>
                <circle cx="0" cy="0" r="24" fill="#CCFF00" stroke="#000" strokeWidth="4" />
                <text x="0" y="45" textAnchor="middle" fill="#fff" fontSize="14" fontFamily="monospace" fontWeight="bold">Gateway</text>
                <text x="0" y="60" textAnchor="middle" fill="#888" fontSize="10" fontFamily="monospace">{report.metadata.target}</text>

                {hosts.map((host: any, index: number) => {
                  const angle = (index / hosts.length) * Math.PI * 2;
                  const radius = 180;
                  const x = Math.cos(angle) * radius;
                  const y = Math.sin(angle) * radius;
                  const isOffline = host.status === 'DOWN' || host.status === 'OFFLINE';
                  const isSelected = selectedHostIp === host.ip;

                  return (
                    <g key={index} className="cursor-pointer transition-transform hover:scale-110" onClick={() => setSelectedHostIp(host.ip)}>
                      <line x1="0" y1="0" x2={x} y2={y} stroke={isOffline ? "#f43f5e" : "#10b981"} strokeWidth={isSelected ? "4" : "2"} strokeDasharray={isOffline ? "4,4" : "0"} />
                      <circle cx={x} cy={y} r="16" fill={isSelected ? "#FF00FF" : (isOffline ? "#f43f5e" : "#10b981")} stroke={isSelected ? "#fff" : "#000"} strokeWidth="3" />
                      <text x={x} y={y + 30} textAnchor="middle" fill={isSelected ? "#FF00FF" : "#fff"} fontSize="12" fontFamily="monospace" fontWeight="bold">{host.ip}</text>
                      <text x={x} y={y + 45} textAnchor="middle" fill="#aaa" fontSize="10" fontFamily="monospace">{host.hostname}</text>
                    </g>
                  );
                })}
              </g>
            </svg>
          )}
        </div>
      </div>
    </div>
  );
}
