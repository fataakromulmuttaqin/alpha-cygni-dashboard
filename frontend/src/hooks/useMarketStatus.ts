"use client";
import { useQuery } from "@tanstack/react-query";
import { indicesApi, newsApi } from "@/lib/api";

export function useMarketIndices() {
  return useQuery({
    queryKey: ["indices"],
    queryFn: () => indicesApi.getAll(),
    staleTime: 2 * 60 * 1000,
    refetchInterval: 2 * 60 * 1000,
  });
}

export function useMarketNews(source = "all", limit = 10, goldFocus = true) {
  return useQuery({
    queryKey: ["news", source, limit, goldFocus],
    queryFn: () => newsApi.getNews(source, limit, goldFocus),
    staleTime: 10 * 60 * 1000,
    refetchInterval: 10 * 60 * 1000,
  });
}

// Check if market is open (Jakarta: 09:00-15:30 WIB, Mon-Fri)
export function useMarketStatus() {
  const now = new Date();
  const jakartaTime = new Date(now.toLocaleString("en-US", { timeZone: "Asia/Jakarta" }));
  const day = jakartaTime.getDay();
  const hour = jakartaTime.getHours();
  const minute = jakartaTime.getMinutes();
  const timeInMinutes = hour * 60 + minute;

  const isWeekday = day >= 1 && day <= 5;
  const isMarketHours = timeInMinutes >= 9 * 60 && timeInMinutes <= 15 * 60 + 30;

  return {
    isOpen: isWeekday && isMarketHours,
    isWeekday,
    jakartaTime: jakartaTime.toLocaleString("id-ID", {
      timeZone: "Asia/Jakarta",
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }),
  };
}
