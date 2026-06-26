"use client";

import { useState } from "react";
import { useDashboard, useLogs } from "@/hooks/useApi";
import { Activity, Target, Clock, ShieldAlert, Network, Terminal } from "lucide-react";

import Loader from "@/components/Loader";

export default function Dashboard() {
  const { data: dashboardData, error: dashboardError, isLoading: dashboardLoading } = useDashboard();
  const { data: logsData } = useLogs();
  const [showTopology, setShowTopology] = useState(false);

  if (dashboardLoading) return <Loader text="Loading System Data..." />;
  if (dashboardError) return <div className="p-8 text-red-600 text-xl font-bold bg-black inline-block p-4">Error loading dashboard</div>;

  const stats = dashboardData?.stats || { total_scans: 0, active_scans: 0, total_hosts: 0, vulns_found: 0 };
  const recentScans = dashboardData?.scans || [];
  const hosts = dashboardData?.hosts || [];
  const recentLogs = logsData?.slice(0, 5) || [];

  const StatCard = ({ title, value, icon: Icon, colorClass }: any) => (
    <div className={`brutal-card p-6 flex items-start justify-between ${colorClass}`}>
      <div>
        <h3 className="text-sm uppercase font-bold tracking-wider mb-2 opacity-80">{title}</h3>
        <p className="text-5xl font-bold font-mono">{value}</p>
      </div>
      <div className="p-3 border-[3px] border-brutal-black bg-white text-brutal-black rounded-full brutal-shadow">
        <Icon size={32} />
      </div>
    </div>
  );

  return (
    <div className="space-y-8 max-w-6xl mx-auto p-4">
      <header className="mb-8">
        <h1 className="text-5xl font-black uppercase tracking-tighter mb-2">System Overview</h1>
        <p className="text-xl font-mono bg-brutal-accent1 inline-block px-2 brutal-border">Live telemetry and scan statistics</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <StatCard title="Total Scans" value={stats.total_scans} icon={Activity} colorClass="!bg-[#CCFF00] text-black" />
        <StatCard title="Active Hosts" value={stats.active_hosts || 0} icon={Target} colorClass="!bg-[#FF00FF] text-black" />
        <StatCard title="Open Ports" value={stats.open_ports || 0} icon={Clock} colorClass="!bg-white text-black" />
        <StatCard title="Services Identified" value={stats.services_identified || 0} icon={ShieldAlert} colorClass="!bg-red-400 text-black" />
      </div>

      <div className="mt-12">
        
        {/* Topology View */}
        <div className="flex flex-col space-y-8">
          <h2 className="text-3xl font-bold uppercase flex items-center gap-3">
            <span className="bg-brutal-black text-white px-3 py-1">Live Topology View</span>
          </h2>
          
          <div className="brutal-card p-6 bg-brutal-bg h-[400px] flex flex-col relative overflow-hidden">
            {!showTopology ? (
              <div className="flex-1 border-4 border-dashed border-brutal-black flex flex-col items-center justify-center gap-4 cursor-pointer hover:bg-brutal-accent1 transition-colors" onClick={() => setShowTopology(true)}>
                <Network size={64} className="text-brutal-black" />
                <h3 className="text-2xl font-black uppercase tracking-tight">Interactive Node Explorer</h3>
                <p className="text-sm font-mono opacity-80 text-center max-w-xs">Render dynamic node relationships of the latest scanned segment using real backend data.</p>
                <button className="brutal-btn px-6 py-2 mt-2">Enable Topology Map</button>
              </div>
            ) : (
              <div className="flex-1 w-full h-full bg-brutal-black relative rounded-sm border-[3px] border-brutal-black overflow-hidden">
                <button className="absolute top-2 right-2 bg-white text-black font-bold font-mono text-xs px-2 py-1 z-10 border-2 border-black" onClick={() => setShowTopology(false)}>Close</button>
                {hosts.length === 0 ? (
                  <div className="text-white font-mono flex items-center justify-center h-full text-xl">No hosts available from the latest scan.</div>
                ) : (
                  <svg width="100%" height="100%" className="absolute inset-0">
                    <g style={{ transform: 'translate(50%, 50%)' }}>
                      <circle cx="0" cy="0" r="20" fill="#6366f1" stroke="#fff" strokeWidth="2" />
                      <text x="0" y="35" textAnchor="middle" fill="#fff" fontSize="12" fontFamily="monospace" fontWeight="bold">Gateway</text>
                      
                      {hosts.map((host: any, index: number) => {
                        const angle = (index / hosts.length) * Math.PI * 2;
                        const radius = 120;
                        const x = Math.cos(angle) * radius;
                        const y = Math.sin(angle) * radius;
                        const isOffline = host.status === 'DOWN' || host.status === 'OFFLINE';

                        return (
                          <g key={host.id}>
                            <line x1="0" y1="0" x2={x} y2={y} stroke={isOffline ? "#f43f5e" : "#10b981"} strokeWidth="2" strokeDasharray={isOffline ? "4,4" : "0"} />
                            <circle cx={x} cy={y} r="12" fill={isOffline ? "#f43f5e" : "#10b981"} stroke="#fff" strokeWidth="2" />
                            <text x={x} y={y + 25} textAnchor="middle" fill="#fff" fontSize="10" fontFamily="monospace">{host.ip_address}</text>
                            <text x={x} y={y + 40} textAnchor="middle" fill="#aaa" fontSize="9" fontFamily="monospace">{host.hostname}</text>
                          </g>
                        );
                      })}
                    </g>
                  </svg>
                )}
              </div>
            )}
          </div>
        </div>


      </div>

    </div>
  );
}
