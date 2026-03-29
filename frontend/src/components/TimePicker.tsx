"use client";

import { useEffect, useState } from "react";
import { format, addDays, startOfToday, parseISO } from "date-fns";
import { Calendar, Clock, ChevronRight, Loader2, CheckCircle2, User, AlertCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { fetchAvailableSlots, createBooking } from "@/lib/api";

interface TimePickerProps {
  serviceId: string;
  storeId: string;
  durationMinutes: number;
}

interface Slot {
  time: Date;
  available: boolean;
}

export default function TimePicker({ serviceId, storeId, durationMinutes }: TimePickerProps) {
  const router = useRouter();
  const today = startOfToday();
  const [selectedDate, setSelectedDate] = useState<Date>(today);
  const [selectedSlot, setSelectedSlot] = useState<Date | null>(null);
  const [customerName, setCustomerName] = useState("");
  const [slots, setSlots] = useState<Slot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate 14 days of options
  const dateOptions = Array.from({ length: 14 }).map((_, i) => addDays(today, i));

  useEffect(() => {
    setIsLoading(true);
    setSelectedSlot(null);
    setError(null);

    const dateStr = format(selectedDate, 'yyyy-MM-dd');
    
    fetchAvailableSlots(storeId, serviceId, dateStr)
      .then((data: any[]) => {
        const mappedSlots = data.map((item) => ({
          time: parseISO(item.start_time),
          available: true
        }));
        setSlots(mappedSlots);
        setIsLoading(false);
      })
      .catch((err) => {
        setError("Failed to load slots");
        setIsLoading(false);
      });
  }, [selectedDate, serviceId, storeId]);

  const handleBooking = async () => {
    if (!selectedSlot || !customerName.trim()) return;

    setIsSubmitting(true);
    setError(null);

    const toastId = toast.loading("Confirming your booking...");

    try {
      const result = await createBooking({
        store_id: storeId,
        service_id: serviceId,
        customer_name: customerName,
        start_time: selectedSlot.toISOString(),
      });
      
      toast.success("Booking confirmed!", {
        id: toastId,
        description: `We'll see you on ${format(selectedSlot, 'MMMM do')} at ${format(selectedSlot, 'h:mm a')}`,
      });

      // Navigate to confirmation page
      router.push(`/bookings/${result.id}/confirmation`);
    } catch (err: any) {
      toast.error(err.message || "Failed to create booking", {
        id: toastId,
      });
      setError(err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-neutral-900 border border-white/10 rounded-2xl p-6 w-full max-w-md flex flex-col gap-6 shadow-2xl">
      
      {/* Date Selector */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 text-white font-medium">
          <Calendar className="w-4 h-4 text-indigo-400" />
          <h3>Select Date</h3>
        </div>
        
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none snap-x">
          {dateOptions.map((date, i) => {
            const isSelected = date.getTime() === selectedDate.getTime();
            return (
              <button
                key={i}
                onClick={() => {
                  setSelectedDate(date);
                }}
                className={`flex flex-col items-center shrink-0 min-w-[4.5rem] p-3 rounded-xl border snap-start transition-all ${
                  isSelected 
                    ? "bg-indigo-500/20 border-indigo-500 text-indigo-300" 
                    : "bg-white/5 border-white/5 text-neutral-400 hover:bg-white/10 hover:text-white"
                }`}
              >
                <span className="text-xs font-semibold uppercase tracking-wider">{format(date, 'EEE')}</span>
                <span className={`text-xl font-bold mt-1 ${isSelected ? "text-indigo-200" : "text-white"}`}>
                  {format(date, 'd')}
                </span>
                <span className="text-xs pt-1">{format(date, 'MMM')}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="h-px bg-white/10 w-full" />

      {/* Time Slots Grid */}
      <div className="flex flex-col gap-3 min-h-[200px]">
        <div className="flex items-center justify-between text-white font-medium">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-indigo-400" />
            <h3>Available Slots</h3>
          </div>
          <span className="text-xs text-neutral-400 bg-white/5 px-2 py-1 rounded-md">
            {durationMinutes} min session
          </span>
        </div>
        
        {isLoading ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-neutral-500">
            <Loader2 className="w-8 h-8 animate-spin text-indigo-500/50" />
            <p className="text-sm">Checking availability...</p>
          </div>
        ) : error && !slots.length ? (
          <div className="flex-1 flex items-center justify-center p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 text-sm italic">
            {error}
          </div>
        ) : slots.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center py-8 text-center gap-2">
            <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center">
              <Clock className="w-6 h-6 text-neutral-600" />
            </div>
            <p className="text-sm text-neutral-500">No slots available on this date.</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-2 max-h-[240px] overflow-y-auto pr-2 custom-scrollbar">
            {slots.map((slot, i) => {
              const isSelected = selectedSlot?.getTime() === slot.time.getTime();
              return (
                <button
                  key={i}
                  onClick={() => setSelectedSlot(slot.time)}
                  className={`py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isSelected
                      ? "bg-indigo-500 text-white shadow-[0_0_15px_rgba(99,102,241,0.4)]"
                      : "bg-white/10 text-neutral-300 hover:bg-white/20 hover:text-white"
                  }`}
                >
                  {format(slot.time, 'h:mm a')}
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="h-px bg-white/10 w-full" />

      {/* Customer Info (Temporary until Auth) */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 text-white font-medium">
          <User className="w-4 h-4 text-indigo-400" />
          <h3>Your Details</h3>
        </div>
        <div className="relative">
          <input 
            type="text"
            placeholder="Enter your name"
            value={customerName}
            onChange={(e) => setCustomerName(e.target.value)}
            className="w-full h-12 bg-white/5 border border-white/10 rounded-xl px-4 text-white placeholder:text-neutral-600 focus:outline-none focus:border-indigo-500/50 transition-colors"
          />
        </div>
      </div>

      {error && slots.length > 0 && (
        <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <p>{error}</p>
        </div>
      )}

      {/* Action Footer */}
      <div className="pt-2">
        <button 
          disabled={!selectedSlot || !customerName.trim() || isSubmitting}
          onClick={handleBooking}
          className={`w-full h-12 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${
            selectedSlot && customerName.trim() && !isSubmitting
              ? "bg-white text-black hover:bg-neutral-200 shadow-xl" 
              : "bg-white/5 text-neutral-500 cursor-not-allowed"
          }`}
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <>
              Confirm Booking
              <ChevronRight className="w-4 h-4" />
            </>
          )}
        </button>
      </div>

    </div>
  );
}
