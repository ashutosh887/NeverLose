"use client";
import { motion } from "framer-motion";
import { Zap, CheckCircle, ChevronRight } from "lucide-react";
import type { EMIScheme } from "@/lib/types";
import { cn } from "@/lib/utils";

const BANK_CONFIG: Record<
  string,
  { dot: string; accent: string; bg: string; border: string }
> = {
  HDFC: {
    dot: "bg-blue-500",
    accent: "text-blue-600",
    bg: "bg-blue-50",
    border: "border-blue-100",
  },
  ICICI: {
    dot: "bg-orange-500",
    accent: "text-orange-600",
    bg: "bg-orange-50",
    border: "border-orange-100",
  },
  SBI: {
    dot: "bg-indigo-600",
    accent: "text-indigo-600",
    bg: "bg-indigo-50",
    border: "border-indigo-100",
  },
  AXIO: {
    dot: "bg-rose-500",
    accent: "text-rose-600",
    bg: "bg-rose-50",
    border: "border-rose-100",
  },
  HOMECREDIT: {
    dot: "bg-red-500",
    accent: "text-red-600",
    bg: "bg-red-50",
    border: "border-red-100",
  },
};

const DEFAULT_BANK = {
  dot: "bg-gray-500",
  accent: "text-gray-600",
  bg: "bg-gray-50",
  border: "border-gray-100",
};

interface EMICardProps {
  scheme: EMIScheme;
  onSelect: (scheme: EMIScheme) => void;
  isSelected?: boolean;
  index?: number;
}

export function EMICard({ scheme, onSelect, isSelected, index = 0 }: EMICardProps) {
  const bankCfg = BANK_CONFIG[scheme.bank_code] ?? DEFAULT_BANK;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      whileTap={{ scale: 0.985 }}
      onClick={() => onSelect(scheme)}
      className={cn(
        "relative p-3.5 rounded-xl border-2 cursor-pointer transition-all select-none",
        isSelected
          ? "border-pine-500 bg-pine-50 shadow-md shadow-pine-100"
          : "border-gray-100 bg-white hover:border-gray-200 hover:shadow-sm"
      )}
    >
      {/* Badge */}
      {scheme.badge && (
        <span className="absolute -top-2 right-3 px-2 py-0.5 bg-pine-500 text-white text-[10px] font-bold rounded-full uppercase tracking-wide shadow-sm">
          {scheme.badge}
        </span>
      )}

      <div className="flex items-start justify-between gap-2">
        {/* Left: Bank + amount */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 mb-1.5">
            <span className={cn("w-2.5 h-2.5 rounded-full flex-shrink-0", bankCfg.dot)} />
            <span className="text-xs font-semibold text-gray-600">
              {scheme.bank_name}
            </span>
            <span className="text-gray-300">·</span>
            <span className="text-xs text-gray-400">{scheme.card_type}</span>
            {scheme.is_no_cost && (
              <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-pine-50 text-pine-600 text-[10px] font-semibold rounded-md border border-pine-200">
                <Zap className="w-2.5 h-2.5" />
                No-Cost
              </span>
            )}
          </div>

          <div className="flex items-baseline gap-1">
            <span className="text-xl font-bold text-gray-900">
              {scheme.monthly_installment_display}
            </span>
            <span className="text-xs text-gray-400 font-normal">/month</span>
          </div>

          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-gray-400">
              {scheme.daily_cost_display}/day
            </span>
            <span className="text-gray-300">·</span>
            <span className={cn("text-xs px-1.5 py-0.5 rounded font-medium", bankCfg.bg, bankCfg.border, bankCfg.accent, "border text-[11px]")}>
              {scheme.tenure_months}m
            </span>
          </div>

          {scheme.eligibility && (
            <p className="text-[10px] text-purple-600 font-medium mt-1.5 flex items-center gap-1">
              <span className="w-1 h-1 rounded-full bg-purple-500" />
              {scheme.eligibility}
            </p>
          )}

          {scheme.total_interest_paisa > 0 && (
            <p className="text-[10px] text-gray-400 mt-1">
              +interest by bank
            </p>
          )}
        </div>

        {/* Right: Select */}
        {isSelected ? (
          <CheckCircle className="w-5 h-5 text-pine-500 flex-shrink-0 mt-1" />
        ) : (
          <button className="flex-shrink-0 mt-1 flex items-center gap-0.5 px-2.5 py-1 rounded-lg border border-gray-200 text-[11px] font-semibold text-gray-600 hover:border-pine-300 hover:text-pine-600 transition-colors">
            Select
            <ChevronRight className="w-3 h-3" />
          </button>
        )}
      </div>
    </motion.div>
  );
}
