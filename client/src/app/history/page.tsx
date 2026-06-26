"use client";

import { useScans, apiFetch } from "@/hooks/useApi";
import { Search } from "lucide-react";

import Loader from "@/components/Loader";

export default function History() {
  const { data, error, isLoading, mutate } = useScans();

  if (isLoading) return <Loader text="Loading Scan History..." />;
  if (error) return <div className="p-8 text-red-600 text-xl font-bold bg-black inline-block p-4">Error loading history</div>;

  const scans = data?.scans || [];

  const handleDeleteAll = async () => {
    if (!confirm("Are you sure you want to delete ALL scans? This cannot be undone.")) return;
    try {
      await apiFetch("/scans", { method: "DELETE" });
      mutate();
    } catch (err) {
      console.error("Failed to delete all scans", err);
    }
  };

  const handleDelete = async (scanId: string) => {
    if (!confirm(`Are you sure you want to delete scan ${scanId}?`)) return;
    try {
      await apiFetch(`/scans/${scanId}`, { method: "DELETE" });
      mutate();
    } catch (err) {
      console.error("Failed to delete scan", err);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto p-4">
      <header className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="text-5xl font-black uppercase tracking-tighter mb-2">Scan History</h1>
          <p className="text-xl font-mono bg-white inline-block px-2 brutal-border">Historical records of discovery operations</p>
        </div>
        {scans.length > 0 && (
          <button 
            onClick={handleDeleteAll}
            className="brutal-btn bg-red-500 text-white hover:bg-red-600 px-6 py-3 flex items-center gap-2"
          >
            Delete All History
          </button>
        )}
      </header>

      <div className="brutal-card p-4 flex gap-4 mb-8">
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-4 opacity-50" />
          <input 
            type="text" 
            placeholder="Search by Target IP or Scan ID..." 
            className="w-full p-4 pl-12 text-lg font-mono brutal-border focus:outline-none focus:ring-4 ring-brutal-accent2 bg-brutal-bg"
          />
        </div>
        <button className="brutal-btn px-8">Filter</button>
      </div>

      <div className="brutal-card overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead className="bg-brutal-black text-brutal-white font-mono text-sm uppercase">
            <tr>
              <th className="p-4 border-b-4 border-r-4 border-brutal-black">Scan ID</th>
              <th className="p-4 border-b-4 border-r-4 border-brutal-black">Target Subnet</th>
              <th className="p-4 border-b-4 border-r-4 border-brutal-black">Status</th>
              <th className="p-4 border-b-4 border-r-4 border-brutal-black">Hosts Found</th>
              <th className="p-4 border-b-4 border-brutal-black">Actions</th>
            </tr>
          </thead>
          <tbody>
            {scans.length === 0 && (
              <tr>
                <td colSpan={5} className="p-8 text-center font-bold text-xl">No scans found</td>
              </tr>
            )}
            {scans.map((scan: any) => (
              <tr key={scan.id} className="border-b-[3px] border-brutal-black last:border-b-0 hover:bg-brutal-bg transition-colors">
                <td className="p-4 font-mono font-bold border-r-[3px] border-brutal-black text-sm">{scan.id}</td>
                <td className="p-4 font-bold border-r-[3px] border-brutal-black">{scan.target}</td>
                <td className="p-4 border-r-[3px] border-brutal-black">
                  <span className={`px-2 py-1 text-sm font-bold uppercase border-2 border-brutal-black ${scan.status === 'COMPLETED' ? 'bg-[#CCFF00]' : 'bg-yellow-400'}`}>
                    {scan.status}
                  </span>
                </td>
                <td className="p-4 font-mono font-bold border-r-[3px] border-brutal-black text-center text-xl">{scan.hosts_found || 0}</td>
                <td className="p-4 flex gap-2">
                  <a href={`/reports?scan_id=${scan.id}`} className="brutal-btn text-sm px-4 py-2 inline-block">View Report</a>
                  <button onClick={() => handleDelete(scan.id)} className="brutal-btn bg-red-400 hover:bg-red-500 text-sm px-4 py-2">Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
