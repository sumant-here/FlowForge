"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Layers,
  Server,
  Network,
  GitMerge,
  Clock,
  Skull,
  Flame,
  LineChart,
  Cpu,
  Home
} from "lucide-react";

const navigation = [
  { name: "Overview", href: "/dashboard", icon: LayoutDashboard },
  { name: "Jobs Explorer", href: "/jobs", icon: Layers },
  { name: "Worker Fleet", href: "/workers", icon: Server },
  { name: "Priority Queues", href: "/queues", icon: Network },
  { name: "DAG Workflows", href: "/workflows", icon: GitMerge },
  { name: "Job Schedules", href: "/schedules", icon: Clock },
  { name: "Dead Letter Queue", href: "/dlq", icon: Skull },
  { name: "Chaos Lab", href: "/chaos", icon: Flame },
  { name: "System Architecture", href: "/architecture", icon: Cpu },
  { name: "Metrics & Logs", href: "/metrics", icon: LineChart },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-border bg-card/40 backdrop-blur-md flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)]">
      <div className="space-y-1">
        <p className="text-[10px] font-mono uppercase tracking-wider text-secondary-foreground px-3 py-2">
          Control Plane
        </p>
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center space-x-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? "bg-primary/15 text-primary border border-primary/30 font-semibold shadow-sm"
                  : "text-secondary-foreground hover:bg-card hover:text-foreground"
              }`}
            >
              <item.icon className={`w-4 h-4 ${isActive ? "text-primary" : "text-secondary-foreground"}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </div>

      <div className="pt-4 border-t border-border/60">
        <Link
          href="/"
          className="flex items-center space-x-2.5 px-3 py-2 rounded-lg text-xs text-secondary-foreground hover:text-foreground hover:bg-card transition-colors"
        >
          <Home className="w-4 h-4" />
          <span>Landing Page</span>
        </Link>
      </div>
    </aside>
  );
}
