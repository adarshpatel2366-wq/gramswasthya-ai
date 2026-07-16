"use client";
import { useEffect, useRef, useState } from "react";
import Navbar from "@/components/Navbar";
import MessageBubble from "@/components/MessageBubble";
import VoiceInput, { speak } from "@/components/VoiceInput";
import { sendChatMessage, ChatMessage } from "@/lib/api";
import { Send, Trash2, Volume2, Languages, Paperclip } from "lucide-react";

const LANGUAGES = [
  { code: "auto", label: "Auto" },
  { code: "hi", label: "हिंदी" },
  { code: "en", label: "English" },
  { code: "hinglish", label: "Hinglish" },
];

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "नमस्ते 🙏 I'm GramSwasthya AI. Aap apni sehat se juda koi bhi sawal Hindi, English ya Hinglish mein pooch sakte hain. How can I help you today?",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState("auto");
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [voiceOut, setVoiceOut] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSend(text?: string) {
    const content = (text ?? input).trim();
    if (!content || loading) return;

    setMessages((prev) => [...prev, { role: "user", content }]);
    setInput("");
    setLoading(true);

    try {
      const data = await sendChatMessage(content, conversationId, language);
      setConversationId(data.conversation_id);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply, is_emergency: data.is_emergency },
      ]);
      if (voiceOut) {
        speak(data.reply, language === "en" ? "en-IN" : "hi-IN");
      }
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "⚠️ Sorry, I couldn't reach the AI service right now (are you logged in, and is the backend running?). Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function clearChat() {
    setMessages([]);
    setConversationId(null);
  }

  return (
    <main className="flex flex-col h-screen">
      <Navbar />

      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-100 dark:border-slate-800 bg-white/60 dark:bg-slate-950/60">
        <div className="flex items-center gap-2">
          <Languages size={16} className="text-slate-400" />
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="text-sm bg-transparent border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1"
          >
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setVoiceOut((v) => !v)}
            className={`p-2 rounded-lg text-sm flex items-center gap-1 ${
              voiceOut ? "bg-brand-blue text-white" : "bg-slate-100 dark:bg-slate-800"
            }`}
            title="Toggle voice output"
          >
            <Volume2 size={16} />
          </button>
          <button
            onClick={clearChat}
            className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-sm flex items-center gap-1"
          >
            <Trash2 size={16} /> Clear
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-3xl w-full mx-auto">
        {messages.map((m, i) => (
          <MessageBubble key={i} msg={m} />
        ))}
        {loading && (
          <div className="flex gap-1 items-center px-4 py-3 text-slate-400 text-sm">
            <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]" />
            <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]" />
            <span className="w-2 h-2 rounded-full bg-slate-400 animate-bounce" />
            <span className="ml-2">GramSwasthya AI is thinking…</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t border-slate-100 dark:border-slate-800 p-4 bg-white dark:bg-slate-950">
        <div className="max-w-3xl mx-auto flex items-center gap-2">
          <label className="p-2.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-500 cursor-pointer hover:text-brand-blue">
            <Paperclip size={18} />
            <input type="file" className="hidden" accept=".pdf,.jpg,.jpeg,.png" />
          </label>
          <VoiceInput onResult={(t) => handleSend(t)} lang={language === "en" ? "en-IN" : "hi-IN"} />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Apna sawal likhein... (Type your health question)"
            className="flex-1 px-4 py-3 rounded-full border border-slate-200 dark:border-slate-700 bg-transparent focus:outline-none focus:ring-2 focus:ring-brand-blue text-sm"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading}
            className="p-3 rounded-full bg-brand-blue text-white hover:opacity-90 disabled:opacity-50"
          >
            <Send size={18} />
          </button>
        </div>
        <p className="text-center text-xs text-slate-400 mt-2">
          GramSwasthya AI gives general guidance, not a diagnosis. In an emergency, call 108.
        </p>
      </div>
    </main>
  );
}
