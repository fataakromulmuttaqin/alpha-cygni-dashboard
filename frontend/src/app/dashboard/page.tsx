"use client";
import { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { ForexRatesCard } from "@/components/dashboard/ForexRatesCard";
import { NewsWidget } from "@/components/dashboard/NewsWidget";
import { TradingViewWidget } from "@/components/charts/TradingViewWidget";
import { MacroIndicators } from "@/components/dashboard/MacroIndicators";
import { EconomicCalendar } from "@/components/dashboard/EconomicCalendar";
import { useMarketStatus } from "@/hooks/useMarketStatus";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

export default function DashboardPage() {
  const { isOpen, jakartaTime } = useMarketStatus();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-gray-950">
      {/* Sidebar — hidden when collapsed */}
      {sidebarOpen && <Sidebar />}

      <div className="flex-1 flex flex-col overflow-hidden">
        <Header>
          {/* Sidebar toggle button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-400 hover:text-white ml-2"
            title={sidebarOpen ? "Hide sidebar" : "Show sidebar"}
          >
            {sidebarOpen ? (
              <ChevronLeft className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
          </Button>
        </Header>

        <main className="flex-1 overflow-auto p-6 space-y-6">
          {/* Market Status Banner */}
          <div className="flex items-center gap-3">
            <Badge
              variant={isOpen ? "default" : "secondary"}
              className={isOpen ? "bg-emerald-500" : "bg-gray-700"}
            >
              {isOpen ? "Market Open" : "Market Closed"}
            </Badge>
            <span className="text-sm text-gray-500">{jakartaTime}</span>
          </div>

          {/* XAU/USD Chart + Macro Sidebar */}
          <div className="grid grid-cols-1 xl:grid-cols-4 gap-6">
            {/* Left: Main Chart */}
            <div className={sidebarOpen ? "xl:col-span-3" : "xl:col-span-1"}>
              <section>
                <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-3">
                  XAU/USD — Gold Spot (USD/oz)
                </h2>
                <div className="bg-gray-800/50 rounded-xl overflow-hidden border border-gray-700">
                  <TradingViewWidget symbol="TVC:XAUUSD" interval="D" height={520} />
                </div>
              </section>
            </div>

            {/* Right: Macro Widgets */}
            {sidebarOpen && (
              <div className="xl:col-span-1 space-y-6">
                <MacroIndicators />
                <EconomicCalendar />
              </div>
            )}
          </div>

          {/* Forex + News */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ForexRatesCard />
            <NewsWidget />
          </div>
        </main>
      </div>
    </div>
  );
}
