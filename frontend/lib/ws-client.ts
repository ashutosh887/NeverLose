"use client";

import config from "@/config";
import type { SignalType, MessageContentType } from "./types";

export type WSEvent =
  | { type: "token"; content: string }
  | { type: "message"; content: string; contentType?: MessageContentType; data?: unknown }
  | { type: "message_end"; session_id: string }
  | { type: "tool_result"; tool_name: string; data: unknown }
  | { type: "tool_event"; tool: string; content_type: string; data: unknown }
  | { type: "tool_start"; tool: string; status: string }
  | { type: "signal_ack"; signal_type: string }
  | { type: "error"; message: string }
  | { type: "ping" };

type Listener = (event: WSEvent) => void;

export class NeverLoseWSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private listeners: Set<Listener> = new Set();
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private shouldReconnect = true;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(url: string) {
    this.url = url;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectDelay = 1000;
        console.log("[NeverLose WS] Connected");
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WSEvent;
          this.listeners.forEach((l) => l(data));
        } catch {
          console.warn("[NeverLose WS] Failed to parse message", event.data);
        }
      };

      this.ws.onclose = () => {
        console.log("[NeverLose WS] Disconnected");
        if (this.shouldReconnect) {
          this.scheduleReconnect();
        }
      };

      this.ws.onerror = (err) => {
        console.error("[NeverLose WS] Error", err);
      };
    } catch (err) {
      console.error("[NeverLose WS] Failed to connect", err);
      this.scheduleReconnect();
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, this.reconnectDelay);
    this.reconnectDelay = Math.min(
      this.reconnectDelay * 2,
      this.maxReconnectDelay
    );
  }

  sendMessage(content: string): void {
    this.send({ type: "message", content });
  }

  sendSignal(signalType: SignalType): void {
    this.send({ type: "signal", signal_type: signalType });
  }

  private send(data: object): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn("[NeverLose WS] Not connected, queuing message");
      this.connect();
    }
  }

  on(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.ws?.close();
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Singleton for the app
let _client: NeverLoseWSClient | null = null;

export function getWSClient(): NeverLoseWSClient {
  if (!_client) {
    _client = new NeverLoseWSClient(config.wsUrl);
  }
  return _client;
}
