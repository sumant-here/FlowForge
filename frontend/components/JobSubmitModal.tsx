"use client";

import React, { useState } from "react";
import { apiRequest } from "@/lib/api-client";
import { X, Sparkles } from "lucide-react";

export default function JobSubmitModal({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState("Execute Batch Compute");
  const [jobType, setJobType] = useState("cpu_intensive");
  const [priority, setPriority] = useState("NORMAL");
  const [maxRetries, setMaxRetries] = useState(3);
  const [baseDelay, setBaseDelay] = useState(2);
  const [payloadStr, setPayloadStr] = useState("{\n  \"limit\": 15000\n}");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      let parsed = {};
      try {
        parsed = JSON.parse(payloadStr);
      } catch (err) {
        throw new Error("Payload must be valid JSON");
      }

      await apiRequest("/jobs", {
        method: "POST",
        body: JSON.stringify({
          name,
          job_type: jobType,
          priority,
          payload: parsed,
          max_retries: maxRetries,
          base_delay_seconds: baseDelay,
        }),
      });
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to submit job");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="w-full max-w-lg bg-card border border-border rounded-xl shadow-2xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-secondary-foreground hover:text-foreground"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2 mb-4">
          <Sparkles className="w-5 h-5 text-primary" />
          <h2 className="text-base font-bold text-foreground">Submit Background Job</h2>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-accent-rose/10 border border-accent-rose/30 rounded text-xs text-accent-rose">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block text-secondary-foreground mb-1 font-medium">Job Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:border-primary font-mono"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-secondary-foreground mb-1 font-medium">Job Type</label>
              <select
                value={jobType}
                onChange={(e) => setJobType(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:border-primary font-mono"
              >
                <option value="cpu_intensive">CPU Intensive (Primes)</option>
                <option value="io_simulation">I/O Network Simulation</option>
                <option value="data_processing">Data Processing ETL</option>
                <option value="image_transformation">Image Transformation</option>
                <option value="report_generator">Report Generator (PDF)</option>
                <option value="failure_simulation">Failure & Retry Simulation</option>
                <option value="sleep_delay">Sleep / Concurrency Stress</option>
              </select>
            </div>

            <div>
              <label className="block text-secondary-foreground mb-1 font-medium">Priority Tier</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground focus:outline-none focus:border-primary font-mono"
              >
                <option value="CRITICAL">CRITICAL (Prio 10)</option>
                <option value="HIGH">HIGH (Prio 7)</option>
                <option value="NORMAL">NORMAL (Prio 4)</option>
                <option value="LOW">LOW (Prio 1)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-secondary-foreground mb-1 font-medium">Max Retries</label>
              <input
                type="number"
                value={maxRetries}
                onChange={(e) => setMaxRetries(parseInt(e.target.value))}
                min={0}
                max={10}
                className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground font-mono"
              />
            </div>
            <div>
              <label className="block text-secondary-foreground mb-1 font-medium">Base Backoff (s)</label>
              <input
                type="number"
                value={baseDelay}
                onChange={(e) => setBaseDelay(parseInt(e.target.value))}
                min={1}
                max={60}
                className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground font-mono"
              />
            </div>
          </div>

          <div>
            <label className="block text-secondary-foreground mb-1 font-medium">JSON Payload</label>
            <textarea
              rows={4}
              value={payloadStr}
              onChange={(e) => setPayloadStr(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-background border border-border text-foreground font-mono text-xs focus:outline-none focus:border-primary"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-secondary text-secondary-foreground hover:bg-border transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-lg bg-primary hover:bg-primary-hover text-white font-semibold shadow-md shadow-primary/25 disabled:opacity-50 transition-all"
            >
              {loading ? "Enqueuing..." : "Dispatch Job"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}