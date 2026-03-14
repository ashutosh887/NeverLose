"use client";

import { useEffect, useRef, useCallback } from "react";
import type { SignalType } from "@/lib/types";

interface UseHesitationDetectionOptions {
  productId: string;
  onSignal: (signal: SignalType) => void;
  onOpenChat: () => void;
  cartHasItem?: boolean;
  onCheckoutPage?: boolean;
}

export function useHesitationDetection({
  productId,
  onSignal,
  onOpenChat,
  cartHasItem = false,
  onCheckoutPage = false,
}: UseHesitationDetectionOptions) {
  const firedSignals = useRef<Set<SignalType>>(new Set());
  const idleTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const priceShockTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cartStallTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const checkoutDropTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastTouchY = useRef<number>(0);
  const lastTouchTime = useRef<number>(0);
  const priceHoverCount = useRef<number>(0);

  const fire = useCallback(
    (signal: SignalType) => {
      if (firedSignals.current.has(signal)) return;
      firedSignals.current.add(signal);
      onSignal(signal);
      onOpenChat();
    },
    [onSignal, onOpenChat]
  );

  const resetIdle = useCallback(() => {
    if (idleTimer.current) clearTimeout(idleTimer.current);
    idleTimer.current = setTimeout(() => fire("IDLE_DETECTED"), 15_000);
  }, [fire]);

  // Price shock: fires after 25s of page dwell without adding to cart
  // or after hovering near the price element 3+ times
  const startPriceShockTimer = useCallback(() => {
    if (priceShockTimer.current) return; // only start once
    priceShockTimer.current = setTimeout(
      () => fire("PRICE_SHOCK_PREDICTED"),
      25_000
    );
  }, [fire]);

  useEffect(() => {
    // ── Return visit ────────────────────────────────────────────
    const seenKey = `nl_seen_${productId}`;
    const seen = sessionStorage.getItem(seenKey);
    if (seen) {
      fire("RETURN_VISIT_DETECTED");
    } else {
      sessionStorage.setItem(seenKey, "1");
    }

    // ── Start price shock timer on page load ─────────────────
    startPriceShockTimer();

    // ── Exit intent (cursor near top of viewport) ────────────
    const onMouseMove = (e: MouseEvent) => {
      resetIdle();

      // Price hover: track mouse near mid-page (where price typically lives)
      // viewport height 30–60% = price zone heuristic
      const midZone = window.innerHeight * 0.6;
      if (e.clientY < midZone && e.clientY > window.innerHeight * 0.2) {
        priceHoverCount.current += 1;
        if (priceHoverCount.current >= 3) {
          // Clear slow timer — they're already showing price interest
          if (priceShockTimer.current) {
            clearTimeout(priceShockTimer.current);
            priceShockTimer.current = null;
          }
          fire("PRICE_SHOCK_PREDICTED");
        }
      }

      if (e.clientY < 10 && e.movementY < 0) {
        fire("EXIT_INTENT_DETECTED");
      }
    };

    // ── Idle timer ────────────────────────────────────────────
    const onActivity = () => resetIdle();

    // ── Price copy ────────────────────────────────────────────
    const onCopy = () => fire("PRICE_COPY_DETECTED");

    // ── Mobile scroll bounce ──────────────────────────────────
    const onTouchMove = (e: TouchEvent) => {
      const y = e.touches[0].clientY;
      const now = Date.now();
      const deltaY = y - lastTouchY.current;
      const deltaT = now - lastTouchTime.current;
      if (deltaY > 150 && deltaT < 300) {
        fire("SCROLL_BOUNCE_DETECTED");
      }
      lastTouchY.current = y;
      lastTouchTime.current = now;
    };

    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("scroll", onActivity);
    document.addEventListener("keydown", onActivity);
    document.addEventListener("copy", onCopy);
    document.addEventListener("touchmove", onTouchMove);
    resetIdle();

    return () => {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("scroll", onActivity);
      document.removeEventListener("keydown", onActivity);
      document.removeEventListener("copy", onCopy);
      document.removeEventListener("touchmove", onTouchMove);
      if (idleTimer.current) clearTimeout(idleTimer.current);
      if (priceShockTimer.current) clearTimeout(priceShockTimer.current);
    };
  }, [productId, fire, resetIdle, startPriceShockTimer]);

  // ── Cart stall (60s after add-to-cart) ───────────────────────
  useEffect(() => {
    if (!cartHasItem) return;
    cartStallTimer.current = setTimeout(
      () => fire("CART_STALL_DETECTED"),
      60_000
    );
    return () => {
      if (cartStallTimer.current) clearTimeout(cartStallTimer.current);
    };
  }, [cartHasItem, fire]);

  // ── Checkout drop (30s on payment page without action) ───────
  useEffect(() => {
    if (!onCheckoutPage) return;
    checkoutDropTimer.current = setTimeout(
      () => fire("CHECKOUT_DROP_DETECTED"),
      30_000
    );
    return () => {
      if (checkoutDropTimer.current) clearTimeout(checkoutDropTimer.current);
    };
  }, [onCheckoutPage, fire]);

  // ── EMI dwell (Intersection Observer on EMI section) ─────────
  const observeEmiSection = useCallback(
    (el: HTMLElement | null) => {
      if (!el) return;
      let dwellTimer: ReturnType<typeof setTimeout> | null = null;
      const observer = new IntersectionObserver(
        ([entry]) => {
          if (entry.isIntersecting) {
            dwellTimer = setTimeout(() => fire("EMI_DWELL_DETECTED"), 10_000);
          } else {
            if (dwellTimer) clearTimeout(dwellTimer);
          }
        },
        { threshold: 0.5 }
      );
      observer.observe(el);
      return () => observer.disconnect();
    },
    [fire]
  );

  const onWishlistAdd = useCallback(
    () => fire("WISHLIST_INSTEAD_OF_CART"),
    [fire]
  );

  return { observeEmiSection, onWishlistAdd };
}
