"use client";
import { Mic, MicOff } from "lucide-react";
import { motion } from "framer-motion";
import { useVoiceInput } from "@/hooks/useVoiceInput";
import { cn } from "@/lib/utils";

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
}

export function VoiceButton({ onTranscript }: VoiceButtonProps) {
  const { isListening, isSupported, start, stop } = useVoiceInput({
    onResult: onTranscript,
  });

  if (!isSupported) return null;

  return (
    <button
      type="button"
      onClick={isListening ? stop : start}
      title={isListening ? "Stop recording" : "Voice input (Hindi/English)"}
      className={cn(
        "relative w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 transition-all",
        isListening
          ? "bg-red-100 text-red-600 shadow-md shadow-red-100"
          : "bg-gray-100 text-gray-500 hover:bg-gray-200 hover:text-gray-600"
      )}
    >
      {/* Pulse ring when listening */}
      {isListening && (
        <>
          <motion.span
            className="absolute inset-0 rounded-full border-2 border-red-400"
            animate={{ scale: [1, 1.5, 1], opacity: [1, 0, 1] }}
            transition={{ repeat: Infinity, duration: 1.2 }}
          />
          <motion.span
            className="absolute inset-0 rounded-full bg-red-400/20"
            animate={{ scale: [1, 1.3] }}
            transition={{ repeat: Infinity, duration: 0.6, repeatType: "reverse" }}
          />
        </>
      )}

      {isListening ? (
        <MicOff className="w-4 h-4 relative z-10" />
      ) : (
        <Mic className="w-4 h-4 relative z-10" />
      )}
    </button>
  );
}
