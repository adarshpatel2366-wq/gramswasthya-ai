"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login({ email, password });
      localStorage.setItem("gs_token", data.access_token);
      router.push("/chat");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed. Please check your details.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <Navbar />
      <div className="max-w-sm mx-auto mt-16 px-4">
        <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
        <p className="text-sm text-slate-500 mb-6">Log in to continue to GramSwasthya AI</p>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            required
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent text-sm"
          />
          <input
            type="password"
            required
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-transparent text-sm"
          />
          {error && <p className="text-sm text-red-500">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-brand-blue text-white font-semibold hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Logging in…" : "Log In"}
          </button>
        </form>

        <p className="text-sm text-slate-500 mt-4 text-center">
          Don't have an account?{" "}
          <Link href="/signup" className="text-brand-blue font-medium">
            Sign up
          </Link>
        </p>
      </div>
    </main>
  );
}
