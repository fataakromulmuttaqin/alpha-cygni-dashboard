"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TrendingUp, DollarSign, Search, Newspaper, Home, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSidebar } from "@/contexts/SidebarContext";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/dashboard", label: "Overview", icon: Home },
  { href: "/dashboard/forex", label: "Forex", icon: DollarSign },
  { href: "/dashboard/screener", label: "Screener", icon: Search },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useSidebar();

  return (
    <aside className={cn(
      "bg-gray-900 border-r border-gray-800 flex flex-col transition-all duration-300",
      sidebarOpen ? "w-64" : "w-16"
    )}>
      {/* Logo + Toggle */}
      <div className="p-4 border-b border-gray-800 flex items-center justify-between">
        {sidebarOpen ? (
          <>
            <h1 className="text-lg font-bold text-white flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-500" />
              Alpha Cygni
            </h1>
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleSidebar}
              className="text-gray-400 hover:text-white p-1"
              title="Hide sidebar"
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
          </>
        ) : (
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleSidebar}
            className="text-gray-400 hover:text-white w-full justify-center"
            title="Show sidebar"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Label below logo when collapsed */}
      {!sidebarOpen && (
        <div className="p-2 border-b border-gray-800 flex justify-center">
          <TrendingUp className="w-5 h-5 text-emerald-500" />
        </div>
      )}

      {sidebarOpen && (
        <>
          <p className="text-xs text-gray-500 mt-1 px-4 pb-3">XAU/USD Gold Trading Edge</p>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                    isActive
                      ? "bg-emerald-500/10 text-emerald-500"
                      : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
                  )}
                >
                  <Icon className="w-4 h-4 flex-shrink-0" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-gray-800">
            <p className="text-xs text-gray-600">Data: FRED · Yahoo Finance</p>
            <p className="text-xs text-gray-600 mt-1">Macro · Gold · XAU/USD</p>
          </div>
        </>
      )}

      {/* Collapsed nav icons */}
      {!sidebarOpen && (
        <nav className="flex-1 p-2 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center justify-center p-2 rounded-lg text-sm font-medium transition-colors",
                  isActive
                    ? "bg-emerald-500/10 text-emerald-500"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
                )}
                title={item.label}
              >
                <Icon className="w-4 h-4" />
              </Link>
            );
          })}
        </nav>
      )}
    </aside>
  );
}
