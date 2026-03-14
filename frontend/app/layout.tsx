import type { Metadata } from "next";
import { Poppins } from "next/font/google";
import "./globals.css";
import config from "@/config";

const poppins = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800"],
  variable: "--font-poppins",
  display: "swap",
});

export const metadata: Metadata = {
  title: `${config.appName} — ${config.appDescription}`,
  description:
    "AI-powered cart abandonment recovery built for the Pine Labs Hackathon. Detects buyer hesitation in real-time and presents stacked EMI + offer deals before customers leave.",
  keywords: config.appKeywords,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={poppins.variable}>
      <body className="min-h-screen bg-background font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
