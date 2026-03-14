"use client";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingCart, Heart, Star, Shield, Truck, Package, ChevronRight, ExternalLink, Check } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { Product } from "@/lib/data/products";
import { cn } from "@/lib/utils";

const TRUST_BADGES = [
  { icon: Shield, label: "1-Year Warranty", sub: "Manufacturer certified" },
  { icon: Truck, label: "Free Delivery", sub: "By tomorrow" },
  { icon: Package, label: "Same-Day EMI", sub: "Instant approval" },
] as const;

interface ProductDetailsProps {
  product: Product;
  isInCart: boolean;
  isWishlisted: boolean;
  observeEmiSection: (el: HTMLElement | null) => void;
  onAddToCart: () => void;
  onWishlist: () => void;
  onOpenChat: () => void;
  onEmiClick: () => void;
}

export function ProductDetails({
  product: p,
  isInCart,
  isWishlisted,
  observeEmiSection,
  onAddToCart,
  onWishlist,
  onOpenChat,
  onEmiClick,
}: ProductDetailsProps) {
  return (
    <div className="space-y-5">
      {/* Title + badges */}
      <div>
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          {p.tags.map((tag) => (
            <Badge
              key={tag}
              variant="secondary"
              className={cn(
                "text-[10px] font-bold uppercase tracking-wide px-2 py-0.5",
                tag === "BESTSELLER" || tag === "HOT DEAL"
                  ? "bg-pine-100 text-pine-700 border-pine-200"
                  : tag === "LIMITED OFFER"
                  ? "bg-amber-100 text-amber-700 border-amber-200"
                  : "bg-blue-100 text-blue-700 border-blue-200"
              )}
            >
              {tag}
            </Badge>
          ))}
        </div>
        <h1 className="text-2xl font-extrabold text-gray-900 leading-tight">{p.name}</h1>
        <p className="text-sm text-gray-500 mt-1.5 leading-relaxed">{p.subtitle}</p>
      </div>

      {/* Rating */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-0.5">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className={cn(
                "w-4 h-4",
                i < Math.floor(p.rating)
                  ? "text-amber-400 fill-amber-400"
                  : i < p.rating
                  ? "text-amber-300 fill-amber-300"
                  : "text-gray-200 fill-gray-200"
              )}
            />
          ))}
        </div>
        <span className="text-sm font-bold text-gray-700">{p.rating}</span>
        <span className="text-xs text-gray-400">
          ({p.review_count.toLocaleString("en-IN")} reviews)
        </span>
      </div>

      {/* Price + EMI block */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 space-y-3">
        <div className="flex items-baseline gap-3 flex-wrap">
          <span className="text-3xl font-extrabold text-gray-900 tracking-tight">
            {p.price_display}
          </span>
          <span className="text-base text-gray-400 line-through font-normal">
            {p.original_price_display}
          </span>
          <span className="text-sm font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-lg border border-green-100">
            {p.discount_display}
          </span>
        </div>
        <p className="text-xs text-gray-400">Inclusive of all taxes · Free delivery</p>
        <Separator />
        <div
          ref={(el) => observeEmiSection(el)}
          className="flex items-start justify-between gap-3"
        >
          <div>
            <p className="text-sm text-gray-700">
              <span className="font-bold text-pine-600">{p.emi_from}/month</span>
              <span className="text-gray-400"> · No-Cost EMI available</span>
            </p>
            <p className="text-xs text-gray-400 mt-0.5">
              {p.emi_daily}/day — less than your Swiggy order
            </p>
          </div>
          <button
            onClick={onEmiClick}
            className="flex items-center gap-1 text-xs font-semibold text-pine-600 hover:text-pine-700 whitespace-nowrap transition-colors"
          >
            See options
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Highlights */}
      <div>
        <p className="text-sm font-bold text-gray-800 mb-2.5">Highlights</p>
        <ul className="space-y-2">
          {p.highlights.map((h, i) => (
            <li key={i} className="flex items-start gap-2.5 text-sm text-gray-600">
              <span className="w-4 h-4 rounded-full bg-pine-100 border border-pine-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Check className="w-2.5 h-2.5 text-pine-600" strokeWidth={3} />
              </span>
              <span className="leading-relaxed">{h}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Trust badges */}
      <div className="grid grid-cols-3 gap-2.5">
        {TRUST_BADGES.map(({ icon: Icon, label, sub }) => (
          <div
            key={label}
            className="flex flex-col items-center gap-1 p-3 bg-white border border-gray-100 rounded-xl shadow-sm text-center hover:border-pine-200 transition-colors"
          >
            <div className="w-8 h-8 bg-pine-50 rounded-lg flex items-center justify-center border border-pine-100">
              <Icon className="w-4 h-4 text-pine-500" />
            </div>
            <span className="text-[11px] font-semibold text-gray-700 leading-tight">{label}</span>
            <span className="text-[10px] text-gray-400">{sub}</span>
          </div>
        ))}
      </div>

      {/* CTAs */}
      <div className="flex gap-3">
        <Button
          onClick={onAddToCart}
          className="flex-1 h-12 font-bold rounded-xl text-sm shadow-md bg-pine-500 hover:bg-pine-600 shadow-pine-200 transition-all"
        >
          <span className="flex items-center gap-1.5">
            <ShoppingCart className="w-4 h-4" />
            {isInCart ? "Added to Cart" : "Add to Cart"}
          </span>
        </Button>

        <Button
          variant="outline"
          onClick={onWishlist}
          className={cn(
            "w-12 h-12 p-0 rounded-xl border-2 transition-all",
            isWishlisted
              ? "border-red-300 bg-red-50 text-red-500 hover:bg-red-100"
              : "border-gray-200 text-gray-400 hover:border-red-200 hover:bg-red-50 hover:text-red-400"
          )}
        >
          <Heart className={cn("w-5 h-5", isWishlisted && "fill-red-500 text-red-500")} />
        </Button>

        <Button
          variant="outline"
          onClick={onOpenChat}
          className="h-12 px-3 rounded-xl border-2 border-gray-200 text-gray-500 hover:border-pine-300 hover:bg-pine-50 hover:text-pine-600 transition-all"
        >
          <ExternalLink className="w-4 h-4" />
        </Button>
      </div>

      {/* Cart nudge */}
      <AnimatePresence>
        {isInCart && (
          <motion.div
            initial={{ opacity: 0, y: 4, height: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="text-xs text-center text-pine-700 bg-pine-50 border border-pine-200 rounded-xl px-4 py-2.5 font-medium"
          >
            Item in cart · Checkout within 60s for best EMI offers
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
