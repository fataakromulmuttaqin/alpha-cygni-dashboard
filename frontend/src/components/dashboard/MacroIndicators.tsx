"use client";
import { useMacroSnapshot } from "@/hooks/useMacroData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown, Minus, DollarSign, Gem, Percent, Activity } from "lucide-react";
import numeral from "numeral";

interface MacroData {
  timestamp: string;
  dxy: { value: number; change: number; change_pct: number };
  gold: { value: number; change: number; change_pct: number };
  yield_10y: { value: number; change: number };
  yield_2y: { value: number };
  real_yield_10y: { value: number };
  yield_curve: { value: number };
  breakeven_inflation: { value: number };
  signals: { gold_dxy_correlation: string };
}

function SignalBadge({ signal }: { signal: string }) {
  const config = {
    bullish: { label: "Bullish", class: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" },
    bearish: { label: "Bearish", class: "bg-red-500/20 text-red-400 border-red-500/30" },
    neutral: { label: "Neutral", class: "bg-gray-500/20 text-gray-400 border-gray-500/30" },
  };
  const s = config[signal as keyof typeof config] || config.neutral;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${s.class}`}>
      {s.label}
    </span>
  );
}

function MacroRow({ icon: Icon, label, value, change, changePct, unit, signal }: {
  icon: React.ElementType;
  label: string;
  value: number | string;
  change?: number;
  changePct?: number;
  unit?: string;
  signal?: "bullish" | "bearish" | "neutral";
}) {
  const isPositive = change !== undefined ? change >= 0 : true;
  const isBullish = signal === "bullish";
  const isBearish = signal === "bearish";
  const colorClass = isBullish ? "text-emerald-400" : isBearish ? "text-red-400" : "text-gray-400";

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-700/50 last:border-0">
      <div className="flex items-center gap-2">
        <Icon className={`w-4 h-4 ${colorClass}`} />
        <span className="text-sm text-gray-400">{label}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm font-semibold text-white">
          {typeof value === "number" ? numeral(value).format(value < 100 ? "0,0.00" : "0,0") : value}
          {unit && <span className="text-gray-400 text-xs ml-1">{unit}</span>}
        </span>
        {change !== undefined && (
          <span className={`flex items-center gap-1 text-xs ${isPositive ? "text-emerald-400" : "text-red-400"}`}>
            {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {changePct !== undefined ? `${changePct >= 0 ? "+" : ""}${changePct.toFixed(2)}%` : `${change >= 0 ? "+" : ""}${change.toFixed(2)}`}
          </span>
        )}
      </div>
    </div>
  );
}

export function MacroIndicators() {
  const { data, isLoading } = useMacroSnapshot();

  if (isLoading) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-gray-400">Macro Indicators</CardTitle>
            <Skeleton className="h-5 w-16" />
          </div>
        </CardHeader>
        <CardContent className="space-y-1">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="flex justify-between py-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-20" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const d: MacroData = data?.data;

  if (!d) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-400">Macro Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">Data unavailable</p>
        </CardContent>
      </Card>
    );
  }

  // Determine signals
  const goldSignal: "bullish" | "bearish" | "neutral" =
    d.gold.change_pct > 0.5 ? "bullish" : d.gold.change_pct < -0.5 ? "bearish" : "neutral";
  const dxySignal: "bullish" | "bearish" | "neutral" =
    d.dxy.change_pct > 0.2 ? "bearish" : d.dxy.change_pct < -0.2 ? "bullish" : "neutral";
  const realYieldSignal: "bullish" | "bearish" | "neutral" =
    d.real_yield_10y.value < 1.5 ? "bullish" : d.real_yield_10y.value > 2.5 ? "bearish" : "neutral";
  const yieldCurveSignal: "bullish" | "bearish" | "neutral" =
    d.yield_curve.value > 0.5 ? "bullish" : d.yield_curve.value < 0.2 ? "bearish" : "neutral";

  return (
    <Card className="bg-gray-800/50 border-gray-700">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-gray-400">Macro Indicators</CardTitle>
          <SignalBadge signal={d.signals.gold_dxy_correlation} />
        </div>
        <p className="text-xs text-gray-500">
          Updated {new Date(d.timestamp).toLocaleTimeString()}
        </p>
      </CardHeader>
      <CardContent className="space-y-0">
        <MacroRow
          icon={DollarSign}
          label="DXY Index"
          value={d.dxy.value}
          change={d.dxy.change}
          changePct={d.dxy.change_pct}
          signal={dxySignal}
        />
        <MacroRow
          icon={Gem}
          label="Gold (GC=F)"
          value={d.gold.value}
          change={d.gold.change_pct}
          changePct={d.gold.change_pct}
          signal={goldSignal}
        />
        <MacroRow
          icon={Percent}
          label="10Y Treasury"
          value={d.yield_10y.value}
          change={d.yield_10y.change}
          unit="%"
          signal={d.yield_10y.value > 4.5 ? "bearish" : d.yield_10y.value < 4.0 ? "bullish" : "neutral"}
        />
        <MacroRow
          icon={Percent}
          label="2Y Treasury"
          value={d.yield_2y.value}
          unit="%"
          signal={d.yield_2y.value > 4.5 ? "bearish" : d.yield_2y.value < 4.0 ? "bullish" : "neutral"}
        />
        <MacroRow
          icon={Activity}
          label="Real Yield"
          value={d.real_yield_10y.value}
          unit="%"
          signal={realYieldSignal}
        />
        <MacroRow
          icon={Activity}
          label="Yield Curve"
          value={d.yield_curve.value}
          unit="spread"
          signal={yieldCurveSignal}
        />
      </CardContent>
    </Card>
  );
}
