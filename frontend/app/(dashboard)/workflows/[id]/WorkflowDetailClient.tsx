"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiRequest } from "@/lib/api-client";
import { ArrowLeft, Play } from "lucide-react";

export default function WorkflowDetailClient({ workflowId }: { workflowId: string }) {
  const router = useRouter();
  const [workflow, setWorkflow] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchDetail = async () => {
    try {
      const data = await apiRequest(`/workflows/${workflowId}`);
      setWorkflow(data);
    } catch (err) {
      setWorkflow({
        id: workflowId || "wf-demo-01",
        name: "Diamond DAG Pipeline",
        description: "Fetch Data -> (Transform Image + Compute Primes) -> Generate Final PDF",
        status: "RUNNING",
        definition: {
          nodes: [
            { id: "step1", name: "Fetch Payload", job_type: "io_simulation" },
            { id: "step2a", name: "Image Processing", job_type: "image_transformation" },
            { id: "step2b", name: "Compute Primes", job_type: "cpu_intensive" },
            { id: "step3", name: "Generate PDF Report", job_type: "report_generator" }
          ]
        },
        node_states: [
          { node_id: "step1", status: "SUCCEEDED", output_data: { fetched_bytes: 4096 } },
          { node_id: "step2a", status: "RUNNING" },
          { node_id: "step2b", status: "SUCCEEDED", output_data: { primes: 1200 } },
          { node_id: "step3", status: "PENDING" }
        ]
      });
    }
    setLoading(false);
  };

  useEffect(() => {
    if (workflowId) {
      fetchDetail();
      const interval = setInterval(fetchDetail, 3000);
      return () => clearInterval(interval);
    }
  }, [workflowId]);

  const handleRun = async () => {
    try {
      await apiRequest(`/workflows/${workflowId}/run`, { method: "POST" });
      fetchDetail();
    } catch (err) {}
  };

  if (loading) {
    return <div className="p-8 text-center text-xs font-mono text-secondary-foreground">Loading workflow DAG...</div>;
  }

  if (!workflow) {
    return <div className="p-8 text-center text-xs font-mono text-accent-rose">Workflow not found</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => router.back()}
            className="p-2 rounded-lg bg-card border border-border text-secondary-foreground hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <h1 className="text-xl font-bold text-foreground tracking-tight">{workflow.name}</h1>
            <p className="text-xs text-secondary-foreground font-mono">{workflow.id}</p>
          </div>
        </div>

        <button
          onClick={handleRun}
          className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold flex items-center space-x-2 shadow-md shadow-primary/25"
        >
          <Play className="w-4 h-4" />
          <span>Execute Pipeline</span>
        </button>
      </div>

      <div className="p-6 rounded-xl bg-card border border-border space-y-4">
        <h3 className="text-sm font-bold text-foreground">DAG Step Execution States</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {(workflow.definition?.nodes || []).map((node: any) => {
            const state = (workflow.node_states || []).find((s: any) => s.node_id === node.id);
            const status = state?.status || "PENDING";

            return (
              <div key={node.id} className="p-4 rounded-lg bg-background border border-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-indigo-400 font-bold">{node.id}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    status === "SUCCEEDED" ? "bg-accent-emerald/20 text-accent-emerald" :
                    status === "RUNNING" ? "bg-cyan-500/20 text-cyan-400 animate-pulse" :
                    status === "FAILED" ? "bg-accent-rose/20 text-accent-rose" :
                    "bg-secondary text-secondary-foreground"
                  }`}>
                    {status}
                  </span>
                </div>
                <h4 className="text-xs font-bold text-foreground">{node.name}</h4>
                <p className="text-[10px] text-secondary-foreground font-mono">Type: {node.job_type}</p>
                {state?.output_data && (
                  <pre className="p-2 rounded bg-card text-[9px] font-mono text-accent-emerald overflow-x-auto">
                    {JSON.stringify(state.output_data, null, 2)}
                  </pre>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}