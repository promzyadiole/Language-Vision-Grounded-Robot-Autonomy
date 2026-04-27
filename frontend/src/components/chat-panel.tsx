"use client";

import { Mic, Square } from "lucide-react";
import { useEffect, useRef, useState } from "react";

type ChatPanelProps = {
  onSendCommand: (message: string) => Promise<void> | void;
  loading?: boolean;
};

declare global {
  interface Window {
    SpeechRecognition?: any;
    webkitSpeechRecognition?: any;
  }
}

export default function ChatPanel({
  onSendCommand,
  loading = false,
}: ChatPanelProps) {
  const [message, setMessage] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(false);
  const [speechStatus, setSpeechStatus] = useState("Microphone ready.");

  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognitionCtor =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognitionCtor) {
      setSpeechSupported(false);
      setSpeechStatus("Voice input is not supported in this browser.");
      return;
    }

    setSpeechSupported(true);

    const recognition = new SpeechRecognitionCtor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      setIsListening(true);
      setSpeechStatus("Listening...");
    };

    recognition.onend = () => {
      setIsListening(false);
      setSpeechStatus("Stopped listening.");
    };

    recognition.onerror = (event: any) => {
      setIsListening(false);
      setSpeechStatus(`Speech error: ${event?.error || "unknown error"}`);
    };

    recognition.onresult = (event: any) => {
      let transcript = "";

      for (let i = 0; i < event.results.length; i += 1) {
        transcript += event.results[i][0].transcript;
      }

      setMessage(transcript.trim());
      setSpeechStatus("Voice captured.");
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleToggleListening = () => {
    if (!recognitionRef.current) return;

    try {
      if (isListening) {
        recognitionRef.current.stop();
      } else {
        recognitionRef.current.start();
      }
    } catch {
      setSpeechStatus("Unable to toggle microphone right now.");
    }
  };

  const handleSend = async () => {
    const trimmed = message.trim();
    if (!trimmed) return;
    await onSendCommand(trimmed);
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <h2 className="text-2xl font-semibold text-slate-900">
        Send Robot Command
      </h2>

      <div className="mt-4 rounded-xl border border-slate-300 focus-within:border-slate-500">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type or speak a command..."
          rows={4}
          className="w-full resize-none rounded-t-xl border-0 px-4 py-3 text-slate-900 outline-none"
        />

        <div className="flex items-center justify-between gap-3 border-t border-slate-200 px-3 py-3">
          <div className="text-sm text-slate-600">{speechStatus}</div>

          <div className="flex items-center gap-2">
            {speechSupported && (
              <button
                type="button"
                onClick={handleToggleListening}
                className={`inline-flex h-11 w-11 items-center justify-center rounded-xl text-white transition ${
                  isListening
                    ? "bg-red-500 hover:bg-red-400"
                    : "bg-emerald-600 hover:bg-emerald-500"
                }`}
                title={isListening ? "Stop listening" : "Start listening"}
              >
                {isListening ? <Square size={18} /> : <Mic size={18} />}
              </button>
            )}

            <button
              type="button"
              onClick={handleSend}
              disabled={loading || !message.trim()}
              className="rounded-xl bg-slate-950 px-5 py-3 font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {loading ? "Sending..." : "Send Command"}
            </button>
          </div>
        </div>
      </div>

      {!speechSupported && (
        <div className="mt-4 rounded-xl bg-slate-100 px-4 py-3 text-sm text-slate-700">
          Voice input is not supported in this browser.
        </div>
      )}
    </div>
  );
}