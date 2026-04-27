"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const items = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/vision", label: "Vision" },
  { href: "/chat", label: "Chat" },
  { href: "/navigation", label: "Navigation" },
  { href: "/control", label: "Control" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-gray-200 bg-white p-4">
      <div className="mb-6">
        <h1 className="text-xl font-bold">Robot Command Center</h1>
        <p className="text-sm text-gray-500">FastAPI + Next.js + ROS2</p>
      </div>

      <nav className="space-y-2">
        {items.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-lg px-3 py-2 text-sm transition ${
                active
                  ? "bg-black text-white"
                  : "bg-gray-100 text-gray-800 hover:bg-gray-200"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}