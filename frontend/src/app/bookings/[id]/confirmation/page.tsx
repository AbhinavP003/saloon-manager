"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { 
  CheckCircle2, 
  Calendar, 
  Clock, 
  MapPin, 
  Scissors, 
  ArrowLeft, 
  Share2, 
  Download,
  Loader2,
  Sparkles
} from "lucide-react";
import { format, parseISO } from "date-fns";
import { motion, AnimatePresence } from "framer-motion";
import { fetchBooking, fetchStoreDetails } from "@/lib/api";

export default function BookingConfirmationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const [booking, setBooking] = useState<any>(null);
  const [store, setStore] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        const bookingData = await fetchBooking(id);
        if (!bookingData) {
          setError("Booking not found");
          setIsLoading(false);
          return;
        }
        setBooking(bookingData);

        if (bookingData.store) {
          setStore(bookingData.store);
        } else {
          const storeData = await fetchStoreDetails(bookingData.store_id);
          setStore(storeData);
        }
        setIsLoading(false);
      } catch (err: any) {
        setError(err.message);
        setIsLoading(false);
      }
    };

    loadData();
  }, [id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
        <p className="text-neutral-400 animate-pulse">Confirming your appointment details...</p>
      </div>
    );
  }

  if (error || !booking) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center p-6 text-center">
        <div className="w-20 h-20 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-6">
          <ArrowLeft className="w-10 h-10 text-red-400" />
        </div>
        <h1 className="text-3xl font-bold mb-2">Booking Not Found</h1>
        <p className="text-neutral-400 max-w-md mb-8">
          We couldn't retrieve the details for this booking. It might have been cancelled or the link is invalid.
        </p>
        <Link 
          href="/"
          className="px-8 h-12 rounded-full bg-white text-black font-semibold flex items-center justify-center hover:bg-neutral-200 transition-all"
        >
          Return Home
        </Link>
      </div>
    );
  }

  const service =
    booking.service ??
    store?.services?.find((s: any) => s.id === booking.service_id);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 selection:bg-indigo-500/30 overflow-x-hidden">
      {/* Background Glows */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] bg-indigo-600/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[60%] h-[60%] bg-purple-600/10 blur-[120px] rounded-full" />
      </div>

      <main className="relative z-10 max-w-2xl mx-auto px-6 pt-20 pb-24">
        
        {/* Success Header */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="flex flex-col items-center text-center mb-12"
        >
          <div className="relative mb-8">
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200, damping: 15 }}
              className="w-24 h-24 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-[0_0_40px_rgba(99,102,241,0.4)]"
            >
              <CheckCircle2 className="w-12 h-12 text-white" />
            </motion.div>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="absolute -inset-2 rounded-full border border-dashed border-indigo-500/30"
            />
            <Sparkles className="absolute -top-2 -right-2 w-6 h-6 text-indigo-400 animate-pulse" />
          </div>
          
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            You're All Set!
          </h1>
          <p className="text-neutral-400 text-lg">
            We've sent a confirmation to your email. See you soon, {booking.customer_name}!
          </p>
        </motion.div>

        {/* Ticket / Card */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="relative"
        >
          {/* Decorative edges */}
          <div className="absolute -left-3 top-1/2 -translate-y-1/2 w-6 h-12 bg-neutral-950 rounded-full z-20" />
          <div className="absolute -right-3 top-1/2 -translate-y-1/2 w-6 h-12 bg-neutral-950 rounded-full z-20" />
          
          <div className="bg-neutral-900 border border-white/10 rounded-[2.5rem] overflow-hidden backdrop-blur-xl shadow-2xl">
            
            {/* Store Banner */}
            <div className="h-32 w-full relative">
              <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-purple-600/20" />
              <div className="absolute inset-0 flex items-center justify-center opacity-30">
                <Scissors className="w-16 h-16 text-white" />
              </div>
            </div>

            <div className="p-8 md:p-10 pt-6">
              <div className="flex justify-between items-start mb-10">
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">{store?.name}</h2>
                  <div className="flex items-center gap-1.5 text-neutral-400 text-sm">
                    <MapPin className="w-3.5 h-3.5" />
                    <span>{store?.address}</span>
                  </div>
                </div>
                <div className="px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-wider">
                  Confirmed
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-neutral-500 font-bold">Service</span>
                  <div className="flex items-center gap-2 text-white font-semibold">
                    <Scissors className="w-4 h-4 text-indigo-400" />
                    {service?.name || "Haircut & Styling"}
                  </div>
                </div>
                
                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-neutral-500 font-bold">Duration</span>
                  <div className="flex items-center gap-2 text-white font-semibold">
                    <Clock className="w-4 h-4 text-indigo-400" />
                    {service?.duration_minutes || 45} Minutes
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-neutral-500 font-bold">Date</span>
                  <div className="flex items-center gap-2 text-white font-semibold">
                    <Calendar className="w-4 h-4 text-indigo-400" />
                    {format(parseISO(booking.start_time), "EEEE, MMMM do")}
                  </div>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] uppercase tracking-widest text-neutral-500 font-bold">Time</span>
                  <div className="flex items-center gap-2 text-white font-semibold">
                    <Clock className="w-4 h-4 text-indigo-400" />
                    {format(parseISO(booking.start_time), "h:mm a")}
                  </div>
                </div>
              </div>

              {/* Perforation line */}
              <div className="border-t border-dashed border-white/10 my-8 w-full" />

              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="flex flex-col items-center md:items-start">
                  <span className="text-[10px] uppercase tracking-widest text-neutral-500 font-bold mb-1">Total Fee</span>
                  <span className="text-3xl font-bold text-white">${Number(service?.price || 0).toFixed(2)}</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <button className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors">
                    <Download className="w-5 h-5" />
                  </button>
                  <button className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center hover:bg-white/10 transition-colors">
                    <Share2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-12 flex flex-col items-center gap-6"
        >
          <Link 
            href="/"
            className="w-full h-14 rounded-2xl bg-white text-black font-bold text-lg flex items-center justify-center hover:scale-[1.02] active:scale-[0.98] transition-all shadow-xl"
          >
            Explore More Saloons
          </Link>
          
          <div className="flex items-center gap-4 text-neutral-500 text-sm">
            <Link href="/" className="hover:text-white transition-colors">Change Booking</Link>
            <span className="w-1 h-1 rounded-full bg-neutral-700" />
            <Link href="/" className="hover:text-white transition-colors">Contact Store</Link>
          </div>
        </motion.div>

      </main>
    </div>
  );
}
