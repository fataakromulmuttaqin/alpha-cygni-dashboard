"use client";
import { useForexRates } from "@/hooks/useForexData";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown } from "lucide-react";
import numeral from "numeral";

export function ForexRatesCard() {
  const { data, isLoading } = useForexRates();

  const rates = data?.data || [];

  if (isLoading) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-gray-400">Forex</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex justify-between">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-24" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gray-800/50 border-gray-700">
      <CardHeader>
        <CardTitle className="text-sm font-medium text-gray-400">Forex</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {rates.slice(0, 6).map((rate: { pair: string; rate: number; change: number; change_pct: number }) => {
          const isPositive = rate.change >= 0;
          return (
            <div key={rate.pair} className="flex justify-between items-center">
              <span className="text-sm font-medium text-gray-300">{rate.pair}</span>
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold text-white">
                  {numeral(rate.rate).format("0,0.0000")}
                </span>
                <span
                  className={`flex items-center gap-1 text-xs ${
                    isPositive ? "text-emerald-500" : "text-red-500"
                  }`}
                >
                  {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  {rate.change_pct.toFixed(2)}%
                </span>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
