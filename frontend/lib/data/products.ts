export type ProductId = "MBP-16-2024" | "DELL-XPS-15" | "SAMSUNG-S24" | "LG-WASHER";

export interface Product {
  id: ProductId;
  tab: string;
  name: string;
  subtitle: string;
  price_paisa: number;
  price_display: string;
  original_price_display: string;
  discount_display: string;
  rating: number;
  review_count: number;
  tags: readonly string[];
  emi_from: string;
  emi_daily: string;
  specs: readonly { label: string; value: string }[];
  highlights: readonly string[];
}

export const PRODUCTS: readonly Product[] = [
  {
    id: "MBP-16-2024",
    tab: 'MacBook Pro 16"',
    name: 'Apple MacBook Pro 16" (M4 Pro)',
    subtitle: '16.2" Liquid Retina XDR · Apple M4 Pro · 24GB RAM · 512GB SSD',
    price_paisa: 24990000,
    price_display: "₹2,49,900",
    original_price_display: "₹2,79,900",
    discount_display: "11% off",
    rating: 4.9,
    review_count: 3847,
    tags: ["DEMO PRODUCT", "IN STOCK"],
    emi_from: "₹11,661",
    emi_daily: "₹389",
    specs: [
      { label: "Display", value: '16.2" Liquid Retina XDR, 120Hz ProMotion, 1000 nits' },
      { label: "Chip", value: "Apple M4 Pro — 14-core CPU, 20-core GPU" },
      { label: "RAM", value: "24GB unified memory" },
      { label: "Storage", value: "512GB SSD" },
      { label: "Battery", value: "100Wh, up to 24 hrs" },
      { label: "Ports", value: "3× Thunderbolt 5, HDMI, SD, MagSafe 3" },
    ],
    highlights: [
      "M4 Pro delivers 2× faster AI processing than M3 Pro",
      "Liquid Retina XDR — 1600 nits peak HDR, nano-texture option",
      "24GB unified memory — runs Xcode + simulator + browser without breaking a sweat",
      "MagSafe 3 + 3× Thunderbolt 5 — full connectivity, zero dongles needed",
    ],
  },
  {
    id: "DELL-XPS-15",
    tab: "Dell XPS 15",
    name: "Dell XPS 15 (2024)",
    subtitle: '15.6" 3.5K OLED · Intel Core Ultra 7 · RTX 4060 · 32GB RAM',
    price_paisa: 8999900,
    price_display: "₹89,999",
    original_price_display: "₹1,09,999",
    discount_display: "18% off",
    rating: 4.7,
    review_count: 2841,
    tags: ["BESTSELLER", "IN STOCK"],
    emi_from: "₹4,722",
    emi_daily: "₹157",
    specs: [
      { label: "Display", value: '15.6" 3.5K OLED, 120Hz, 100% DCI-P3' },
      { label: "Processor", value: "Intel Core Ultra 7 185H" },
      { label: "Graphics", value: "NVIDIA RTX 4060 8GB GDDR6" },
      { label: "RAM", value: "32GB LPDDR5X 6400MHz" },
      { label: "Storage", value: "1TB PCIe Gen 4 NVMe SSD" },
      { label: "Battery", value: "86Wh, MagSafe 130W Adapter" },
    ],
    highlights: [
      "OLED display with 100% DCI-P3 color gamut — vibrant, true-to-life",
      "Dell AI Studio — on-device AI acceleration, privacy-first",
      "CNC machined aluminum chassis, just 1.86 kg",
      "Thunderbolt 4 × 2, USB-C, SD card reader",
    ],
  },
  {
    id: "SAMSUNG-S24",
    tab: "Galaxy S24 Ultra",
    name: "Samsung Galaxy S24 Ultra",
    subtitle: '6.8" QHD+ AMOLED · Snapdragon 8 Gen 3 · 12GB RAM · 256GB',
    price_paisa: 12999900,
    price_display: "₹1,29,999",
    original_price_display: "₹1,54,999",
    discount_display: "16% off",
    rating: 4.8,
    review_count: 5123,
    tags: ["HOT DEAL", "IN STOCK"],
    emi_from: "₹6,111",
    emi_daily: "₹204",
    specs: [
      { label: "Display", value: '6.8" QHD+ AMOLED, 120Hz, 2600 nits' },
      { label: "Processor", value: "Snapdragon 8 Gen 3 for Galaxy" },
      { label: "Camera", value: "200MP + 50MP + 12MP + 10MP" },
      { label: "RAM", value: "12GB LPDDR5X" },
      { label: "Storage", value: "256GB UFS 4.0" },
      { label: "Battery", value: "5000mAh, 45W fast charge" },
    ],
    highlights: [
      "Galaxy AI on-device — live translate, circle to search, edit suggestions",
      "200MP ProVisual Engine with optical 5x zoom",
      "Titanium frame, Corning Gorilla Armor 2",
      "IP68 water resistant, S Pen included",
    ],
  },
  {
    id: "LG-WASHER",
    tab: "LG WashTower",
    name: "LG WashTower (2024)",
    subtitle: "24kg Washer · 16kg Dryer · AI Direct Drive · Inverter",
    price_paisa: 4599900,
    price_display: "₹45,999",
    original_price_display: "₹59,999",
    discount_display: "23% off",
    rating: 4.5,
    review_count: 1230,
    tags: ["LIMITED OFFER", "IN STOCK"],
    emi_from: "₹2,167",
    emi_daily: "₹72",
    specs: [
      { label: "Washer Capacity", value: "24 kg Front Load" },
      { label: "Dryer Capacity", value: "16 kg Condenser Dryer" },
      { label: "Technology", value: "AI Direct Drive + TurboWash 360°" },
      { label: "Energy Rating", value: "5 Star Inverter" },
      { label: "Programs", value: "14 wash programs" },
      { label: "Noise", value: "44 dB — whisper quiet" },
    ],
    highlights: [
      "AI Direct Drive learns fabric type and adjusts wash motion",
      "TurboWash 360° — complete cycle in 39 minutes",
      "LG ThinQ app — start, monitor, diagnose remotely",
      "10-year motor warranty — industry leading",
    ],
  },
] as const;
