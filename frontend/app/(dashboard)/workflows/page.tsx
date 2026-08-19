"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { apiRequest } from "@/lib/api-client";
import { timeAgo } from "@/lib/utils";
import { GitMerge, Play, ArrowUpRight } from "lucide-react";

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchWorkflows = async () => {
    try {
      const data: any = await apiRequest("/workflows");
      setWorkflows(data || []);
    } catch (err) {}
    setLoading(false);
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const handleRun = async (id: string) => {
    try {
      await apiRequest(`/workflows/${id}/run`, { method: "POST" });
      fetchWorkflows();
    } catch (err) {}
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-tight">DAG Workflow Pipelines</h1>
          <p className="text-xs text-secondary-foreground font-mono mt-0.5">
            Directed Acyclic Graph multi-stage asynchronous execution pipelines
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {workflows.map((wf) => (
          <div key={wf.id} className="p-5 rounded-xl bg-card border border-border space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <Link href={`/workflows/${wf.id}`} className="font-bold text-foreground hover:text-primary transition-colors text-base flex items-center space-x-1.5">
                  <span>{wf.name}</span>
                  <ArrowUpRight className="w-4 h-4 text-secondary-foreground" />
                </Link>
                <p className="text-xs text-secondary-foreground mt-1 leading-relaxed">{wf.description}</p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-400">
                {wf.status}
              </span>
            </div>

            <div className="p-3 rounded-lg bg-background border border-border/70">
              <p className="text-[10px] font-mono text-secondary-foreground mb-2">PIPELINE TOPOLOGY ({wf.definition?.nodes?.length || 0} NODES)</p>
              <div className="flex flex-wrap items-center gap-2">
                {(wf.definition?.nodes || []).map((node: any, idx: number) => (
                  <div key={node.id} className="flex items-center space-x-1 text-xs font-mono">
                    <span className="px-2 py-1 rounded bg-card border border-border text-foreground">
                      {node.name}
                    </span>
                    {idx < wf.definition.nodes.length - 1 && <span className="text-secondary-foreground">➔</span>}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-border/60 text-xs font-mono text-secondary-foreground">
              <span>Created {timeAgo(wf.created_at)}</span>
              <div className="flex items-center space-x-2">
                <Link
                  href={`/workflows/${wf.id}`}
                  className="px-3 py-1.5 rounded-lg bg-secondary hover:bg-border text-foreground transition-colors"
                >
                  View DAG
                </Link>
                <button
                  onClick={() => handleRun(wf.id)}
                  className="px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white flex items-center space-x-1.5 shadow-sm"
                >
                  <Play className="w-3.5 h-3.5" />
                  <span>Execute</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
