import { NextResponse } from "next/server";
import redis from "@/lib/redis";

const REDIS_KEY = "user:prompts";

// DELETE: Remove a prompt
export async function DELETE(
  req: Request,
  { params }: { params: Promise<{ id: string }> }, // Note: params is a Promise in Next.js 15+
) {
  const { id } = await params;
  await redis.hdel(REDIS_KEY, id);
  return NextResponse.json({ success: true });
}

// PUT: Update a prompt
export async function PUT(
  req: Request,
  { params }: { params: Promise<{ id: string }> },
) {
  const { id } = await params;
  const body = await req.json();

  // 1. Get existing to merge (optional, safer)
  const existingStr = await redis.hget(REDIS_KEY, id);
  if (!existingStr)
    return NextResponse.json({ error: "Not found" }, { status: 404 });

  const existing = JSON.parse(existingStr);
  const updated = { ...existing, ...body };

  // 2. Save back
  await redis.hset(REDIS_KEY, id, JSON.stringify(updated));

  return NextResponse.json(updated);
}
