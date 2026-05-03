"use client";
import { useQuery } from "@tanstack/react-query";
import { economicCalendarApi } from "@/lib/api";

export function useEconomicCalendar() {
  return useQuery({
    queryKey: ["economic-calendar"],
    queryFn: () => economicCalendarApi.getCalendar(),
    staleTime: 60 * 1000,
    refetchInterval: 60 * 1000,
  });
}

export function useLatestJobsData() {
  return useQuery({
    queryKey: ["economic-calendar", "jobs"],
    queryFn: () => economicCalendarApi.getLatest(),
    staleTime: 5 * 60 * 1000,
  });
}
