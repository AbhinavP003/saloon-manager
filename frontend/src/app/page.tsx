import Link from "next/link";
import { ArrowRight, CalendarDays, Scissors, User } from "lucide-react";
import StoreList from "@/components/StoreList";

export default function Home() {
  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 selection:bg-indigo-500/30">
      {/* Navigation Bar */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-neutral-950/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Scissors className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">SaloonManager</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-neutral-400">
            <Link href="#services" className="hover:text-white transition-colors">Services</Link>
            <Link href="#locations" className="hover:text-white transition-colors">Locations</Link>
            <Link href="#about" className="hover:text-white transition-colors">About</Link>
          </div>
          <div className="flex items-center gap-4">
            <button className="hidden md:flex items-center gap-2 text-sm font-medium hover:text-white transition-colors text-neutral-400">
              <User className="w-4 h-4" />
              Sign In
            </button>
            <button className="h-10 px-5 rounded-full bg-white text-black text-sm font-medium hover:bg-neutral-200 transition-colors">
              Book Now
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden flex flex-col items-center min-h-screen justify-center text-center px-6">
        
        {/* Background Gradients */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] opacity-20 pointer-events-none">
          <div className="absolute inset-0 rounded-full bg-indigo-500 blur-[120px] mix-blend-screen animate-pulse duration-10000" />
          <div className="absolute top-20 left-20 w-96 h-96 rounded-full bg-purple-500 blur-[100px] mix-blend-screen" />
        </div>

        <div className="relative z-10 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md mb-8">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-medium uppercase tracking-wider text-neutral-300">New Stores Added in Kochi</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl min-h-[5rem] font-bold tracking-tighter mb-8 leading-tight">
            Book Your Next{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
              Session
            </span>
          </h1>
          
          <p className="text-lg md:text-xl text-neutral-400 mb-12 max-w-2xl mx-auto leading-relaxed">
            Experience premium grooming with real-time availability. Discover top-rated saloons near you and secure your slot instantly.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button className="h-14 px-8 rounded-full bg-white text-black font-semibold text-lg flex items-center gap-2 hover:scale-105 active:scale-95 transition-all w-full sm:w-auto justify-center group">
              <CalendarDays className="w-5 h-5" />
              Find Appointments
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="h-14 px-8 rounded-full border border-white/10 bg-white/5 text-white font-medium text-lg hover:bg-white/10 transition-colors w-full sm:w-auto justify-center">
              Explore Services
            </button>
          </div>
        </div>

        {/* Floating cards / social proof */}
        <div className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto w-full px-6 relative z-10">
          {[
            { label: "Active Saloons", value: "50+" },
            { label: "Happy Clients", value: "10k+" },
            { label: "Bookings/Day", value: "500+" },
            { label: "Avg Rating", value: "4.9/5" },
          ].map((stat, i) => (
            <div key={i} className="p-6 rounded-2xl border border-white/5 bg-white/[0.02] backdrop-blur-md flex flex-col items-center justify-center">
              <div className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-b from-white to-white/50">{stat.value}</div>
              <div className="text-sm text-neutral-500 mt-1 font-medium">{stat.label}</div>
            </div>
          ))}
        </div>
      </main>

      {/* Featured Stores Section */}
      <StoreList />
    </div>
  );
}
