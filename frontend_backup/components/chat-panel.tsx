"use client";

import { useState } from "react";
import { sendChatCommand } from "@/lib/api";

export default function ChatPanel() {
  const [message, setMessage] = useState("What do you see?");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data = await sendChatCommand(message);
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-4">
      <form
        onSubmit={onSubmit}
        className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
      >
        <h3 className="mb-4 text-lg font-semibold">Send Robot Command</h3>

        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          className="min-h-28 w-full rounded-lg border border-gray-300 p-3 text-sm outline-none focus:border-black"
          placeholder="Type a command like: What do you see?"
        />

        <button
          type="submit"
          disabled={loading}
          className="mt-4 rounded-lg bg-black px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {loading ? "Processing..." : "Send Command"}
        </button>
      </form>

      {error ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold">Response</h3>
        <pre className="overflow-x-auto whitespace-pre-wrap text-sm text-gray-800">
          {result ? JSON.stringify(result, null, 2) : "No response yet."}
        </pre>
      </div>
    </div>
  );
}