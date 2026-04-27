import Topbar from "@/components/topbar";
import CommandButtons from "@/components/command-buttons";

export default function NavigationPage() {
  return (
    <div className="space-y-6">
      <Topbar
        title="Navigation"
        subtitle="Send quick place-based navigation commands."
      />
      <CommandButtons mode="navigation" />
    </div>
  );
}