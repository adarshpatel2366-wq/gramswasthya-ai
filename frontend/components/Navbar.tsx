"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { Moon, Sun, Stethoscope, Siren } from "lucide-react";

export default function Navbar() {
  const [dark, setDark] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem("gs_theme");
    const isDark = saved === "dark";
    setDark(isDark);
    document.documentElement.classList.toggle("dark", isDark);
  }, []);

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem("gs_theme", next ? "dark" : "light");
  }

  return (
    <nav className="sticky top-0 z-40 backdrop-blur bg-white/80 dark:bg-slate-950/80 border-b border-slate-100 dark:border-slate-800">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-bold text-lg text-brand-blue">
          <Stethoscope size={22} />
          GramSwasthya <span className="text-brand-green">AI</span>
        </Link>
        <div className="flex items-center gap-3">
          <Link
            href="/chat"
            className="hidden sm:flex items-center gap-1 text-sm font-medium px-3 py-1.5 rounded-full bg-red-50 text-red-600 dark:bg-red-950/40 dark:text-red-400"
          >
            <Siren size={16} /> Emergency
          </Link>
          <Link href="/dashboard" className="text-sm font-medium hover:text-brand-blue">
            Dashboard
          </Link>
          <Link
            href="/chat"
            className="text-sm font-semibold px-4 py-2 rounded-full bg-brand-blue text-white hover:opacity-90 transition"
          >
            Start Chat
          </Link>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800"
            aria-label="Toggle dark mode"
          >
            {dark ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </div>
    </nav>
  );
}
