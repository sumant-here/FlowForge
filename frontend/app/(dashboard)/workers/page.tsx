"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { Server, Activity, ShieldCheck, Power, Cpu } from "lucide-react";

export default function WorkersPage() {
  const [workers, setWorkers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchWorkers = async () => {
    try {
      const data: any = await apiRequest("/workers");
      setWorkers(data || []);
    } catch (err) {}
    setLoading(false);
  };

  useEffect(() => {
    fetchWorkers();
    const interval = setInterval(fetchWorkers, 3000);
    return () => clearInterval(interval);
  }, []);

  const handleDrain = async (workerId: string) => {
    try {
      await apiRequest(`/workers/${workerId}/drain`, { method: "POST" });
      fetchWorkers();
    } catch (err) {}
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-tight">Worker Fleet Orchestration</h1>
          <p className="text-xs text-secondary-foreground font-mono mt-0.5">
            Active distributed worker instances, health heartbeats, and resource utilization
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {workers.map((w) => (
          <div key={w.id} className="p-5 rounded-xl bg-card border border-border space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                  <Server className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-foreground font-mono">{w.id}</h3>
                  <p className="text-[10px] text-secondary-foreground font-mono">{w.hostname} ({w.ip_address})</p>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                w.status === "BUSY" ? "bg-cyan-500/20 text-cyan-400 animate-pulse" :
                w.status === "IDLE" ? "bg-accent-emerald/20 text-accent-emerald" :
                "bg-accent-rose/20 text-accent-rose"
              }`}>
                {w.status}
              </span>
            </div>

            {/* Resources */}
            <div className="space-y-2 text-xs font-mono">
              <div>
                <div className="flex justify-between text-secondary-foreground text-[11px] mb-1">
                  <span>CPU LOAD</span>
                  <span>{w.cpu_usage}%</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-background overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${w.cpu_usage}%` }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-secondary-foreground text-[11px] mb-1">
                  <span>MEMORY ALLOCATION</span>
                  <span>{w.memory_usage}%</span>
                </div>
                <div className="w-full h-1.5 rounded-full bg-background overflow-hidden">
                  <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${w.memory_usage}%` }} />
                </div>
              </div>
            </div>

            {/* Performance Stats */}
            <div className="grid grid-cols-3 gap-2 pt-3 border-t border-border/60 text-center">
              <div className="p-2 rounded bg-background">
                <p className="text-[10px] text-secondary-foreground font-mono">PROCESSED</p>
                <p className="text-sm font-bold font-mono text-foreground">{w.jobs_processed}</p>
              </div>
              <div className="p-2 rounded bg-background">
                <p className="text-[10px] text-accent-emerald font-mono">SUCCESS</p>
                <p className="text-sm font-bold font-mono text-accent-emerald">{w.jobs_succeeded}</p>
              </div>
              <div className="p-2 rounded bg-background">
                <p className="text-[10px] text-accent-rose font-mono">FAILED</p>
                <p className="text-sm font-bold font-mono text-accent-rose">{w.jobs_failed}</p>
              </div>
            </div>

            {/* Action */}
            <div className="flex justify-end pt-2">
              <button
                onClick={() => handleDrain(w.id)}
                className="px-3 py-1 rounded bg-secondary hover:bg-border text-secondary-foreground hover:text-foreground text-[11px] font-mono transition-colors"
              >
                Drain Worker
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
