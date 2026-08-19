"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { Network, Activity } from "lucide-react";

export default function QueuesPage() {
  const [queues, setQueues] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchQueues = async () => {
    try {
      const data: any = await apiRequest("/queues");
      setQueues(data?.queues || []);
    } catch (err) {}
    setLoading(false);
  };

  useEffect(() => {
    fetchQueues();
    const interval = setInterval(fetchQueues, 2000);
    return () => clearInterval(interval);
  }, []);

  const getPriorityColor = (name: string) => {
    if (name.includes("critical")) return "text-accent-rose border-accent-rose/30 bg-accent-rose/10";
    if (name.includes("high")) return "text-amber-400 border-amber-400/30 bg-amber-400/10";
    if (name.includes("normal")) return "text-indigo-400 border-indigo-400/30 bg-indigo-400/10";
    if (name.includes("dlq")) return "text-red-500 border-red-500/30 bg-red-500/10";
    return "text-cyan-400 border-cyan-400/30 bg-cyan-400/10";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-tight">Priority Queues Monitor</h1>
          <p className="text-xs text-secondary-foreground font-mono mt-0.5">
            Real-time depth, consumer counts, and throughput across RabbitMQ AMQP priority tiers
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {queues.map((q) => (
          <div key={q.name} className="p-5 rounded-xl bg-card border border-border space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Network className="w-5 h-5 text-indigo-400" />
                <h3 className="text-sm font-bold text-foreground font-mono">{q.name}</h3>
              </div>
              <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${getPriorityColor(q.name)}`}>
                {q.name.split(".").pop()?.toUpperCase()}
              </span>
            </div>

            <div className="p-4 rounded-lg bg-background flex items-center justify-between">
              <div>
                <p className="text-[10px] text-secondary-foreground font-mono">CURRENT DEPTH</p>
                <p className="text-3xl font-bold text-foreground font-mono">{q.depth}</p>
              </div>
              <Activity className="w-6 h-6 text-cyan-400 animate-pulse" />
            </div>

            <div className="grid grid-cols-3 gap-2 text-center text-xs font-mono">
              <div className="p-2 rounded bg-background">
                <p className="text-[10px] text-secondary-foreground">ENQUEUED</p>
                <p className="font-bold text-foreground">{q.enqueued}</p>
              </div>
              <div className="p-2 rounded bg-background">
                <p className="text-[10px] text-accent-emerald">PROCESSED</p>
                <p className="font-bold text-accent-emerald">{q.processed}</p>
              </div>
              <div className="p-2 rounded bg-background">
                <p className="text-[10px] text-accent-rose">FAILED</p>
                <p className="font-bold text-accent-rose">{q.failed}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
