"use client";
import { SidebarProvider } from "@/contexts/SidebarContext";
import { Sidebar } from "@/components/layout/Sidebar";
import { useSidebar } from "@/contexts/SidebarContext";

function SidebarWrapper({ children }: { children: React.ReactNode }) {
  const { sidebarOpen } = useSidebar();
  return (
    <>
      {sidebarOpen && <Sidebar />}
      {children}
    </>
  );
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex h-screen bg-gray-950">
        <SidebarWrapper>{children}</SidebarWrapper>
      </div>
    </SidebarProvider>
  );
}
