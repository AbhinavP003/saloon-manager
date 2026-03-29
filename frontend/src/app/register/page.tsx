"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { register, login } from "@/lib/api";
import { 
  User, 
  Mail, 
  Lock, 
  ArrowRight, 
  Loader2, 
  Scissors,
  CheckCircle2,
  ChevronLeft,
  Building2,
  ShieldCheck
} from "lucide-react";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";

export default function RegisterPage() {
  const router = useRouter();
  
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"customer" | "owner">("customer");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    const toastId = toast.loading("Creating account...");
    
    try {
      await register({
        full_name: fullName,
        email,
        password,
        role: role === "owner" ? "owner" : "customer"
      });
      
      toast.success("Account created successfully!", { id: toastId });
      
      // Auto login after registration
      toast.loading("Logging you in...", { id: toastId });
      await login(email, password);
      
      router.push("/");
      router.refresh();
    } catch (err: any) {
      toast.error(err.message || "Registration failed", { id: toastId });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-50 flex flex-col items-center justify-center p-6 selection:bg-indigo-500/30">
      
      <div className="fixed top-12 left-12 hidden lg:block">
        <a 
          href="/login" 
          className="flex items-center gap-2 text-neutral-500 hover:text-white transition-colors group"
        >
          <div className="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:scale-110 transition-transform">
            <ChevronLeft className="w-5 h-5" />
          </div>
          <span className="text-xs font-bold uppercase tracking-widest">Back to Login</span>
        </a>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-xl mx-auto"
      >
        {/* Decorative Background Elements */}
        <div className="absolute -top-32 -right-32 w-80 h-80 bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute -bottom-32 -left-32 w-80 h-80 bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none" />

        <div className="bg-neutral-900/50 border border-white/5 backdrop-blur-2xl p-10 rounded-[2.5rem] shadow-2xl relative z-10">
          <div className="flex flex-col items-center mb-10 text-center">
            <div className="w-16 h-16 bg-white flex items-center justify-center rounded-2xl shadow-xl mb-6">
              <Scissors className="w-8 h-8 text-black" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight mb-2">Create Account</h1>
            <p className="text-neutral-500 text-sm max-w-[280px]">
              Join the future of local saloon marketplace management.
            </p>
          </div>

          {/* Role Selector */}
          <div className="flex items-center gap-4 mb-10 p-1.5 bg-black/40 rounded-3xl border border-white/5 overflow-hidden">
            {[
              { id: "customer", label: "I'm a Customer", icon: User },
              { id: "owner", label: "I'm a Store Owner", icon: Building2 }
            ].map((r) => (
              <button
                key={r.id}
                onClick={() => setRole(r.id as any)}
                className={`flex-1 h-12 flex items-center justify-center gap-3 rounded-[1.25rem] text-xs font-bold transition-all ${
                  role === r.id 
                    ? "bg-white text-black shadow-[0_10px_30px_-5px_rgba(255,255,255,0.3)]" 
                    : "text-neutral-500 hover:text-white"
                }`}
              >
                <r.icon className={`w-4 h-4 ${role === r.id ? "text-indigo-500" : ""}`} />
                {r.label}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 ml-4">Full Name</label>
                <div className="relative group">
                  <User className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500 group-focus-within:text-indigo-400 transition-colors" />
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full h-14 pl-14 pr-6 rounded-2xl bg-black/40 border border-white/5 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 outline-none transition-all text-sm font-medium"
                    placeholder="Abhinav P"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 ml-4">Email Address</label>
                <div className="relative group">
                  <Mail className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500 group-focus-within:text-indigo-400 transition-colors" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full h-14 pl-14 pr-6 rounded-2xl bg-black/40 border border-white/5 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 outline-none transition-all text-sm font-medium"
                    placeholder="name@example.com"
                    required
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-500 ml-4">Create Password</label>
              <div className="relative group">
                <Lock className="absolute left-5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-500 group-focus-within:text-indigo-400 transition-colors" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full h-14 pl-14 pr-6 rounded-2xl bg-black/40 border border-white/5 focus:border-indigo-500/50 focus:ring-4 focus:ring-indigo-500/5 outline-none transition-all text-sm font-medium"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            <div className="p-4 bg-indigo-500/5 border border-indigo-500/10 rounded-2xl flex gap-3 items-start">
              <CheckCircle2 className="w-4 h-4 text-indigo-400 mt-0.5" />
              <p className="text-[11px] text-neutral-400 leading-relaxed">
                By creating an account, you agree to our <span className="text-white hover:underline cursor-pointer">Terms of Service</span> and <span className="text-white hover:underline cursor-pointer">Privacy Policy</span>.
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full h-16 rounded-[1.5rem] bg-indigo-500 hover:bg-indigo-400 text-white font-bold transition-all shadow-lg shadow-indigo-500/25 flex items-center justify-center gap-3 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Launch Experience
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
          </form>

          <div className="mt-10 pt-10 border-t border-white/5 text-center">
            <p className="text-neutral-500 text-sm">
              Already have an account?{" "}
              <a 
                href="/login" 
                className="text-white font-bold hover:text-indigo-400 transition-colors"
              >
                Sign In Instead
              </a>
            </p>
          </div>
        </div>
      </motion.div>

      <div className="mt-12 flex items-center gap-8 opacity-40 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-700">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4" />
          <span className="text-[10px] font-bold uppercase tracking-widest">TLS 1.3 Certified</span>
        </div>
      </div>
    </div>
  );
}
