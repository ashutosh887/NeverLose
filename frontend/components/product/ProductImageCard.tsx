"use client";
import { motion } from "framer-motion";
import { Laptop, Smartphone, Wind, Package, Zap, Headphones } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ProductId } from "@/lib/data/products";

const PRODUCT_ICONS: Record<ProductId, React.ElementType> = {
  "MBP-16-2024": Laptop,
  "DELL-XPS-15": Laptop,
  "SAMSUNG-S24": Smartphone,
  "IPHONE-15-PRO": Smartphone,
  "SONY-WH1000XM5": Headphones,
  "LG-WASHER": Wind,
};

const THUMBNAIL_ICONS = [Package, Zap];

interface ProductImageCardProps {
  productId: ProductId;
}

export function ProductImageCard({ productId }: ProductImageCardProps) {
  const Icon = PRODUCT_ICONS[productId];

  return (
    <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="flex flex-col items-center justify-center p-10 min-h-[360px] bg-gradient-to-br from-gray-50 to-white">
        <motion.div
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
          className="mb-6"
        >
          <Icon className="w-32 h-32 text-gray-300" strokeWidth={1} />
        </motion.div>
        <div className="flex gap-2">
          <button className="w-12 h-12 bg-white border border-pine-400 shadow-sm shadow-pine-100 rounded-xl flex items-center justify-center transition-all">
            <Icon className="w-5 h-5 text-pine-500" />
          </button>
          {THUMBNAIL_ICONS.map((TIcon, i) => (
            <button
              key={i}
              className="w-12 h-12 bg-white border border-gray-200 hover:border-gray-300 rounded-xl flex items-center justify-center transition-all"
            >
              <TIcon className="w-5 h-5 text-gray-400" />
            </button>
          ))}
        </div>
      </div>
      <div className="px-5 py-3 border-t border-gray-100 flex items-center justify-between bg-gradient-to-r from-pine-50 to-white">
        <span className="text-xs text-gray-500 font-medium">Sold by TechMart</span>
        <span className={cn(
          "inline-flex items-center gap-1 text-[10px] font-semibold text-pine-600",
          "bg-pine-100 px-2 py-0.5 rounded-full border border-pine-200"
        )}>
          <Zap className="w-2.5 h-2.5" />
          Pine Labs Verified
        </span>
      </div>
    </div>
  );
}
