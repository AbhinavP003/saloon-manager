"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MapPin, Star, Scissors } from "lucide-react";
import { fetchStores } from "@/lib/api";

// Mocking the StoreRead schema as defined in the backend
interface ServiceRead {
  id: string;
  name: string;
  price: number;
  duration_minutes: number;
}

export interface StoreRead {
  id: string;
  name: string;
  address: string;
  contact_number?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  services?: ServiceRead[];
  // UI ONLY fields for placeholder presentation
  imageUrl?: string;
  rating?: number;
  reviews?: number;
}

export default function StoreList() {
  const [stores, setStores] = useState<StoreRead[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStores()
      .then((data) => {
        // Enforce some UI defaults if backend doesn't provide them yet
        const enriched = data.map((s: StoreRead) => ({
          ...s,
          rating: s.rating ?? 4.5 + Math.random() * 0.5,
          reviews: s.reviews ?? Math.floor(Math.random() * 200),
          imageUrl: s.imageUrl ?? "https://images.unsplash.com/photo-1521590832167-7bfc17484d20?auto=format&fit=crop&q=80&w=800"
        }));
        setStores(enriched);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setIsLoading(false);
      });
  }, []);

  return (
    <section id="locations" className="py-24 px-6 max-w-7xl mx-auto w-full relative z-20 bg-neutral-950">
      <div className="flex items-end justify-between mb-12">
        <div>
          <h2 className="text-3xl font-bold tracking-tight text-white mb-2">Featured Saloons</h2>
          <p className="text-neutral-400">Discover top-rated grooming destinations near you.</p>
        </div>
        <button className="text-sm font-medium text-indigo-400 hover:text-indigo-300 transition-colors hidden sm:block">
          View all locations &rarr;
        </button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse flex flex-col gap-4">
              <div className="aspect-[4/5] bg-white/5 rounded-2xl" />
              <div className="h-6 bg-white/5 rounded w-3/4 mx-1" />
              <div className="h-4 bg-white/5 rounded w-1/2 mx-1" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="p-8 rounded-2xl border border-red-500/20 bg-red-500/10 text-red-400 text-center">
          <p>Unable to load local saloons. Please ensure the backend is running.</p>
          <p className="text-sm opacity-70 mt-2">{error}</p>
        </div>
      ) : stores.length === 0 ? (
        <div className="text-center p-12 text-neutral-500 bg-white/5 rounded-2xl border border-white/5">
          <Scissors className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium text-white">No Saloons Found</h3>
          <p>There are currently no active saloons in your area.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {stores.map((store) => (
            <Link href={`/stores/${store.id}`} key={store.id} className="group cursor-pointer flex flex-col gap-4">
              {/* Image Container */}
              <div className="relative aspect-[4/5] overflow-hidden rounded-2xl bg-neutral-900 border border-white/5">
                <img 
                  src={store.imageUrl} 
                  alt={store.name}
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-neutral-950/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                {/* Floating Action Button */}
                <div className="absolute bottom-5 right-5 translate-y-4 opacity-0 group-hover:translate-y-0 group-hover:opacity-100 transition-all duration-300">
                  <div className="h-10 px-5 rounded-full bg-white text-black text-sm font-semibold shadow-2xl flex items-center justify-center hover:bg-neutral-200 hover:scale-105 transition-all">
                    Book Slot
                  </div>
                </div>
              </div>

              {/* Content Container */}
              <div className="flex flex-col gap-1.5 px-1">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold text-white text-lg leading-tight truncate">
                    {store.name}
                  </h3>
                  <div className="flex items-center gap-1 shrink-0 mt-0.5">
                    <Star className="w-4 h-4 fill-indigo-400 text-indigo-400" />
                    <span className="text-sm font-medium text-white">{store.rating?.toFixed(1)}</span>
                    <span className="text-sm text-neutral-500">({store.reviews})</span>
                  </div>
                </div>
                
                <div className="flex items-center gap-1.5 text-neutral-400">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm truncate">{store.address}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}
