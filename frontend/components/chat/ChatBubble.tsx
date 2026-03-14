"use client";
import { motion } from "framer-motion";
import { EMICard } from "@/components/emi/EMICard";
import { StackedDealCard } from "@/components/emi/StackedDealCard";
import { TenureSlider } from "@/components/emi/TenureSlider";
import { PaymentOptions } from "@/components/payment/PaymentOptions";
import { ProductCard } from "@/components/shared/ProductCard";
import type {
  ChatMessage,
  EMIScheme,
  StackedDeal,
  PaymentOptions as POData,
  AccessoryUpsell,
} from "@/lib/types";
import { cn } from "@/lib/utils";

interface ChatBubbleProps {
  message: ChatMessage;
  onSelectEMI?: (scheme: EMIScheme) => void;
  onClaimDeal?: () => void;
}

export function ChatBubble({ message, onSelectEMI, onClaimDeal }: ChatBubbleProps) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 12, y: 4 }}
        animate={{ opacity: 1, x: 0, y: 0 }}
        transition={{ type: "spring", stiffness: 400, damping: 30 }}
        className="flex justify-end"
      >
        <div
          className={cn(
            "max-w-[82%] px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm font-medium shadow-sm",
            "bg-pine-500 text-white"
          )}
        >
          {message.content}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -12, y: 4 }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{ type: "spring", stiffness: 400, damping: 30 }}
      className="flex flex-col gap-2 max-w-[94%]"
    >
      {/* Text content */}
      {message.content && (
        <div
          className={cn(
            "px-4 py-2.5 bg-white border border-gray-100 rounded-2xl rounded-tl-sm",
            "text-sm text-gray-800 shadow-sm leading-relaxed"
          )}
        >
          {message.isStreaming ? (
            <span>
              {message.content}
              <motion.span
                className="inline-block w-0.5 h-4 bg-pine-500 ml-0.5 align-middle"
                animate={{ opacity: [1, 0, 1] }}
                transition={{ repeat: Infinity, duration: 0.7 }}
              />
            </span>
          ) : (
            message.content
          )}
        </div>
      )}

      {/* Rich content: EMI schemes */}
      {message.contentType === "emi_schemes" && message.data && (
        <div className="space-y-2">
          {(
            (message.data as unknown as { emi_schemes: EMIScheme[] }).emi_schemes ??
            (message.data as EMIScheme[])
          )
            ?.slice(0, 4)
            .map((scheme: EMIScheme) => (
              <EMICard
                key={scheme.scheme_id}
                scheme={scheme}
                onSelect={onSelectEMI ?? (() => {})}
              />
            ))}
          <TenureSlider
            principalPaisa={
              (message.data as unknown as { amount_in_paisa: number }).amount_in_paisa ??
              8499900
            }
            onSelectTenure={() => {}}
          />
        </div>
      )}

      {/* Rich content: Stacked deal */}
      {message.contentType === "stacked_deal" && message.data && (
        <StackedDealCard
          deal={message.data as StackedDeal}
          onClaim={onClaimDeal ?? (() => {})}
        />
      )}

      {/* Rich content: Payment options */}
      {message.contentType === "payment_options" && message.data && (
        <div className="bg-white border border-gray-100 rounded-2xl rounded-tl-sm p-3 shadow-sm">
          <PaymentOptions data={message.data as POData} />
        </div>
      )}

      {/* Rich content: Accessory upsell */}
      {message.contentType === "accessory_upsell" && message.data && (
        <ProductCard
          accessory={message.data as AccessoryUpsell}
          onAdd={() => {}}
        />
      )}
    </motion.div>
  );
}
