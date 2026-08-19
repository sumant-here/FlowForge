"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    const fetchM = async () => {
      try {
        const data = await apiRequest("/metrics/summary");
        setMetrics(data);
      } catch (err) {}
    };
    fetchM();
    const interval = setInterval(fetchM, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Observability & Prometheus Telemetry</h1>
        <p className="text-xs text-secondary-foreground font-mono mt-0.5">
          Scraped metrics, queue pressure gauges, and host system health
        </p>
      </div>

      <div className="p-6 rounded-xl bg-card border border-border space-y-4">
        <h3 className="text-sm font-bold text-foreground">Prometheus Metrics Endpoint</h3>
        <p className="text-xs text-secondary-foreground">
          Real-time metrics are exported at <code className="px-2 py-0.5 rounded bg-background text-indigo-400 font-mono">/metrics</code> in standard Prometheus format.
        </p>
        <div className="p-4 rounded-lg bg-background font-mono text-xs text-foreground space-y-1">
          <p className="text-secondary-foreground"># HELP flowforge_http_requests_total Total HTTP requests</p>
          <p className="text-secondary-foreground"># TYPE flowforge_http_requests_total counter</p>
          <p>flowforge_http_requests_total&#123;endpoint="/api/v1/jobs",method="POST",status="200"&#125; 1142</p>
          <p>flowforge_http_requests_total&#123;endpoint="/api/v1/workers",method="GET",status="200"&#125; 480</p>
        </div>
      </div>
    </div>
  );
}
