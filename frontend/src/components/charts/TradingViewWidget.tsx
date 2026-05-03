"use client";
import { useEffect, useRef } from "react";

interface TradingViewWidgetProps {
  symbol: string;
  interval?: string;
  height?: number;
  width?: string | number;
}

declare global {
  interface Window {
    TradingView?: {
      widget: new (config: Record<string, unknown>) => { remove: () => void };
    };
  }
}

export function TradingViewWidget({
  symbol,
  interval = "D",
  height = 400,
  width = "100%",
}: TradingViewWidgetProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const containerId = `tradingview_${symbol.replace(/[^a-zA-Z0-9]/g, "_")}_${Date.now()}`;
    containerRef.current.id = containerId;

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    script.onload = () => {
      if (window.TradingView && containerRef.current) {
        new window.TradingView.widget({
          symbol: symbol,
          interval: interval,
          timezone: "Asia/Jakarta",
          theme: "dark",
          style: "1",
          locale: "id",
          toolbar_bg: "#1e293b",
          enable_publishing: false,
          allow_symbol_change: true,
          container_id: containerRef.current!.id,
          autosize: width === "100%",
          width: width,
          height: height,
          hide_top_toolbar: false,
          hide_legend: false,
          save_image: false,
        });
      }
    };

    document.head.appendChild(script);

    return () => {
      if (containerRef.current) {
        containerRef.current.innerHTML = "";
      }
      document.head.removeChild(script);
    };
  }, [symbol, interval, height, width]);

  return (
    <div
      ref={containerRef}
      className="tradingview-widget-container"
      style={{ height, width: width === "100%" ? "100%" : width }}
    />
  );
}
