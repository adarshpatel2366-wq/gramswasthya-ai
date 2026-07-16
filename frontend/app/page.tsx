import Link from "next/link";
import Navbar from "@/components/Navbar";
import {
  MessageCircle,
  FileText,
  Camera,
  MapPin,
  Mic,
  Languages,
  ShieldCheck,
} from "lucide-react";

const features = [
  { icon: MessageCircle, title: "Chat with AI", desc: "Get instant health guidance in simple language, day or night." },
  { icon: FileText, title: "Report & Prescription Explainer", desc: "Upload a report or prescription and get a plain-language summary." },
  { icon: Camera, title: "Skin Image Insight", desc: "Upload a photo for general guidance — always paired with doctor advice." },
  { icon: MapPin, title: "Nearby Hospitals", desc: "Find hospitals, PHCs, CHCs and pharmacies close to you." },
  { icon: Mic, title: "Voice Chat", desc: "Speak instead of typing — great for low-literacy users." },
  { icon: Languages, title: "Hindi · English · Hinglish", desc: "The AI automatically replies in your language." },
];

export default function Home() {
  return (
    <main>
      <Navbar />

      <section className="max-w-6xl mx-auto px-4 pt-16 pb-20 text-center">
        <span className="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-brand-softblue text-brand-blue dark:bg-blue-950/40 mb-6">
          <ShieldCheck size={14} /> Trusted health guidance for every village
        </span>
        <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight mb-4">
          Health guidance, <span className="text-brand-blue">anytime</span>,
          <br className="hidden sm:block" /> in <span className="text-brand-green">your language</span>.
        </h1>
        <p className="max-w-2xl mx-auto text-slate-500 dark:text-slate-400 mb-8">
          GramSwasthya AI helps rural communities across India understand symptoms, reports,
          and prescriptions, and find the nearest hospital — all in Hindi, English, or Hinglish.
        </p>
        <div className="flex items-center justify-center gap-3">
          <Link href="/chat" className="px-6 py-3 rounded-full bg-brand-blue text-white font-semibold hover:opacity-90 transition">
            Start Chatting
          </Link>
          <Link href="/signup" className="px-6 py-3 rounded-full border border-slate-200 dark:border-slate-700 font-semibold hover:bg-slate-50 dark:hover:bg-slate-900 transition">
            Create Account
          </Link>
        </div>
      </section>

      <section className="max-w-6xl mx-auto px-4 pb-24 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {features.map((f) => (
          <div
            key={f.title}
            className="p-6 rounded-xl2 border border-slate-100 dark:border-slate-800 hover:shadow-lg transition bg-white dark:bg-slate-900"
          >
            <div className="w-11 h-11 rounded-xl bg-brand-softblue dark:bg-blue-950/40 flex items-center justify-center text-brand-blue mb-4">
              <f.icon size={22} />
            </div>
            <h3 className="font-semibold mb-1">{f.title}</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">{f.desc}</p>
          </div>
        ))}
      </section>

      <footer className="border-t border-slate-100 dark:border-slate-800 py-8 text-center text-sm text-slate-400">
        GramSwasthya AI is a guidance tool and does not replace professional medical care.
        In an emergency, call 108 immediately.
      </footer>
    </main>
  );
}
