"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { timeAgo } from "@/lib/utils";
import { Skull, RotateCw, Trash2 } from "lucide-react";

export default function DLQPage() {
  const [dlqJobs, setDlqJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDLQ = async () => {
    try {
      const data: any = await apiRequest("/dlq");
      setDlqJobs(data || []);
    } catch (err) {}
    setLoading(false);
  };

  useEffect(() => {
    fetchDLQ();
  }, []);

  const handleReplay = async (id: string) => {
    try {
      await apiRequest(`/dlq/${id}/replay`, { method: "POST" });
      fetchDLQ();
    } catch (err) {}
  };

  const handlePurge = async () => {
    if (confirm("Are you sure you want to purge all dead-lettered jobs?")) {
      try {
        await apiRequest("/dlq/purge", { method: "DELETE" });
        fetchDLQ();
      } catch (err) {}
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-tight">Dead Letter Queue (DLQ)</h1>
          <p className="text-xs text-secondary-foreground font-mono mt-0.5">
            Failed jobs exceeding maximum retry limits requiring manual diagnostic triage
          </p>
        </div>
        {dlqJobs.length > 0 && (
          <button
            onClick={handlePurge}
            className="px-3.5 py-1.5 rounded-lg bg-accent-rose/20 text-accent-rose border border-accent-rose/30 hover:bg-accent-rose/30 text-xs font-semibold flex items-center space-x-2"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Purge DLQ</span>
          </button>
        )}
      </div>

      <div className="space-y-4">
        {loading ? (
          <div className="p-8 text-center text-xs font-mono text-secondary-foreground">Loading DLQ records...</div>
        ) : dlqJobs.length === 0 ? (
          <div className="p-12 text-center rounded-xl bg-card border border-border space-y-2">
            <Skull className="w-8 h-8 text-secondary-foreground mx-auto opacity-50" />
            <p className="text-sm font-bold text-foreground">DLQ is Empty</p>
            <p className="text-xs text-secondary-foreground font-mono">All jobs are healthy or resolved.</p>
          </div>
        ) : (
          dlqJobs.map((j) => (
            <div key={j.id} className="p-5 rounded-xl bg-card border border-accent-rose/30 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-foreground font-mono">{j.job_name}</h3>
                  <p className="text-xs text-secondary-foreground font-mono">Original Job ID: {j.original_job_id}</p>
                </div>
                <button
                  onClick={() => handleReplay(j.id)}
                  className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center space-x-1.5"
                >
                  <RotateCw className="w-3.5 h-3.5" />
                  <span>Replay Job</span>
                </button>
              </div>

              <div className="p-3 rounded-lg bg-accent-rose/10 border border-accent-rose/20 font-mono text-xs text-accent-rose">
                <p className="font-bold mb-1">FAILURE REASON: {j.failure_reason}</p>
                {j.stack_trace && <pre className="text-[10px] opacity-80 overflow-x-auto">{j.stack_trace}</pre>}
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono text-secondary-foreground">
                <span>Queue: {j.queue_name}</span>
                <span>Attempts: {j.attempts_count}</span>
                <span>Moved to DLQ {timeAgo(j.moved_to_dlq_at)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
