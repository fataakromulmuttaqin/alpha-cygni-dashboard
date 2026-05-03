export interface StockQuote {
  ticker: string;
  yahoo_symbol?: string;
  name?: string;
  price: number;
  open?: number;
  high?: number;
  low?: number;
  prev_close?: number;
  volume?: number;
  market_cap?: number;
  change: number;
  change_pct: number;
  currency?: string;
  exchange?: string;
  sector?: string;
  industry?: string;
  timestamp?: string;
  source?: string;
}

export interface StockHistory {
  time: number;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number;
  sma_20: number | null;
  sma_50: number | null;
  rsi_14: number | null;
}

export interface StockInfo {
  ticker: string;
  name: string;
  description: string;
  sector: string;
  industry: string;
  employees: number;
  website: string;
  pe_ratio: number;
  forward_pe: number;
  pb_ratio: number;
  ps_ratio: number;
  peg_ratio: number;
  debt_to_equity: number;
  roe: number;
  roa: number;
  profit_margin: number;
  gross_margin: number;
  operating_margin: number;
  revenue: number;
  revenue_growth: number;
  earnings_growth: number;
  dividend_yield: number;
  dividend_rate: number;
  beta: number;
  w52_high: number;
  w52_low: number;
  avg_volume_3m: number;
  shares_outstanding: number;
  market_cap: number;
  enterprise_value: number;
  book_value: number;
  earnings_per_share: number;
}

export interface ForexRate {
  pair: string;
  rate: number;
  change: number;
  change_pct: number;
  high: number;
  low: number;
  timestamp: string;
}

export interface IndexData {
  name: string;
  symbol: string;
  price: number;
  change: number;
  change_pct: number;
  high: number;
  low: number;
}

export interface NewsItem {
  title: string;
  summary: string;
  url: string;
  published: string;
  source: string;
}
