/**
 * NeverLose REST API Client
 * ==========================
 *
 * Centralised fetch wrapper for all calls to the backend REST API.
 * Base URL comes from NEXT_PUBLIC_API_URL (set in .env.local).
 *
 * All endpoints:
 *   GET  /health                          — backend health check
 *   POST /api/chat                        — REST fallback for chat
 *   GET  /api/events                      — SSE stream (use connectSSE instead)
 *   GET  /api/payment-status/:orderId     — UPI QR payment status polling
 *
 * Usage:
 *   import { apiClient } from "@/lib/clients/api";
 *   const data = await apiClient.get("/health");
 *   const status = await apiClient.get(`/api/payment-status/${orderId}`);
 */

"use client";

import config from "@/config";

// ── Config ──────────────────────────────────────────────────────────────────
const BASE_URL = config.backendUrl;
const DEFAULT_TIMEOUT_MS = 10_000;

// ── Headers ──────────────────────────────────────────────────────────────────
const DEFAULT_HEADERS: HeadersInit = {
  "Content-Type": "application/json",
  Accept: "application/json",
};

// ── Types ────────────────────────────────────────────────────────────────────
export class APIError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string,
  ) {
    super(message);
    this.name = "APIError";
  }
}

// ── Core fetch wrapper ───────────────────────────────────────────────────────
async function request<T>(
  path: string,
  init: RequestInit = {},
  timeoutMs = DEFAULT_TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: { ...DEFAULT_HEADERS, ...(init.headers ?? {}) },
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new APIError(
        response.status,
        response.statusText,
        `${init.method ?? "GET"} ${path} → ${response.status} ${response.statusText}`,
      );
    }

    return response.json() as Promise<T>;
  } finally {
    clearTimeout(timer);
  }
}

// ── Public client ─────────────────────────────────────────────────────────────
export const apiClient = {
  /** GET request — returns parsed JSON. */
  get<T>(path: string, timeoutMs?: number): Promise<T> {
    return request<T>(path, { method: "GET" }, timeoutMs);
  },

  /** POST request with JSON body — returns parsed JSON. */
  post<T>(path: string, body: unknown, timeoutMs?: number): Promise<T> {
    return request<T>(
      path,
      { method: "POST", body: JSON.stringify(body) },
      timeoutMs,
    );
  },
};

// ── Typed helpers ─────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: "ok";
  use_mock: boolean;
  region: string;
}

export interface PaymentStatusResponse {
  payment: {
    order_id: string;
    status: "PENDING" | "SUCCESS" | "FAILED";
    amount_paisa?: number;
    paid_at?: string;
    payment_method?: string;
  };
}

/** Check if the backend is reachable and in what mode it's running. */
export function checkHealth(): Promise<HealthResponse> {
  return apiClient.get<HealthResponse>("/health", 5_000);
}

/** Poll UPI QR payment status — used by QRCodeDisplay component. */
export function getPaymentStatus(orderId: string): Promise<PaymentStatusResponse> {
  return apiClient.get<PaymentStatusResponse>(
    `/api/payment-status/${orderId}`,
    8_000,
  );
}
