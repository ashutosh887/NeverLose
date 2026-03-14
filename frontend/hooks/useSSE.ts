"use client";

import { useEffect, useState } from "react";
import { connectSSE } from "@/lib/sse-client";
import type { ConversionEvent, DashboardSeed } from "@/lib/types";

export function useSSE() {
  const [conversions, setConversions] = useState<ConversionEvent[]>([]);
  const [totalWeekly, setTotalWeekly] = useState<DashboardSeed["total_weekly"] | null>(null);
  const [dailySummary, setDailySummary] = useState<DashboardSeed["daily_summary"]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const disconnect = connectSSE("/api/events", (event) => {
      setIsConnected(true);
      if (event.type === "seed") {
        setConversions(event.recent_conversions);
        setTotalWeekly(event.total_weekly);
        setDailySummary(event.daily_summary);
      } else if (event.type === "conversion") {
        setConversions((prev) => [event.data, ...prev].slice(0, 50));
        // Update totals
        setTotalWeekly((prev) =>
          prev
            ? {
                ...prev,
                saves: prev.saves + 1,
                gmv_recovered_paisa:
                  prev.gmv_recovered_paisa + event.data.amount_paisa,
              }
            : prev
        );
      }
    });

    return disconnect;
  }, []);

  return { conversions, totalWeekly, dailySummary, isConnected };
}
