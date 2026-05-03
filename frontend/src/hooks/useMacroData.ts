"use client";
import { useQuery } from "@tanstack/react-query";
import { macroApi } from "@/lib/api";

export function useMacroSnapshot() {
  return useQuery({
    queryKey: ["macro", "snapshot"],
    queryFn: () => macroApi.getSnapshot(),
    staleTime: 60 * 1000,
    refetchInterval: 60 * 1000,
  });
}

export function useMacroHistory(seriesKey: string, period = "1mo", interval = "1d") {
  return useQuery({
    queryKey: ["macro", "history", seriesKey, period, interval],
    queryFn: () => macroApi.getHistory(seriesKey, period, interval),
    enabled: !!seriesKey,
    staleTime: 5 * 60 * 1000,
  });
}
