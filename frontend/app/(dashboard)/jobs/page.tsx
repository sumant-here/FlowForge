"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiRequest } from "@/lib/api-client";
import { formatDuration, timeAgo } from "@/lib/utils";
import { Search, Filter, RotateCw, Plus, Layers, ArrowUpRight } from "lucide-react";
import JobSubmitModal from "@/components/JobSubmitModal";

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [showSubmitModal, setShowSubmitModal] = useState(false);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: "25",
        ...(search && { search }),
        ...(statusFilter && { status: statusFilter }),
        ...(priorityFilter && { priority: priorityFilter }),
      });
      const data: any = await apiRequest(`/jobs?${params.toString()}`);
      setJobs(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {}
    setLoading(false);
  };

  useEffect(() => {
    fetchJobs();
  }, [page, statusFilter, priorityFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "SUCCEEDED":
        return "bg-accent-emerald/15 text-accent-emerald border-accent-emerald/30";
      case "RUNNING":
        return "bg-cyan-500/15 text-cyan-400 border-cyan-500/30 animate-pulse";
      case "QUEUED":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "RETRYING":
        return "bg-indigo-500/15 text-indigo-400 border-indigo-500/30";
      case "DEAD_LETTERED":
      case "FAILED":
        return "bg-accent-rose/15 text-accent-rose border-accent-rose/30";
      case "CANCELLED":
        return "bg-secondary text-secondary-foreground border-border";
      default:
        return "bg-border text-foreground";
    }
  };

  const getPriorityBadge = (prio: string) => {
    switch (prio) {
      case "CRITICAL":
        return "text-accent-rose font-bold";
      case "HIGH":
        return "text-amber-400 font-semibold";
      case "NORMAL":
        return "text-indigo-400";
      default:
        return "text-secondary-foreground";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-tight">Jobs Explorer</h1>
          <p className="text-xs text-secondary-foreground font-mono mt-0.5">
            Total {total} background workloads processed
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowSubmitModal(true)}
            className="flex items-center space-x-2 px-3.5 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-md shadow-primary/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Submit Job</span>
          </button>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="p-4 rounded-xl bg-card border border-border flex flex-col md:flex-row md:items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-secondary-foreground absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search by job name or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-background border border-border text-xs text-foreground font-mono focus:outline-none focus:border-primary"
          />
        </form>

        <div className="flex flex-wrap items-center gap-3">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-background border border-border text-xs text-foreground font-mono focus:outline-none focus:border-primary"
          >
            <option value="">All Statuses</option>
            <option value="QUEUED">QUEUED</option>
            <option value="RUNNING">RUNNING</option>
            <option value="SUCCEEDED">SUCCEEDED</option>
            <option value="RETRYING">RETRYING</option>
            <option value="FAILED">FAILED</option>
            <option value="DEAD_LETTERED">DEAD_LETTERED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-background border border-border text-xs text-foreground font-mono focus:outline-none focus:border-primary"
          >
            <option value="">All Priorities</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="HIGH">HIGH</option>
            <option value="NORMAL">NORMAL</option>
            <option value="LOW">LOW</option>
          </select>

          <button
            onClick={fetchJobs}
            className="p-1.5 rounded-lg bg-background border border-border text-secondary-foreground hover:text-foreground"
          >
            <RotateCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl bg-card border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-background/80 border-b border-border text-secondary-foreground font-mono uppercase text-[10px]">
              <tr>
                <th className="py-3 px-4">Job Name / ID</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Duration</th>
                <th className="py-3 px-4">Attempts</th>
                <th className="py-3 px-4">Created</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 font-mono">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-secondary-foreground">
                    Loading jobs...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-8 text-center text-secondary-foreground">
                    No jobs found matching criteria.
                  </td>
                </tr>
              ) : (
                jobs.map((j) => (
                  <tr key={j.id} className="hover:bg-background/40 transition-colors">
                    <td className="py-3 px-4">
                      <Link href={`/jobs/${j.id}`} className="font-bold text-foreground hover:text-primary transition-colors flex items-center space-x-1.5">
                        <span>{j.name}</span>
                        <ArrowUpRight className="w-3 h-3 text-secondary-foreground opacity-60" />
                      </Link>
                      <span className="text-[10px] text-secondary-foreground block">{j.id.slice(0, 8)}...</span>
                    </td>
                    <td className="py-3 px-4 text-secondary-foreground">{j.job_type}</td>
                    <td className={`py-3 px-4 ${getPriorityBadge(j.priority)}`}>{j.priority}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-0.5 rounded-full border text-[10px] font-semibold ${getStatusBadge(j.status)}`}>
                        {j.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-secondary-foreground">{formatDuration(j.execution_duration_ms)}</td>
                    <td className="py-3 px-4 text-secondary-foreground">{j.retry_count}/{j.max_retries}</td>
                    <td className="py-3 px-4 text-secondary-foreground">{timeAgo(j.created_at)}</td>
                    <td className="py-3 px-4 text-right">
                      <Link
                        href={`/jobs/${j.id}`}
                        className="px-2.5 py-1 rounded bg-border/40 hover:bg-border text-foreground transition-colors text-[11px]"
                      >
                        Inspect
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showSubmitModal && <JobSubmitModal onClose={() => { setShowSubmitModal(false); fetchJobs(); }} />}
    </div>
  );
}
