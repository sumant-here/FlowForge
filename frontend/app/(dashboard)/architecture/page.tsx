"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { Cpu, Zap } from "lucide-react";

export default function ArchitecturePage() {
  const [arch, setArch] = useState<any>(null);
  const [selectedComponent, setSelectedComponent] = useState<any>(null);

  useEffect(() => {
    apiRequest("/system/architecture").then((data: any) => {
      setArch(data);
      if (data?.components?.length) setSelectedComponent(data.components[0]);
    });
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">System Architecture & Subsystems</h1>
        <p className="text-xs text-secondary-foreground font-mono mt-0.5">
          Interactive topology breakdown of the FlowForge distributed execution stack
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {(arch?.components || []).map((c: any) => {
            const isSelected = selectedComponent?.id === c.id;
            return (
              <div
                key={c.id}
                onClick={() => setSelectedComponent(c)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? "bg-primary/10 border-primary shadow-lg shadow-primary/10 scale-[1.02]"
                    : "bg-card border-border hover:border-border/80"
                }`}
              >
                <div className="flex items-center space-x-3 mb-2">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                    <Cpu className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-foreground">{c.name}</h3>
                    <span className="text-[9px] font-mono text-secondary-foreground">{c.id}</span>
                  </div>
                </div>
                <p className="text-xs text-secondary-foreground line-clamp-2 leading-relaxed">{c.role}</p>
              </div>
            );
          })}
        </div>

        {selectedComponent && (
          <div className="p-6 rounded-xl bg-card border border-primary/40 space-y-4 h-fit sticky top-20">
            <div className="flex items-center space-x-2 text-primary font-mono text-xs">
              <Zap className="w-4 h-4" />
              <span>SUBSYSTEM DEEP-DIVE</span>
            </div>
            <h2 className="text-base font-bold text-foreground">{selectedComponent.name}</h2>
            <div>
              <p className="text-[10px] font-mono text-secondary-foreground uppercase mb-1">Architecture Responsibility</p>
              <p className="text-xs text-foreground leading-relaxed bg-background p-3 rounded-lg border border-border">
                {selectedComponent.role}
              </p>
            </div>
            <div>
              <p className="text-[10px] font-mono text-secondary-foreground uppercase mb-1">Technology Stack</p>
              <p className="text-xs text-indigo-400 font-mono bg-background p-3 rounded-lg border border-border">
                {selectedComponent.tech}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
