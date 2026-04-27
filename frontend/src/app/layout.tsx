import "./globals.css";
import type { Metadata } from "next";
import Sidebar from "@/components/sidebar";

export const metadata: Metadata = {
  title: "Robot Command Center",
  description: "FastAPI + Next.js frontend for ROS2 navigation, vision, and chat.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <div className="mx-auto flex min-h-screen w-full max-w-[1600px]">
          <aside className="w-64 shrink-0 border-r border-slate-200 bg-white">
            <Sidebar />
          </aside>

          <main className="min-w-0 flex-1 overflow-x-auto p-4 md:p-6">
            <div className="mx-auto w-full max-w-6xl">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}