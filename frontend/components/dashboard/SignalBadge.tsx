"use client";
import { cn } from "@/lib/utils";
import type { SignalType } from "@/lib/types";

const SIGNAL_CONFIG: Record<
  SignalType,
  { label: string; dotColor: string; classes: string }
> = {
  EXIT_INTENT_DETECTED: {
    label: "Exit Intent",
    dotColor: "bg-red-400",
    classes: "bg-red-950/60 text-red-300 border-red-800/50",
  },
  CART_STALL_DETECTED: {
    label: "Cart Stall",
    dotColor: "bg-amber-400",
    classes: "bg-amber-950/60 text-amber-300 border-amber-800/50",
  },
  CHECKOUT_DROP_DETECTED: {
    label: "Checkout Drop",
    dotColor: "bg-red-500",
    classes: "bg-red-950/60 text-red-300 border-red-800/50",
  },
  RETURN_VISIT_DETECTED: {
    label: "Return Visit",
    dotColor: "bg-blue-400",
    classes: "bg-blue-950/60 text-blue-300 border-blue-800/50",
  },
  IDLE_DETECTED: {
    label: "Idle",
    dotColor: "bg-slate-400",
    classes: "bg-slate-800/60 text-slate-400 border-slate-700/50",
  },
  SCROLL_BOUNCE_DETECTED: {
    label: "Scroll Bounce",
    dotColor: "bg-purple-400",
    classes: "bg-purple-950/60 text-purple-300 border-purple-800/50",
  },
  PRICE_COPY_DETECTED: {
    label: "Price Copy",
    dotColor: "bg-teal-400",
    classes: "bg-teal-950/60 text-teal-300 border-teal-800/50",
  },
  WISHLIST_INSTEAD_OF_CART: {
    label: "Wishlist",
    dotColor: "bg-pink-400",
    classes: "bg-pink-950/60 text-pink-300 border-pink-800/50",
  },
  EMI_DWELL_DETECTED: {
    label: "EMI Dwell",
    dotColor: "bg-indigo-400",
    classes: "bg-indigo-950/60 text-indigo-300 border-indigo-800/50",
  },
  PRICE_SHOCK_PREDICTED: {
    label: "Price Shock",
    dotColor: "bg-orange-400",
    classes: "bg-orange-950/60 text-orange-300 border-orange-800/50",
  },
};

interface SignalBadgeProps {
  signal: string;
  variant?: "dark" | "light";
}

export function SignalBadge({ signal, variant = "dark" }: SignalBadgeProps) {
  const config = SIGNAL_CONFIG[signal as SignalType];

  if (!config) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-semibold rounded-full border bg-slate-800/60 text-slate-400 border-slate-700/50">
        {signal}
      </span>
    );
  }

  if (variant === "light") {
    // Light mode variant for product page
    const lightClasses: Record<SignalType, string> = {
      EXIT_INTENT_DETECTED: "bg-red-50 text-red-700 border-red-200",
      CART_STALL_DETECTED: "bg-amber-50 text-amber-700 border-amber-200",
      CHECKOUT_DROP_DETECTED: "bg-red-50 text-red-700 border-red-200",
      RETURN_VISIT_DETECTED: "bg-blue-50 text-blue-700 border-blue-200",
      IDLE_DETECTED: "bg-slate-50 text-slate-600 border-slate-200",
      SCROLL_BOUNCE_DETECTED: "bg-purple-50 text-purple-700 border-purple-200",
      PRICE_COPY_DETECTED: "bg-teal-50 text-teal-700 border-teal-200",
      WISHLIST_INSTEAD_OF_CART: "bg-pink-50 text-pink-700 border-pink-200",
      EMI_DWELL_DETECTED: "bg-indigo-50 text-indigo-700 border-indigo-200",
      PRICE_SHOCK_PREDICTED: "bg-orange-50 text-orange-700 border-orange-200",
    };
    return (
      <span
        className={cn(
          "inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-semibold rounded-full border",
          lightClasses[signal as SignalType]
        )}
      >
        {config.label}
      </span>
    );
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2 py-0.5 text-[10px] font-semibold rounded-full border",
        config.classes
      )}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full flex-shrink-0", config.dotColor)} />
      {config.label}
    </span>
  );
}
