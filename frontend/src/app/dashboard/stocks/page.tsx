"use client";
import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { useAllQuotes } from "@/hooks/useStockData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown, Star } from "lucide-react";
import Link from "next/link";
import numeral from "numeral";

export default function StocksPage() {
  const [filter, setFilter] = useState("");
  const { data, isLoading } = useAllQuotes();

  const stocks = data?.data || [];
  const filtered = stocks.filter((s: { ticker: string; name?: string }) =>
    s.ticker.toLowerCase().includes(filter.toLowerCase()) ||
    s.name?.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6 space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">Daftar Saham IDX</h1>
            <Input
              placeholder="Filter ticker..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-64 bg-gray-800 border-gray-700"
            />
          </div>

          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-400">
                {filtered.length} Saham
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 10 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-gray-400 border-b border-gray-700">
                        <th className="text-left py-3 px-2 font-medium">Ticker</th>
                        <th className="text-right py-3 px-2 font-medium">Price</th>
                        <th className="text-right py-3 px-2 font-medium">Change</th>
                        <th className="text-right py-3 px-2 font-medium">Volume</th>
                        <th className="text-right py-3 px-2 font-medium">High</th>
                        <th className="text-right py-3 px-2 font-medium">Low</th>
                        <th className="text-center py-3 px-2 font-medium">Detail</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map((stock: { ticker: string; price: number; change: number; change_pct: number; volume: number; high: number; low: number; name?: string }) => {
                        const isPos = stock.change >= 0;
                        return (
                          <tr
                            key={stock.ticker}
                            className="border-b border-gray-800 hover:bg-gray-700/30"
                          >
                            <td className="py-3 px-2">
                              <div className="font-semibold text-white">{stock.ticker}</div>
                              <div className="text-xs text-gray-500 truncate max-w-[150px]">
                                {stock.name || "-"}
                              </div>
                            </td>
                            <td className="py-3 px-2 text-right text-white font-medium">
                              {numeral(stock.price).format("0,0.00")}
                            </td>
                            <td className={`py-3 px-2 text-right flex items-center justify-end gap-1 ${isPos ? "text-emerald-500" : "text-red-500"}`}>
                              {isPos ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                              {isPos ? "+" : ""}
                              {stock.change_pct.toFixed(2)}%
                            </td>
                            <td className="py-3 px-2 text-right text-gray-400">
                              {numeral(stock.volume).format("0.0a")}
                            </td>
                            <td className="py-3 px-2 text-right text-gray-400">
                              {numeral(stock.high).format("0,0.00")}
                            </td>
                            <td className="py-3 px-2 text-right text-gray-400">
                              {numeral(stock.low).format("0,0.00")}
                            </td>
                            <td className="py-3 px-2 text-center">
                              <Link
                                href={`/dashboard/stocks/${stock.ticker}`}
                                className="inline-flex items-center gap-1 text-emerald-500 hover:text-emerald-400 text-xs font-medium"
                              >
                                <Star className="w-3 h-3" />
                                Detail
                              </Link>
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
    </div>
  );
}
