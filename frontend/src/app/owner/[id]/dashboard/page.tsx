"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { 
  fetchStoreBookings, 
  fetchStoreDetails, 
  updateBookingStatus 
} from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";
import { 
  Calendar, 
  Clock, 
  User, 
  CheckCircle2, 
  XCircle, 
  UserMinus, 
  ChevronRight, 
  Loader2, 
  Scissors, 
  LayoutDashboard,
  TrendingUp,
  AlertCircle,
  MoreVertical,
  Filter
} from "lucide-react";
import { format, parseISO, isToday, isFuture, isPast } from "date-fns";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";

export default function OwnerDashboardPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const { user, logout } = useAuth();
  const [store, setStore] = useState<any>(null);
  const [bookings, setBookings] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "pending" | "confirmed">("all");

  useEffect(() => {
    const loadData = async () => {
      try {
        const [storeData, bookingsData] = await Promise.all([
          fetchStoreDetails(id),
          fetchStoreBookings(id)
        ]);
        setStore(storeData);
        setBookings(bookingsData);
      } catch (err: any) {
        toast.error("Failed to load dashboard data");
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, [id]);

  const handleStatusUpdate = async (bookingId: string, newStatus: string) => {
    const toastId = toast.loading(`Updating status to ${newStatus}...`);
    try {
      const updated = await updateBookingStatus(bookingId, newStatus);
      setBookings(prev => prev.map(b => b.id === bookingId ? updated : b));
      toast.success(`Booking ${newStatus} successfully`, { id: toastId });
    } catch (err: any) {
      toast.error(err.message, { id: toastId });
    }
  };

  const filteredBookings = bookings.filter(b => {
    if (filter === "all") return true;
    return b.status === filter;
  });

  const stats = {
    total: bookings.length,
    pending: bookings.filter(b => b.status === "pending").length,
    today: bookings.filter(b => isToday(parseISO(b.start_time))).length,
    revenue: bookings
      .filter(b => b.status === "completed")
      .reduce((acc, b) => {
        const service = store?.services?.find((s: any) => s.id === b.service_id);
        return acc + Number(service?.price || 0);
      }, 0)
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
        <p className="text-neutral-400 animate-pulse font-medium">Loading your Command Center...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 selection:bg-indigo-500/30">
      
      {/* Sidebar Navigation (Horizontal for this view) */}
      <nav className="fixed top-0 w-full z-50 border-b border-white/10 bg-neutral-950/50 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <LayoutDashboard className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight block leading-none">{store?.name}</span>
              <span className="text-[10px] text-neutral-500 uppercase tracking-widest font-bold">Owner Dashboard</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-6 text-sm font-medium text-neutral-400 mr-8">
              <Link href="/" className="hover:text-white transition-colors">Explorer</Link>
              <Link href="#" className="text-white">Overview</Link>
              <Link href="#" className="hover:text-white transition-colors">Services</Link>
            </div>
            
            <div className="flex items-center gap-3 pr-4 border-r border-white/10 mr-4">
               <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-xs font-bold text-white shadow-lg shadow-indigo-500/20">
                 {user?.full_name?.[0] || 'O'}
               </div>
               <span className="text-xs font-bold text-neutral-400">{user?.full_name || 'Owner'}</span>
            </div>

            <button 
              onClick={() => logout()}
              className="h-10 px-5 rounded-full bg-white/5 border border-white/10 text-sm font-medium hover:bg-red-500/10 hover:text-red-400 transition-all flex items-center gap-2"
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      <main className="pt-32 pb-24 px-6 max-w-7xl mx-auto">
        
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {[
            { label: "Today's Bookings", value: stats.today, icon: Calendar, color: "indigo" },
            { label: "Pending Approvals", value: stats.pending, icon: AlertCircle, color: "amber" },
            { label: "Completion Rate", value: `${stats.total > 0 ? Math.round((bookings.filter(b => b.status === "completed").length / stats.total) * 100) : 0}%`, icon: CheckCircle2, color: "emerald" },
            { label: "Estimated Revenue", value: `$${stats.revenue.toFixed(2)}`, icon: TrendingUp, color: "purple" },
          ].map((stat, i) => (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              key={i} 
              className="p-6 rounded-3xl bg-neutral-900 border border-white/5 relative overflow-hidden group"
            >
              <div className={`absolute top-0 right-0 w-32 h-32 -mr-8 -mt-8 opacity-5 group-hover:scale-110 transition-transform duration-500 rounded-full bg-${stat.color}-500 blur-3xl`} />
              <div className="flex flex-col gap-4">
                <div className={`w-12 h-12 rounded-2xl bg-${stat.color}-500/10 flex items-center justify-center text-${stat.color}-400`}>
                  <stat.icon className="w-6 h-6" />
                </div>
                <div>
                  <div className="text-3xl font-bold">{stat.value}</div>
                  <div className="text-sm text-neutral-500 font-medium">{stat.label}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Schedule Section */}
        <div className="bg-neutral-900/50 border border-white/5 rounded-[2.5rem] overflow-hidden backdrop-blur-xl">
          <div className="px-8 py-6 border-b border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <h2 className="text-2xl font-bold flex items-center gap-3">
              Appointment Schedule
              <span className="text-xs bg-indigo-500/10 text-indigo-400 px-3 py-1 rounded-full uppercase tracking-widest font-bold">
                {filteredBookings.length} Bookings
              </span>
            </h2>
            
            <div className="flex items-center gap-2 p-1 bg-black/40 rounded-full border border-white/5">
              {[
                { id: "all", label: "All" },
                { id: "pending", label: "Pending" },
                { id: "confirmed", label: "Confirmed" }
              ].map((t) => (
                <button
                  key={t.id}
                  onClick={() => setFilter(t.id as any)}
                  className={`px-5 py-2 rounded-full text-xs font-bold transition-all ${
                    filter === t.id ? "bg-white text-black shadow-lg" : "text-neutral-500 hover:text-white"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-white/5">
                  <th className="px-8 py-4 text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Customer</th>
                  <th className="px-8 py-4 text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Service</th>
                  <th className="px-8 py-4 text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Scheduled Time</th>
                  <th className="px-8 py-4 text-[10px] font-bold text-neutral-500 uppercase tracking-widest">Status</th>
                  <th className="px-8 py-4 text-[10px] font-bold text-neutral-500 uppercase tracking-widest text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                <AnimatePresence mode="popLayout">
                  {filteredBookings.length > 0 ? (
                    filteredBookings.map((booking, idx) => {
                      const service = store?.services?.find((s: any) => s.id === booking.service_id);
                      const isBookingToday = isToday(parseISO(booking.start_time));
                      
                      return (
                        <motion.tr 
                          layout
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, scale: 0.95 }}
                          transition={{ delay: idx * 0.05 }}
                          key={booking.id} 
                          className="hover:bg-white/[0.02] transition-colors group"
                        >
                          <td className="px-8 py-6">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center font-bold text-neutral-400">
                                {booking.customer_name.charAt(0)}
                              </div>
                              <div>
                                <div className="font-bold text-white leading-none mb-1">{booking.customer_name}</div>
                                <div className="text-xs text-neutral-500">ID: ...{booking.id.slice(-6)}</div>
                              </div>
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <div className="flex items-center gap-2">
                              <Scissors className="w-3.5 h-3.5 text-indigo-400" />
                              <span className="text-sm font-medium">{service?.name || "Service"}</span>
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <div className="flex flex-col">
                              <span className={`text-sm font-bold ${isBookingToday ? 'text-indigo-400' : 'text-neutral-200'}`}>
                                {format(parseISO(booking.start_time), 'h:mm a')}
                              </span>
                              <span className="text-xs text-neutral-500">{format(parseISO(booking.start_time), 'MMM d, yyyy')}</span>
                            </div>
                          </td>
                          <td className="px-8 py-6">
                            <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                              booking.status === "confirmed" ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" :
                              booking.status === "pending" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" :
                              booking.status === "cancelled" ? "bg-red-500/10 text-red-400 border border-red-500/20" :
                              "bg-neutral-800 text-neutral-400"
                            }`}>
                              {booking.status}
                            </span>
                          </td>
                          <td className="px-8 py-6 text-right">
                            <div className="flex items-center justify-end gap-2">
                              {booking.status === "pending" && (
                                <>
                                  <button 
                                    onClick={() => handleStatusUpdate(booking.id, "confirmed")}
                                    className="h-8 px-4 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-bold hover:bg-emerald-500 text-white transition-all"
                                  >
                                    Confirm
                                  </button>
                                  <button 
                                    onClick={() => handleStatusUpdate(booking.id, "cancelled")}
                                    className="h-8 px-4 rounded-lg bg-red-500/10 text-red-400 text-xs font-bold hover:bg-red-500 text-white transition-all"
                                  >
                                    Decline
                                  </button>
                                </>
                              )}
                              {booking.status === "confirmed" && (
                                <>
                                  <button 
                                    onClick={() => handleStatusUpdate(booking.id, "completed")}
                                    className="h-8 px-4 rounded-lg bg-white text-black text-xs font-bold hover:bg-neutral-200 transition-all flex items-center gap-2"
                                  >
                                    Mark Done
                                    <CheckCircle2 className="w-3 h-3" />
                                  </button>
                                  <button 
                                    onClick={() => handleStatusUpdate(booking.id, "no-show")}
                                    className="h-8 px-4 rounded-lg bg-neutral-800 text-neutral-400 text-xs font-bold hover:bg-red-500/10 hover:text-red-400 transition-all flex items-center gap-2"
                                  >
                                    No-Show
                                    <UserMinus className="w-3 h-3" />
                                  </button>
                                </>
                              )}
                              {["completed", "cancelled", "no-show"].includes(booking.status) && (
                                <button className="h-8 px-4 rounded-lg bg-white/5 text-neutral-600 text-xs font-bold cursor-not-allowed">
                                  Finalized
                                </button>
                              )}
                            </div>
                          </td>
                        </motion.tr>
                      );
                    })
                  ) : (
                    <tr>
                      <td colSpan={5} className="px-8 py-20 text-center text-neutral-500 italic">
                        <Calendar className="w-12 h-12 mx-auto mb-4 opacity-20" />
                        No bookings found matching the current filter.
                      </td>
                    </tr>
                  )}
                </AnimatePresence>
              </tbody>
            </table>
          </div>
        </div>

      </main>
    </div>
  );
}
