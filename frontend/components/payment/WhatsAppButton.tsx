"use client";
import { MessageCircle, ExternalLink } from "lucide-react";
import { motion } from "framer-motion";

interface WhatsAppButtonProps {
  whatsappUrl: string;
  label?: string;
  message?: string;
}

export function WhatsAppButton({
  whatsappUrl,
  label = "Send to WhatsApp",
  message,
}: WhatsAppButtonProps) {
  return (
    <motion.a
      href={whatsappUrl}
      target="_blank"
      rel="noopener noreferrer"
      whileHover={{ scale: 1.01 }}
      whileTap={{ scale: 0.98 }}
      className="group flex items-center justify-between w-full px-4 py-3.5 bg-[#25D366] hover:bg-[#1fbc59] text-white font-semibold rounded-xl transition-colors text-sm shadow-md shadow-green-200"
    >
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
          <MessageCircle className="w-4 h-4" />
        </div>
        <div className="text-left">
          <p className="font-semibold leading-tight">{label}</p>
          {message && (
            <p className="text-xs text-green-100 font-normal mt-0.5 leading-tight line-clamp-1">
              {message}
            </p>
          )}
        </div>
      </div>
      <ExternalLink className="w-3.5 h-3.5 opacity-70 group-hover:opacity-100 transition-opacity" />
    </motion.a>
  );
}
