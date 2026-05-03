"use client";
import { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickSeries, LineSeries, HistogramSeries } from "lightweight-charts";

interface LightweightChartProps {
  data: any;
  type?: "candlestick" | "line" | "histogram";
  height?: number;
  width?: string | number;
  color?: string;
}

export function LightweightChart({ data, type = "candlestick", height = 400, width = "100%", color }: LightweightChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | ISeriesApi<"Line"> | ISeriesApi<"Histogram"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    chartRef.current = createChart(containerRef.current, {
      width: width as number,
      height,
      layout: {
        background: { color: "transparent" },
        textColor: "#9ca3af",
      },
      grid: {
        vertLines: { color: "#1f2937" },
        horzLines: { color: "#1f2937" },
      },
      crosshair: {
        mode: 1,
        vertLine: { color: "#6b7280", labelBackgroundColor: "#374151" },
        horzLine: { color: "#6b7280", labelBackgroundColor: "#374151" },
      },
      rightPriceScale: {
        borderColor: "#374151",
      },
      timeScale: {
        borderColor: "#374151",
        timeVisible: true,
        secondsVisible: false,
      },
    });

    if (type === "candlestick") {
      seriesRef.current = chartRef.current.addSeries(CandlestickSeries, {
        upColor: "#10b981",
        downColor: "#ef4444",
        borderUpColor: "#10b981",
        borderDownColor: "#ef4444",
        wickUpColor: "#10b981",
        wickDownColor: "#ef4444",
      });
    } else if (type === "line") {
      seriesRef.current = chartRef.current.addSeries(LineSeries, {
        color: color || "#3b82f6",
        lineWidth: 2,
      });
    } else if (type === "histogram") {
      seriesRef.current = chartRef.current.addSeries(HistogramSeries, {
        color: color || "#3b82f6",
      });
    }

    if (seriesRef.current && data?.length) {
      seriesRef.current.setData(data);
    }

    chartRef.current.timeScale().fitContent();

    const handleResize = () => {
      if (chartRef.current && containerRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [type, height, width, color]);

  useEffect(() => {
    if (seriesRef.current && data?.length) {
      seriesRef.current.setData(data);
      chartRef.current?.timeScale().fitContent();
    }
  }, [data]);

  return <div ref={containerRef} className="w-full" style={{ height }} />;
}
