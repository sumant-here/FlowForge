"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useSocket } from "@/lib/socket-context";
import { useAuth } from "@/lib/auth-context";
import { Zap, Activity, Plus, Shield, User, Terminal, LogOut } from "lucide-react";
import JobSubmitModal from "./JobSubmitModal";

export default function Navbar() {
  const { isConnected } = useSocket();
  const { user, logout } = useAuth();
  const [showSubmitModal, setShowSubmitModal] = useState(false);

  return (
    <>
      <header className="h-16 border-b border-border bg-card/60 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
        <div className="flex items-center space-x-4">
          <Link href="/dashboard" className="flex items-center space-x-3 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-lg text-foreground tracking-tight">FlowForge</span>
              <span className="text-[10px] ml-2 px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-400 font-mono">v1.0.0</span>
            </div>
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          {/* Real-time Status */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-border/40 border border-border text-xs">
            <span className={`w-2 h-2 rounded-full ${isConnected ? "bg-accent-emerald animate-pulse" : "bg-accent-rose"}`} />
            <span className="text-secondary-foreground font-mono">{isConnected ? "LIVE TELEMETRY" : "CONNECTING..."}</span>
          </div>

          {/* Quick Action Button */}
          <button
            onClick={() => setShowSubmitModal(true)}
            className="flex items-center space-x-2 px-3.5 py-1.5 rounded-lg bg-primary hover:bg-primary-hover text-white text-xs font-semibold shadow-md shadow-primary/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Submit Job</span>
          </button>

          {/* User Profile */}
          {user ? (
            <div className="flex items-center space-x-3 pl-2 border-l border-border">
              <div className="text-right">
                <p className="text-xs font-medium text-foreground">{user.full_name || user.email}</p>
                <p className="text-[10px] text-secondary-foreground font-mono">{user.role}</p>
              </div>
              <button
                onClick={logout}
                title="Logout"
                className="p-1.5 rounded-lg bg-border/50 hover:bg-border text-secondary-foreground hover:text-foreground transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="text-xs font-medium text-indigo-400 hover:text-indigo-300 px-3 py-1.5 rounded-lg bg-indigo-500/10 border border-indigo-500/30"
            >
              Sign In
            </Link>
          )}
        </div>
      </header>

      {showSubmitModal && <JobSubmitModal onClose={() => setShowSubmitModal(false)} />}
    </>
  );
}
