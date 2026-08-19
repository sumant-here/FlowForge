"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useSocket } from "@/lib/socket-context";
import { apiRequest } from "@/lib/api-client";
import {
  Layers,
  Server,
  Network,
  CheckCircle2,
  AlertTriangle,
  RotateCw,
  Skull,
  Activity,
  ArrowRight,
  TrendingUp,
  Cpu,
  Clock
} from "lucide-react";

export default function DashboardPage() {
  const { lastEvent, eventsHistory } = useSocket();
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchMetrics = async () => {
    try {
      const data = await apiRequest("/metrics/summary");
      setMetrics(data);
    } catch (err) {}
    setLoading(false);
  };

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-tight">Distributed Fleet Overview</h1>
          <p className="text-xs text-secondary-foreground font-mono mt-0.5">
            Real-time telemetry, queue throughput, and worker cluster health
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchMetrics}
            className="p-2 rounded-lg bg-card border border-border text-secondary-foreground hover:text-foreground text-xs font-mono flex items-center space-x-2"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Sync</span>
          </button>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        <div className="p-4 rounded-xl bg-card border border-border">
          <div className="flex items-center justify-between text-secondary-foreground mb-2">
            <span className="text-[11px] font-mono">TOTAL JOBS</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <p className="text-2xl font-bold text-foreground font-mono">{metrics?.total_jobs ?? "-"}</p>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <div className="flex items-center justify-between text-secondary-foreground mb-2">
            <span className="text-[11px] font-mono">RUNNING</span>
            <Activity className="w-4 h-4 text-cyan-400 animate-spin" />
          </div>
          <p className="text-2xl font-bold text-cyan-400 font-mono">{metrics?.running_jobs ?? "-"}</p>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <div className="flex items-center justify-between text-secondary-foreground mb-2">
            <span className="text-[11px] font-mono">QUEUED</span>
            <Network className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-2xl font-bold text-amber-400 font-mono">{metrics?.queued_jobs ?? "-"}</p>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <div className="flex items-center justify-between text-secondary-foreground mb-2">
            <span className="text-[11px] font-mono">SUCCEEDED</span>
            <CheckCircle2 className="w-4 h-4 text-accent-emerald" />
          </div>
          <p className="text-2xl font-bold text-accent-emerald font-mono">{metrics?.succeeded_jobs ?? "-"}</p>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <div className="flex items-center justify-between text-secondary-foreground mb-2">
            <span className="text-[11px] font-mono">RETRYING</span>
            <RotateCw className="w-4 h-4 text-indigo-400 animate-spin" />
          </div>
          <p className="text-2xl font-bold text-indigo-400 font-mono">{metrics?.retrying_jobs ?? "-"}</p>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <div className="flex items-center justify-between text-secondary-foreground mb-2">
            <span className="text-[11px] font-mono">DEAD LETTER</span>
            <Skull className="w-4 h-4 text-accent-rose" />
          </div>
          <p className="text-2xl font-bold text-accent-rose font-mono">{metrics?.dead_lettered_jobs ?? "-"}</p>
        </div>

        <div className="p-4 rounded-xl bg-card border border-border">
          <div className="flex items-center justify-between text-secondary-foreground mb-2">
            <span className="text-[11px] font-mono">WORKERS</span>
            <Server className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-2xl font-bold text-emerald-400 font-mono">{metrics?.active_workers ?? "-"}</p>
        </div>
      </div>

      {/* Middle Grid: Priority Queues & System Health */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Priority Queues Depth */}
        <div className="lg:col-span-2 p-5 rounded-xl bg-card border border-border space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Network className="w-4 h-4 text-indigo-400" />
              <h3 className="text-sm font-bold text-foreground">Priority Queue Depths</h3>
            </div>
            <Link href="/queues" className="text-xs text-primary hover:underline flex items-center space-x-1">
              <span>Inspect Queues</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {(metrics?.queues || []).map((q: any) => (
              <div key={q.name} className="p-3 rounded-lg bg-background border border-border">
                <p className="text-[11px] font-mono text-secondary-foreground uppercase truncate">
                  {q.name.replace("queue.", "")}
                </p>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-xl font-bold font-mono text-foreground">{q.depth}</span>
                  <span className="text-[10px] text-secondary-foreground font-mono">in queue</span>
                </div>
                <div className="mt-2 text-[10px] font-mono text-secondary-foreground">
                  Processed: {q.processed}
                </div>
              </div>
            ))}
          </div>

          {/* Host Resources */}
          <div className="pt-2 grid grid-cols-2 gap-4 border-t border-border/60">
            <div>
              <div className="flex justify-between text-xs font-mono text-secondary-foreground mb-1">
                <span>HOST CPU UTILIZATION</span>
                <span>{metrics?.host_cpu_percent ?? 0}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-border overflow-hidden">
                <div
                  className="h-full bg-indigo-500 rounded-full transition-all"
                  style={{ width: `${Math.min(100, metrics?.host_cpu_percent || 0)}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs font-mono text-secondary-foreground mb-1">
                <span>HOST MEMORY USAGE</span>
                <span>{metrics?.host_memory_percent ?? 0}%</span>
              </div>
              <div className="w-full h-2 rounded-full bg-border overflow-hidden">
                <div
                  className="h-full bg-cyan-500 rounded-full transition-all"
                  style={{ width: `${Math.min(100, metrics?.host_memory_percent || 0)}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Live Activity Feed Stream */}
        <div className="p-5 rounded-xl bg-card border border-border flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-3">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold text-foreground">Live Telemetry Feed</h3>
            </div>
            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
              {eventsHistory.length === 0 ? (
                <p className="text-xs text-secondary-foreground font-mono py-8 text-center">
                  Waiting for live telemetry stream...
                </p>
              ) : (
                eventsHistory.slice(0, 8).map((ev, i) => (
                  <div key={i} className="p-2 rounded bg-background border border-border/70 text-xs font-mono flex items-center justify-between">
                    <div>
                      <span className="text-indigo-400 font-bold">{ev.event}</span>
                      <p className="text-[10px] text-secondary-foreground truncate max-w-[180px]">
                        {ev.data?.job_id || ev.data?.worker_id || ev.data?.name || "-"}
                      </p>
                    </div>
                    <span className="text-[9px] text-secondary-foreground">
                      {new Date().toLocaleTimeString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <Link
            href="/jobs"
            className="mt-4 w-full py-2 rounded-lg bg-border/40 hover:bg-border text-secondary-foreground hover:text-foreground text-xs text-center font-mono transition-colors block"
          >
            View All Jobs ➔
          </Link>
        </div>
      </div>
    </div>
  );
}
