import Chat from "@/components/Chat";

export default function Home() {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">LegiSync</h1>
      <p className="text-gray-600 mb-4">
        AI-powered Texas Legislative Bill Search
      </p>
      <Chat />
    </div>
  );
}
