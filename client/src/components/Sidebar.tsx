"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Radar, History, FileText, ScrollText } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  if (pathname === "/") return null;

  const links = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/new-scan", label: "New Scan", icon: Radar },
    { href: "/history", label: "Scan History", icon: History },
    { href: "/reports", label: "Reports", icon: FileText },
    { href: "/logs", label: "Logs", icon: ScrollText },
  ];

  return (
    <aside className="w-64 flex-shrink-0 brutal-border bg-brutal-white h-[calc(100vh-2rem)] m-4 flex flex-col brutal-shadow">
      <div className="p-6 border-b-[3px] border-brutal-black bg-brutal-accent1">
        <h1 className="text-2xl font-bold uppercase tracking-tighter">Netdiscover</h1>
      </div>
      <nav className="flex-1 overflow-y-auto p-4 space-y-2">
        {links.map((link) => {
          const isActive = pathname === link.href;
          const Icon = link.icon;
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 p-3 text-lg font-bold brutal-border transition-all ${
                isActive
                  ? "bg-brutal-black text-brutal-accent1"
                  : "bg-brutal-white hover:bg-brutal-accent2 hover:text-brutal-white"
              }`}
            >
              <Icon size={24} />
              {link.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t-[3px] border-brutal-black">
        <div className="text-sm font-mono opacity-70 mb-2">
          Backend: localhost:5000<br/>
          Status: <span className="text-green-600 font-bold">ONLINE</span>
        </div>
        <div className="text-xs font-mono font-bold pt-2 border-t-2 border-dashed border-brutal-black">
          Made with ❤️ by Shinjan
        </div>
      </div>
    </aside>
  );
}
