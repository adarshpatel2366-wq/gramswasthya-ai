"use client";
import { useState, useRef } from "react";
import { Mic, MicOff } from "lucide-react";

export default function VoiceInput({
  onResult,
  lang = "hi-IN",
}: {
  onResult: (text: string) => void;
  lang?: string;
}) {
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  function toggleListening() {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("Voice input isn't supported in this browser. Try Chrome on Android/desktop.");
      return;
    }

    if (listening) {
      recognitionRef.current?.stop();
      setListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = lang; // e.g. 'hi-IN' or 'en-IN'
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
    };
    recognition.onend = () => setListening(false);
    recognition.onerror = () => setListening(false);

    recognitionRef.current = recognition;
    recognition.start();
    setListening(true);
  }

  return (
    <button
      type="button"
      onClick={toggleListening}
      className={`p-2.5 rounded-full transition ${
        listening
          ? "bg-red-500 text-white animate-pulse"
          : "bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-brand-blue"
      }`}
      title="Voice input"
    >
      {listening ? <MicOff size={18} /> : <Mic size={18} />}
    </button>
  );
}

export function speak(text: string, lang = "hi-IN") {
  if (typeof window === "undefined") return;
  const synth = window.speechSynthesis;
  if (!synth) return;
  synth.cancel();
  const utterance = new SpeechSynthesisUtterance(text.replace(/[*#_`]/g, ""));
  utterance.lang = lang;
  synth.speak(utterance);
}
