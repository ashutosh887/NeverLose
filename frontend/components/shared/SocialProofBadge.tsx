"use client";
import { motion } from "framer-motion";
import { Users } from "lucide-react";

export function SocialProofBadge({ count = 47 }: { count?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2 }}
      className="inline-flex items-center gap-2 px-3 py-1.5 bg-pine-50 border border-pine-200 rounded-full"
    >
      <div className="relative flex items-center justify-center">
        <span className="absolute w-3 h-3 bg-pine-500 rounded-full opacity-30 animate-ping" />
        <span className="relative w-2 h-2 bg-pine-500 rounded-full" />
      </div>
      <Users className="w-3 h-3 text-pine-600" />
      <span className="text-xs font-semibold text-pine-700">
        {count} customers bought this on EMI today
      </span>
    </motion.div>
  );
}
