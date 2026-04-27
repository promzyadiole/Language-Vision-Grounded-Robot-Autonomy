"use client";

import { useEffect, useState } from "react";
import Topbar from "@/components/topbar";
import StatusCard from "@/components/status-card";
import { getHealth, getRobotStatus } from "@/lib/api";

export default function DashboardPage() {
  const [health, setHealth] = useState<any>(null);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    async function load() {
      try {
        const [healthData, statusData] = await Promise.all([
          getHealth(),
          getRobotStatus(),
        ]);
        setHealth(healthData);
        setStatus(statusData);
      } catch (err) {
        console.error(err);
      }
    }

    load();
  }, []);

  return (
    <div>
      <Topbar
        title="Dashboard"
        subtitle="System health, robot status, and current pose."
      />

      <div className="grid gap-4 md:grid-cols-3">
        <StatusCard
          title="Backend"
          value={health ? "Online" : "Loading..."}
          description="FastAPI system health"
        />
        <StatusCard
          title="Nav2 Ready"
          value={status ? String(status.nav2_ready) : "Loading..."}
        />
        <StatusCard
          title="Navigating"
          value={status ? String(status.is_navigating) : "Loading..."}
        />
      </div>

      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold">Robot Status JSON</h3>
        <pre className="overflow-x-auto whitespace-pre-wrap text-sm">
          {JSON.stringify(status, null, 2)}
        </pre>
      </div>
    </div>
  );
}