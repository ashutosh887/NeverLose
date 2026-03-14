"use client";
import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { formatInr, dailyCost } from "@/lib/signals";
import { Slider } from "@/components/ui/slider";
import { cn } from "@/lib/utils";

const TENURES = [3, 6, 9, 12, 18, 24];

interface TenureSliderProps {
  principalPaisa: number;
  onSelectTenure: (tenure: number) => void;
}

export function TenureSlider({ principalPaisa, onSelectTenure }: TenureSliderProps) {
  const [tenureIdx, setTenureIdx] = useState(4); // default: 18m
  const tenure = TENURES[tenureIdx];
  const monthlyPaisa = Math.ceil(principalPaisa / tenure);
  const monthly = formatInr(monthlyPaisa);
  const daily = dailyCost(monthlyPaisa);

  const handleChange = useCallback(
    (values: number[]) => {
      const idx = values[0];
      setTenureIdx(idx);
      onSelectTenure(TENURES[idx]);
    },
    [onSelectTenure]
  );

  return (
    <div className="p-4 bg-gradient-to-br from-pine-50 via-white to-emerald-50 rounded-xl border border-pine-100 shadow-sm">
      <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-3">
        Adjust tenure · Drag to explore
      </p>

      {/* Live amount display */}
      <AnimatePresence mode="wait">
        <motion.div
          key={tenure}
          initial={{ opacity: 0, y: 6, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -6, scale: 0.96 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
          className="text-center mb-4"
        >
          <div className="inline-flex flex-col items-center gap-0.5">
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-bold text-gray-900 tabular-nums">
                {monthly}
              </span>
              <span className="text-sm font-normal text-gray-400">/month</span>
            </div>
            <span className="text-xs font-semibold text-pine-600">
              {daily}/day · {tenure} months · No-Cost EMI
            </span>
          </div>
        </motion.div>
      </AnimatePresence>

      {/* Slider */}
      <Slider
        min={0}
        max={TENURES.length - 1}
        step={1}
        value={[tenureIdx]}
        onValueChange={handleChange}
        className="mb-3"
      />

      {/* Tenure labels */}
      <div className="flex justify-between">
        {TENURES.map((t, i) => (
          <button
            key={t}
            onClick={() => handleChange([i])}
            className={cn(
              "text-[10px] font-medium transition-colors w-7 text-center py-0.5 rounded",
              i === tenureIdx
                ? "text-pine-600 font-bold bg-pine-100 border border-pine-200"
                : "text-gray-400 hover:text-gray-600"
            )}
          >
            {t}m
          </button>
        ))}
      </div>

      {/* Hint */}
      <p className="text-[10px] text-center text-gray-400 mt-2.5">
        Less than a Swiggy order per day
      </p>
    </div>
  );
}
