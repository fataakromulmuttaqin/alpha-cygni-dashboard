"use client";
import { useEconomicCalendar } from "@/hooks/useEconomicCalendar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Calendar, AlertCircle } from "lucide-react";

interface CalendarEvent {
  name: string;
  frequency: string;
  typical_date: string;
  impact: string;
  impact_color: string;
  description: string;
  category: string;
  next_release: string;
}

function ImpactBadge({ color }: { color: string }) {
  const colorMap: Record<string, string> = {
    red: "bg-red-500/20 text-red-400 border-red-500/30",
    yellow: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    green: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  };
  const cls = colorMap[color] || colorMap.yellow;
  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium border ${cls}`}>
      {color === "red" ? "HIGH" : color === "yellow" ? "MED" : "LOW"}
    </span>
  );
}

function EventRow({ event }: { event: CalendarEvent }) {
  const isToday = event.next_release === new Date().toISOString().split("T")[0];
  const isTomorrow =
    event.next_release ===
    new Date(Date.now() + 86400000).toISOString().split("T")[0];

  let dateLabel = event.next_release;
  if (isToday) dateLabel = "Today";
  else if (isTomorrow) dateLabel = "Tomorrow";
  else if (event.next_release !== "TBD") {
    const d = new Date(event.next_release);
    dateLabel = d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  }

  return (
    <div className="flex items-start gap-3 py-2 border-b border-gray-700/50 last:border-0">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-sm font-medium text-white truncate">{event.name}</span>
          <ImpactBadge color={event.impact_color} />
        </div>
        <p className="text-xs text-gray-500 line-clamp-1">{event.description}</p>
      </div>
      <div className="text-right shrink-0">
        <span className={`text-xs font-medium ${isToday ? "text-emerald-400" : "text-gray-400"}`}>
          {dateLabel}
        </span>
        {event.typical_date !== "TBD" && (
          <p className="text-xs text-gray-600">{event.typical_date}</p>
        )}
      </div>
    </div>
  );
}

export function EconomicCalendar() {
  const { data, isLoading } = useEconomicCalendar();

  if (isLoading) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-400">Economic Calendar</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex justify-between py-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-4 w-12" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const events: CalendarEvent[] = data?.data || [];

  // Filter high impact + near-term events
  const highImpact = events.filter((e) => e.impact === "HIGH").slice(0, 6);
  const upcoming = events.filter(
    (e) =>
      e.next_release !== "TBD" &&
      new Date(e.next_release).getTime() - Date.now() < 14 * 86400000
  );

  const displayEvents = upcoming.length > 0 ? upcoming : highImpact;

  if (displayEvents.length === 0) {
    return (
      <Card className="bg-gray-800/50 border-gray-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-gray-400">Economic Calendar</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-500">No upcoming events</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-gray-800/50 border-gray-700">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium text-gray-400">Economic Calendar</CardTitle>
          <Calendar className="w-4 h-4 text-gray-500" />
        </div>
        <p className="text-xs text-gray-500">
          {upcoming.length > 0 ? "Upcoming (14 days)" : "High Impact Events"}
        </p>
      </CardHeader>
      <CardContent className="space-y-0">
        {displayEvents.map((event, i) => (
          <EventRow key={i} event={event} />
        ))}
      </CardContent>
    </Card>
  );
}
