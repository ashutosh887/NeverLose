"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Clock } from "lucide-react";
import { cn } from "@/lib/utils";

const INITIAL_SECONDS = 600; // 10 minutes

export function CountdownTimer() {
  const [seconds, setSeconds] = useState(INITIAL_SECONDS);

  useEffect(() => {
    if (seconds <= 0) return;
    const timer = setInterval(() => setSeconds((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(timer);
  }, [seconds]);

  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  const timeStr = `${mins}:${secs.toString().padStart(2, "0")}`;

  const isRed = seconds <= 60;
  const isOrange = seconds <= 300 && seconds > 60;
  const isExpired = seconds === 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: 4 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ type: "spring", stiffness: 400, damping: 25 }}
      className={cn(
        "flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl border-2 text-sm font-bold w-fit",
        isExpired && "bg-gray-100 border-gray-200 text-gray-500",
        isRed && !isExpired && "bg-red-50 border-red-300 text-red-700",
        isOrange && "bg-orange-50 border-orange-300 text-orange-700",
        !isRed && !isOrange && !isExpired && "bg-amber-50 border-amber-300 text-amber-800"
      )}
    >
      <motion.div
        animate={isRed && !isExpired ? { scale: [1, 1.15, 1] } : {}}
        transition={{ repeat: Infinity, duration: 0.7 }}
      >
        <Clock className="w-4 h-4 flex-shrink-0" />
      </motion.div>
      <span>
        {isExpired
          ? "This offer has expired — want me to check current options?"
          : `Deal expires in ${timeStr}`}
      </span>
    </motion.div>
  );
}
