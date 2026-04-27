"use client";

import { useEffect, useState } from "react";
import Topbar from "@/components/topbar";
import VisionPanel from "@/components/vision-panel";
import { getVisionObjectsFastAnnotated, getVisionSummaryFast } from "@/lib/api";

export default function VisionPage() {
  const [summaryData, setSummaryData] = useState<any>(null);
  const [annotatedData, setAnnotatedData] = useState<any>(null);

  useEffect(() => {
    async function load() {
      try {
        const [summary, annotated] = await Promise.all([
          getVisionSummaryFast(),
          getVisionObjectsFastAnnotated(),
        ]);
        setSummaryData(summary);
        setAnnotatedData(annotated);
      } catch (err) {
        console.error(err);
      }
    }

    load();
  }, []);

  return (
    <div>
      <Topbar
        title="Vision"
        subtitle="Fast scene summary, annotated image, and object detections."
      />

      <VisionPanel
        summary={summaryData?.summary}
        annotatedImage={annotatedData?.annotated_image}
        objects={annotatedData?.objects || []}
      />
    </div>
  );
}