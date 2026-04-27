"use client";

import { useState } from "react";
import { goToPlace, stopRobot } from "@/lib/api";

const places = ["kitchen", "garage", "home"];

export default function CommandButtons() {
  const [status, setStatus] = useState("No action yet.");
  const [loading, setLoading] = useState(false);

  async function handleGo(place: string) {
    setLoading(true);
    try {
      const result = await goToPlace(place);
      setStatus(result.message || `Navigation request sent to ${place}`);
    } catch (err: any) {
      setStatus(err.message || "Navigation failed");
    } finally {
      setLoading(false);
    }
  }

  async function handleStop() {
    setLoading(true);
    try {
      const result = await stopRobot();
      setStatus(result.message || "Robot stopped");
    } catch (err: any) {
      setStatus(err.message || "Stop failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="text-lg font-semibold">Quick Commands</h3>

      <div className="flex flex-wrap gap-3">
        {places.map((place) => (
          <button
            key={place}
            onClick={() => handleGo(place)}
            disabled={loading}
            className="rounded-lg bg-gray-900 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            Go to {place}
          </button>
        ))}

        <button
          onClick={handleStop}
          disabled={loading}
          className="rounded-lg bg-red-600 px-4 py-2 text-sm text-white disabled:opacity-50"
        >
          Stop Robot
        </button>
      </div>

      <p className="text-sm text-gray-600">{status}</p>
    </div>
  );
}