"use client";
import { useState } from "react";
import { Globe, MessageCircle, QrCode, Phone } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { QRCodeDisplay } from "./QRCodeDisplay";
import { WhatsAppButton } from "./WhatsAppButton";
import { CallOverlay } from "./CallOverlay";
import type { PaymentOptions as PaymentOptionsData } from "@/lib/types";
import { cn } from "@/lib/utils";

interface PaymentOptionsProps {
  data: PaymentOptionsData;
  productName?: string;
  monthlyDisplay?: string;
  onPaymentSuccess?: () => void;
}

type Channel = "none" | "web" | "whatsapp" | "qr" | "call";

const OPTION_CONFIG = {
  web: {
    icon: Globe,
    label: "Web Checkout",
    sub: "Open checkout",
    selected: "border-blue-400 bg-blue-50",
    idle: "border-gray-100 bg-white hover:border-gray-200 hover:bg-gray-50",
    iconBg: "bg-blue-100",
    iconColor: "text-blue-600",
  },
  whatsapp: {
    icon: MessageCircle,
    label: "WhatsApp",
    sub: "Send link",
    selected: "border-green-400 bg-green-50",
    idle: "border-gray-100 bg-white hover:border-gray-200 hover:bg-gray-50",
    iconBg: "bg-green-100",
    iconColor: "text-green-600",
  },
  qr: {
    icon: QrCode,
    label: "UPI QR",
    sub: "Scan & pay",
    selected: "border-purple-400 bg-purple-50",
    idle: "border-gray-100 bg-white hover:border-gray-200 hover:bg-gray-50",
    iconBg: "bg-purple-100",
    iconColor: "text-purple-600",
  },
  call: {
    icon: Phone,
    label: "Call Me",
    sub: "Priya will call",
    selected: "border-pine-400 bg-pine-50",
    idle: "border-gray-100 bg-white hover:border-pine-200 hover:bg-pine-50",
    iconBg: "bg-pine-100",
    iconColor: "text-pine-600",
  },
};

export function PaymentOptions({ data, productName, monthlyDisplay, onPaymentSuccess }: PaymentOptionsProps) {
  const [channel, setChannel] = useState<Channel>("none");
  const [callVisible, setCallVisible] = useState(false);

  const available: Array<"web" | "whatsapp" | "qr" | "call"> = [];
  if (data.checkout_url) available.push("web");
  if (data.payment_link?.whatsapp_url) available.push("whatsapp");
  if (data.qr) available.push("qr");
  available.push("call");

  const gridCols = available.length === 4 ? "grid-cols-4" : available.length === 3 ? "grid-cols-3" : `grid-cols-${available.length}`;

  return (
    <>
      <CallOverlay
        isVisible={callVisible}
        onClose={() => setCallVisible(false)}
        productName={productName}
        monthlyDisplay={monthlyDisplay}
        checkoutUrl={data.checkout_url}
        whatsappUrl={data.payment_link?.whatsapp_url}
      />

      <div className="space-y-3">
        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          How would you like to pay?
        </p>

        <div className={cn("grid gap-2", gridCols)}>
          {available.map((ch) => {
            const cfg = OPTION_CONFIG[ch];
            const Icon = cfg.icon;
            const isSelected = channel === ch;

            return (
              <button
                key={ch}
                onClick={() => {
                  if (ch === "web" && data.checkout_url) {
                    window.open(data.checkout_url, "_blank");
                  }
                  if (ch === "call") {
                    setCallVisible(true);
                    return;
                  }
                  setChannel(isSelected ? "none" : ch);
                }}
                className={cn(
                  "flex flex-col items-center gap-1.5 p-2.5 rounded-xl border-2 transition-all text-center",
                  isSelected ? cfg.selected : cfg.idle
                )}
              >
                <div className={cn("w-8 h-8 rounded-full flex items-center justify-center", cfg.iconBg)}>
                  <Icon className={cn("w-4 h-4", cfg.iconColor)} />
                </div>
                <div>
                  <p className="text-[10px] font-bold text-gray-800 leading-tight">{cfg.label}</p>
                  <p className="text-[9px] text-gray-400">{cfg.sub}</p>
                </div>
              </button>
            );
          })}
        </div>

        <AnimatePresence mode="wait">
          {channel === "whatsapp" && data.payment_link && (
            <motion.div
              key="whatsapp"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
            >
              <WhatsAppButton
                whatsappUrl={data.payment_link.whatsapp_url}
                message={data.payment_link.whatsapp_message}
              />
            </motion.div>
          )}

          {channel === "qr" && data.qr && (
            <motion.div
              key="qr"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="bg-white rounded-xl border border-gray-100 p-4 shadow-sm"
            >
              <QRCodeDisplay
                upiString={data.qr.upi_string}
                qrBase64={data.qr.qr_image_base64}
                amountPaisa={data.qr.amount_paisa}
                orderId={data.order_id}
                onPaymentSuccess={onPaymentSuccess}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
