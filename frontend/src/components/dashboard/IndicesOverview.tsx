"use client";
import { useMarketIndices } from "@/hooks/useMarketStatus";
import { IndexCard } from "./IndexCard";

export function IndicesOverview() {
  const { data, isLoading } = useMarketIndices();

  const indices = data?.data || [];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {isLoading
        ? Array.from({ length: 3 }).map((_, i) => (
            <IndexCard key={i} isLoading />
          ))
        : indices.map((index: { name: string; symbol: string; price: number; change: number; change_pct: number; high: number; low: number }) => (
            <IndexCard key={index.symbol} data={index} />
          ))}
    </div>
  );
}
