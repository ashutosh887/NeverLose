// ─── Shared TypeScript types for NeverLose frontend ───────────────

export type SignalType =
  | "EXIT_INTENT_DETECTED"
  | "CART_STALL_DETECTED"
  | "CHECKOUT_DROP_DETECTED"
  | "RETURN_VISIT_DETECTED"
  | "IDLE_DETECTED"
  | "SCROLL_BOUNCE_DETECTED"
  | "PRICE_COPY_DETECTED"
  | "WISHLIST_INSTEAD_OF_CART"
  | "EMI_DWELL_DETECTED";

export type MessageContentType =
  | "text"
  | "emi_schemes"
  | "stacked_deal"
  | "payment_options"
  | "qr_code"
  | "accessory_upsell";

export interface EMIScheme {
  bank_name: string;
  bank_code: string;
  card_type: string;
  tenure_months: number;
  annual_rate_percent: number;
  is_no_cost: boolean;
  label: string;
  badge?: string | null;
  scheme_id: string;
  monthly_installment_paisa: number;
  monthly_installment_display: string;
  daily_cost_paisa: number;
  daily_cost_display: string;
  total_interest_paisa: number;
  eligibility?: string;
}

export interface Offer {
  offer_id: string;
  offer_name: string;
  offer_type: string;
  discount_amount_paisa?: number;
  discount_percentage?: number;
  max_discount_paisa?: number;
  is_stackable: boolean;
  description: string;
}

export interface AppliedOffer {
  offer_id: string;
  offer_name: string;
  type: string;
  saving_paisa: number;
  saving_display: string;
}

export interface StackedDeal {
  original_amount_paisa: number;
  original_amount_display: string;
  net_price_paisa: number;
  net_price_display: string;
  total_discount_paisa: number;
  total_discount_display: string;
  cashback_paisa: number;
  cashback_display: string;
  total_savings_paisa: number;
  total_savings_display: string;
  applied_offers: AppliedOffer[];
  emi_on_net_price: EMIScheme;
  headline: string;
  savings_line: string;
}

export interface PaymentOptions {
  order_id: string;
  checkout_url?: string;
  payment_link?: {
    payment_link_url: string;
    whatsapp_url: string;
    whatsapp_message: string;
  };
  qr?: {
    upi_string: string;
    qr_image_base64: string;
    amount_paisa: number;
  };
}

export interface AccessoryUpsell {
  id: string;
  name: string;
  price_paisa: number;
  image: string;
  incremental_monthly_paisa: number;
  incremental_monthly_display: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  contentType: MessageContentType;
  data?: StackedDeal | EMIScheme[] | PaymentOptions | AccessoryUpsell | null;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ConversionEvent {
  id: string;
  timestamp: string;
  product: string;
  product_id: string;
  amount_paisa: number;
  amount_display: string;
  emi_scheme: {
    bank: string;
    tenure_months: number;
    monthly_display: string;
    is_no_cost: boolean;
  };
  channel: "web" | "whatsapp" | "qr" | "voice";
  signal: SignalType;
  pine_labs_products: string[];
  customer_city: string;
}

export interface DashboardSeed {
  total_weekly: {
    saves: number;
    gmv_recovered_paisa: number;
    gmv_recovered_display: string;
    avg_emi_tenure_months: number;
    top_product: string;
    top_pine_labs_product: string;
    channel_breakdown: Record<string, number>;
  };
  daily_summary: Array<{
    date: string;
    saves: number;
    gmv_recovered_paisa: number;
    gmv_recovered_display: string;
    top_signal: string;
  }>;
  recent_conversions: ConversionEvent[];
}
