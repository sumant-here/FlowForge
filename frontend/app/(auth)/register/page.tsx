"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { apiRequest } from "@/lib/api-client";
import { Zap, Lock, Mail, User, ArrowRight } from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { login } = useAuth();
  const router = useRouter();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res: any = await apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, full_name: fullName }),
      });
      login(res.access_token, res.user);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-card border border-border rounded-2xl shadow-2xl p-8">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/25">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-foreground">Create FlowForge Account</h1>
            <p className="text-xs text-secondary-foreground font-mono">Distributed Control Plane</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-accent-rose/10 border border-accent-rose/30 text-xs text-accent-rose">
            {error}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4 text-xs">
          <div>
            <label className="block text-secondary-foreground mb-1 font-medium">Full Name</label>
            <div className="relative">
              <User className="w-4 h-4 text-secondary-foreground absolute left-3 top-2.5" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-background border border-border text-foreground font-mono focus:outline-none focus:border-primary"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-secondary-foreground mb-1 font-medium">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-secondary-foreground absolute left-3 top-2.5" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-background border border-border text-foreground font-mono focus:outline-none focus:border-primary"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-secondary-foreground mb-1 font-medium">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-secondary-foreground absolute left-3 top-2.5" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 rounded-lg bg-background border border-border text-foreground font-mono focus:outline-none focus:border-primary"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-lg bg-primary hover:bg-primary-hover text-white font-semibold shadow-md shadow-primary/25 disabled:opacity-50 transition-all flex items-center justify-center space-x-2"
          >
            <span>{loading ? "Creating account..." : "Register Account"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-border text-center">
          <Link href="/login" className="text-xs text-indigo-400 hover:underline">
            Already have an account? Sign in ➔
          </Link>
        </div>
      </div>
    </div>
  );
}
