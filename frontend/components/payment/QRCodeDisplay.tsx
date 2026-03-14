"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Confetti from "react-confetti";
import Image from "next/image";
import { CheckCircle2, Loader2, RefreshCw } from "lucide-react";
import QRCode from "react-qr-code";
import { Progress } from "@/components/ui/progress";
import { formatInr } from "@/lib/signals";
import { getPaymentStatus } from "@/lib/clients/api";
import { cn } from "@/lib/utils";

interface QRCodeDisplayProps {
  upiString: string;
  qrBase64?: string;
  amountPaisa: number;
  orderId: string;
}

type PaymentStatus = "PENDING" | "SUCCESS" | "FAILED";

const UPI_APP_BADGES = [
  { label: "G", name: "GPay", bg: "bg-white border-gray-200", text: "text-blue-600", style: { fontSize: "14px", fontWeight: "800" } },
  { label: "P", name: "PhonePe", bg: "bg-purple-600 border-purple-700", text: "text-white", style: {} },
  { label: "P", name: "Paytm", bg: "bg-blue-500 border-blue-600", text: "text-white", style: {} },
];

const CORNER_POSITIONS = [
  "top-2 left-2 border-l-2 border-t-2",
  "top-2 right-2 border-r-2 border-t-2",
  "bottom-2 left-2 border-l-2 border-b-2",
  "bottom-2 right-2 border-r-2 border-b-2",
];

const MAX_WAIT = 120;

function playKaching() {
  try {
    const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    const ctx = new AudioCtx();
    [[880, 0], [1100, 0.13], [1320, 0.26]].forEach(([freq, delay]) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.frequency.value = freq;
      osc.type = "sine";
      gain.gain.setValueAtTime(0.35, ctx.currentTime + delay);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + 0.18);
      osc.start(ctx.currentTime + delay);
      osc.stop(ctx.currentTime + delay + 0.18);
    });
  } catch {
    // audio not supported
  }
}

export function QRCodeDisplay({ upiString, qrBase64, amountPaisa, orderId }: QRCodeDisplayProps) {
  const [status, setStatus] = useState<PaymentStatus>("PENDING");
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (status === "SUCCESS") playKaching();
  }, [status]);

  useEffect(() => {
    if (status !== "PENDING") return;
    const interval = setInterval(async () => {
      try {
        const data = await getPaymentStatus(orderId);
        if (data.payment?.status === "SUCCESS") {
          setStatus("SUCCESS");
          clearInterval(interval);
        }
      } catch {
        // network errors are ignored; polling continues
      }
    }, 3000);
    return () => clearInterval(interval);
  }, [orderId, status]);

  useEffect(() => {
    if (status !== "PENDING") return;
    const timer = setInterval(() => {
      setElapsed((e) => {
        if (e >= MAX_WAIT) {
          clearInterval(timer);
          return MAX_WAIT;
        }
        return e + 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [status]);

  const progressPct = Math.min(100, (elapsed / MAX_WAIT) * 100);

  if (status === "SUCCESS") {
    return (
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="relative flex flex-col items-center gap-4 p-6 bg-gradient-to-br from-pine-50 to-emerald-50 rounded-2xl border-2 border-pine-200 overflow-hidden"
      >
        <Confetti recycle={false} numberOfPieces={200} />
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 15, delay: 0.1 }}
        >
          <CheckCircle2 className="w-16 h-16 text-pine-500" />
        </motion.div>
        <div className="text-center">
          <p className="text-xl font-bold text-pine-700">Payment Successful!</p>
          <p className="text-sm text-pine-600 mt-1">{formatInr(amountPaisa)} received</p>
        </div>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-xs text-gray-500 text-center"
        >
          Thank you! Your order is confirmed.
        </motion.p>
      </motion.div>
    );
  }

  const qrValue = upiString || `upi://pay?pa=merchant@hdfc&pn=TechMart&am=${amountPaisa / 100}&cu=INR`;

  return (
    <div className="flex flex-col items-center gap-3">
      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
        Scan &amp; Pay — {formatInr(amountPaisa)}
      </p>

      <div className="relative p-4 bg-white border-2 border-gray-100 rounded-2xl shadow-sm">
        {CORNER_POSITIONS.map((pos, i) => (
          <div key={i} className={cn("absolute w-5 h-5 border-pine-400 rounded-sm", pos)} />
        ))}

        {qrBase64 ? (
          <Image
            src={`data:image/png;base64,${qrBase64}`}
            alt="UPI QR Code"
            width={192}
            height={192}
          />
        ) : (
          <QRCode
            value={qrValue}
            size={192}
            fgColor="#1a1a1a"
            bgColor="#ffffff"
            level="M"
          />
        )}
      </div>

      <div className="flex items-center gap-3">
        {UPI_APP_BADGES.map((app) => (
          <div key={app.name} className="flex flex-col items-center gap-1">
            <div
              className={cn(
                "w-8 h-8 rounded-full border flex items-center justify-center font-bold",
                app.bg,
                app.text
              )}
              style={app.style}
            >
              {app.label}
            </div>
            <span className="text-[9px] text-gray-400">{app.name}</span>
          </div>
        ))}
      </div>

      <div className="w-full space-y-1.5">
        <Progress value={progressPct} className="h-1.5" />
        <div className="flex items-center justify-center gap-1.5 text-xs text-gray-400">
          <Loader2 className="w-3 h-3 animate-spin" />
          <span>Waiting for payment...</span>
          <button
            onClick={() => setElapsed(0)}
            className="ml-1 text-pine-500 hover:text-pine-600 transition-colors"
            title="Refresh QR"
          >
            <RefreshCw className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
}
