"use client";

import { useEffect, useState } from "react";
import { fetchMyBookings, cancelBooking } from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";
import { 
  Calendar, 
  MapPin, 
  Clock, 
  XCircle, 
  CheckCircle2, 
  AlertCircle,
  Loader2,
  Scissors,
  ChevronRight,
  TrendingDown
} from "lucide-react";
import { format, parseISO, isPast, isFuture } from "date-fns";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "@/components/Navbar";

export default function MyBookingsPage() {
  const { user, loading: authLoading } = useAuth();
  const [bookings, setBookings] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadBookings();
    } else if (!authLoading) {
      setIsLoading(false);
    }
  }, [user, authLoading]);

  const loadBookings = async () => {
    try {
      const data = await fetchMyBookings();
      setBookings(data);
    } catch (err: any) {
      toast.error(err.message || "Failed to load bookings");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = async (bookingId: string) => {
    const toastId = toast.loading("Cancelling appointment...");
    try {
      await cancelBooking(bookingId);
      toast.success("Appointment cancelled successfully", { id: toastId });
      loadBookings(); // Refresh the list
    } catch (err: any) {
      toast.error(err.message || "Cancellation failed", { id: toastId });
    }
  };

  if (authLoading || (isLoading && user)) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
        <p className="text-neutral-400 animate-pulse font-medium">Loading your appointments...</p>
      </div>
    );
  }

  if (!user && !authLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center p-6 text-center">
        <Navbar />
        <div className="max-w-md bg-neutral-900/50 border border-white/5 p-10 rounded-[2.5rem] backdrop-blur-xl">
          <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <XCircle className="w-8 h-8 text-neutral-500" />
          </div>
          <h1 className="text-2xl font-bold mb-4">Authentication Required</h1>
          <p className="text-neutral-400 mb-8 leading-relaxed">
            Please sign in to view and manage your grooming appointments.
          </p>
          <a 
            href="/login?callbackUrl=/bookings" 
            className="inline-flex h-12 px-8 rounded-full bg-white text-black font-bold items-center justify-center hover:bg-neutral-200 transition-all active:scale-95"
          >
            Sign In Now
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 selection:bg-indigo-500/30">
      <Navbar />
      
      <main className="pt-32 pb-24 px-6 max-w-4xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
          <div>
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/20 bg-indigo-500/10 text-indigo-400 text-[10px] font-bold uppercase tracking-widest mb-4"
            >
              <Calendar className="w-3 h-3" />
              Member Access
            </motion.div>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight">Your Appointments</h1>
          </div>
          
          <div className="flex gap-4">
            <div className="p-4 bg-neutral-900 border border-white/5 rounded-2xl text-center min-w-[120px]">
              <div className="text-2xl font-bold">{bookings.length}</div>
              <div className="text-[10px] text-neutral-500 font-bold uppercase tracking-widest">Total Visits</div>
            </div>
            <div className="p-4 bg-neutral-900 border border-white/5 rounded-2xl text-center min-w-[120px]">
              <div className="text-2xl font-bold text-emerald-400">
                {bookings.filter(b => b.status === "completed").length}
              </div>
              <div className="text-[10px] text-neutral-500 font-bold uppercase tracking-widest">Completed</div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <AnimatePresence mode="popLayout">
            {bookings.length > 0 ? (
              bookings.map((booking, idx) => (
                <motion.div
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95 }}
                  transition={{ delay: idx * 0.1 }}
                  key={booking.id}
                  className="group relative bg-neutral-900/50 border border-white/5 rounded-[2rem] p-8 backdrop-blur-xl hover:bg-neutral-900 transition-all duration-500 overflow-hidden"
                >
                  {/* Status Indicator */}
                  <div className={`absolute top-0 right-0 w-32 h-32 -mr-8 -mt-8 opacity-5 rounded-full blur-3xl 
                    ${booking.status === 'confirmed' ? 'bg-emerald-500' : 
                      booking.status === 'pending' ? 'bg-amber-500' : 
                      booking.status === 'cancelled' ? 'bg-red-500' : 'bg-neutral-500'}`} 
                  />

                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-8 relative z-10">
                    <div className="flex items-start gap-6">
                      <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/5 flex items-center justify-center shrink-0">
                        <Scissors className="w-8 h-8 text-indigo-400" />
                      </div>
                      <div>
                        <h2 className="text-xl font-bold mb-1">{booking.service?.name || "Premium Grooming"}</h2>
                        <div className="flex items-center gap-2 text-neutral-400 text-sm mb-4">
                          <MapPin className="w-3.5 h-3.5" />
                          <span>{booking.store?.name || "Saloon"}</span>
                          <span className="text-neutral-700">•</span>
                          <span>{booking.store?.address}</span>
                        </div>
                        
                        <div className="flex flex-wrap gap-4">
                          <div className="flex items-center gap-2 text-xs font-bold text-neutral-500 uppercase tracking-widest bg-black/40 px-3 py-1.5 rounded-lg border border-white/5">
                            <Calendar className="w-3.5 h-3.5 text-indigo-500" />
                            {format(parseISO(booking.start_time), "MMM d, yyyy")}
                          </div>
                          <div className="flex items-center gap-2 text-xs font-bold text-neutral-500 uppercase tracking-widest bg-black/40 px-3 py-1.5 rounded-lg border border-white/5">
                            <Clock className="w-3.5 h-3.5 text-indigo-500" />
                            {format(parseISO(booking.start_time), "h:mm a")}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-3 min-w-[140px]">
                      <span className={`px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest border
                        ${booking.status === 'confirmed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                          booking.status === 'pending' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 
                          booking.status === 'cancelled' ? 'bg-red-500/10 text-red-500 border-red-500/20' : 
                          'bg-white/5 text-neutral-400 border-white/10'}`}
                      >
                        {booking.status}
                      </span>
                      
                      {booking.status !== 'cancelled' && isFuture(parseISO(booking.start_time)) && (
                        <button 
                          onClick={() => handleCancel(booking.id)}
                          className="text-[10px] font-bold uppercase tracking-widest text-neutral-600 hover:text-red-400 transition-colors py-2 px-1"
                        >
                          Cancel Appointment
                        </button>
                      )}
                      
                      {booking.status === 'completed' && (
                        <div className="flex items-center gap-1.5 text-emerald-400">
                          <CheckCircle2 className="w-4 h-4" />
                          <span className="text-[10px] font-bold uppercase tracking-widest">Visit Logged</span>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))
            ) : (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="py-32 text-center"
              >
                <div className="w-20 h-20 bg-neutral-900 border border-white/5 rounded-[2rem] flex items-center justify-center mx-auto mb-8">
                  <Calendar className="w-10 h-10 text-neutral-700" />
                </div>
                <h3 className="text-xl font-bold mb-2">No Appointments Yet</h3>
                <p className="text-neutral-500 mb-8 max-w-xs mx-auto">
                  Your grooming journey starts here. Discover our premium saloons and book your first session.
                </p>
                <a 
                  href="/" 
                  className="inline-flex h-12 px-8 rounded-full border border-indigo-500/30 text-indigo-400 font-bold items-center justify-center hover:bg-indigo-500 hover:text-white transition-all"
                >
                  Explore Saloons
                </a>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}
