import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(request: NextRequest) {
  const path = request.nextUrl.pathname.replace("/api/proxy", "");
  const searchParams = request.nextUrl.search;

  try {
    const response = await fetch(`${API_URL}${path}${searchParams}`, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: "Proxy error", message: String(error) },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  const path = request.nextUrl.pathname.replace("/api/proxy", "");
  const body = await request.json();

  try {
    const response = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: "Proxy error", message: String(error) },
      { status: 500 }
    );
  }
}
