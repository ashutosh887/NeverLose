"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Phone, PhoneOff, X } from "lucide-react";

interface CallOverlayProps {
  isVisible: boolean;
  onClose: () => void;
  productName?: string;
  monthlyDisplay?: string;
  checkoutUrl?: string;
  whatsappUrl?: string;
}

type CallState = "ringing" | "active" | "ended";

export function CallOverlay({
  isVisible,
  onClose,
  productName = "your item",
  monthlyDisplay,
  checkoutUrl,
  whatsappUrl,
}: CallOverlayProps) {
  const [callState, setCallState] = useState<CallState>("ringing");

  useEffect(() => {
    if (!isVisible) {
      setCallState("ringing");
      if (typeof window !== "undefined") speechSynthesis.cancel();
    }
  }, [isVisible]);

  const handleAccept = () => {
    setCallState("active");
    if (typeof window === "undefined" || !("speechSynthesis" in window)) {
      setTimeout(() => setCallState("ended"), 3000);
      return;
    }
    const text = monthlyDisplay
      ? `Hi! I'm Priya from TechMart. Great news about ${productName} — with our No-Cost EMI, it's just ${monthlyDisplay} per month. That's an incredible deal with zero interest. Shall I send you the payment link on WhatsApp, or would you like to complete checkout right now?`
      : `Hi! I'm Priya from TechMart. I noticed you're checking out ${productName}. I've found you an amazing EMI deal with Pine Labs. Would you like me to walk you through it? I can send you a payment link on WhatsApp or help you complete the purchase directly.`;

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-IN";
    utterance.rate = 0.92;
    utterance.pitch = 1.1;
    utterance.onend = () => setTimeout(() => setCallState("ended"), 600);
    speechSynthesis.speak(utterance);
  };

  const handleDecline = () => {
    if (typeof window !== "undefined") speechSynthesis.cancel();
    onClose();
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[200] flex items-center justify-center bg-gray-950/96 backdrop-blur-lg"
        >
          <motion.div
            initial={{ scale: 0.88, y: 28 }}
            animate={{ scale: 1, y: 0 }}
            exit={{ scale: 0.88, y: 28 }}
            transition={{ type: "spring", stiffness: 360, damping: 30 }}
            className="relative flex flex-col items-center gap-8 px-10 py-14 max-w-xs w-full mx-4"
          >
            <button
              onClick={handleDecline}
              className="absolute top-2 right-2 p-2 text-white/30 hover:text-white/70 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Avatar with pulsing rings */}
            <div className="relative flex items-center justify-center">
              {callState === "ringing" &&
                [1.55, 2.05].map((scale, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-28 h-28 rounded-full border-2 border-pine-400/40"
                    animate={{ scale: [1, scale, scale], opacity: [0.5, 0, 0] }}
                    transition={{
                      duration: 1.7,
                      repeat: Infinity,
                      delay: i * 0.55,
                      ease: "easeOut",
                    }}
                  />
                ))}
              <div className="w-28 h-28 rounded-full bg-gradient-to-br from-pine-400 to-emerald-500 flex items-center justify-center text-white text-5xl font-bold shadow-2xl shadow-pine-900/60">
                P
              </div>
              {callState === "active" && (
                <motion.div
                  className="absolute -bottom-1 -right-1 w-8 h-8 bg-green-400 rounded-full border-[3px] border-gray-950 flex items-center justify-center"
                  animate={{ scale: [1, 1.15, 1] }}
                  transition={{ duration: 0.9, repeat: Infinity }}
                >
                  <Phone className="w-4 h-4 text-white" />
                </motion.div>
              )}
            </div>

            <div className="text-center space-y-1.5">
              <p className="text-white text-2xl font-bold tracking-tight">Priya</p>
              <p className="text-white/50 text-sm">TechMart Shopping Assistant</p>
              {callState === "ringing" && (
                <motion.p
                  className="text-pine-300 text-sm font-medium mt-2"
                  animate={{ opacity: [1, 0.4, 1] }}
                  transition={{ duration: 1.4, repeat: Infinity }}
                >
                  Incoming call...
                </motion.p>
              )}
              {callState === "active" && (
                <div className="flex items-center justify-center gap-1.5 mt-3">
                  {[0, 1, 2, 3].map((i) => (
                    <motion.div
                      key={i}
                      className="w-1 bg-pine-400 rounded-full"
                      animate={{ height: ["6px", "22px", "6px"] }}
                      transition={{ duration: 0.55, repeat: Infinity, delay: i * 0.12 }}
                    />
                  ))}
                  <span className="text-pine-300 text-xs ml-2">Speaking...</span>
                </div>
              )}
              {callState === "ended" && (
                <p className="text-white/40 text-sm mt-1">Call ended</p>
              )}
            </div>

            {callState === "ringing" && (
              <div className="flex items-center gap-14">
                <div className="flex flex-col items-center gap-2">
                  <button
                    onClick={handleDecline}
                    className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 active:scale-95 transition-all flex items-center justify-center shadow-xl shadow-red-900/40"
                  >
                    <PhoneOff className="w-6 h-6 text-white" />
                  </button>
                  <span className="text-white/40 text-xs">Decline</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <motion.button
                    onClick={handleAccept}
                    animate={{ scale: [1, 1.07, 1] }}
                    transition={{ duration: 1.1, repeat: Infinity }}
                    className="w-16 h-16 rounded-full bg-green-500 hover:bg-green-600 active:scale-95 transition-all flex items-center justify-center shadow-xl shadow-green-900/40"
                  >
                    <Phone className="w-6 h-6 text-white" />
                  </motion.button>
                  <span className="text-white/40 text-xs">Accept</span>
                </div>
              </div>
            )}

            {callState === "active" && (
              <button
                onClick={handleDecline}
                className="w-16 h-16 rounded-full bg-red-500 hover:bg-red-600 transition-colors flex items-center justify-center shadow-xl"
              >
                <PhoneOff className="w-6 h-6 text-white" />
              </button>
            )}

            {callState === "ended" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-3 w-full"
              >
                {whatsappUrl ? (
                  <a
                    href={whatsappUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 py-3.5 rounded-2xl bg-green-500 text-white text-sm font-bold text-center hover:bg-green-600 transition-colors shadow-lg"
                  >
                    WhatsApp
                  </a>
                ) : null}
                {checkoutUrl ? (
                  <a
                    href={checkoutUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 py-3.5 rounded-2xl bg-pine-500 text-white text-sm font-bold text-center hover:bg-pine-600 transition-colors shadow-lg"
                  >
                    Checkout
                  </a>
                ) : null}
                {!whatsappUrl && !checkoutUrl && (
                  <button
                    onClick={onClose}
                    className="flex-1 py-3.5 rounded-2xl bg-white/10 text-white text-sm font-medium hover:bg-white/20 transition-colors"
                  >
                    Close
                  </button>
                )}
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
