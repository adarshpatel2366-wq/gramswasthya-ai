"use client";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import { fetchConversations, fetchNearbyHospitals } from "@/lib/api";
import { MapPin, MessageSquare, Loader2 } from "lucide-react";

export default function DashboardPage() {
  const [conversations, setConversations] = useState<any[]>([]);
  const [hospitals, setHospitals] = useState<any[]>([]);
  const [loadingHospitals, setLoadingHospitals] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchConversations()
      .then(setConversations)
      .catch(() => setError("Log in to see your conversation history."));
  }, []);

  function findHospitals() {
    setLoadingHospitals(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const data = await fetchNearbyHospitals(pos.coords.latitude, pos.coords.longitude);
          setHospitals(data);
        } catch {
          setError("Could not fetch nearby hospitals right now.");
        } finally {
          setLoadingHospitals(false);
        }
      },
      () => {
        setError("Location permission denied. Try entering your PIN code instead.");
        setLoadingHospitals(false);
      }
    );
  }

  return (
    <main>
      <Navbar />
      <div className="max-w-5xl mx-auto px-4 py-10">
        <h1 className="text-2xl font-bold mb-6">Your Dashboard</h1>
        {error && <p className="text-sm text-amber-600 mb-4">{error}</p>}

        <div className="grid md:grid-cols-2 gap-6">
          <section className="p-5 rounded-xl2 border border-slate-100 dark:border-slate-800">
            <h2 className="font-semibold flex items-center gap-2 mb-4">
              <MessageSquare size={18} className="text-brand-blue" /> Chat History
            </h2>
            {conversations.length === 0 ? (
              <p className="text-sm text-slate-400">No conversations yet — start chatting to see history here.</p>
            ) : (
              <ul className="space-y-2">
                {conversations.map((c) => (
                  <li key={c.id} className="text-sm p-3 rounded-lg bg-slate-50 dark:bg-slate-900">
                    {c.title}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="p-5 rounded-xl2 border border-slate-100 dark:border-slate-800">
            <h2 className="font-semibold flex items-center gap-2 mb-4">
              <MapPin size={18} className="text-brand-green" /> Nearby Hospitals
            </h2>
            <button
              onClick={findHospitals}
              disabled={loadingHospitals}
              className="text-sm px-4 py-2 rounded-full bg-brand-green text-white flex items-center gap-2 disabled:opacity-50"
            >
              {loadingHospitals && <Loader2 size={14} className="animate-spin" />}
              Use my location
            </button>
            <ul className="mt-4 space-y-2">
              {hospitals.map((h, i) => (
                <li key={i} className="text-sm p-3 rounded-lg bg-slate-50 dark:bg-slate-900">
                  <p className="font-medium">{h.name}</p>
                  <p className="text-xs text-slate-400">
                    {h.type} · {h.distance_km} km away
                  </p>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </main>
  );
}
