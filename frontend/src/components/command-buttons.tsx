"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { goToPlace, stopRobot, sendChatCommand } from "@/lib/api";

type Mode = "navigation" | "control";

type CommandButtonsProps = {
  mode: Mode;
};

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function streamText(
  text: string,
  setValue: (value: string) => void,
  activeId: React.MutableRefObject<number>
) {
  const runId = activeId.current;
  return (async () => {
    let out = "";
    for (const ch of text) {
      if (activeId.current !== runId) return;
      out += ch;
      setValue(out);
      await sleep(12);
    }
  })();
}

function summarizeExecution(result: any, mode: Mode, actionLabel: string) {
  if (!result) {
    return "No response was returned by the backend.";
  }

  const message = result?.message;
  const data = result?.data;

  if (mode === "navigation") {
    if (actionLabel === "stop") {
      return message
        ? `Stop command completed. ${message}`
        : "Stop command completed.";
    }

    const poseText =
      typeof message === "string"
        ? message
        : `Navigation command for ${actionLabel} was sent successfully.`;

    return `Navigation request processed. ${poseText}`;
  }

  if (actionLabel === "stop") {
    return message ? `Robot stop completed. ${message}` : "Robot stop completed.";
  }

  const executionType = data?.execution_type;
  const motionKey = data?.motion_key;
  const cmdVel = data?.cmd_vel;

  if (executionType === "motion" && cmdVel) {
    const parts = [
      `Motion command executed: ${motionKey ?? actionLabel}.`,
      `Linear velocity ${cmdVel.linear_x ?? 0}.`,
      `Angular velocity ${cmdVel.angular_z ?? 0}.`,
      `Duration ${cmdVel.duration_sec ?? 0} seconds.`,
    ];
    return parts.join(" ");
  }

  return message
    ? `Command completed. ${message}`
    : `Command completed for ${actionLabel}.`;
}

export default function CommandButtons({ mode }: CommandButtonsProps) {
  const [result, setResult] = useState<string>("No command sent yet.");
  const [responseText, setResponseText] = useState<string>("No response yet.");
  const [loading, setLoading] = useState<string | null>(null);
  const streamRunRef = useRef(0);

  const title = useMemo(
    () => (mode === "navigation" ? "Quick Navigation" : "Manual Control"),
    [mode]
  );

  useEffect(() => {
    setResult("No command sent yet.");
    setResponseText("No response yet.");
    setLoading(null);
    streamRunRef.current += 1;
  }, [mode]);

  async function runAction(label: string, action: () => Promise<any>) {
    try {
      setLoading(label);
      setResult("Waiting for backend response...");
      setResponseText("Streaming response...");
      streamRunRef.current += 1;

      const res = await action();
      setResult(JSON.stringify(res, null, 2));

      const summary = summarizeExecution(res, mode, label);
      await streamText(summary, setResponseText, streamRunRef);
    } catch (error: any) {
      const msg = error?.message || "Command failed.";
      setResult(msg);
      streamRunRef.current += 1;
      await streamText(`Execution failed. ${msg}`, setResponseText, streamRunRef);
    } finally {
      setLoading(null);
    }
  }

  if (mode === "navigation") {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-2xl font-semibold text-slate-900">{title}</h2>

        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => runAction("kitchen", () => goToPlace("kitchen"))}
            className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white hover:bg-slate-800"
          >
            {loading === "kitchen" ? "Going..." : "Go to kitchen"}
          </button>

          <button
            onClick={() => runAction("garage", () => goToPlace("garage"))}
            className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white hover:bg-slate-800"
          >
            {loading === "garage" ? "Going..." : "Go to garage"}
          </button>

          <button
            onClick={() => runAction("home", () => goToPlace("home"))}
            className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white hover:bg-slate-800"
          >
            {loading === "home" ? "Going..." : "Go to home"}
          </button>

          <button
            onClick={() => runAction("stop", () => stopRobot())}
            className="rounded-xl bg-red-600 px-5 py-3 font-medium text-white hover:bg-red-700"
          >
            {loading === "stop" ? "Stopping..." : "Stop Robot"}
          </button>
        </div>

        <div className="mt-4 rounded-xl bg-slate-50 p-4">
          <h3 className="mb-2 text-lg font-semibold text-slate-900">Response</h3>
          <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
            {responseText}
          </p>
        </div>

        <div className="mt-4 rounded-xl bg-slate-50 p-4">
          <h3 className="mb-2 text-lg font-semibold text-slate-900">Raw Output</h3>
          <pre className="overflow-x-auto whitespace-pre-wrap text-sm text-slate-700">
            {result}
          </pre>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-2xl font-semibold text-slate-900">{title}</h2>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => runAction("forward", () => sendChatCommand("move forward"))}
          className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white hover:bg-slate-800"
        >
          {loading === "forward" ? "Sending..." : "Move Forward"}
        </button>

        <button
          onClick={() => runAction("backward", () => sendChatCommand("move backward"))}
          className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white hover:bg-slate-800"
        >
          {loading === "backward" ? "Sending..." : "Move Backward"}
        </button>

        <button
          onClick={() => runAction("left", () => sendChatCommand("turn left"))}
          className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white hover:bg-slate-800"
        >
          {loading === "left" ? "Sending..." : "Turn Left"}
        </button>

        <button
          onClick={() => runAction("right", () => sendChatCommand("turn right"))}
          className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white hover:bg-slate-800"
        >
          {loading === "right" ? "Sending..." : "Turn Right"}
        </button>

        <button
          onClick={() => runAction("rotate", () => sendChatCommand("rotate"))}
          className="rounded-xl bg-amber-600 px-5 py-3 font-medium text-white hover:bg-amber-700"
        >
          {loading === "rotate" ? "Sending..." : "Rotate"}
        </button>

        <button
          onClick={() => runAction("stop", () => stopRobot())}
          className="rounded-xl bg-red-600 px-5 py-3 font-medium text-white hover:bg-red-700"
        >
          {loading === "stop" ? "Stopping..." : "Stop Robot"}
        </button>
      </div>

      <div className="mt-4 rounded-xl bg-slate-50 p-4">
        <h3 className="mb-2 text-lg font-semibold text-slate-900">Response</h3>
        <p className="whitespace-pre-wrap text-sm leading-7 text-slate-700">
          {responseText}
        </p>
      </div>

      <div className="mt-4 rounded-xl bg-slate-50 p-4">
        <h3 className="mb-2 text-lg font-semibold text-slate-900">Raw Output</h3>
        <pre className="overflow-x-auto whitespace-pre-wrap text-sm text-slate-700">
          {result}
        </pre>
      </div>
    </div>
  );
}