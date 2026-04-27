type VisionObject = {
  label: string;
  confidence: number;
  bbox: number[];
  center_px: number[];
  mask_id?: number;
  direction?: string;
};

type VisionPanelProps = {
  summary?: string;
  annotatedImage?: string | null;
  objects?: VisionObject[];
};

export default function VisionPanel({
  summary,
  annotatedImage,
  objects = [],
}: VisionPanelProps) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-2 text-lg font-semibold">Scene Summary</h3>
        <p className="text-sm text-gray-700">
          {summary || "No scene summary available yet."}
        </p>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold">Annotated Vision</h3>
        {annotatedImage ? (
          <img
            src={`data:image/jpeg;base64,${annotatedImage}`}
            alt="Annotated vision"
            className="w-full rounded-lg border border-gray-200"
          />
        ) : (
          <div className="rounded-lg border border-dashed border-gray-300 p-8 text-sm text-gray-500">
            No annotated image available.
          </div>
        )}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
        <h3 className="mb-4 text-lg font-semibold">Detected Objects</h3>
        <div className="space-y-3">
          {objects.length === 0 ? (
            <p className="text-sm text-gray-500">No objects detected.</p>
          ) : (
            objects.map((obj, idx) => (
              <div
                key={`${obj.label}-${idx}`}
                className="rounded-lg border border-gray-100 bg-gray-50 p-3"
              >
                <div className="flex items-center justify-between gap-4">
                  <p className="font-medium text-gray-900">{obj.label}</p>
                  <p className="text-sm text-gray-600">
                    confidence: {obj.confidence.toFixed(2)}
                  </p>
                </div>
                <p className="mt-1 text-sm text-gray-600">
                  direction: {obj.direction || "unknown"}
                </p>
                <p className="mt-1 text-xs text-gray-500">
                  bbox: [{obj.bbox.join(", ")}]
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}