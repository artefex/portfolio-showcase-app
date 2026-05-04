import { ChatContainer } from "@/components/ChatContainer";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <h1 className="mb-8 text-3xl font-bold">Recipe Assistant Showcase</h1>
      <ChatContainer />
    </main>
  );
}
