"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { getWSClient, type WSEvent } from "@/lib/ws-client";
import type { SignalType, ChatMessage, MessageContentType } from "@/lib/types";

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export function useWebSocket() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [toolStatus, setToolStatus] = useState("");
  const client = useRef(getWSClient());

  useEffect(() => {
    const ws = client.current;
    ws.connect();

    const off = ws.on((event: WSEvent) => {
      if (event.type === "token") {
        // Accumulate tokens into current assistant message
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.isStreaming) {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + event.content },
            ];
          }
          // Start new streaming message
          const newMsg: ChatMessage = {
            id: uid(),
            role: "assistant",
            content: event.content,
            contentType: "text",
            timestamp: new Date(),
            isStreaming: true,
          };
          return [...prev, newMsg];
        });
      } else if (event.type === "message") {
        // Full non-streaming message (from /api/chat fallback or tool result message)
        const newMsg: ChatMessage = {
          id: uid(),
          role: "assistant",
          content: event.content,
          contentType: (event.contentType as MessageContentType) ?? "text",
          data: event.data as ChatMessage["data"],
          timestamp: new Date(),
          isStreaming: false,
        };
        setMessages((prev) => {
          // Replace streaming placeholder if exists
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.isStreaming) {
            return [...prev.slice(0, -1), newMsg];
          }
          return [...prev, newMsg];
        });
        setIsLoading(false);
      } else if (event.type === "message_end") {
        // Finalise streaming message
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.isStreaming) {
            return [...prev.slice(0, -1), { ...last, isStreaming: false }];
          }
          return prev;
        });
        // Level 3 negotiation — inject countdown timer message
        if (event.negotiation_level === 3) {
          setMessages((prev) => {
            // Only inject if no countdown already present
            if (prev.some((m) => m.contentType === "countdown")) return prev;
            return [
              ...prev,
              {
                id: uid(),
                role: "assistant" as const,
                content: "",
                contentType: "countdown" as const,
                timestamp: new Date(),
                isStreaming: false,
              },
            ];
          });
        }
        setToolStatus("");
        setIsLoading(false);
      } else if (event.type === "tool_start") {
        // Show tool running status in the widget
        setToolStatus(event.status);
      } else if (event.type === "tool_event") {
        // Rich structured result from a tool call — backend sends this
        setToolStatus("");
        const CONTENT_TYPE_MAP: Record<string, MessageContentType> = {
          emi_schemes: "emi_schemes",
          stacked_deal: "stacked_deal",
          payment_options: "payment_options",
          qr_code: "qr_code",
          accessory_upsell: "accessory_upsell",
        };
        const mappedType = CONTENT_TYPE_MAP[event.content_type];
        if (mappedType) {
          const richMsg: ChatMessage = {
            id: uid(),
            role: "assistant",
            content: "",
            contentType: mappedType,
            data: event.data as ChatMessage["data"],
            timestamp: new Date(),
            isStreaming: false,
          };
          setMessages((prev) => [...prev, richMsg]);
        }
      }
    });

    // Poll connection state
    const interval = setInterval(() => {
      setIsConnected(ws.isConnected);
    }, 1000);

    return () => {
      off();
      clearInterval(interval);
    };
  }, []);

  const sendMessage = useCallback((content: string) => {
    if (!content.trim()) return;
    const userMsg: ChatMessage = {
      id: uid(),
      role: "user",
      content,
      contentType: "text",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    client.current.sendMessage(content);
  }, []);

  const sendSignal = useCallback((signalType: SignalType) => {
    client.current.sendSignal(signalType);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setToolStatus("");
    setIsLoading(false);
  }, []);

  const injectMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  return { messages, isConnected, isLoading, toolStatus, sendMessage, sendSignal, clearMessages, injectMessage };
}
