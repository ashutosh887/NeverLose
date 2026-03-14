"use client";

import config from "@/config";
import type { ConversionEvent, DashboardSeed } from "./types";

export type SSEData =
  | { type: "seed"; daily_summary: DashboardSeed["daily_summary"]; total_weekly: DashboardSeed["total_weekly"]; recent_conversions: ConversionEvent[] }
  | { type: "conversion"; data: ConversionEvent }
  | { type: "ping" };

type SSEListener = (event: SSEData) => void;

export function connectSSE(
  url: string,
  listener: SSEListener
): () => void {
  const apiUrl = config.backendUrl + url;
  const source = new EventSource(apiUrl);

  source.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as SSEData;
      listener(data);
    } catch {
      // ignore parse errors
    }
  };

  source.onerror = () => {
    // EventSource auto-reconnects
  };

  return () => source.close();
}
