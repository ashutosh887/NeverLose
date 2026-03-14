"use client";
import { motion } from "framer-motion";
import { CheckCircle, CreditCard, Sparkles, ArrowRight, Users } from "lucide-react";
import type { StackedDeal } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";

interface StackedDealCardProps {
  deal: StackedDeal;
  onClaim: () => void;
}

const containerVariants = {
  hidden: { opacity: 0, scale: 0.96 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -8 },
  visible: { opacity: 1, x: 0 },
};

export function StackedDealCard({ deal, onClaim }: StackedDealCardProps) {
  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="relative overflow-hidden rounded-2xl bg-white border-2 border-pine-400 shadow-lg shadow-pine-100"
    >
      {/* Gradient stripe top */}
      <div className="h-1 w-full bg-gradient-to-r from-pine-400 via-emerald-400 to-pine-600" />

      <div className="p-4">
        {/* Header */}
        <motion.div variants={itemVariants} className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-pine-500" />
            <span className="text-sm font-bold text-gray-900">Your Stacked Deal</span>
          </div>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 bg-pine-500 text-white text-xs font-bold rounded-full shadow-sm">
            Save {deal.total_savings_display}
          </span>
        </motion.div>

        {/* Price waterfall */}
        <div className="space-y-2 mb-4">
          {/* Original */}
          <motion.div variants={itemVariants} className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Original price</span>
            <span className="text-gray-400 line-through">{deal.original_amount_display}</span>
          </motion.div>

          {/* Applied offers */}
          {deal.applied_offers.map((offer, i) => (
            <motion.div
              key={offer.offer_id}
              variants={itemVariants}
              className={cn(
                "flex items-center justify-between text-sm rounded-lg px-2.5 py-1.5",
                i === 0 ? "bg-green-50 border border-green-100" : "bg-blue-50 border border-blue-100"
              )}
            >
              <div className="flex items-center gap-1.5 min-w-0 flex-1">
                <CheckCircle
                  className={cn("w-3.5 h-3.5 flex-shrink-0", i === 0 ? "text-green-500" : "text-blue-500")}
                />
                <span className="text-gray-700 text-xs font-medium truncate">{offer.offer_name}</span>
                {offer.type === "cashback" && (
                  <span className="text-[10px] text-blue-500 font-medium flex-shrink-0">
                    · credited in 30d
                  </span>
                )}
              </div>
              <span className={cn("font-bold text-xs flex-shrink-0 ml-2", i === 0 ? "text-green-600" : "text-blue-600")}>
                −{offer.saving_display}
              </span>
            </motion.div>
          ))}

          {/* Net price */}
          <motion.div variants={itemVariants}>
            <Separator className="my-2" />
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-700">Net price</span>
              <span className="text-lg font-bold text-gray-900">{deal.net_price_display}</span>
            </div>
          </motion.div>
        </div>

        {/* EMI highlight */}
        <motion.div
          variants={itemVariants}
          className="p-3.5 bg-gradient-to-br from-pine-500 to-pine-600 rounded-xl text-white mb-3"
        >
          <div className="flex items-baseline gap-1 mb-0.5">
            <span className="text-2xl font-bold tracking-tight">
              {deal.emi_on_net_price.monthly_installment_display}
            </span>
            <span className="text-sm opacity-80">/month</span>
            {deal.emi_on_net_price.is_no_cost && (
              <span className="ml-1.5 px-1.5 py-0.5 bg-white/20 text-white text-[10px] font-bold rounded-md border border-white/20">
                No-Cost
              </span>
            )}
          </div>
          <p className="text-xs opacity-90">
            {deal.emi_on_net_price.daily_cost_display}/day · {deal.emi_on_net_price.tenure_months}m ·{" "}
            {deal.emi_on_net_price.bank_name}
          </p>
          <p className="text-[11px] opacity-70 mt-0.5">
            Less than a Swiggy order per day
          </p>
        </motion.div>

        {/* Cashback note */}
        {deal.cashback_paisa > 0 && (
          <motion.div
            variants={itemVariants}
            className="flex items-center gap-2 mb-3 p-2 bg-blue-50 rounded-lg border border-blue-100"
          >
            <CreditCard className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
            <span className="text-xs text-blue-700 font-medium">
              +{deal.cashback_display} cashback credited after 30 days
            </span>
          </motion.div>
        )}

        {/* CTA */}
        <motion.button
          variants={itemVariants}
          onClick={onClaim}
          whileTap={{ scale: 0.97 }}
          className="w-full flex items-center justify-center gap-2 py-3 bg-pine-500 hover:bg-pine-600 text-white font-bold rounded-xl text-sm transition-colors shadow-md shadow-pine-200"
        >
          Claim This Deal
          <ArrowRight className="w-4 h-4" />
        </motion.button>

        {/* Social proof */}
        <motion.p variants={itemVariants} className="text-[10px] text-center text-gray-400 mt-2.5 flex items-center justify-center gap-1">
          <Users className="w-2.5 h-2.5" />
          47 customers claimed this deal today
        </motion.p>
      </div>
    </motion.div>
  );
}
