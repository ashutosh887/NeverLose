"use client";
import { useEffect, useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { TrendingUp, IndianRupee, Clock, CreditCard, Zap } from "lucide-react";
import type { DashboardSeed } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ConversionStatsProps {
  weekly: DashboardSeed["total_weekly"] | null;
}

function AnimatedNumber({ value, prefix = "" }: { value: number; prefix?: string }) {
  const motionValue = useMotionValue(0);
  const spring = useSpring(motionValue, { duration: 1200, bounce: 0.1 });
  const display = useTransform(spring, (v) => `${prefix}${Math.floor(v).toLocaleString("en-IN")}`);
  const prevRef = useRef(0);

  useEffect(() => {
    if (value !== prevRef.current) {
      motionValue.set(value);
      prevRef.current = value;
    }
  }, [value, motionValue]);

  return <motion.span>{display}</motion.span>;
}

const STAT_CONFIG = [
  {
    key: "saves",
    label: "Saves This Week",
    icon: TrendingUp,
    iconBg: "bg-pine-500/20",
    iconColor: "text-pine-400",
    gradient: "from-pine-500/10 to-emerald-500/5",
    valueSuffix: "",
    borderColor: "border-pine-500/20",
  },
  {
    key: "gmv",
    label: "GMV Recovered",
    icon: IndianRupee,
    iconBg: "bg-blue-500/20",
    iconColor: "text-blue-400",
    gradient: "from-blue-500/10 to-cyan-500/5",
    valueSuffix: "",
    borderColor: "border-blue-500/20",
  },
  {
    key: "tenure",
    label: "Avg EMI Tenure",
    icon: Clock,
    iconBg: "bg-purple-500/20",
    iconColor: "text-purple-400",
    gradient: "from-purple-500/10 to-violet-500/5",
    valueSuffix: " months",
    borderColor: "border-purple-500/20",
  },
  {
    key: "bank",
    label: "Top Bank",
    icon: CreditCard,
    iconBg: "bg-amber-500/20",
    iconColor: "text-amber-400",
    gradient: "from-amber-500/10 to-yellow-500/5",
    valueSuffix: "",
    borderColor: "border-amber-500/20",
  },
];

export function ConversionStats({ weekly }: ConversionStatsProps) {
  if (!weekly) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {STAT_CONFIG.map((s) => (
          <div
            key={s.key}
            className="h-28 rounded-2xl bg-slate-800/50 border border-slate-700/50 animate-pulse"
          />
        ))}
      </div>
    );
  }

  const topBank =
    Object.entries(weekly.channel_breakdown).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "HDFC";

  const stats = [
    { key: "saves", numericValue: weekly.saves, displayValue: String(weekly.saves), suffix: "" },
    {
      key: "gmv",
      numericValue: Math.floor(weekly.gmv_recovered_paisa / 100),
      displayValue: weekly.gmv_recovered_display,
      suffix: "",
    },
    {
      key: "tenure",
      numericValue: weekly.avg_emi_tenure_months,
      displayValue: String(weekly.avg_emi_tenure_months),
      suffix: " months",
    },
    { key: "bank", numericValue: 0, displayValue: topBank.toUpperCase(), suffix: "" },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {STAT_CONFIG.map((config, i) => {
        const stat = stats.find((s) => s.key === config.key)!;
        const Icon = config.icon;

        return (
          <motion.div
            key={config.key}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08, type: "spring", stiffness: 200, damping: 20 }}
            className={cn(
              "relative overflow-hidden rounded-2xl p-5",
              "bg-gradient-to-br border",
              config.gradient,
              config.borderColor,
              "backdrop-blur-sm"
            )}
            style={{ background: "rgba(15, 23, 42, 0.7)" }}
          >
            {/* Glow accent */}
            <div
              className={cn(
                "absolute top-0 right-0 w-24 h-24 rounded-full blur-2xl opacity-20",
                config.iconBg.replace("/20", "")
              )}
              style={{ transform: "translate(30%, -30%)" }}
            />

            <div className="relative">
              <div className={cn("inline-flex p-2.5 rounded-xl mb-3", config.iconBg)}>
                <Icon className={cn("w-4 h-4", config.iconColor)} />
              </div>
              <p className="text-xs font-medium text-slate-400 mb-1 uppercase tracking-wide">
                {config.label}
              </p>
              <p className="text-2xl font-bold text-slate-100 leading-none">
                {config.key === "saves" ? (
                  <AnimatedNumber value={stat.numericValue} />
                ) : config.key === "tenure" ? (
                  <>
                    <AnimatedNumber value={stat.numericValue} />
                    <span className="text-base font-medium text-slate-400">{stat.suffix}</span>
                  </>
                ) : (
                  stat.displayValue
                )}
              </p>
              {config.key === "saves" && (
                <div className="mt-2 flex items-center gap-1">
                  <Zap className="w-3 h-3 text-pine-400" />
                  <span className="text-[10px] text-pine-400 font-medium">+3 from yesterday</span>
                </div>
              )}
              {config.key === "gmv" && (
                <div className="mt-2 flex items-center gap-1">
                  <TrendingUp className="w-3 h-3 text-blue-400" />
                  <span className="text-[10px] text-blue-400 font-medium">↑ 22% vs last week</span>
                </div>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
