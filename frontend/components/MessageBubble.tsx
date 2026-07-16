"use client";
import ReactMarkdown from "react-markdown";
import { Copy, AlertTriangle } from "lucide-react";
import { ChatMessage } from "@/lib/api";

export default function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[85%] sm:max-w-[70%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? "bg-brand-blue text-white rounded-br-sm"
            : msg.is_emergency
            ? "bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900 text-red-900 dark:text-red-200 rounded-bl-sm"
            : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-100 rounded-bl-sm"
        }`}
      >
        {msg.is_emergency && !isUser && (
          <div className="flex items-center gap-1 text-xs font-bold mb-1 uppercase tracking-wide">
            <AlertTriangle size={14} /> Emergency guidance
          </div>
        )}
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown>{msg.content}</ReactMarkdown>
        </div>
        {!isUser && (
          <button
            onClick={() => navigator.clipboard.writeText(msg.content)}
            className="mt-2 flex items-center gap-1 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
          >
            <Copy size={12} /> Copy
          </button>
        )}
      </div>
    </div>
  );
}
