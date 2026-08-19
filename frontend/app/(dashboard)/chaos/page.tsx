"use client";

import React, { useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { Flame, Skull, Zap, AlertTriangle } from "lucide-react";

export default function ChaosLabPage() {
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<any[]>([]);

  const triggerChaos = async (action: string, params: any = {}) => {
    setLoading(true);
    try {
      const res: any = await apiRequest("/chaos/execute", {
        method: "POST",
        body: JSON.stringify({ action, ...params }),
      });
      setLogs((prev) => [{ time: new Date().toLocaleTimeString(), action, ...res }, ...prev]);
    } catch (err: any) {
      setLogs((prev) => [{ time: new Date().toLocaleTimeString(), action, error: err.message }, ...prev]);
    }
    setLoading(false);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Chaos Engineering Lab</h1>
        <p className="text-xs text-secondary-foreground font-mono mt-0.5">
          Simulate distributed disasters and observe real-time automated recovery mechanisms
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
        <div className="p-5 rounded-xl bg-card border border-accent-rose/30 space-y-3">
          <div className="flex items-center space-x-2 text-accent-rose">
            <Skull className="w-5 h-5" />
            <h3 className="text-sm font-bold">Kill Random Worker</h3>
          </div>
          <p className="text-xs text-secondary-foreground leading-relaxed">
            Instantly kills an active worker daemon. The scheduler detects heartbeat timeout and auto-requeues in-flight jobs.
          </p>
          <button
            onClick={() => triggerChaos("kill_worker")}
            disabled={loading}
            className="w-full py-2 rounded-lg bg-accent-rose hover:bg-rose-600 text-white text-xs font-semibold shadow-md transition-all"
          >
            Simulate Worker Crash
          </button>
        </div>

        <div className="p-5 rounded-xl bg-card border border-amber-500/30 space-y-3">
          <div className="flex items-center space-x-2 text-amber-400">
            <AlertTriangle className="w-5 h-5" />
            <h3 className="text-sm font-bold">Inject Failure Stress</h3>
          </div>
          <p className="text-xs text-secondary-foreground leading-relaxed">
            Submits a job that intentionally crashes on initial attempts to test exponential backoff and jitter calculations.
          </p>
          <button
            onClick={() => triggerChaos("force_job_failure")}
            disabled={loading}
            className="w-full py-2 rounded-lg bg-amber-500 hover:bg-amber-600 text-black text-xs font-semibold shadow-md transition-all"
          >
            Inject Failure Workload
          </button>
        </div>

        <div className="p-5 rounded-xl bg-card border border-indigo-500/30 space-y-3">
          <div className="flex items-center space-x-2 text-indigo-400">
            <Zap className="w-5 h-5" />
            <h3 className="text-sm font-bold">Queue Flood (50 Jobs)</h3>
          </div>
          <p className="text-xs text-secondary-foreground leading-relaxed">
            Floods the message broker with 50 priority-weighted jobs to test concurrency and worker consumer preemption.
          </p>
          <button
            onClick={() => triggerChaos("flood_queue", { job_count: 50 })}
            disabled={loading}
            className="w-full py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-md transition-all"
          >
            Trigger Load Flood
          </button>
        </div>
      </div>

      <div className="p-5 rounded-xl bg-card border border-border space-y-3">
        <h3 className="text-sm font-bold text-foreground">Disaster Simulation Log</h3>
        <div className="p-4 rounded-lg bg-background font-mono text-xs space-y-2 max-h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-secondary-foreground text-center py-4">No chaos drills run in this session.</p>
          ) : (
            logs.map((l, i) => (
              <div key={i} className="border-b border-border/40 pb-2">
                <span className="text-secondary-foreground mr-2">[{l.time}]</span>
                <span className="text-accent-rose font-bold">[{l.action}]</span>
                <p className="text-foreground mt-0.5">{l.impact || l.error}</p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
