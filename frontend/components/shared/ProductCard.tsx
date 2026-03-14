"use client";
import { motion } from "framer-motion";
import { Plus, Sparkles } from "lucide-react";
import { formatInr } from "@/lib/signals";
import type { AccessoryUpsell } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ProductCardProps {
  accessory: AccessoryUpsell;
  onAdd: () => void;
}

export function ProductCard({ accessory, onAdd }: ProductCardProps) {
  const priceDisplay = formatInr(accessory.price_paisa);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "relative flex items-start gap-3 p-3.5 bg-white border border-gray-100 rounded-2xl shadow-sm",
        "hover:shadow-md hover:border-pine-200 transition-all cursor-pointer group"
      )}
    >
      {/* Smart Upsell indicator */}
      <div className="absolute -top-2 left-3">
        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-400 text-amber-900 text-[10px] font-bold rounded-full shadow-sm">
          <Sparkles className="w-2.5 h-2.5" />
          Smart Upsell
        </span>
      </div>

      {/* Image placeholder */}
      <div className="mt-1 w-14 h-14 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl flex items-center justify-center border border-gray-100 flex-shrink-0">
        <Package className="w-6 h-6 text-gray-400" />
      </div>

      {/* Details */}
      <div className="flex-1 min-w-0 pt-1">
        <p className="text-sm font-semibold text-gray-900 truncate leading-tight">
          {accessory.name}
        </p>
        <p className="text-xs text-gray-400 mt-0.5">{priceDisplay}</p>
        <div className="mt-1.5 inline-flex items-center gap-1 px-2 py-0.5 bg-pine-50 border border-pine-100 rounded-lg">
          <span className="text-[11px] font-semibold text-pine-600">
            +{accessory.incremental_monthly_display}/month more
          </span>
        </div>
        <p className="text-[10px] text-gray-400 mt-1">
          &lt;10% incremental EMI — barely noticeable
        </p>
      </div>

      {/* Add button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onAdd();
        }}
        className={cn(
          "mt-1 flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          "bg-pine-500 hover:bg-pine-600 text-white transition-colors shadow-sm",
          "group-hover:scale-105 transition-transform"
        )}
      >
        <Plus className="w-4 h-4" />
      </button>
    </motion.div>
  );
}
