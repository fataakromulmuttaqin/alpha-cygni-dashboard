"use client";
import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { useQuery } from "@tanstack/react-query";
import { screenerApi } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import numeral from "numeral";
import Link from "next/link";
import { Star } from "lucide-react";

export default function ScreenerPage() {
  const [sector, setSector] = useState<string>("");
  const [maxPe, setMaxPe] = useState("");
  const [minRoe, setMinRoe] = useState("");
  const [sortBy, setSortBy] = useState("market_cap");
  const [order, setOrder] = useState("desc");

  const { data: sectorsData } = useQuery({
    queryKey: ["screener", "sectors"],
    queryFn: () => screenerApi.getSectors(),
  });

  const { data: screenerData, isLoading, refetch } = useQuery({
    queryKey: ["screener", sector, maxPe, minRoe, sortBy, order],
    queryFn: () =>
      screenerApi.screener({
        sector: sector || undefined,
        max_pe: maxPe ? parseFloat(maxPe) : undefined,
        min_roe: minRoe ? parseFloat(minRoe) : undefined,
        sort_by: sortBy,
        order,
        limit: 50,
      }),
    select: (data) => data,
  });

  const results = (screenerData as any)?.results || [];
  const sectors = (sectorsData as any)?.sectors || [];

  return (
    <div className="flex h-screen bg-gray-950">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-auto p-6 space-y-6">
          <h1 className="text-2xl font-bold text-white">Stock Screener</h1>

          {/* Filters */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-400">Filter</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4 items-end">
                <div className="space-y-1.5">
                  <label className="text-xs text-gray-500">Sector</label>
                  <Select value={sector} onValueChange={(v) => setSector(v || "")}>
                    <SelectTrigger className="w-48 bg-gray-700 border-gray-600">
                      <SelectValue placeholder="All Sectors" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Sectors</SelectItem>
                      {sectors.map((s: string) => (
                        <SelectItem key={s} value={s}>{s}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-gray-500">Max P/E Ratio</label>
                  <Input
                    type="number"
                    placeholder="e.g. 20"
                    value={maxPe}
                    onChange={(e) => setMaxPe(e.target.value)}
                    className="w-32 bg-gray-700 border-gray-600"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-gray-500">Min ROE (%)</label>
                  <Input
                    type="number"
                    placeholder="e.g. 10"
                    value={minRoe}
                    onChange={(e) => setMinRoe(e.target.value)}
                    className="w-32 bg-gray-700 border-gray-600"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-gray-500">Sort By</label>
                  <Select value={sortBy} onValueChange={(v) => setSortBy(v || "market_cap")}>
                    <SelectTrigger className="w-36 bg-gray-700 border-gray-600">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="market_cap">Market Cap</SelectItem>
                      <SelectItem value="pe">P/E Ratio</SelectItem>
                      <SelectItem value="roe">ROE</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-gray-500">Order</label>
                  <Select value={order} onValueChange={(v) => setOrder(v || "desc")}>
                    <SelectTrigger className="w-28 bg-gray-700 border-gray-600">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="desc">Descending</SelectItem>
                      <SelectItem value="asc">Ascending</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <Button onClick={() => refetch()} className="bg-emerald-500 hover:bg-emerald-600">
                  Apply Filter
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Results */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-sm font-medium text-gray-400">
                {results.length} Hasil
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {Array.from({ length: 10 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : results.length === 0 ? (
                <p className="text-gray-500 text-sm py-8 text-center">
                  Tidak ada hasil. Coba ubah filter.
                </p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-gray-400 border-b border-gray-700">
                        <th className="text-left py-3 px-2 font-medium">Ticker</th>
                        <th className="text-left py-3 px-2 font-medium">Name</th>
                        <th className="text-right py-3 px-2 font-medium">Sector</th>
                        <th className="text-right py-3 px-2 font-medium">Market Cap</th>
                        <th className="text-right py-3 px-2 font-medium">P/E</th>
                        <th className="text-right py-3 px-2 font-medium">ROE</th>
                        <th className="text-center py-3 px-2 font-medium">Detail</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((stock: {
                        ticker: string;
                        name: string;
                        sector: string;
                        market_cap: number;
                        pe_ratio: number;
                        roe: number;
                      }) => (
                        <tr
                          key={stock.ticker}
                          className="border-b border-gray-800 hover:bg-gray-700/30"
                        >
                          <td className="py-3 px-2 font-semibold text-white">{stock.ticker}</td>
                          <td className="py-3 px-2 text-gray-400 max-w-[150px] truncate">
                            {stock.name}
                          </td>
                          <td className="py-3 px-2 text-right text-gray-400 text-xs">
                            {stock.sector}
                          </td>
                          <td className="py-3 px-2 text-right text-white">
                            {stock.market_cap ? numeral(stock.market_cap).format("0.0a") : "-"}
                          </td>
                          <td className="py-3 px-2 text-right text-white">
                            {stock.pe_ratio ? numeral(stock.pe_ratio).format("0.00") : "-"}
                          </td>
                          <td className="py-3 px-2 text-right text-white">
                            {stock.roe ? numeral(stock.roe).format("0.00%") : "-"}
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
                      ))}
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
