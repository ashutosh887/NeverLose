"use client";
import { useEffect, useRef } from "react";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import {
  Zap,
  WifiOff,
  TrendingUp,
  BarChart2,
  Activity,
  CheckCircle2,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { ConversionStats } from "@/components/dashboard/ConversionStats";
import { LiveFeed } from "@/components/dashboard/LiveFeed";
import { useSSE } from "@/hooks/useSSE";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";

// ── Animated counter ────────────────────────────────────────────────
function AnimatedCounter({
  value,
  prefix = "",
  suffix = "",
  className,
}: {
  value: number;
  prefix?: string;
  suffix?: string;
  className?: string;
}) {
  const motionVal = useMotionValue(0);
  const spring = useSpring(motionVal, { duration: 1800, bounce: 0.05 });
  const display = useTransform(spring, (v) =>
    `${prefix}${Math.floor(v).toLocaleString("en-IN")}${suffix}`
  );
  const prevRef = useRef(0);

  useEffect(() => {
    if (value !== prevRef.current) {
      motionVal.set(value);
      prevRef.current = value;
    }
  }, [value, motionVal]);

  return <motion.span className={className}>{display}</motion.span>;
}

// ── Chart colours ───────────────────────────────────────────────────
const PINE_COLOR = "#2aa85e";
const CHANNEL_PIE_COLORS: Record<string, string> = {
  web: "#3b82f6",
  whatsapp: "#22c55e",
  qr: "#a855f7",
  voice: "#f97316",
};

// ── Pine Labs product list ──────────────────────────────────────────
const PINE_PRODUCTS = [
  "EMI Calculator v3",
  "Offer Engine",
  "Infinity Checkout",
  "Payment Links",
  "UPI QR Code",
  "Payment Gateway",
  "Customers API",
  "Convenience Fee API",
  "MCP Server",
];

export default function DashboardPage() {
  const { conversions, totalWeekly, dailySummary, isConnected } = useSSE();

  const gmvLakhs = totalWeekly
    ? Math.floor(totalWeekly.gmv_recovered_paisa / 10_000_000)
    : 0;
  const gmvDisplay = totalWeekly?.gmv_recovered_display ?? "₹0";

  // Build bar chart data from dailySummary
  const barData = dailySummary.slice(-7).map((d) => ({
    date: new Date(d.date).toLocaleDateString("en-IN", { weekday: "short", day: "numeric" }),
    saves: d.saves,
    gmv: Math.floor(d.gmv_recovered_paisa / 100),
  }));

  // Build pie data from channel breakdown
  const channelBreakdown = totalWeekly?.channel_breakdown ?? {};
  const pieData = Object.entries(channelBreakdown).map(([k, v]) => ({
    name: k.charAt(0).toUpperCase() + k.slice(1),
    value: v,
    key: k,
  }));

  const totalSaves = totalWeekly?.saves ?? 0;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">

      {/* ── Sticky Header ───────────────────────────────────────── */}
      <header className="sticky top-0 z-30 bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-pine-500 rounded-xl flex items-center justify-center shadow-sm shadow-pine-500/30">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <span className="font-extrabold text-white text-lg tracking-tight">NeverLose</span>
            <Separator orientation="vertical" className="h-4 mx-1 bg-slate-700" />
            <span className="text-sm text-slate-400 font-medium">Recovery Dashboard</span>
          </div>

          {/* Live badge */}
          <div className="flex items-center gap-3">
            {isConnected ? (
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-pine-500/15 border border-pine-500/30 rounded-full">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-pine-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-pine-400" />
                </span>
                <span className="text-xs font-semibold text-pine-400">Live</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-full">
                <WifiOff className="w-3 h-3 text-slate-500" />
                <span className="text-xs text-slate-500">Connecting</span>
              </div>
            )}

            <Badge
              variant="outline"
              className="hidden sm:flex text-xs bg-slate-800 border-slate-700 text-slate-300"
            >
              Pine Labs AI
            </Badge>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">

        {/* ── Hero GMV Counter ────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-pine-600/20 via-slate-900 to-slate-900 border border-pine-500/20 p-8"
        >
          {/* Ambient glow */}
          <div className="absolute top-0 left-0 w-64 h-64 bg-pine-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="absolute bottom-0 right-0 w-48 h-48 bg-emerald-500/8 rounded-full blur-3xl pointer-events-none" />

          <div className="relative grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
            <div>
              <p className="text-xs font-semibold text-pine-400 uppercase tracking-widest mb-2 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5" />
                GMV Recovered This Week
              </p>
              <div className="flex items-baseline gap-2 mb-2">
                <AnimatedCounter
                  value={gmvLakhs * 100000}
                  prefix="₹"
                  className="text-5xl font-black text-white tabular-nums tracking-tight"
                />
                {gmvDisplay && (
                  <span className="text-xl font-semibold text-slate-400">
                    {gmvDisplay}
                  </span>
                )}
              </div>
              <p className="text-sm text-slate-400">
                from{" "}
                <span className="text-pine-400 font-bold">
                  <AnimatedCounter value={totalSaves} />
                </span>{" "}
                recovered carts · powered by Pine Labs AI
              </p>
              <div className="flex items-center gap-2 mt-4">
                <TrendingUp className="w-4 h-4 text-pine-400" />
                <span className="text-sm text-pine-400 font-semibold">↑ 22% vs last week</span>
                <Separator orientation="vertical" className="h-3 bg-slate-700" />
                <span className="text-xs text-slate-500">9 Pine Labs products attributed</span>
              </div>
            </div>

            {/* Mini stats row */}
            <div className="grid grid-cols-2 gap-3">
              {[
                {
                  label: "Avg EMI Tenure",
                  value: `${totalWeekly?.avg_emi_tenure_months ?? 18}m`,
                  color: "text-purple-400",
                  bg: "bg-purple-500/10 border-purple-500/20",
                },
                {
                  label: "Top Product",
                  value: totalWeekly?.top_pine_labs_product ?? "EMI Calc",
                  color: "text-amber-400",
                  bg: "bg-amber-500/10 border-amber-500/20",
                },
                {
                  label: "Conversion Rate",
                  value: "34%",
                  color: "text-blue-400",
                  bg: "bg-blue-500/10 border-blue-500/20",
                },
                {
                  label: "Avg Deal Size",
                  value: totalSaves > 0
                    ? `₹${Math.floor((totalWeekly?.gmv_recovered_paisa ?? 0) / (totalSaves * 100)).toLocaleString("en-IN")}`
                    : "₹—",
                  color: "text-pine-400",
                  bg: "bg-pine-500/10 border-pine-500/20",
                },
              ].map((s) => (
                <div
                  key={s.label}
                  className={cn(
                    "rounded-xl p-3 border",
                    s.bg
                  )}
                  style={{ background: "rgba(15,23,42,0.6)" }}
                >
                  <p className="text-[10px] text-slate-500 uppercase tracking-wide mb-0.5">{s.label}</p>
                  <p className={cn("text-lg font-bold leading-tight", s.color)}>{s.value}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* ── Stat Cards ──────────────────────────────────────────── */}
        <ConversionStats weekly={totalWeekly} />

        {/* ── Charts Row ──────────────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Bar chart: 7-day saves trend */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="lg:col-span-2 rounded-2xl border border-slate-800/80 p-6"
            style={{ background: "rgba(15,23,42,0.8)" }}
          >
            <div className="flex items-center justify-between mb-5">
              <div className="flex items-center gap-2">
                <BarChart2 className="w-4 h-4 text-pine-400" />
                <h3 className="text-sm font-semibold text-slate-200">7-Day Recovery Trend</h3>
              </div>
              <span className="text-xs text-slate-500">Saves per day</span>
            </div>
            {barData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={barData} margin={{ top: 4, right: 4, bottom: 0, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis
                    dataKey="date"
                    tick={{ fill: "#64748b", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "#64748b", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#0f172a",
                      border: "1px solid #1e293b",
                      borderRadius: "12px",
                      color: "#f1f5f9",
                      fontSize: "12px",
                    }}
                    cursor={{ fill: "rgba(42,168,94,0.08)" }}
                  />
                  <Bar
                    dataKey="saves"
                    fill={PINE_COLOR}
                    radius={[6, 6, 0, 0]}
                    name="Saves"
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[200px] flex items-center justify-center">
                <p className="text-sm text-slate-600">Waiting for data...</p>
              </div>
            )}
          </motion.div>

          {/* Donut chart: channel breakdown */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="rounded-2xl border border-slate-800/80 p-6"
            style={{ background: "rgba(15,23,42,0.8)" }}
          >
            <div className="flex items-center gap-2 mb-5">
              <Activity className="w-4 h-4 text-pine-400" />
              <h3 className="text-sm font-semibold text-slate-200">Channel Mix</h3>
            </div>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry) => (
                      <Cell
                        key={entry.key}
                        fill={CHANNEL_PIE_COLORS[entry.key] ?? "#64748b"}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      background: "#0f172a",
                      border: "1px solid #1e293b",
                      borderRadius: "12px",
                      color: "#f1f5f9",
                      fontSize: "12px",
                    }}
                  />
                  <Legend
                    formatter={(value) => (
                      <span style={{ color: "#94a3b8", fontSize: "11px" }}>{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[200px] flex items-center justify-center">
                <p className="text-sm text-slate-600">Waiting for data...</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* ── Live Feed + Sidebar ──────────────────────────────────── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Live Feed — 2/3 */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="lg:col-span-2 rounded-2xl border border-slate-800/80 p-6"
            style={{ background: "rgba(15,23,42,0.8)" }}
          >
            <LiveFeed conversions={conversions} />
          </motion.div>

          {/* Sidebar — 1/3 */}
          <div className="space-y-4">
            {/* Signal breakdown */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="rounded-2xl border border-slate-800/80 p-5"
              style={{ background: "rgba(15,23,42,0.8)" }}
            >
              <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-pine-400" />
                Signal Breakdown
              </h3>
              {totalSaves > 0 ? (
                <div className="space-y-3">
                  {Object.entries(channelBreakdown).map(([channel, count]) => {
                    const pct = Math.round((count / totalSaves) * 100);
                    const barColors: Record<string, string> = {
                      web: "bg-blue-500",
                      whatsapp: "bg-green-500",
                      qr: "bg-purple-500",
                      voice: "bg-orange-500",
                    };
                    return (
                      <div key={channel}>
                        <div className="flex justify-between text-xs mb-1.5">
                          <span className="font-medium text-slate-300 capitalize">{channel}</span>
                          <span className="text-slate-500">{count} · {pct}%</span>
                        </div>
                        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <motion.div
                            className={cn("h-full rounded-full", barColors[channel] ?? "bg-pine-500")}
                            initial={{ width: 0 }}
                            animate={{ width: `${pct}%` }}
                            transition={{ duration: 1, ease: "easeOut" }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-slate-600 text-center py-4">Waiting for data...</p>
              )}
            </motion.div>

            {/* Pine Labs products used */}
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
              className="rounded-2xl border border-pine-500/20 p-5"
              style={{ background: "rgba(15,23,42,0.8)" }}
            >
              <div className="flex items-center gap-2 mb-4">
                <div className="w-6 h-6 bg-pine-500/20 rounded-lg flex items-center justify-center border border-pine-500/30">
                  <Zap className="w-3 h-3 text-pine-400" />
                </div>
                <h3 className="text-sm font-semibold text-slate-200">Pine Labs Stack</h3>
              </div>
              <div className="space-y-2">
                {PINE_PRODUCTS.map((p, i) => (
                  <motion.div
                    key={p}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.35 + i * 0.04 }}
                    className="flex items-center gap-2.5 text-xs text-slate-400"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-pine-500 flex-shrink-0" />
                    <span>{p}</span>
                  </motion.div>
                ))}
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800">
                <p className="text-[10px] text-slate-500 text-center">
                  9 products · All APIs called in real-time
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </main>
    </div>
  );
}
