import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const { query } = await request.json();
  const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";
  const res = await fetch(`${backendUrl}/rag`, {
    method: "POST",
    body: JSON.stringify({ query }),
    headers: { "Content-Type": "application/json" },
  });
  const data = await res.json();
  return NextResponse.json(data);
}
