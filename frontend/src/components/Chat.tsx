"use client";
import { useState } from "react";

export default function Chat() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async () => {
    const res = await fetch("/api/rag", {
      method: "POST",
      body: JSON.stringify({ query }),
      headers: { "Content-Type": "application/json" },
    });
    const data = await res.json();
    setResponse(data.result);
  };

  return (
    <div className="mt-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="border p-2 rounded"
        placeholder="Ask about a bill..."
      />
      <button
        onClick={handleSubmit}
        className="ml-2 p-2 bg-blue-500 text-white rounded"
      >
        Submit
      </button>
      <p className="mt-2">{response}</p>
    </div>
  );
}
