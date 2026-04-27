"use client";

import { useState } from "react";
import Topbar from "@/components/topbar";
import ChatPanel from "@/components/chat-panel";
import { sendChatCommand } from "@/lib/api";

export default function ChatPage() {
  const [answer, setAnswer] = useState("No answer yet.");
  const [response, setResponse] = useState("No response yet.");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSendCommand(message: string) {
    try {
      setLoading(true);
      setError("");

      const result = await sendChatCommand(message);

      setResponse(JSON.stringify(result, null, 2));
      setAnswer(result?.data?.answer ?? result?.message ?? "Command processed.");
    } catch (err) {
      console.error(err);
      setError("Failed to fetch");
      setAnswer("No answer yet.");
      setResponse("No response yet.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Topbar
        title="Chat"
        subtitle="Send natural-language commands to the robot backend."
      />

      <ChatPanel onSendCommand={handleSendCommand} loading={loading} />

      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-red-700">
          {error}
        </div>
      )}

      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="text-2xl font-semibold text-slate-900">Answer</h2>
        <div className="mt-4 rounded-xl bg-slate-100 px-4 py-3 text-slate-800">
          {answer}
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="text-2xl font-semibold text-slate-900">Response</h2>
        <pre className="mt-4 overflow-x-auto rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-800">
          {response}
        </pre>
      </div>
    </div>
  );
}