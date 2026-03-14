export type ProductId =
  | "MBP-16-2024"
  | "DELL-XPS-15"
  | "SAMSUNG-S24"
  | "IPHONE-15-PRO"
  | "SONY-WH1000XM5"
  | "LG-WASHER";

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
    tags: ["BESTSELLER", "IN STOCK"],
    emi_from: "₹11,661",
    emi_daily: "₹389",
    specs: [
      { label: "Display", value: '16.2" Liquid Retina XDR, 120Hz ProMotion, 1000 nits sustained / 1600 nits HDR' },
      { label: "Chip", value: "Apple M4 Pro — 14-core CPU, 20-core GPU, 38-TOPS Neural Engine" },
      { label: "RAM", value: "24GB unified memory (up to 64GB)" },
      { label: "Storage", value: "512GB SSD — up to 7.4 GB/s read" },
      { label: "Battery", value: "100Wh — up to 24 hrs video playback" },
      { label: "Ports", value: "3× Thunderbolt 5 (120 Gbps), HDMI 2.1, SD 4.0, MagSafe 3" },
      { label: "Camera", value: "12MP Center Stage webcam, Studio-quality 3-mic array" },
      { label: "Audio", value: "6-speaker sound system with Spatial Audio" },
      { label: "Weight", value: "2.14 kg" },
    ],
    highlights: [
      "M4 Pro delivers 2× faster AI processing and 40% faster CPU than M3 Pro",
      "Liquid Retina XDR — 1600 nits peak HDR, nano-texture glass option, P3 wide colour",
      "24GB unified memory — run Xcode, Simulator, Figma, and 20 Chrome tabs without breaking a sweat",
      "Thunderbolt 5 — charge two 6K displays and transfer 4K footage at 120 Gbps simultaneously",
      "MagSafe 3 charges at 140W — from 0 to 80% in under 30 minutes",
      "24-hour battery in a 2.14 kg chassis — thinnest MacBook Pro ever made",
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
    tags: ["HOT DEAL", "IN STOCK"],
    emi_from: "₹4,722",
    emi_daily: "₹157",
    specs: [
      { label: "Display", value: '15.6" 3.5K OLED, 120Hz, 100% DCI-P3, 400 nits, HDR500' },
      { label: "Processor", value: "Intel Core Ultra 7 185H — 16-core, up to 5.1 GHz" },
      { label: "Graphics", value: "NVIDIA GeForce RTX 4060 8GB GDDR6 + Intel Arc" },
      { label: "RAM", value: "32GB LPDDR5X 6400 MHz (upgradeable to 64GB)" },
      { label: "Storage", value: "1TB PCIe Gen 4 NVMe SSD — up to 7,400 MB/s" },
      { label: "Battery", value: "86Wh, 130W MagSafe USB-C adapter" },
      { label: "Ports", value: "2× Thunderbolt 4, 1× USB-C 3.2, 1× SD card, 3.5mm jack" },
      { label: "Build", value: "CNC machined aluminium, 1.86 kg, 18mm thin" },
    ],
    highlights: [
      "OLED display with 100% DCI-P3 — colours that make every photo, video and design pop",
      "RTX 4060 handles 4K video editing, 3D rendering and gaming at 60+ fps",
      "Dell AI Studio with Intel AI Boost — on-device AI, privacy-first, no cloud needed",
      "CNC aluminium chassis at just 1.86 kg — the thinnest XPS 15 Dell has ever built",
      "Thunderbolt 4 × 2 — connect 8K displays, docking stations, external GPUs",
      "86Wh battery with fast charge — 80% in 60 minutes from any USB-C wall adapter",
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
      { label: "Display", value: '6.8" QHD+ Dynamic AMOLED 2X, 120Hz, 2600 nits peak' },
      { label: "Processor", value: "Snapdragon 8 Gen 3 for Galaxy — world's fastest mobile chip" },
      { label: "Camera", value: "200MP main + 50MP periscope 5× + 12MP ultrawide + 10MP 3× telephoto" },
      { label: "Front Camera", value: "12MP f/2.2, autofocus, 4K video" },
      { label: "RAM", value: "12GB LPDDR5X" },
      { label: "Storage", value: "256GB UFS 4.0 (up to 1TB)" },
      { label: "Battery", value: "5000mAh, 45W wired, 15W wireless, 4.5W reverse" },
      { label: "Build", value: "Titanium frame, Gorilla Armor 2, IP68" },
    ],
    highlights: [
      "Galaxy AI: live translate calls, circle to search anything on screen, AI photo editing",
      "200MP ProVisual Engine with 100× Space Zoom — moon shots that actually look sharp",
      "Titanium frame — the same alloy used in aerospace; Gorilla Armor 2 glass front",
      "Built-in S Pen with 2.8ms latency — best note-taking experience on any phone",
      "IP68 rated — survived 30 minutes at 1.5m depth; dust proof",
      "45W fast charge + 15W wireless — never worry about battery on a long day",
    ],
  },
  {
    id: "IPHONE-15-PRO",
    tab: "iPhone 15 Pro",
    name: "Apple iPhone 15 Pro Max",
    subtitle: '6.7" Super Retina XDR · A17 Pro · 256GB · Titanium',
    price_paisa: 15999900,
    price_display: "₹1,59,999",
    original_price_display: "₹1,79,900",
    discount_display: "11% off",
    rating: 4.9,
    review_count: 6782,
    tags: ["BESTSELLER", "IN STOCK"],
    emi_from: "₹7,500",
    emi_daily: "₹250",
    specs: [
      { label: "Display", value: '6.7" Super Retina XDR OLED, ProMotion 1–120Hz, 2000 nits' },
      { label: "Chip", value: "Apple A17 Pro — first 3nm chip in a smartphone" },
      { label: "Camera", value: "48MP main f/1.78 + 12MP ultrawide + 12MP 5× periscope telephoto" },
      { label: "Video", value: "4K 60fps ProRes, Log video, Action Button" },
      { label: "Storage", value: "256GB (up to 1TB)" },
      { label: "Battery", value: "4422mAh, 27W fast charge, MagSafe 15W wireless" },
      { label: "Build", value: "Grade 5 titanium frame, textured matte glass back" },
      { label: "Connectivity", value: "USB 3 (40 Gbps), Wi-Fi 6E, Bluetooth 5.3, Thread" },
    ],
    highlights: [
      "A17 Pro chip — 20% faster CPU, 20% faster GPU, and a dedicated ray-tracing unit",
      "Grade 5 titanium frame — stronger than steel, lighter than aluminium",
      "5× optical zoom periscope lens captures detail at 120mm that no Android can match",
      "Action Button: customise it — camera shortcut, flashlight, translation, anything",
      "USB 3 at 40 Gbps — transfer an hour of ProRes 4K in under two minutes",
      "Emergency SOS via satellite and Crash Detection — safety features that matter",
    ],
  },
  {
    id: "SONY-WH1000XM5",
    tab: "Sony XM5",
    name: "Sony WH-1000XM5 Headphones",
    subtitle: "Industry-best ANC · 30-hr battery · Hi-Res Audio · Multipoint",
    price_paisa: 2499000,
    price_display: "₹24,990",
    original_price_display: "₹34,990",
    discount_display: "29% off",
    rating: 4.8,
    review_count: 4210,
    tags: ["LIMITED OFFER", "IN STOCK"],
    emi_from: "₹1,388",
    emi_daily: "₹46",
    specs: [
      { label: "ANC", value: "8 microphones, 2 processors — industry-leading noise cancellation" },
      { label: "Audio", value: "30mm driver, Hi-Res Audio, LDAC (990kbps), DSEE Extreme" },
      { label: "Battery", value: "30 hrs with ANC on; 3-min charge = 3 hrs playback" },
      { label: "Multipoint", value: "Connect 2 devices simultaneously" },
      { label: "Microphone", value: "Beamforming mics + precise voice pickup with AI noise reduction" },
      { label: "Controls", value: "Touch panel, speak-to-chat, quick attention mode" },
      { label: "Weight", value: "250g with headband redesign for all-day wear" },
      { label: "Connectivity", value: "Bluetooth 5.2, NFC, 3.5mm (passive), USB-C" },
    ],
    highlights: [
      "Industry-best ANC with 8 microphones — blocks out flights, offices, construction sites",
      "LDAC codec streams 3× more data than standard Bluetooth — studio-quality on the go",
      "30-hour battery with ANC on; 3-minute quick charge gives 3 hours",
      "Multipoint: answer a call from your laptop while your phone stays connected",
      "Speak-to-Chat pauses audio the moment you start talking — no hands needed",
      "Redesigned 250g headband for 8-hour wear without neck fatigue",
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
      { label: "Washer Capacity", value: "24 kg Front Load — handles a family of 5 in one load" },
      { label: "Dryer Capacity", value: "16 kg Condenser Dryer" },
      { label: "Technology", value: "AI Direct Drive + TurboWash 360° + Steam Clean" },
      { label: "Energy Rating", value: "5 Star BEE Inverter" },
      { label: "Programs", value: "14 wash programs including Allergiene and Baby Care" },
      { label: "Noise", value: "44 dB — quieter than a library" },
      { label: "Smart Home", value: "LG ThinQ Wi-Fi — start, monitor, diagnose remotely" },
      { label: "Warranty", value: "10-year motor warranty, 2-year product warranty" },
    ],
    highlights: [
      "AI Direct Drive detects fabric weight and type — 6 motion patterns adjust automatically",
      "TurboWash 360° — complete a full cycle in just 39 minutes",
      "LG ThinQ app: start wash from office, get cycle-done notifications, diagnose issues remotely",
      "Steam Clean removes 99.9% of allergens and bacteria without harsh chemicals",
      "10-year motor warranty — LG backs it with the longest warranty in the category",
      "44 dB noise level — quieter than a normal conversation; install it anywhere in your home",
    ],
  },
] as const;
