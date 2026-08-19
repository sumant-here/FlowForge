"use client";

import React, { useEffect, useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { Clock } from "lucide-react";

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchSchedules = async () => {
    try {
      const data: any = await apiRequest("/schedules");
      setSchedules(data || []);
    } catch (err) {}
    setLoading(false);
  };

  useEffect(() => {
    fetchSchedules();
  }, []);

  const handleToggle = async (id: string) => {
    try {
      await apiRequest(`/schedules/${id}/toggle`, { method: "PATCH" });
      fetchSchedules();
    } catch (err) {}
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-foreground tracking-tight">Recurring & Cron Schedules</h1>
        <p className="text-xs text-secondary-foreground font-mono mt-0.5">
          Automated background cron triggers and interval schedules
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {schedules.map((s) => (
          <div key={s.id} className="p-5 rounded-xl bg-card border border-border space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="text-sm font-bold text-foreground">{s.name}</h3>
                <p className="text-xs font-mono text-indigo-400 mt-0.5">{s.cron_expression || `Every ${s.interval_seconds}s`}</p>
              </div>
              <button
                onClick={() => handleToggle(s.id)}
                className={`px-3 py-1 rounded-full text-[10px] font-mono font-bold border transition-colors ${
                  s.is_active
                    ? "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40"
                    : "bg-secondary text-secondary-foreground border-border"
                }`}
              >
                {s.is_active ? "ENABLED" : "PAUSED"}
              </button>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-secondary-foreground bg-background p-3 rounded-lg">
              <div>
                <p className="text-[10px]">TOTAL RUNS</p>
                <p className="text-foreground font-bold">{s.total_runs}</p>
              </div>
              <div>
                <p className="text-[10px]">NEXT EXECUTION</p>
                <p className="text-foreground font-bold">{s.next_run_at ? new Date(s.next_run_at).toLocaleTimeString() : "-"}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
