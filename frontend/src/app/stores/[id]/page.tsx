"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { ArrowLeft, Clock, MapPin, Scissors, Star, Timer, Loader2 } from "lucide-react";
import { StoreRead } from "@/components/StoreList";
import TimePicker from "@/components/TimePicker";
import { fetchStoreDetails } from "@/lib/api";
import { scrollToSection } from "@/lib/scroll";

export default function StoreDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [store, setStore] = useState<StoreRead | null>(null);
  const [selectedService, setSelectedService] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStoreDetails(id)
      .then((data) => {
        if (!data) {
          setError("Store not found");
        } else {
          // Enrich with UI defaults
          setStore({
            ...data,
            rating: data.rating ?? 4.8,
            reviews: data.reviews ?? 150,
            imageUrl: data.imageUrl ?? "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&q=80&w=1200"
          });
        }
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });
  }, [id]);

  useEffect(() => {
    if (isLoading || !store || window.location.hash !== "#services") return;
    requestAnimationFrame(() => scrollToSection("services"));
  }, [isLoading, store]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
        <p className="text-neutral-400 animate-pulse">Loading grooming destination...</p>
      </div>
    );
  }

  if (error || !store) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-20 h-20 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-6">
          <MapPin className="w-10 h-10 text-red-400" />
        </div>
        <h1 className="text-3xl font-bold mb-2">{error === "Store not found" ? "Saloon Not Found" : "Connection Error"}</h1>
        <p className="text-neutral-400 max-w-md mb-8">
          {error === "Store not found" 
            ? "The saloon you're looking for doesn't exist or may have been removed." 
            : "We're having trouble connecting to our booking system. Please try again later."}
        </p>
        <Link 
          href="/"
          className="px-8 h-12 rounded-full bg-white text-black font-semibold flex items-center justify-center hover:bg-neutral-200 transition-all"
        >
          Back to Explorations
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50">
      {/* Detail Header / Hero */}
      <div className="relative h-[40vh] min-h-[300px] w-full max-w-7xl mx-auto rounded-b-[3rem] overflow-hidden">
        <img
          src={store.imageUrl}
          alt={store.name}
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-neutral-950 via-neutral-950/40 to-black/20" />

        <div className="absolute top-6 left-6 z-10">
          <Link
            href="/"
            className="flex items-center justify-center w-12 h-12 rounded-full bg-white/10 backdrop-blur-md border border-white/20 hover:bg-white/20 transition-colors"
          >
            <ArrowLeft className="w-5 h-5 text-white" />
          </Link>
        </div>

        <div className="absolute bottom-0 left-0 w-full p-8 md:p-12 max-w-4xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md border border-white/10 mb-4">
            <Star className="w-4 h-4 fill-indigo-400 text-indigo-400" />
            <span className="text-sm font-medium">
              {store.rating} ({store.reviews} reviews)
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            {store.name}
          </h1>
          <div className="flex items-center gap-2 text-neutral-300">
            <MapPin className="w-5 h-5" />
            <span className="text-lg">{store.address}</span>
          </div>
        </div>
      </div>

      {/* Services List Section */}
      <main className="max-w-7xl mx-auto px-6 py-12 md:py-20 flex flex-col lg:flex-row gap-12">
        
        {/* Left Column: Services */}
        <div id="services" className="scroll-mt-24 flex-1">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
              <Scissors className="w-5 h-5 text-indigo-400" />
            </div>
            <h2 className="text-2xl font-bold">Services & Pricing</h2>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {store.services && store.services.length > 0 ? (
              store.services.map((service) => {
                const isSelected = selectedService === service.id;
                
                return (
                  <div
                    key={service.id}
                    className={`group p-5 rounded-2xl border transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-6 ${
                      isSelected ? "bg-indigo-500/10 border-indigo-500/50" : "bg-neutral-900 border-white/5 hover:border-white/10"
                    }`}
                  >
                    <div className="flex flex-col gap-2">
                      <h3 className="text-lg font-semibold text-white">
                        {service.name}
                      </h3>
                      <div className="flex items-center gap-4 text-sm text-neutral-400">
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-4 h-4" />
                          <span>{service.duration_minutes} mins</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center justify-between sm:justify-end gap-6 border-t border-white/5 sm:border-t-0 pt-4 sm:pt-0">
                      <div className="text-xl font-bold text-white">
                        ${Number(service.price).toFixed(2)}
                      </div>
                      <button 
                        onClick={() => setSelectedService(service.id)}
                        className={`h-10 px-6 rounded-full font-medium transition-colors shrink-0 ${
                          isSelected 
                            ? "bg-white text-black" 
                            : "bg-indigo-500 hover:bg-indigo-600 text-white"
                        }`}
                      >
                        {isSelected ? "Selected" : "Book Now"}
                      </button>
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="p-12 rounded-2xl border border-dashed border-white/10 bg-white/5 text-center text-neutral-500">
                <Timer className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium text-white">No Services Available</h3>
                <p>This saloon hasn't listed their services yet.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: TimePicker */}
        <div className="w-full lg:w-[450px] shrink-0">
          <div className="sticky top-24">
            {selectedService ? (
              <TimePicker 
                storeId={store.id} 
                serviceId={selectedService} 
                durationMinutes={store.services?.find(s => s.id === selectedService)?.duration_minutes || 30}
              />
            ) : (
              <div className="bg-neutral-900 border border-white/10 rounded-2xl p-8 text-center text-neutral-400 flex flex-col items-center gap-4">
                <div className="w-16 h-16 rounded-full border border-dashed border-white/20 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-neutral-600" />
                </div>
                <p>Select a service to view available appointments and book your slot.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
