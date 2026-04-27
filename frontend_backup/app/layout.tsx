import "./globals.css";
import type { Metadata } from "next";
import Sidebar from "@/components/sidebar";

export const metadata: Metadata = {
  title: "Robot Command Center",
  description: "Frontend for ROS2 + Nav2 + Vision + Chat control",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-gray-100 text-gray-900">
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}