import Topbar from "@/components/topbar";
import CommandButtons from "@/components/command-buttons";

export default function ControlPage() {
  return (
    <div className="space-y-6">
      <Topbar
        title="Control"
        subtitle="Send direct robot motion and stop commands."
      />
      <CommandButtons mode="control" />
    </div>
  );
}