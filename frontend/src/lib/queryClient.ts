import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,          // Data dianggap stale setelah 1 menit
      gcTime: 5 * 60 * 1000,         // Hapus dari cache setelah 5 menit
      retry: 2,
      refetchOnWindowFocus: false,
      refetchInterval: 5 * 60 * 1000, // Auto-refetch setiap 5 menit
    },
  },
});
