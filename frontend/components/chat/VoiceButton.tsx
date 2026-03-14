"use client";
import { useState } from "react";
import { Mic, MicOff } from "lucide-react";
import { motion } from "framer-motion";
import { useVoiceInput } from "@/hooks/useVoiceInput";
import { cn } from "@/lib/utils";

interface VoiceButtonProps {
  onTranscript: (text: string) => void;
}

export function VoiceButton({ onTranscript }: VoiceButtonProps) {
  const [lang, setLang] = useState<"en-IN" | "hi-IN">("en-IN");

  const { isListening, isSupported, start, stop } = useVoiceInput({
    onResult: onTranscript,
    lang,
  });

  if (!isSupported) return null;

  return (
    <div className="flex flex-col items-center gap-0.5 flex-shrink-0">
      <button
        type="button"
        onClick={isListening ? stop : start}
        title={isListening ? "Stop recording" : `Voice input (${lang === "en-IN" ? "English" : "Hindi"})`}
        className={cn(
          "relative w-9 h-9 rounded-full flex items-center justify-center transition-all",
          isListening
            ? "bg-red-100 text-red-600 shadow-md shadow-red-100"
            : "bg-gray-100 text-gray-500 hover:bg-gray-200 hover:text-gray-600"
        )}
      >
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

      {/* Language toggle — tap to switch EN ↔ हि */}
      <button
        type="button"
        disabled={isListening}
        onClick={() => setLang((l) => (l === "en-IN" ? "hi-IN" : "en-IN"))}
        className="text-[9px] font-bold leading-none text-gray-400 hover:text-pine-500 disabled:opacity-40 transition-colors"
        title="Toggle voice language"
      >
        {lang === "en-IN" ? "EN" : "हि"}
      </button>
    </div>
  );
}
