import Topbar from "@/components/topbar";
import ChatPanel from "@/components/chat-panel";

export default function ChatPage() {
  return (
    <div>
      <Topbar
        title="Chat"
        subtitle="Send natural-language commands to the robot backend."
      />
      <ChatPanel />
    </div>
  );
}