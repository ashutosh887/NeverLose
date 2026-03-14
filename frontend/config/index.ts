const config = {
  appName: "NeverLose",
  appDescription:
    "The AI Agent That Converts Every Hesitant Buyer Into a Paying Customer",
  appKeywords: [
    "Pine Labs",
    "EMI",
    "cart abandonment",
    "AI",
    "payments",
    "hackathon",
  ],
  storeName: "TechMart",
  navLinks: ["Laptops", "Mobiles", "Appliances", "Offers"],
  backendUrl: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000",
  wsUrl: process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000/ws/chat",
};

export default config;
