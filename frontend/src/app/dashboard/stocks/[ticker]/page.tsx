"use client";
import { use } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { useStockQuote, useStockHistory, useStockInfo } from "@/hooks/useStockData";
import { TradingViewWidget } from "@/components/charts/TradingViewWidget";
import { LightweightChart } from "@/components/charts/LightweightChart";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown } from "lucide-react";
import numeral from "numeral";

interface Props {
  params: Promise<{ ticker: string }>;
}

export default function StockDetailPage({ params }: Props) {
  const { ticker } = use(params);
  const { data: quote, isLoading: quoteLoading } = useStockQuote(ticker);
  const { data: info } = useStockInfo(ticker);
  const { data: history } = useStockHistory(ticker, "1y", "1d");

  const chartData = history?.data?.map((d: { time: number; open: number; high: number; low: number; close: number }) => ({
    time: d.time as number,
    open: d.open,
    high: d.high,
    low: d.low,
    close: d.close,
  })) || [];

  const isPos = (quote?.change || 0) >= 0;

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6 space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div>
              {quoteLoading ? (
                <Skeleton className="h-8 w-32" />
              ) : (
                <h1 className="text-2xl font-bold text-white">{ticker}</h1>
              )}
              {quote?.name && (
                <p className="text-sm text-gray-400 mt-1">{quote.name}</p>
              )}
            </div>
            {quote && (
              <div className="text-right">
                <div className="text-3xl font-bold text-white">
                  {numeral(quote.price).format("0,0.00")}{" "}
                  <span className="text-sm text-gray-500">IDR</span>
                </div>
                <div className={`flex items-center justify-end gap-1 mt-1 ${isPos ? "text-emerald-500" : "text-red-500"}`}>
                  {isPos ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                  {isPos ? "+" : ""}
                  {quote.change.toFixed(2)} ({quote.change_pct.toFixed(2)}%)
                </div>
              </div>
            )}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* TradingView Embed */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-gray-400">TradingView Chart</CardTitle>
              </CardHeader>
              <CardContent>
                <TradingViewWidget symbol={`IDX:${ticker}`} height={400} />
              </CardContent>
            </Card>

            {/* Lightweight Chart */}
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-gray-400">Historical Data</CardTitle>
              </CardHeader>
              <CardContent>
                {chartData.length > 0 ? (
                  <LightweightChart data={chartData} type="candlestick" height={400} />
                ) : (
                  <Skeleton className="h-96 w-full" />
                )}
              </CardContent>
            </Card>
          </div>

          {/* Info */}
          {info && (
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-gray-400">Informasi Fundamental</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  <InfoItem label="Sector" value={info.sector || "-"} />
                  <InfoItem label="Industry" value={info.industry || "-"} />
                  <InfoItem label="Market Cap" value={info.market_cap ? numeral(info.market_cap).format("0.0a") : "-"} />
                  <InfoItem label="P/E Ratio" value={info.pe_ratio ? numeral(info.pe_ratio).format("0.00") : "-"} />
                  <InfoItem label="ROE" value={info.roe ? numeral(info.roe).format("0.00%") : "-"} />
                  <InfoItem label="ROA" value={info.roa ? numeral(info.roa).format("0.00%") : "-"} />
                  <InfoItem label="Debt/Equity" value={info.debt_to_equity ? numeral(info.debt_to_equity).format("0.00") : "-"} />
                  <InfoItem label="Beta" value={info.beta ? numeral(info.beta).format("0.00") : "-"} />
                  <InfoItem label="Dividend Yield" value={info.dividend_yield ? numeral(info.dividend_yield).format("0.00%") : "-"} />
                  <InfoItem label="52W High" value={info.w52_high ? numeral(info.w52_high).format("0,0.00") : "-"} />
                  <InfoItem label="52W Low" value={info.w52_low ? numeral(info.w52_low).format("0,0.00") : "-"} />
                  <InfoItem label="Avg Volume" value={info.avg_volume_3m ? numeral(info.avg_volume_3m).format("0.0a") : "-"} />
                </div>
              </CardContent>
            </Card>
          )}
        </main>
      </div>
    </div>
  );
}

function InfoItem({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-sm font-medium text-white">{value}</p>
    </div>
  );
}
