"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, MapPin } from "lucide-react";
import { SignalBadge } from "./SignalBadge";
import { CHANNEL_LABELS } from "@/lib/signals";
import type { ConversionEvent } from "@/lib/types";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";

interface LiveFeedProps {
  conversions: ConversionEvent[];
}

const PRODUCT_EMOJI: Record<string, string> = {
  "DELL-XPS-15": "💻",
  "SAMSUNG-S24": "📱",
  "LG-WASHER": "🫧",
};

const CHANNEL_BADGE: Record<string, { classes: string; label: string }> = {
  web: { classes: "bg-blue-900/60 text-blue-300 border-blue-800/50", label: "Web" },
  whatsapp: { classes: "bg-green-900/60 text-green-300 border-green-800/50", label: "WhatsApp" },
  qr: { classes: "bg-purple-900/60 text-purple-300 border-purple-800/50", label: "UPI QR" },
  voice: { classes: "bg-orange-900/60 text-orange-300 border-orange-800/50", label: "Voice" },
};

function TimeAgo({ timestamp }: { timestamp: string }) {
  const [now] = useState(() => Date.now());
  const d = new Date(timestamp);
  const diff = Math.floor((now - d.getTime()) / 1000);
  if (diff < 60) return <span>{diff}s ago</span>;
  if (diff < 3600) return <span>{Math.floor(diff / 60)}m ago</span>;
  return (
    <span>
      {d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
    </span>
  );
}

export function LiveFeed({ conversions }: LiveFeedProps) {
  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="relative">
            <span className="absolute inset-0 rounded-full bg-pine-500 animate-ping opacity-30" />
            <span className="relative w-2 h-2 rounded-full bg-pine-400 block" />
          </div>
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-1.5">
            <Activity className="w-4 h-4 text-pine-400" />
            Live Conversions
          </h3>
        </div>
        <span className="text-xs text-slate-500 font-medium">
          {conversions.length} total
        </span>
      </div>

      {/* Feed */}
      <ScrollArea className="flex-1 max-h-[500px] scrollbar-hide">
        <AnimatePresence initial={false}>
          {conversions.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center h-48 text-center"
            >
              <div className="w-12 h-12 rounded-full bg-slate-800 flex items-center justify-center mb-3">
                <Activity className="w-5 h-5 text-slate-600" />
              </div>
              <p className="text-sm text-slate-500">Waiting for conversions...</p>
              <p className="text-xs text-slate-600 mt-1">Events will appear here in real-time</p>
            </motion.div>
          ) : (
            <div className="space-y-2 pr-2">
              {conversions.map((c, idx) => {
                const channelBadge = CHANNEL_BADGE[c.channel] ?? CHANNEL_BADGE.web;
                const emoji = PRODUCT_EMOJI[c.product_id] ?? "🛍️";

                return (
                  <motion.div
                    key={c.id}
                    initial={{ opacity: 0, y: -12, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{
                      type: "spring",
                      stiffness: 300,
                      damping: 25,
                      delay: idx === 0 ? 0 : 0,
                    }}
                    layout
                    className={cn(
                      "group flex items-start gap-3 p-3.5 rounded-xl border transition-colors",
                      "bg-slate-900/80 border-slate-800/80 hover:border-slate-700/80",
                      idx === 0 && "border-pine-800/60 bg-pine-950/30"
                    )}
                  >
                    {/* Emoji */}
                    <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-xl flex-shrink-0 border border-slate-700/50">
                      {emoji}
                    </div>

                    {/* Main content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-semibold text-slate-200 truncate leading-tight">
                          {c.product}
                        </p>
                        <p className="text-[10px] text-slate-500 flex-shrink-0">
                          <TimeAgo timestamp={c.timestamp} />
                        </p>
                      </div>

                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        <span className="text-xs font-bold text-pine-400">
                          {c.amount_display}
                        </span>
                        <span className="text-slate-700">·</span>
                        <span className="text-xs text-slate-400">
                          {c.emi_scheme.monthly_display}/mo
                        </span>
                        {c.emi_scheme.is_no_cost && (
                          <>
                            <span className="text-slate-700">·</span>
                            <span className="text-[10px] font-semibold text-pine-400">
                              No-Cost
                            </span>
                          </>
                        )}
                      </div>

                      <div className="flex items-center gap-1.5 mt-2 flex-wrap">
                        <span
                          className={cn(
                            "inline-flex items-center gap-1 px-1.5 py-0.5 text-[10px] font-semibold rounded-md border",
                            channelBadge.classes
                          )}
                        >
                          {CHANNEL_LABELS[c.channel] ?? c.channel}
                        </span>
                        <SignalBadge signal={c.signal} variant="dark" />
                        <span className="flex items-center gap-0.5 text-[10px] text-slate-500">
                          <MapPin className="w-2.5 h-2.5" />
                          {c.customer_city}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </AnimatePresence>
      </ScrollArea>
    </div>
  );
}
