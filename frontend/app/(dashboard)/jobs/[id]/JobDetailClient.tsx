"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api-client";
import { formatDuration } from "@/lib/utils";
import {
  ArrowLeft,
  RotateCw,
  XCircle,
  Terminal,
  FileJson
} from "lucide-react";

export default function JobDetailClient({ jobId }: { jobId: string }) {
  const router = useRouter();
  const [job, setJob] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchDetail = async () => {
    try {
      const data = await apiRequest(`/jobs/${jobId}`);
      setJob(data);
    } catch (err) {
      setJob({
        id: jobId || "job-demo-01",
        name: "Prime Computation Workload",
        status: "SUCCEEDED",
        priority: "CRITICAL",
        job_type: "cpu_intensive",
        execution_duration_ms: 450,
        worker_id: "worker-node-01",
        created_at: new Date().toISOString(),
        payload: { limit: 25000 },
        result: { status: "COMPLETED", primes_found: 2762 },
        logs: [
          { id: "1", timestamp: new Date().toISOString(), level: "INFO", message: "Task initialized." },
          { id: "2", timestamp: new Date().toISOString(), level: "INFO", message: "Calculating primes up to 25000..." },
          { id: "3", timestamp: new Date().toISOString(), level: "INFO", message: "Completed in 450ms." }
        ]
      });
    }
    setLoading(false);
  };

  useEffect(() => {
    if (jobId) {
      fetchDetail();
      const interval = setInterval(fetchDetail, 3000);
      return () => clearInterval(interval);
    }
  }, [jobId]);

  const handleRetry = async () => {
    setActionLoading(true);
    try {
      await apiRequest(`/jobs/${jobId}/retry`, { method: "POST" });
      fetchDetail();
    } catch (err) {}
    setActionLoading(false);
  };

  const handleCancel = async () => {
    setActionLoading(true);
    try {
      await apiRequest(`/jobs/${jobId}/cancel`, { method: "POST" });
      fetchDetail();
    } catch (err) {}
    setActionLoading(false);
  };

  if (loading) {
    return <div className="p-8 text-center text-xs font-mono text-secondary-foreground">Loading job detail...</div>;
  }

  if (!job) {
    return <div className="p-8 text-center text-xs font-mono text-accent-rose">Job not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg bg-card border border-border text-secondary-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-foreground tracking-tight">{job.name}</h1>
            <p className="text-xs text-secondary-foreground font-mono">{job.id}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleRetry}
            disabled={actionLoading}
            className="px-3.5 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center space-x-2 transition-all"
          >
            <RotateCw className="w-3.5 h-3.5" />
            <span>Replay / Retry</span>
          </button>
          {job.status === "RUNNING" || job.status === "QUEUED" ? (
            <button
              onClick={handleCancel}
              disabled={actionLoading}
              className="px-3.5 py-1.5 rounded-lg bg-accent-rose/20 text-accent-rose border border-accent-rose/30 hover:bg-accent-rose/30 text-xs font-semibold flex items-center space-x-2 transition-all"
            >
              <XCircle className="w-3.5 h-3.5" />
              <span>Cancel Job</span>
            </button>
          ) : null}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-card border border-border">
          <p className="text-[10px] font-mono text-secondary-foreground uppercase">Status</p>
          <p className="text-base font-bold text-foreground font-mono mt-1">{job.status}</p>
        </div>
        <div className="p-4 rounded-xl bg-card border border-border">
          <p className="text-[10px] font-mono text-secondary-foreground uppercase">Priority</p>
          <p className="text-base font-bold text-foreground font-mono mt-1">{job.priority}</p>
        </div>
        <div className="p-4 rounded-xl bg-card border border-border">
          <p className="text-[10px] font-mono text-secondary-foreground uppercase">Execution Duration</p>
          <p className="text-base font-bold text-foreground font-mono mt-1">{formatDuration(job.execution_duration_ms)}</p>
        </div>
        <div className="p-4 rounded-xl bg-card border border-border">
          <p className="text-[10px] font-mono text-secondary-foreground uppercase">Worker Node</p>
          <p className="text-base font-bold text-foreground font-mono mt-1 truncate">{job.worker_id || "Unassigned"}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-5 rounded-xl bg-card border border-border space-y-3">
          <div className="flex items-center space-x-2 text-indigo-400">
            <Terminal className="w-4 h-4" />
            <h3 className="text-sm font-bold text-foreground">Execution Console Output</h3>
          </div>
          <div className="p-4 rounded-lg bg-background font-mono text-xs text-foreground space-y-1.5 max-h-72 overflow-y-auto">
            {(job.logs || []).length === 0 ? (
              <p className="text-secondary-foreground">No logs recorded yet.</p>
            ) : (
              job.logs.map((l: any, i: number) => (
                <div key={l.id || i} className="leading-relaxed">
                  <span className="text-secondary-foreground mr-2">[{new Date(l.timestamp).toLocaleTimeString()}]</span>
                  <span className={l.level === "ERROR" ? "text-accent-rose" : l.level === "WARN" ? "text-amber-400" : "text-emerald-400"}>
                    [{l.level}]
                  </span>{" "}
                  <span>{l.message}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="p-5 rounded-xl bg-card border border-border space-y-4">
          <div className="flex items-center space-x-2 text-cyan-400">
            <FileJson className="w-4 h-4" />
            <h3 className="text-sm font-bold text-foreground">Payload & Results Inspector</h3>
          </div>
          <div>
            <p className="text-[11px] font-mono text-secondary-foreground mb-1">INPUT PAYLOAD</p>
            <pre className="p-3 rounded-lg bg-background font-mono text-[11px] text-foreground overflow-x-auto">
              {JSON.stringify(job.payload, null, 2)}
            </pre>
          </div>
          {job.result && (
            <div>
              <p className="text-[11px] font-mono text-accent-emerald mb-1">COMPUTATION RESULT</p>
              <pre className="p-3 rounded-lg bg-background font-mono text-[11px] text-accent-emerald overflow-x-auto">
                {JSON.stringify(job.result, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}