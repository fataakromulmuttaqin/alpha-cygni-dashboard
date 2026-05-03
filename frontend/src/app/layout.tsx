import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/QueryProvider";
import { TooltipProvider } from "@/components/ui/tooltip";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "IDX Financial Dashboard",
  description: "Dashboard riset pasar saham Indonesia dan Forex",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body className={`${inter.className} h-full bg-gray-950 text-gray-100 antialiased`}>
        <TooltipProvider>
          <QueryProvider>
            {children}
          </QueryProvider>
        </TooltipProvider>
      </body>
    </html>
  );
}
