import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const { query } = await request.json();
    const backendUrl = process.env.BACKEND_URL || "http://localhost:8000";

    console.log("API Route - Backend URL:", backendUrl);
    console.log("API Route - Query:", query);

    const res = await fetch(`${backendUrl}/rag`, {
      method: "POST",
      body: JSON.stringify({ query }),
      headers: { "Content-Type": "application/json" },
    });

    console.log("API Route - Response status:", res.status);

    if (!res.ok) {
      console.error("API Route - Backend error:", res.status, res.statusText);
      return NextResponse.json(
        { error: `Backend responded with ${res.status}: ${res.statusText}` },
        { status: res.status }
      );
    }

    const data = await res.json();
    console.log("API Route - Response data:", data);
    return NextResponse.json(data);
  } catch (error) {
    console.error("API Route - Error:", error);
    return NextResponse.json(
      { error: "Failed to process request", details: String(error) },
      { status: 500 }
    );
  }
}
