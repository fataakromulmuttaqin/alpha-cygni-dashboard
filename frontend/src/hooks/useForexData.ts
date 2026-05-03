"use client";
import { useQuery } from "@tanstack/react-query";
import { forexApi } from "@/lib/api";

export function useForexRates() {
  return useQuery({
    queryKey: ["forex", "rates"],
    queryFn: () => forexApi.getAllRates(),
    staleTime: 60 * 1000,
    refetchInterval: 60 * 1000,
  });
}

export function useForexHistory(pair: string, period = "1y", interval = "1d") {
  return useQuery({
    queryKey: ["forex", pair, "history", period, interval],
    queryFn: () => forexApi.getHistory(pair, period, interval),
    enabled: !!pair,
    staleTime: 5 * 60 * 1000,
  });
}
