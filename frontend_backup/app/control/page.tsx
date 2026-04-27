import Topbar from "@/components/topbar";
import CommandButtons from "@/components/command-buttons";

export default function ControlPage() {
  return (
    <div>
      <Topbar
        title="Control"
        subtitle="Robot control actions such as stop and quick commands."
      />
      <CommandButtons />
    </div>
  );
}