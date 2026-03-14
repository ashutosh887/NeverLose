"use client";
import { motion } from "framer-motion";
import { Zap } from "lucide-react";
import { cn } from "@/lib/utils";

interface ProductImageCardProps {
  emoji: string;
}

export function ProductImageCard({ emoji }: ProductImageCardProps) {
  return (
    <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="flex flex-col items-center justify-center p-10 min-h-[360px] bg-gradient-to-br from-gray-50 to-white">
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
          className="text-[120px] leading-none mb-6 select-none"
        >
          {emoji}
        </motion.div>
        <div className="flex gap-2">
          {[emoji, "📦", "🔌"].map((img, i) => (
            <button
              key={i}
              className={cn(
                "w-12 h-12 bg-white border rounded-xl text-xl flex items-center justify-center transition-all",
                i === 0
                  ? "border-pine-400 shadow-sm shadow-pine-100"
                  : "border-gray-200 hover:border-gray-300"
              )}
            >
              {img}
            </button>
          ))}
        </div>
      </div>
      <div className="px-5 py-3 border-t border-gray-100 flex items-center justify-between bg-gradient-to-r from-pine-50 to-white">
        <span className="text-xs text-gray-500 font-medium">Sold by TechMart</span>
        <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-pine-600 bg-pine-100 px-2 py-0.5 rounded-full border border-pine-200">
          <Zap className="w-2.5 h-2.5" />
          Pine Labs Verified
        </span>
      </div>
    </div>
  );
}
