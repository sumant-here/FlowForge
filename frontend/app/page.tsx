"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Zap,
  ArrowRight,
  Server,
  Layers,
  Network,
  Cpu,
  ShieldAlert,
  GitMerge,
  Flame,
  CheckCircle2,
  Terminal,
  Activity
} from "lucide-react";

export default function LandingPage() {
  const [activeTab, setActiveTab] = useState<"normal" | "chaos">("normal");

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col">
      {/* Top Header */}
      <header className="h-16 border-b border-border px-8 flex items-center justify-between sticky top-0 bg-background/80 backdrop-blur-md z-40">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-xl tracking-tight">FlowForge</span>
        </div>
        <div className="flex items-center space-x-4">
          <Link
            href="/dashboard"
            className="px-4 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-lg shadow-primary/25 transition-all flex items-center space-x-2"
          >
            <span>Launch Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-8 max-w-6xl mx-auto text-center relative">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-mono mb-6">
          <span className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse" />
          <span>PRODUCTION-GRADE DISTRIBUTED WORKFLOW ENGINE</span>
        </div>
        
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          Distributed Workloads. <br />
          <span className="bg-gradient-to-r from-indigo-400 via-cyan-400 to-emerald-400 bg-clip-text text-transparent">
            Deterministic Orchestration.
          </span>
        </h1>
        
        <p className="text-base sm:text-lg text-secondary-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
          Execute, orchestrate, and observe background jobs across distributed worker fleets with AMQP priority queues, DAG workflow topology, exponential retries, and automated crash recovery.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 mb-16">
          <Link
            href="/dashboard"
            className="px-6 py-3 rounded-xl bg-primary hover:bg-primary-hover text-white text-sm font-semibold shadow-xl shadow-primary/30 flex items-center space-x-2 transition-all"
          >
            <span>Explore Live Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/architecture"
            className="px-6 py-3 rounded-xl bg-card hover:bg-card-hover border border-border text-foreground text-sm font-semibold flex items-center space-x-2 transition-all"
          >
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>System Architecture</span>
          </Link>
        </div>

        {/* Live Animated Architecture Visualizer */}
        <div className="p-6 rounded-2xl bg-card border border-border shadow-2xl text-left">
          <div className="flex items-center justify-between pb-4 border-b border-border mb-6">
            <div className="flex items-center space-x-3">
              <Activity className="w-5 h-5 text-indigo-400" />
              <h3 className="text-sm font-bold text-foreground">Interactive Distributed Pipeline Visualizer</h3>
            </div>
            <div className="flex items-center space-x-2 bg-background p-1 rounded-lg border border-border">
              <button
                onClick={() => setActiveTab("normal")}
                className={`px-3 py-1 text-xs font-mono rounded ${activeTab === "normal" ? "bg-primary text-white" : "text-secondary-foreground"}`}
              >
                Normal Flow
              </button>
              <button
                onClick={() => setActiveTab("chaos")}
                className={`px-3 py-1 text-xs font-mono rounded ${activeTab === "chaos" ? "bg-accent-rose text-white" : "text-secondary-foreground"}`}
              >
                Worker Crash & Requeue
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-center items-center py-4">
            {/* Step 1: Client */}
            <div className="p-4 rounded-xl bg-background border border-border">
              <p className="text-xs font-mono text-indigo-400 mb-1">CLIENT</p>
              <p className="text-xs font-bold text-foreground">Next.js UI / SDK</p>
              <p className="text-[10px] text-secondary-foreground mt-1">HTTP / JSON</p>
            </div>

            <div className="text-secondary-foreground font-mono text-xs hidden md:block">➔ HTTP ➔</div>

            {/* Step 2: Gateway */}
            <div className="p-4 rounded-xl bg-background border border-border">
              <p className="text-xs font-mono text-cyan-400 mb-1">GATEWAY</p>
              <p className="text-xs font-bold text-foreground">FastAPI Router</p>
              <p className="text-[10px] text-secondary-foreground mt-1">JWT / Rate Limit</p>
            </div>

            <div className="text-secondary-foreground font-mono text-xs hidden md:block">➔ AMQP ➔</div>

            {/* Step 3: Broker */}
            <div className="p-4 rounded-xl bg-background border border-border">
              <p className="text-xs font-mono text-amber-400 mb-1">BROKER</p>
              <p className="text-xs font-bold text-foreground">RabbitMQ</p>
              <p className="text-[10px] text-secondary-foreground mt-1">4 Priority Tiers</p>
            </div>
          </div>

          {/* Workers Grid */}
          <div className="mt-4 p-4 rounded-xl bg-background/60 border border-border/70">
            <p className="text-xs font-mono text-secondary-foreground mb-3 uppercase tracking-wider">
              Autonomous Distributed Workers ({activeTab === "chaos" ? "Simulated Crash Active" : "Operational"})
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-card border border-border flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-foreground font-mono">worker-us-east-01</p>
                  <p className="text-[10px] text-accent-emerald">BUSY (CPU Task)</p>
                </div>
                <span className="w-2.5 h-2.5 rounded-full bg-accent-emerald" />
              </div>

              <div className={`p-3 rounded-lg border flex items-center justify-between transition-all ${
                activeTab === "chaos"
                  ? "bg-accent-rose/10 border-accent-rose/40 text-accent-rose animate-pulse"
                  : "bg-card border-border"
              }`}>
                <div>
                  <p className="text-xs font-bold font-mono">worker-eu-west-01</p>
                  <p className="text-[10px]">{activeTab === "chaos" ? "CRASHED (Requeuing Job...)" : "IDLE"}</p>
                </div>
                <span className={`w-2.5 h-2.5 rounded-full ${activeTab === "chaos" ? "bg-accent-rose" : "bg-accent-emerald"}`} />
              </div>

              <div className="p-3 rounded-lg bg-card border border-border flex items-center justify-between">
                <div>
                  <p className="text-xs font-bold text-foreground font-mono">worker-ap-south-01</p>
                  <p className="text-[10px] text-indigo-400">EXECUTING REQUEUED JOB</p>
                </div>
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-400" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Pillars */}
      <section className="py-16 px-8 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-card border border-border">
          <Network className="w-7 h-7 text-indigo-400 mb-4" />
          <h3 className="text-base font-bold text-foreground mb-2">Multi-Tier Priority Broker</h3>
          <p className="text-xs text-secondary-foreground leading-relaxed">
            Strict AMQP priority queues (Critical, High, Normal, Low) with Dead Letter Exchange (DLX) routing and isolated retries.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border">
          <GitMerge className="w-7 h-7 text-cyan-400 mb-4" />
          <h3 className="text-base font-bold text-foreground mb-2">DAG Workflow Engine</h3>
          <p className="text-xs text-secondary-foreground leading-relaxed">
            Kahn's topological sorting, cyclic graph validation, fan-out parallel joins, and dynamic context propagation.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border">
          <Flame className="w-7 h-7 text-amber-400 mb-4" />
          <h3 className="text-base font-bold text-foreground mb-2">Chaos Engineering Lab</h3>
          <p className="text-xs text-secondary-foreground leading-relaxed">
            Interactive disaster simulation: inject worker crashes, latency delays, and queue floods to verify auto-recovery.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto py-8 border-t border-border text-center text-xs text-secondary-foreground">
        <p>FlowForge Distributed Systems Platform | Built for Scale and Resilience</p>
      </footer>
    </div>
  );
}
