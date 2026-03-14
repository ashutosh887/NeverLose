"use client";
import { useState, useRef, useEffect, startTransition, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, MessageCircle, ShoppingBag, Loader2 } from "lucide-react";
import { ChatBubble } from "./ChatBubble";
import { ChatInput } from "./ChatInput";
import { SocialProofBadge } from "@/components/shared/SocialProofBadge";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { SignalType, PostPurchaseData } from "@/lib/types";
import { cn } from "@/lib/utils";

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function getDeliveryDate(): string {
  const d = new Date();
  d.setDate(d.getDate() + 3);
  return d.toLocaleDateString("en-IN", { weekday: "long", month: "short", day: "numeric" });
}

function getEmiDueDate(): string {
  const d = new Date();
  d.setMonth(d.getMonth() + 1);
  d.setDate(15);
  return d.toLocaleDateString("en-IN", { month: "long", day: "numeric" });
}

interface ChatWidgetProps {
  productId: string;
  productName: string;
  amountPaisa: number;
  triggerSignal?: SignalType | null;
  forceOpen?: boolean;
}

export function ChatWidget({
  productId: _productId,
  productName,
  amountPaisa: _amountPaisa,
  triggerSignal,
  forceOpen = false,
}: ChatWidgetProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [showBadge, setShowBadge] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { messages, isConnected, isLoading, toolStatus, sendMessage, sendSignal, clearMessages, injectMessage } = useWebSocket();
  const signalFiredRef = useRef<Set<SignalType>>(new Set());

  const handlePaymentSuccess = useCallback(() => {
    const data: PostPurchaseData = {
      productName: productName,
      amountDisplay: "",
      monthlyDisplay: "₹4,722",
      bankName: "HDFC Bank",
      deliveryDate: getDeliveryDate(),
      emiDueDate: getEmiDueDate(),
    };
    injectMessage({
      id: uid(),
      role: "assistant",
      content: "",
      contentType: "post_purchase",
      data,
      timestamp: new Date(),
      isStreaming: false,
    });
  }, [productName, injectMessage]);

  // Auto-open and fire signal
  useEffect(() => {
    if (triggerSignal && !signalFiredRef.current.has(triggerSignal)) {
      signalFiredRef.current.add(triggerSignal);
      sendSignal(triggerSignal);
      startTransition(() => {
        setIsOpen(true);
        setShowBadge(true);
      });
      setTimeout(() => startTransition(() => setShowBadge(false)), 5000);
    }
  }, [triggerSignal, sendSignal]);

  useEffect(() => {
    if (forceOpen) startTransition(() => setIsOpen(true));
  }, [forceOpen]);

  // Reset signals when product changes
  useEffect(() => {
    signalFiredRef.current = new Set();
  }, [_productId]);

  // Ctrl+Shift+R — reset demo
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === "R") {
        e.preventDefault();
        clearMessages();
        signalFiredRef.current = new Set();
        startTransition(() => setIsOpen(false));
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [clearMessages]);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Determine loading tool status text
  const lastMsg = messages[messages.length - 1];
  const showTypingDots = isLoading && lastMsg?.role !== "assistant";

  return (
    <>
      {/* FAB */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            key="fab"
            initial={{ scale: 0, rotate: -10 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0, rotate: 10 }}
            transition={{ type: "spring", stiffness: 300, damping: 20 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-pine-500 hover:bg-pine-600 text-white rounded-full shadow-xl shadow-pine-200 flex items-center justify-center transition-colors group"
          >
            {/* Notification badge */}
            {showBadge && (
              <motion.span
                className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-md"
                initial={{ scale: 0 }}
                animate={{ scale: [0, 1.2, 1] }}
                transition={{ duration: 0.3 }}
              >
                !
              </motion.span>
            )}
            {/* Pulse ring on badge */}
            {showBadge && (
              <span className="absolute inset-0 rounded-full border-2 border-pine-400 animate-ping opacity-40" />
            )}
            <MessageCircle className="w-6 h-6 group-hover:scale-110 transition-transform" />
          </motion.button>
        )}
      </AnimatePresence>

      {/* Chat Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="chat-panel"
            initial={{ opacity: 0, y: 24, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24, scale: 0.96 }}
            transition={{ type: "spring", stiffness: 400, damping: 35 }}
            className="fixed bottom-6 right-6 z-50 w-[380px] max-w-[calc(100vw-1.5rem)] bg-white rounded-2xl shadow-2xl border border-gray-200/80 flex flex-col overflow-hidden"
            style={{ height: "min(590px, calc(100vh - 3rem))" }}
          >
            {/* Header */}
            <div className="flex items-center gap-3 px-4 py-3.5 bg-gradient-to-r from-pine-500 to-pine-600 text-white flex-shrink-0">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-white/30 to-white/10 border border-white/20 flex items-center justify-center font-bold text-base">
                P
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-sm leading-tight">TechMart · AI</p>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <span
                    className={cn(
                      "w-1.5 h-1.5 rounded-full",
                      isConnected ? "bg-green-300 animate-pulse" : "bg-white/40"
                    )}
                  />
                  <p className="text-xs text-white/80">
                    {isConnected ? "Online · Pine Labs AI" : "Connecting..."}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-white/20 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 min-h-0 overflow-y-auto px-4 py-3" style={{ scrollbarWidth: "none" }}>
              {messages.length === 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex flex-col items-center text-center py-6 gap-3"
                >
                  <div className="w-16 h-16 bg-gradient-to-br from-pine-100 to-emerald-100 rounded-2xl flex items-center justify-center border border-pine-200">
                    <ShoppingBag className="w-8 h-8 text-pine-500" strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-gray-800 mb-1">
                      Hey! I&apos;m your TechMart shopping assistant
                    </p>
                    <p className="text-xs text-gray-400 leading-relaxed max-w-[240px]">
                      I&apos;ve found a great EMI deal on {productName}. Let me show you!
                    </p>
                  </div>
                  <SocialProofBadge />

                  <div className="flex flex-wrap gap-1.5 justify-center mt-1">
                    {[
                      "What EMI options do I have?",
                      "Show me the best deal",
                      "Can I get No-Cost EMI?",
                    ].map((prompt) => (
                      <button
                        key={prompt}
                        onClick={() => sendMessage(prompt)}
                        className="px-2.5 py-1 text-xs bg-gray-50 border border-gray-200 rounded-full text-gray-600 hover:border-pine-300 hover:text-pine-600 hover:bg-pine-50 transition-colors"
                      >
                        {prompt}
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              <div className="space-y-3">
                {messages.map((msg, i) => (
                  <ChatBubble
                    key={msg.id}
                    message={msg}
                    index={i}
                    onClaimDeal={() => sendMessage("Yes, I want to claim this deal")}
                    onPaymentSuccess={handlePaymentSuccess}
                  />
                ))}

                {/* Typing indicator */}
                {showTypingDots && (
                  <motion.div
                    initial={{ opacity: 0, y: 4 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center gap-2 px-4 py-3 bg-white border border-gray-100 rounded-2xl rounded-tl-sm w-fit shadow-sm"
                  >
                    {[0, 1, 2].map((i) => (
                      <motion.div
                        key={i}
                        className="w-1.5 h-1.5 bg-gray-400 rounded-full"
                        animate={{ y: [0, -5, 0], backgroundColor: ["#9ca3af", "#2aa85e", "#9ca3af"] }}
                        transition={{ delay: i * 0.15, repeat: Infinity, duration: 0.7 }}
                      />
                    ))}
                  </motion.div>
                )}

                {/* Tool status shimmer */}
                {toolStatus && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex items-center gap-2 text-xs text-pine-600 px-2"
                  >
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span className="font-medium">{toolStatus}</span>
                  </motion.div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input */}
            <ChatInput onSend={sendMessage} disabled={isLoading} />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
