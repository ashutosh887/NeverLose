"use client";
import { motion } from "framer-motion";
import { ShoppingCart, Zap } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import config from "@/config";

interface NavbarProps {
  cartCount: number;
}

export function Navbar({ cartCount }: NavbarProps) {
  return (
    <nav className="bg-white/95 backdrop-blur-md border-b border-gray-200/80 sticky top-0 z-40 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-pine-500 rounded-xl flex items-center justify-center shadow-sm">
            <Zap className="w-4 h-4 text-white" />
          </div>
          <span className="font-extrabold text-gray-900 text-lg tracking-tight">
            {config.storeName}
          </span>
          <Separator orientation="vertical" className="h-4 mx-1" />
          <span className="hidden sm:inline-flex items-center gap-1 text-xs text-gray-500 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-pine-400" />
            Powered by Pine Labs
          </span>
        </div>

        <div className="hidden md:flex items-center gap-6">
          {config.navLinks.map((item) => (
            <span
              key={item}
              className="text-sm text-gray-500 hover:text-gray-900 cursor-pointer transition-colors font-medium"
            >
              {item}
            </span>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <button className="relative p-2 hover:bg-gray-100 rounded-xl transition-colors">
            <ShoppingCart className="w-5 h-5 text-gray-700" />
            {cartCount > 0 && (
              <motion.span
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-pine-500 text-white text-[9px] rounded-full flex items-center justify-center font-bold shadow-sm"
              >
                {cartCount}
              </motion.span>
            )}
          </button>
        </div>
      </div>
    </nav>
  );
}
