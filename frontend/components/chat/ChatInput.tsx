"use client";
import { useState, useRef } from "react";
import { Send } from "lucide-react";
import { VoiceButton } from "./VoiceButton";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSend,
  disabled,
  placeholder = "Ask about EMI, offers, deals...",
}: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = `${Math.min(el.scrollHeight, 100)}px`;
    }
  };

  const handleVoiceTranscript = (text: string) => {
    setValue(text);
    setTimeout(() => {
      onSend(text);
      setValue("");
    }, 80);
  };

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className="flex items-end gap-2 p-3 border-t border-gray-100 bg-white/95 backdrop-blur-sm rounded-b-2xl">
      <VoiceButton onTranscript={handleVoiceTranscript} />

      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={cn(
            "w-full resize-none bg-gray-50 border border-gray-200 rounded-xl",
            "px-3 py-2 pr-2 text-sm text-gray-900 placeholder-gray-400",
            "focus:outline-none focus:border-pine-400 focus:bg-white focus:ring-2 focus:ring-pine-100",
            "transition-all disabled:opacity-50 disabled:cursor-not-allowed",
            "leading-relaxed"
          )}
          style={{ minHeight: "38px", maxHeight: "100px" }}
        />
      </div>

      <button
        onClick={handleSend}
        disabled={!canSend}
        className={cn(
          "w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 transition-all",
          canSend
            ? "bg-pine-500 hover:bg-pine-600 text-white shadow-md shadow-pine-200 scale-100"
            : "bg-gray-100 text-gray-300 cursor-not-allowed scale-95"
        )}
      >
        <Send className="w-4 h-4" />
      </button>
    </div>
  );
}
