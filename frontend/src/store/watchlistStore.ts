import { create } from "zustand";
import { persist } from "zustand/middleware";

interface WatchlistItem {
  ticker: string;
  addedAt: number;
}

interface WatchlistStore {
  watchlist: WatchlistItem[];
  addToWatchlist: (ticker: string) => void;
  removeFromWatchlist: (ticker: string) => void;
  isInWatchlist: (ticker: string) => boolean;
}

export const useWatchlistStore = create<WatchlistStore>()(
  persist(
    (set, get) => ({
      watchlist: [],

      addToWatchlist: (ticker: string) => {
        if (!get().isInWatchlist(ticker)) {
          set((state) => ({
            watchlist: [...state.watchlist, { ticker, addedAt: Date.now() }],
          }));
        }
      },

      removeFromWatchlist: (ticker: string) => {
        set((state) => ({
          watchlist: state.watchlist.filter((item) => item.ticker !== ticker),
        }));
      },

      isInWatchlist: (ticker: string) => {
        return get().watchlist.some((item) => item.ticker === ticker);
      },
    }),
    {
      name: "idx-watchlist",
    }
  )
);
