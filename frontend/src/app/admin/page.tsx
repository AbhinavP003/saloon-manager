"use client";

import { useState } from "react";
import Link from "next/link";
import { 
  ArrowLeft, 
  LayoutDashboard, 
  PlusCircle, 
  Scissors, 
  Sparkles, 
  Loader2, 
  CheckCircle2, 
  AlertTriangle, 
  ExternalLink,
  Store,
  Clock,
  MapPin,
  Phone,
  Plus,
  Trash2,
  Save
} from "lucide-react";
import { API_URL } from "@/lib/api";

const ADMIN_TOKEN =
  process.env.NEXT_PUBLIC_ADMIN_TOKEN || "saloon-admin-secret";

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

const PRESETS = {
  barbershop: {
    store: {
      name: "The Modern Gentleman",
      address: "123 Barber St, Kochi, Kerala",
      contact_number: "+91 98765 43210",
      latitude: 10.0159,
      longitude: 76.3419
    },
    hours: DAYS.map((_, i) => ({ day_of_week: i, open_time: "10:00", close_time: "20:00", is_closed: false })),
    services: [
      { name: "Classic Scissor Cut", price: 350.0, duration_minutes: 30, description: "Classic scissor cut" },
      { name: "Beard Sculpting", price: 200.0, duration_minutes: 20, description: "Premium beard shaping" },
      { name: "Luxury Shave", price: 450.0, duration_minutes: 45, description: "Classic hot towel shave" },
    ]
  },
  spa: {
    store: {
      name: "Serenity Wellness Spa",
      address: "456 Orchid Ave, Kakkanad, Kochi",
      contact_number: "+91 99999 88888",
      latitude: 10.0151,
      longitude: 76.3415
    },
    hours: DAYS.map((_, i) => ({ day_of_week: i, open_time: "09:00", close_time: "21:00", is_closed: false })),
    services: [
      { name: "Swedish Deep Tissue", price: 2500.0, duration_minutes: 60, description: "Full body relaxation" },
      { name: "Hydra-Facial", price: 1800.0, duration_minutes: 45, description: "Advanced skin care" },
      { name: "Organic Body Scrub", price: 1500.0, duration_minutes: 60, description: "Natural exfoliation" },
    ]
  }
};

export default function AdminPage() {
  // --- Form State ---
  const [store, setStore] = useState(PRESETS.barbershop.store);
  const [hours, setHours] = useState(PRESETS.barbershop.hours);
  const [services, setServices] = useState(PRESETS.barbershop.services);

  // --- UI State ---
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successData, setSuccessData] = useState<{ store_id: string; message: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const applyPreset = (key: 'barbershop' | 'spa') => {
    setStore(PRESETS[key].store);
    setHours(PRESETS[key].hours);
    setServices(PRESETS[key].services);
    setSuccessData(null);
    setError(null);
  };

  const addService = () => {
    setServices([...services, { name: "", price: 0, duration_minutes: 30, description: "" }]);
  };

  const removeService = (index: number) => {
    setServices(services.filter((_, i) => i !== index));
  };

  const updateService = (index: number, field: string, value: any) => {
    const next = [...services];
    next[index] = { ...next[index], [field]: value };
    setServices(next);
  };

  const updateHours = (index: number, field: string, value: any) => {
    const next = [...hours];
    next[index] = { ...next[index], [field]: value };
    setHours(next);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    setSuccessData(null);

    // Basic Validation
    if (!store.name || !store.address) {
      setError("Store name and address are required.");
      setIsSubmitting(false);
      return;
    }

    try {
      const res = await fetch(`${API_URL}/internal/onboard-store`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Admin-Token": ADMIN_TOKEN
        },
        body: JSON.stringify({ store, hours, services })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to onboard store");
      setSuccessData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 selection:bg-indigo-500/30">
      
      {/* Detail Header / Nav */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-neutral-950/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">Onboarding Simulator</span>
          </div>
          <Link href="/" className="text-sm font-medium text-neutral-400 hover:text-white transition-colors flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Marketplace
          </Link>
        </div>
      </nav>

      <main className="pt-32 pb-24 px-6 max-w-5xl mx-auto">
        
        {/* Intro */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div className="max-w-2xl">
            <h1 className="text-4xl font-bold tracking-tight mb-4">Onboard Your Saloon</h1>
            <p className="text-neutral-400">
              Mimic the real onboarding process. Fill in your details, set your opening hours, and define your service menu. 
              Use presets to quickly see the schema in action.
            </p>
          </div>
          <div className="flex gap-2">
            <button 
              onClick={() => applyPreset('barbershop')}
              className="px-4 h-10 rounded-full bg-white/5 border border-white/10 text-xs font-semibold hover:bg-white/10 transition-colors flex items-center gap-2"
            >
              <Scissors className="w-3.5 h-3.5" />
              Fill Barbershop
            </button>
            <button 
              onClick={() => applyPreset('spa')}
              className="px-4 h-10 rounded-full bg-white/5 border border-white/10 text-xs font-semibold hover:bg-white/10 transition-colors flex items-center gap-2"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Fill Spa
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-12">
          
          {/* SECTION 1: BASIC INFO */}
          <div className="bg-neutral-900/50 border border-white/5 rounded-3xl p-8">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center">
                <Store className="w-5 h-5 text-indigo-400" />
              </div>
              <h2 className="text-2xl font-bold">1. Saloon Details</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Saloon Name</label>
                <input 
                  type="text"
                  value={store.name}
                  onChange={(e) => setStore({...store, name: e.target.value})}
                  placeholder="e.g. Blade & Barrel"
                  className="h-12 bg-black/40 border border-white/10 rounded-xl px-4 text-white focus:border-indigo-500/50 outline-none transition-colors"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Contact Number</label>
                <input 
                  type="text"
                  value={store.contact_number || ""}
                  onChange={(e) => setStore({...store, contact_number: e.target.value})}
                  placeholder="+91 ..."
                  className="h-12 bg-black/40 border border-white/10 rounded-xl px-4 text-white focus:border-indigo-500/50 outline-none transition-colors"
                />
              </div>
              <div className="md:col-span-2 flex flex-col gap-2">
                <label className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Full Address</label>
                <input 
                  type="text"
                  value={store.address}
                  onChange={(e) => setStore({...store, address: e.target.value})}
                  placeholder="Street, City, Building..."
                  className="h-12 bg-black/40 border border-white/10 rounded-xl px-4 text-white focus:border-indigo-500/50 outline-none transition-colors"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Latitude</label>
                <input 
                  type="number"
                  step="0.0001"
                  value={Number(store.latitude)}
                  onChange={(e) => setStore({...store, latitude: Number(e.target.value)})}
                  className="h-12 bg-black/40 border border-white/10 rounded-xl px-4 text-white focus:border-indigo-500/50 outline-none transition-colors"
                />
              </div>
              <div className="flex flex-col gap-2">
                <label className="text-xs font-bold text-neutral-500 uppercase tracking-widest">Longitude</label>
                <input 
                  type="number"
                  step="0.0001"
                  value={Number(store.longitude)}
                  onChange={(e) => setStore({...store, longitude: Number(e.target.value)})}
                  className="h-12 bg-black/40 border border-white/10 rounded-xl px-4 text-white focus:border-indigo-500/50 outline-none transition-colors"
                />
              </div>
            </div>
          </div>

          {/* SECTION 2: OPERATING HOURS */}
          <div className="bg-neutral-900/50 border border-white/5 rounded-3xl p-8">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
                <Clock className="w-5 h-5 text-purple-400" />
              </div>
              <h2 className="text-2xl font-bold">2. Operating Hours</h2>
            </div>

            <div className="space-y-4">
              {hours.map((day, idx) => (
                <div key={idx} className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 bg-black/20 rounded-2xl border border-white/5 hover:border-white/10 transition-colors">
                  <div className="flex items-center gap-4 min-w-[140px]">
                    <div className={`w-2 h-2 rounded-full ${day.is_closed ? "bg-red-500" : "bg-emerald-500"}`} />
                    <span className="font-bold">{DAYS[idx]}</span>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <input 
                        type="time"
                        value={day.open_time}
                        disabled={day.is_closed}
                        onChange={(e) => updateHours(idx, "open_time", e.target.value)}
                        className="bg-neutral-800 border border-white/10 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-purple-500/50 disabled:opacity-30 transition-all"
                      />
                      <span className="text-neutral-600">to</span>
                      <input 
                        type="time"
                        value={day.close_time}
                        disabled={day.is_closed}
                        onChange={(e) => updateHours(idx, "close_time", e.target.value)}
                        className="bg-neutral-800 border border-white/10 rounded-lg px-3 py-1.5 text-sm outline-none focus:border-purple-500/50 disabled:opacity-30 transition-all"
                      />
                    </div>
                    <label className="flex items-center gap-2 cursor-pointer select-none ml-4">
                      <input 
                        type="checkbox"
                        checked={day.is_closed}
                        onChange={(e) => updateHours(idx, "is_closed", e.target.checked)}
                        className="w-4 h-4 rounded border-white/10 bg-black/40 text-indigo-500 focus:ring-0"
                      />
                      <span className="text-sm text-neutral-400">Closed</span>
                    </label>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* SECTION 3: SERVICES */}
          <div className="bg-neutral-900/50 border border-white/5 rounded-3xl p-8">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center">
                  <Scissors className="w-5 h-5 text-emerald-400" />
                </div>
                <h2 className="text-2xl font-bold">3. Service Menu</h2>
              </div>
              <button 
                onClick={addService}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-sm font-bold hover:bg-emerald-500/20 transition-all"
              >
                <Plus className="w-4 h-4" />
                Add Service
              </button>
            </div>

            <div className="space-y-4">
              {services.map((service, idx) => (
                <div key={idx} className="p-6 bg-black/20 rounded-2xl border border-white/5 hover:border-white/10 transition-all grid grid-cols-1 md:grid-cols-12 gap-6 relative group">
                  <div className="md:col-span-5 flex flex-col gap-2">
                    <label className="text-[10px] font-bold text-neutral-600 uppercase tracking-widest">Service Name</label>
                    <input 
                      type="text"
                      value={service.name}
                      onChange={(e) => updateService(idx, "name", e.target.value)}
                      placeholder="e.g. Full Beard Trim"
                      className="bg-transparent border-b border-white/10 py-1 text-white focus:border-emerald-500/50 outline-none transition-colors"
                    />
                  </div>
                  <div className="md:col-span-3 flex flex-col gap-2">
                    <label className="text-[10px] font-bold text-neutral-600 uppercase tracking-widest">Price (INR)</label>
                    <input 
                      type="number"
                      value={service.price}
                      onChange={(e) => updateService(idx, "price", Number(e.target.value))}
                      className="bg-transparent border-b border-white/10 py-1 text-white focus:border-emerald-500/50 outline-none transition-colors"
                    />
                  </div>
                  <div className="md:col-span-3 flex flex-col gap-2">
                    <label className="text-[10px] font-bold text-neutral-600 uppercase tracking-widest">Duration (Mins)</label>
                    <input 
                      type="number"
                      value={service.duration_minutes}
                      onChange={(e) => updateService(idx, "duration_minutes", Number(e.target.value))}
                      className="bg-transparent border-b border-white/10 py-1 text-white focus:border-emerald-500/50 outline-none transition-colors"
                    />
                  </div>
                  <div className="md:col-span-1 flex items-center justify-center">
                    <button 
                      onClick={() => removeService(idx)}
                      className="w-10 h-10 rounded-full flex items-center justify-center text-neutral-600 hover:bg-red-500/10 hover:text-red-400 transition-all opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              ))}
              
              {services.length === 0 && (
                <div className="p-12 text-center border border-dashed border-white/5 rounded-3xl text-neutral-600 italic">
                  No services added yet. Click "Add Service" to build your menu.
                </div>
              )}
            </div>
          </div>

          {/* FINAL SUBMISSION */}
          <div className="flex flex-col items-center gap-6 pt-8 border-t border-white/5">
            
            {error && (
              <div className="w-full p-4 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-400 flex items-start gap-3 animate-in shake duration-300">
                <AlertTriangle className="w-5 h-5 shrink-0" />
                <p className="text-sm font-medium">{error}</p>
              </div>
            )}

            {successData && (
              <div className="w-full p-6 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex flex-col items-center gap-4 animate-in zoom-in-95 duration-500">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-6 h-6" />
                  <h3 className="text-lg font-bold">Saloon Onboarded Successfully!</h3>
                </div>
                <p className="text-sm opacity-90">{successData.message}</p>
                <div className="flex gap-4 mt-2">
                  <Link 
                    href={`/stores/${successData.store_id}`}
                    className="h-10 px-6 rounded-full bg-emerald-500 text-black font-bold flex items-center gap-2 hover:bg-emerald-400 transition-all"
                  >
                    View Live Page
                    <ExternalLink className="w-4 h-4" />
                  </Link>
                  <button 
                    onClick={() => setSuccessData(null)}
                    className="h-10 px-6 rounded-full bg-white/5 border border-white/10 text-white font-bold hover:bg-white/10 transition-all"
                  >
                    Onboard Another
                  </button>
                </div>
              </div>
            )}

            {!successData && (
              <button 
                disabled={isSubmitting}
                onClick={handleSubmit}
                className="w-full max-w-md h-16 rounded-2xl bg-white text-black font-bold text-xl flex items-center justify-center gap-3 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-2xl shadow-white/5"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    Onboarding In Progress...
                  </>
                ) : (
                  <>
                    <Save className="w-6 h-6" />
                    Complete Onboarding
                  </>
                )}
              </button>
            )}
            
            <p className="text-neutral-500 text-xs text-center max-w-sm">
              Note: This simulator performs real database transactions. Once submitted, the saloon will be available for public discovery.
            </p>
          </div>

        </div>
      </main>
    </div>
  );
}
