"use client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, TrendingDown } from "lucide-react";
import type { IndexData } from "@/types/stock";

interface IndexCardProps {
  data?: IndexData;
  isLoading?: boolean;
}

export function IndexCard({ data, isLoading }: IndexCardProps) {
  if (isLoading) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader className="pb-2">
          <Skeleton className="h-4 w-20" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-4 w-24" />
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  const isPositive = data.change >= 0;

  return (
    <Card className="bg-gray-800/50 border-gray-700">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-gray-400">{data.name}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-white">
            {data.price.toLocaleString("id-ID", { minimumFractionDigits: 2 })}
          </span>
          <span
            className={`flex items-center gap-1 text-sm font-medium ${
              isPositive ? "text-emerald-500" : "text-red-500"
            }`}
          >
            {isPositive ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            {isPositive ? "+" : ""}
            {data.change.toFixed(2)} ({data.change_pct.toFixed(2)}%)
          </span>
        </div>
        <div className="mt-2 flex gap-4 text-xs text-gray-500">
          <span>High: {data.high.toLocaleString("id-ID")}</span>
          <span>Low: {data.low.toLocaleString("id-ID")}</span>
        </div>
      </CardContent>
    </Card>
  );
}
