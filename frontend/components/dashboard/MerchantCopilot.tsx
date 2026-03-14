"use client";
import { useState, useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Send, Bot, Loader2 } from "lucide-react";
import { getMerchantWSClient, type WSEvent } from "@/lib/ws-client";
import { cn } from "@/lib/utils";

interface MerchantMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

const QUICK_PROMPTS = [
  "What's my best EMI scheme today?",
  "Create a 5% flash offer on Samsung S24",
  "Which product has highest abandonment?",
  "How many carts did I recover this week?",
];

export function MerchantCopilot() {
  const [messages, setMessages] = useState<MerchantMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const clientRef = useRef(getMerchantWSClient());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ws = clientRef.current;
    ws.connect();

    const off = ws.on((event: WSEvent) => {
      if (event.type === "token") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.isStreaming) {
            return [...prev.slice(0, -1), { ...last, content: last.content + event.content }];
          }
          return [...prev, { id: uid(), role: "assistant", content: event.content, isStreaming: true }];
        });
      } else if (event.type === "message_end") {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant" && last.isStreaming) {
            return [...prev.slice(0, -1), { ...last, isStreaming: false }];
          }
          return prev;
        });
        setIsLoading(false);
      }
    });

    const interval = setInterval(() => setIsConnected(ws.isConnected), 1000);
    return () => { off(); clearInterval(interval); };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = useCallback((text: string) => {
    const content = text.trim();
    if (!content || isLoading) return;
    setMessages((prev) => [...prev, { id: uid(), role: "user", content }]);
    setIsLoading(true);
    setInput("");
    clientRef.current.sendMessage(content);
  }, [isLoading]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="rounded-2xl border border-slate-800/80 flex flex-col overflow-hidden"
      style={{ background: "rgba(15,23,42,0.8)", height: "420px" }}
    >
      {/* Header */}
      <div className="flex items-center gap-2.5 px-4 py-3 border-b border-slate-800 flex-shrink-0">
        <div className="w-7 h-7 bg-pine-500/20 border border-pine-500/30 rounded-lg flex items-center justify-center">
          <Bot className="w-3.5 h-3.5 text-pine-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-slate-200 leading-tight">Priya — Merchant Copilot</p>
          <p className="text-[10px] text-slate-500">Ask about performance, create offers</p>
        </div>
        <span className={cn(
          "w-1.5 h-1.5 rounded-full flex-shrink-0",
          isConnected ? "bg-pine-400" : "bg-slate-600"
        )} />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-3 py-3 space-y-2.5 scrollbar-hide">
        {messages.length === 0 && (
          <div className="space-y-1.5 pt-1">
            <p className="text-xs text-slate-500 px-1 mb-2">Quick questions:</p>
            {QUICK_PROMPTS.map((p) => (
              <button
                key={p}
                onClick={() => send(p)}
                className="block w-full text-left text-xs px-3 py-2 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-400 hover:text-slate-200 hover:border-pine-500/40 transition-colors"
              >
                {p}
              </button>
            ))}
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={cn("flex", msg.role === "user" ? "justify-end" : "justify-start")}>
            <div className={cn(
              "max-w-[88%] px-3 py-2 rounded-xl text-xs leading-relaxed",
              msg.role === "user"
                ? "bg-pine-500/20 border border-pine-500/30 text-pine-100"
                : "bg-slate-800 border border-slate-700 text-slate-300"
            )}>
              {msg.content}
              {msg.isStreaming && (
                <motion.span
                  className="inline-block w-0.5 h-3 bg-pine-400 ml-0.5 align-middle"
                  animate={{ opacity: [1, 0, 1] }}
                  transition={{ repeat: Infinity, duration: 0.7 }}
                />
              )}
            </div>
          </div>
        ))}

        {isLoading && messages[messages.length - 1]?.role !== "assistant" && (
          <div className="flex justify-start">
            <div className="px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 flex items-center gap-1.5">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-1 h-1 bg-slate-500 rounded-full"
                  animate={{ y: [0, -3, 0] }}
                  transition={{ delay: i * 0.15, repeat: Infinity, duration: 0.6 }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="flex items-center gap-2 px-3 py-2.5 border-t border-slate-800 flex-shrink-0">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send(input)}
          placeholder="Ask about performance or create an offer..."
          className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-pine-500/50 transition-colors"
        />
        <button
          onClick={() => send(input)}
          disabled={!input.trim() || isLoading}
          className="w-7 h-7 bg-pine-500 hover:bg-pine-600 disabled:opacity-40 rounded-lg flex items-center justify-center transition-colors flex-shrink-0"
        >
          {isLoading ? (
            <Loader2 className="w-3.5 h-3.5 text-white animate-spin" />
          ) : (
            <Send className="w-3.5 h-3.5 text-white" />
          )}
        </button>
      </div>
    </motion.div>
  );
}
