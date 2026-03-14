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
        setIsLoading(false);
      } else if (event.type === "tool_result") {
        // Rich structured result from a tool call
        const toolName = (event as { type: "tool_result"; tool_name: string; data: unknown }).tool_name;
        const data = (event as { type: "tool_result"; tool_name: string; data: unknown }).data;
        let contentType: MessageContentType = "text";
        if (toolName === "calculate_stacked_deal") contentType = "stacked_deal";
        else if (toolName === "check_emi_options") contentType = "emi_schemes";
        else if (toolName === "generate_qr_code") contentType = "qr_code";
        else if (toolName === "create_checkout" || toolName === "generate_payment_link") contentType = "payment_options";
        else if (toolName === "find_accessories") contentType = "accessory_upsell";

        if (contentType !== "text") {
          const richMsg: ChatMessage = {
            id: uid(),
            role: "assistant",
            content: "",
            contentType,
            data: data as ChatMessage["data"],
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

  return { messages, isConnected, isLoading, sendMessage, sendSignal };
}
