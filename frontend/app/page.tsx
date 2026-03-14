"use client";
import { useState, useCallback, useMemo } from "react";
import { motion } from "framer-motion";
import { AnimatePresence } from "framer-motion";
import { ChevronRight, Search } from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Navbar } from "@/components/layout/Navbar";
import { ChatWidget } from "@/components/chat/ChatWidget";
import { SocialProofBadge } from "@/components/shared/SocialProofBadge";
import { ProductImageCard } from "@/components/product/ProductImageCard";
import { ProductDetails } from "@/components/product/ProductDetails";
import { SpecsTable } from "@/components/product/SpecsTable";
import { useHesitationDetection } from "@/hooks/useHesitationDetection";
import { PRODUCTS, type ProductId } from "@/lib/data/products";
import type { SignalType } from "@/lib/types";
import { cn } from "@/lib/utils";

export default function ProductPage() {
  const [activeProductId, setActiveProductId] = useState<ProductId>("DELL-XPS-15");
  const [cartHasItem, setCartHasItem] = useState(false);
  const [addedToCart, setAddedToCart] = useState<Set<ProductId>>(new Set());
  const [wishlist, setWishlist] = useState<Set<ProductId>>(new Set());
  const [triggerSignal, setTriggerSignal] = useState<SignalType | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [search, setSearch] = useState("");

  const visibleProducts = useMemo(() => {
    if (!search.trim()) return PRODUCTS;
    const q = search.toLowerCase();
    return PRODUCTS.filter(
      (p) =>
        p.name.toLowerCase().includes(q) ||
        p.tab.toLowerCase().includes(q) ||
        p.tags.some((t) => t.toLowerCase().includes(q))
    );
  }, [search]);

  const product = PRODUCTS.find((p) => p.id === activeProductId)!;

  const handleSignal = useCallback((signal: SignalType) => setTriggerSignal(signal), []);
  const handleOpenChat = useCallback(() => setChatOpen(true), []);

  const { observeEmiSection, onWishlistAdd } = useHesitationDetection({
    productId: activeProductId,
    onSignal: handleSignal,
    onOpenChat: handleOpenChat,
    cartHasItem,
  });

  const handleAddToCart = () => {
    setAddedToCart((prev) => new Set([...prev, activeProductId]));
    setCartHasItem(true);
  };

  const handleWishlist = () => {
    setWishlist((prev) => {
      const next = new Set(prev);
      if (next.has(activeProductId)) {
        next.delete(activeProductId);
      } else {
        next.add(activeProductId);
        onWishlistAdd();
      }
      return next;
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar cartCount={addedToCart.size} />

      {/* Breadcrumb */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3">
        <div className="flex items-center gap-1 text-xs text-gray-400">
          {["Home", "Laptops", "Dell", product.name].map((crumb, i, arr) => (
            <span key={crumb} className="flex items-center gap-1">
              <span className={cn(i === arr.length - 1 ? "text-gray-600 font-medium" : "hover:text-gray-600 cursor-pointer")}>
                {crumb}
              </span>
              {i < arr.length - 1 && <ChevronRight className="w-3 h-3 text-gray-300" />}
            </span>
          ))}
        </div>
      </div>

      {/* Product tabs */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 pb-16">
        <Tabs
          value={activeProductId}
          onValueChange={(v) => setActiveProductId(v as ProductId)}
          className="space-y-8"
        >
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <TabsList className="bg-white border border-gray-200 p-1 rounded-2xl shadow-sm h-auto flex-wrap gap-1 flex-1">
              {visibleProducts.length > 0 ? visibleProducts.map((p) => (
                <TabsTrigger
                  key={p.id}
                  value={p.id}
                  className="rounded-xl text-sm font-medium data-[state=active]:bg-pine-500 data-[state=active]:text-white data-[state=active]:shadow-sm px-4 py-2"
                >
                  {p.tab}
                </TabsTrigger>
              )) : (
                <span className="px-4 py-2 text-sm text-gray-400">No products match</span>
              )}
            </TabsList>
            <div className="relative shrink-0">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400 pointer-events-none" />
              <input
                type="text"
                placeholder="Search products..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-8 pr-3 py-2 text-sm bg-white border border-gray-200 rounded-xl shadow-sm focus:outline-none focus:border-pine-400 focus:ring-1 focus:ring-pine-400 w-44 transition-all"
              />
            </div>
          </div>

          {PRODUCTS.map((p) => (
            <TabsContent key={p.id} value={p.id}>
              <AnimatePresence mode="wait">
                <motion.div
                  key={p.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.2 }}
                  className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12"
                >
                  <ProductImageCard productId={p.id} />
                  <ProductDetails
                    product={p}
                    isInCart={addedToCart.has(p.id)}
                    isWishlisted={wishlist.has(p.id)}
                    observeEmiSection={observeEmiSection}
                    onAddToCart={handleAddToCart}
                    onWishlist={handleWishlist}
                    onOpenChat={handleOpenChat}
                    onEmiClick={() => {
                      setTriggerSignal("EMI_DWELL_DETECTED");
                      setChatOpen(true);
                    }}
                  />
                </motion.div>
              </AnimatePresence>
              <SpecsTable specs={p.specs} />
            </TabsContent>
          ))}
        </Tabs>

        {/* Savings ticker */}
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-8 flex items-center justify-center"
        >
          <motion.div
            animate={{ scale: [1, 1.015, 1] }}
            transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-amber-50 border border-amber-200 rounded-full shadow-sm"
          >
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse flex-shrink-0" />
            <span className="text-xs font-semibold text-amber-800">
              TechMart customers saved <span className="text-amber-600">₹14.2L</span> with Priya this week
            </span>
          </motion.div>
        </motion.div>

        {/* Social proof bar */}
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mt-4 bg-white border border-gray-100 rounded-2xl p-4 flex items-center justify-between shadow-sm"
        >
          <SocialProofBadge />
          <button
            onClick={handleOpenChat}
            className="flex items-center gap-1.5 text-sm font-bold text-pine-600 hover:text-pine-700 transition-colors"
          >
            Get my deal
            <ChevronRight className="w-4 h-4" />
          </button>
        </motion.div>
      </div>

      <ChatWidget
        productId={product.id}
        productName={product.name}
        amountPaisa={product.price_paisa}
        triggerSignal={triggerSignal}
        forceOpen={chatOpen}
      />
    </div>
  );
}
