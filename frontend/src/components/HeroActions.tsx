"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, CalendarDays } from "lucide-react";
import { fetchStores } from "@/lib/api";
import { scrollToSection } from "@/lib/scroll";

export default function HeroActions() {
  const router = useRouter();
  const [firstStoreId, setFirstStoreId] = useState<string | null>(null);

  useEffect(() => {
    fetchStores()
      .then((stores) => {
        if (stores.length > 0) setFirstStoreId(stores[0].id);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (window.location.hash === "#locations") {
      requestAnimationFrame(() => scrollToSection("locations"));
    }
  }, []);

  const handleFindAppointments = () => {
    scrollToSection("locations");
  };

  const handleExploreServices = () => {
    if (firstStoreId) {
      router.push(`/stores/${firstStoreId}#services`);
      return;
    }
    scrollToSection("locations");
  };

  return (
    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
      <button
        type="button"
        onClick={handleFindAppointments}
        className="h-14 px-8 rounded-full bg-white text-black font-semibold text-lg flex items-center gap-2 hover:scale-105 active:scale-95 transition-all w-full sm:w-auto justify-center group"
      >
        <CalendarDays className="w-5 h-5" />
        Find Appointments
        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
      </button>
      <button
        type="button"
        onClick={handleExploreServices}
        className="h-14 px-8 rounded-full border border-white/10 bg-white/5 text-white font-medium text-lg hover:bg-white/10 transition-colors w-full sm:w-auto flex items-center justify-center"
      >
        Explore Services
      </button>
    </div>
  );
}
