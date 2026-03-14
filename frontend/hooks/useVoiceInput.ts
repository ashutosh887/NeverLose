"use client";

import { useState, useRef, useCallback } from "react";

interface UseVoiceInputOptions {
  onResult: (transcript: string) => void;
  lang?: string;
}

export function useVoiceInput({
  onResult,
  lang = "en-IN",
}: UseVoiceInputOptions) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);

  const start = useCallback(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    const SpeechRecognitionImpl = w.SpeechRecognition || w.webkitSpeechRecognition;

    if (!SpeechRecognitionImpl) {
      setIsSupported(false);
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const recognition: any = new SpeechRecognitionImpl();
    // Use explicitly passed lang (e.g. toggled by user); never auto-override from navigator.language
    // because browser locale rarely matches what the user wants to speak in a demo.
    recognition.lang = lang;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript;
      onResult(transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  }, [onResult, lang]);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
    setIsListening(false);
  }, []);

  return { isListening, isSupported, start, stop };
}
