"use client";
import { useQuery } from "@tanstack/react-query";
import { stocksApi } from "../lib/api";
import type { StockQuote, StockHistory, StockInfo } from "../types/stock";

export function useStockQuote(ticker: string) {
  return useQuery<StockQuote>({
    queryKey: ["stock", ticker, "quote"],
    queryFn: () => stocksApi.getQuote(ticker) as unknown as Promise<StockQuote>,
    enabled: !!ticker,
    staleTime: 60 * 1000,
  });
}

export function useStockHistory(ticker: string, period = "1y", interval = "1d") {
  return useQuery<{ data: StockHistory[] }>({
    queryKey: ["stock", ticker, "history", period, interval],
      queryFn: () => stocksApi.getHistory(ticker, period, interval) as unknown as Promise<{ data: StockHistory[] }>,
    enabled: !!ticker,
    staleTime: 5 * 60 * 1000,
  });
}

export function useStockInfo(ticker: string) {
  return useQuery<StockInfo>({
    queryKey: ["stock", ticker, "info"],
    queryFn: () => stocksApi.getInfo(ticker) as unknown as Promise<StockInfo>,
    enabled: !!ticker,
    staleTime: 60 * 60 * 1000,
  });
}

export function useStockFinancials(ticker: string) {
  return useQuery({
    queryKey: ["stock", ticker, "financials"],
    queryFn: () => stocksApi.getFinancials(ticker),
    enabled: !!ticker,
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useStockList() {
  return useQuery({
    queryKey: ["stock", "list"],
    queryFn: () => stocksApi.getList(),
    staleTime: 60 * 60 * 1000,
  });
}

export function useAllQuotes(tickers?: string) {
  return useQuery({
    queryKey: ["stocks", "quotes", tickers],
    queryFn: () => stocksApi.getAllQuotes(tickers),
    staleTime: 60 * 1000,
  });
}
