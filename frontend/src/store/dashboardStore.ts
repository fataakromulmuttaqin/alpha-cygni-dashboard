import { create } from "zustand";

interface DashboardStore {
  selectedTicker: string;
  selectedPeriod: string;
  selectedInterval: string;
  selectedForexPair: string;

  setSelectedTicker: (ticker: string) => void;
  setSelectedPeriod: (period: string) => void;
  setSelectedInterval: (interval: string) => void;
  setSelectedForexPair: (pair: string) => void;
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  selectedTicker: "BBCA",
  selectedPeriod: "1y",
  selectedInterval: "1d",
  selectedForexPair: "USD/IDR",

  setSelectedTicker: (ticker) => set({ selectedTicker: ticker }),
  setSelectedPeriod: (period) => set({ selectedPeriod: period }),
  setSelectedInterval: (interval) => set({ selectedInterval: interval }),
  setSelectedForexPair: (pair) => set({ selectedForexPair: pair }),
}));
