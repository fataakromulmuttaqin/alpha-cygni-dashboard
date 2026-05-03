"use client";
import { useState } from "react";
import { Header } from "@/components/layout/Header";
import { useForexRates, useForexHistory } from "@/hooks/useForexData";
import { TradingViewWidget } from "@/components/charts/TradingViewWidget";
import { LightweightChart } from "@/components/charts/LightweightChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown } from "lucide-react";
import numeral from "numeral";

const FOREX_PAIRS = [
  "XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY",
  "AUD/USD", "USD/CHF", "USD/CAD", "NZD/USD"
];

const TV_SYMBOLS: Record<string, string> = {
  "XAU/USD": "TVC:XAUUSD",
  "EUR/USD": "FX:EURUSD",
  "GBP/USD": "FX:GBPUSD",
  "USD/JPY": "FX:USDJPY",
  "AUD/USD": "FX:AUDUSD",
  "USD/CHF": "FX:USDCHF",
  "USD/CAD": "FX:USDCAD",
  "NZD/USD": "FX:NZDUSD",
};

export default function ForexPage() {
  const [selectedPair, setSelectedPair] = useState("XAU/USD");
  const { data: ratesData, isLoading } = useForexRates();
  const { data: historyData } = useForexHistory(selectedPair, "1y", "1d");

  const rates = ratesData?.data || [];
  const history = historyData?.data || [];

  const chartData = history.map((d: { time: number; close: number }) => ({
    time: d.time as number,
    value: d.close as number,
  }));

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <Header />
      <main className="flex-1 overflow-auto p-6 space-y-6">
        <h1 className="text-2xl font-bold text-white">Forex — USD Majors</h1>

        {/* Pair Selector */}
        <div className="flex gap-2 flex-wrap">
          {FOREX_PAIRS.map((pair) => (
            <button
              key={pair}
              onClick={() => setSelectedPair(pair)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedPair === pair
                  ? "bg-emerald-500 text-white"
                  : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              {pair}
            </button>
          ))}
        </div>

        {/* Chart */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-400">
                TradingView — {selectedPair}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <TradingViewWidget
                symbol={TV_SYMBOLS[selectedPair] || `FX:${selectedPair.replace("/", "")}`}
                height={400}
              />
            </CardContent>
          </Card>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-400">
                Historical — {selectedPair}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {chartData.length > 0 ? (
                <LightweightChart
                  data={chartData}
                  type="line"
                  height={400}
                  color="#3b82f6"
                />
              ) : (
                <Skeleton className="h-96 w-full" />
              )}
            </CardContent>
          </Card>
        </div>

        {/* All Rates Table */}
        <Card className="bg-gray-800/50 border-gray-700">
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-400">
              Semua Kurs Forex
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-gray-400 border-b border-gray-700">
                      <th className="text-left py-3 px-2 font-medium">Pair</th>
                      <th className="text-right py-3 px-2 font-medium">Rate</th>
                      <th className="text-right py-3 px-2 font-medium">Change</th>
                      <th className="text-right py-3 px-2 font-medium">High</th>
                      <th className="text-right py-3 px-2 font-medium">Low</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rates.map((rate: { pair: string; rate: number; change: number; change_pct: number; high: number; low: number }) => {
                      const isPos = rate.change >= 0;
                      return (
                        <tr
                          key={rate.pair}
                          className="border-b border-gray-800 hover:bg-gray-700/30 cursor-pointer"
                          onClick={() => setSelectedPair(rate.pair)}
                        >
                          <td className="py-3 px-2 font-semibold text-white">{rate.pair}</td>
                          <td className="py-3 px-2 text-right text-white">
                            {numeral(rate.rate).format("0,0.0000")}
                          </td>
                          <td className={`py-3 px-2 text-right flex items-center justify-end gap-1 ${isPos ? "text-emerald-500" : "text-red-500"}`}>
                            {isPos ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                            {isPos ? "+" : ""}
                            {rate.change_pct.toFixed(2)}%
                          </td>
                          <td className="py-3 px-2 text-right text-gray-400">
                            {numeral(rate.high).format("0,0.0000")}
                          </td>
                          <td className="py-3 px-2 text-right text-gray-400">
                            {numeral(rate.low).format("0,0.0000")}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
