import Topbar from "@/components/topbar";

export default function HomePage() {
  return (
    <div>
      <Topbar
        title="Robot Command Center"
        subtitle="FastAPI + Next.js frontend for ROS2 navigation, vision, and chat."
      />

      <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold">Welcome</h3>
        <p className="mt-2 text-sm text-gray-600">
          Use the sidebar to open the dashboard, vision, chat, navigation, and control pages.
        </p>
      </div>
    </div>
  );
}
