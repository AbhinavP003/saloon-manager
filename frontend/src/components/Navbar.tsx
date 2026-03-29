"use client";

import Link from "next/link";
import { useAuth } from "@/lib/AuthContext";
import { 
  Scissors, 
  User as UserIcon, 
  LogOut, 
  LayoutDashboard, 
  ChevronDown,
  Calendar
} from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-neutral-950/50 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
            <Scissors className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight">SaloonManager</span>
        </Link>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-neutral-400">
          <Link href="/" className="hover:text-white transition-colors">Explore</Link>
          <Link href="/bookings" className="hover:text-white transition-colors">My Bookings</Link>
          <Link href="/about" className="hover:text-white transition-colors">About</Link>
        </div>

        {/* Auth Actions */}
        <div className="flex items-center gap-4">
          {loading ? (
            <div className="w-8 h-8 rounded-full bg-white/5 animate-pulse" />
          ) : user ? (
            <div className="relative">
              <button 
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-3 p-1 pl-3 rounded-full bg-white/5 border border-white/10 hover:bg-white/10 transition-all group"
              >
                <span className="text-xs font-bold text-neutral-300 group-hover:text-white transition-colors whitespace-nowrap">
                  {user.full_name.split(' ')[0]}
                </span>
                <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-white font-bold text-xs ring-2 ring-transparent group-hover:ring-indigo-500/30 transition-all">
                  {user.full_name[0]}
                </div>
                <ChevronDown className={`w-4 h-4 text-neutral-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
              </button>

              <AnimatePresence>
                {isOpen && (
                  <>
                    <div 
                      className="fixed inset-0 z-10" 
                      onClick={() => setIsOpen(false)} 
                    />
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      className="absolute right-0 mt-3 w-56 rounded-2xl bg-neutral-900 border border-white/10 shadow-2xl z-20 overflow-hidden"
                    >
                      <div className="px-5 py-4 border-b border-white/5 bg-white/[0.02]">
                        <p className="text-[10px] uppercase font-bold tracking-widest text-neutral-500 mb-1">Logged in as</p>
                        <p className="text-sm font-bold text-white truncate">{user.email}</p>
                      </div>
                      <div className="p-2">
                        {user.role === 'owner' && (
                          <Link 
                            href="/owner/dashboard" 
                            className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-400 hover:text-white hover:bg-white/5 rounded-xl transition-all"
                            onClick={() => setIsOpen(false)}
                          >
                            <LayoutDashboard className="w-4 h-4 text-indigo-400" />
                            Owner Dashboard
                          </Link>
                        )}
                        <Link 
                          href="/bookings" 
                          className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-400 hover:text-white hover:bg-white/5 rounded-xl transition-all"
                          onClick={() => setIsOpen(false)}
                        >
                          <Calendar className="w-4 h-4 text-emerald-400" />
                          Appointments
                        </Link>
                        <button 
                          onClick={() => {
                            logout();
                            setIsOpen(false);
                          }}
                          className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-red-400 hover:bg-red-500/10 rounded-xl transition-all"
                        >
                          <LogOut className="w-4 h-4" />
                          Sign Out
                        </button>
                      </div>
                    </motion.div>
                  </>
                )}
              </AnimatePresence>
            </div>
          ) : (
            <div className="flex items-center gap-3">
              <Link 
                href="/login" 
                className="hidden md:flex items-center gap-2 text-sm font-medium text-neutral-400 hover:text-white transition-colors"
              >
                <UserIcon className="w-4 h-4" />
                Sign In
              </Link>
              <Link 
                href="/register" 
                className="h-10 px-5 rounded-full bg-white text-black text-sm font-bold hover:bg-neutral-200 transition-all active:scale-95"
              >
                Join Now
              </Link>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
