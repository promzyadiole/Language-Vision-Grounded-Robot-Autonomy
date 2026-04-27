const API_BASE = "http://127.0.0.1:8000";

async function handleJsonResponse(res: Response) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Request failed");
  }
  return res.json();
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/api/system/health`, {
    cache: "no-store",
  });
  return handleJsonResponse(res);
}

export async function getRobotStatus() {
  const res = await fetch(`${API_BASE}/api/robot/status`, {
    cache: "no-store",
  });
  return handleJsonResponse(res);
}

export async function getVisionSummaryFast() {
  const res = await fetch(`${API_BASE}/api/vision/scene-summary-fast`, {
    cache: "no-store",
  });
  return handleJsonResponse(res);
}

export async function getVisionObjectsFast() {
  const res = await fetch(`${API_BASE}/api/vision/objects-fast`, {
    cache: "no-store",
  });
  return handleJsonResponse(res);
}

export async function getVisionObjectsFastAnnotated() {
  const res = await fetch(`${API_BASE}/api/vision/objects-fast-annotated`, {
    cache: "no-store",
  });
  return handleJsonResponse(res);
}

export async function sendChatCommand(message: string) {
  const res = await fetch(`${API_BASE}/api/chat/command`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message }),
  });
  return handleJsonResponse(res);
}

export async function stopRobot() {
  const res = await fetch(`${API_BASE}/api/robot/stop`, {
    method: "POST",
  });
  return handleJsonResponse(res);
}

export async function goToPlace(place: string) {
  const res = await fetch(`${API_BASE}/api/navigation/go-to`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ place }),
  });
  return handleJsonResponse(res);
}