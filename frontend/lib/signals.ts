import type { SignalType } from "./types";

export const SIGNAL_LABELS: Record<SignalType, string> = {
  EXIT_INTENT_DETECTED: "Exit Intent",
  CART_STALL_DETECTED: "Cart Stall",
  CHECKOUT_DROP_DETECTED: "Checkout Drop",
  RETURN_VISIT_DETECTED: "Return Visit",
  IDLE_DETECTED: "Idle",
  SCROLL_BOUNCE_DETECTED: "Scroll Bounce",
  PRICE_COPY_DETECTED: "Price Copy",
  WISHLIST_INSTEAD_OF_CART: "Wishlist",
  EMI_DWELL_DETECTED: "EMI Dwell",
};

export const SIGNAL_COLORS: Record<SignalType, string> = {
  EXIT_INTENT_DETECTED: "bg-red-100 text-red-700 border-red-200",
  CART_STALL_DETECTED: "bg-orange-100 text-orange-700 border-orange-200",
  CHECKOUT_DROP_DETECTED: "bg-red-100 text-red-700 border-red-200",
  RETURN_VISIT_DETECTED: "bg-blue-100 text-blue-700 border-blue-200",
  IDLE_DETECTED: "bg-yellow-100 text-yellow-700 border-yellow-200",
  SCROLL_BOUNCE_DETECTED: "bg-purple-100 text-purple-700 border-purple-200",
  PRICE_COPY_DETECTED: "bg-teal-100 text-teal-700 border-teal-200",
  WISHLIST_INSTEAD_OF_CART: "bg-pink-100 text-pink-700 border-pink-200",
  EMI_DWELL_DETECTED: "bg-indigo-100 text-indigo-700 border-indigo-200",
};

export const CHANNEL_LABELS: Record<string, string> = {
  web: "Web Checkout",
  whatsapp: "WhatsApp",
  qr: "UPI QR",
  voice: "Voice",
};

export const CHANNEL_COLORS: Record<string, string> = {
  web: "bg-blue-100 text-blue-700",
  whatsapp: "bg-green-100 text-green-700",
  qr: "bg-purple-100 text-purple-700",
  voice: "bg-orange-100 text-orange-700",
};

export function formatInr(paisa: number): string {
  const rupees = Math.floor(paisa / 100);
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(rupees);
}

export function dailyCost(monthlyPaisa: number): string {
  return formatInr(Math.floor(monthlyPaisa / 30));
}
