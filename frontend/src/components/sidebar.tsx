"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
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
    <aside className="flex min-h-screen w-[280px] shrink-0 flex-col border-r border-slate-200 bg-slate-50 px-4 py-6">
      <div>
        <h1 className="text-2xl font-bold leading-tight text-slate-950">
          Robot Command
          <br />
          Center
        </h1>
        <p className="mt-2 text-lg text-slate-500">Next.js + ROS2</p>
      </div>

      <nav className="mt-6 space-y-3">
        {navItems.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block rounded-2xl px-4 py-4 text-lg font-medium transition ${
                active
                  ? "bg-slate-950 text-white"
                  : "bg-slate-200 text-slate-800 hover:bg-slate-300"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto pt-6">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="relative h-14 w-14 overflow-hidden rounded-full border border-slate-200">
              <Image
                src="/profile.png"
                alt="Profile picture"
                fill
                sizes="56px"
                className="object-cover"
              />
            </div>

            <div>
              <p className="text-sm text-slate-500">Built by</p>
              <p className="text-base font-semibold text-slate-900">
                Promise Adiole
              </p>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <div className="flex items-center justify-center rounded-xl bg-slate-50 p-3">
              <Image
                src="/logo-1.png"
                alt="Organization logo 1"
                width={180}
                height={60}
                style={{ width: "auto", height: "auto", maxWidth: "100%" }}
                className="object-contain"
              />
            </div>

            <div className="flex items-center justify-center rounded-xl bg-slate-50 p-3">
              <Image
                src="/logo-2.png"
                alt="Organization logo 2"
                width={180}
                height={60}
                style={{ width: "auto", height: "auto", maxWidth: "100%" }}
                className="object-contain"
              />
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}