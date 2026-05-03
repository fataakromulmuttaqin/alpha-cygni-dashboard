"use client";
import { useMarketNews } from "@/hooks/useMarketStatus";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { ExternalLink } from "lucide-react";

export function NewsWidget() {
  const { data, isLoading } = useMarketNews("all", 8, true);

  const news = data?.data || [];

  if (isLoading) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader>
          <CardTitle className="text-sm font-medium text-gray-400">Gold & Macro News</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-3 w-24" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gray-800/50 border-gray-700">
      <CardHeader>
        <CardTitle className="text-sm font-medium text-gray-400">Gold & Macro News</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {news.length === 0 && (
          <p className="text-sm text-gray-500">No gold-related news found.</p>
        )}
        {news.slice(0, 6).map((item: { title: string; url: string; source: string; published: string }, index: number) => (
          <div key={index} className="space-y-1">
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium text-gray-200 hover:text-emerald-500 line-clamp-2 flex items-start gap-2"
            >
              <ExternalLink className="w-3 h-3 mt-0.5 shrink-0" />
              {item.title}
            </a>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="text-xs border-gray-600 text-gray-400">
                {item.source}
              </Badge>
              <span className="text-xs text-gray-500">{item.published}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
