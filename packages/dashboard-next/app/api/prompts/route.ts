import { NextResponse } from "next/server";
import redis from "@/lib/redis";
import { v4 as uuidv4 } from "uuid";

const REDIS_KEY = "user:prompts";

// GET: Fetch all prompts
export async function GET() {
  try {
    // HGETALL returns an object { "id1": "json_string", "id2": "json_string" }
    const data = await redis.hgetall(REDIS_KEY);

    // Convert values from JSON strings back to objects
    const prompts = Object.values(data).map((jsonStr) => JSON.parse(jsonStr));

    return NextResponse.json(prompts);
  } catch (error) {
    console.error("Redis Error:", error);
    return NextResponse.json(
      { error: "Failed to fetch prompts" },
      { status: 500 },
    );
  }
}

// POST: Create a new prompt
export async function POST(req: Request) {
  try {
    const body = await req.json();

    // Create new entry
    const newPrompt = {
      id: uuidv4(),
      title: body.title || "Untitled Prompt",
      summary: body.summary || "No summary provided.",
      inputs: body.inputs || ["text"],
      systemPrompt: body.systemPrompt || "",
      addSysPrompt: body.addSysPrompt || [],
      model: body.model || "gemini-2.5-flash",
      createdAt: new Date().toISOString(),
    };

    // Save to Redis Hash (Field=ID, Value=JSON String)
    await redis.hset(REDIS_KEY, newPrompt.id, JSON.stringify(newPrompt));

    return NextResponse.json(newPrompt);
  } catch (error) {
    return NextResponse.json(
      { error: "Failed to save prompt" },
      { status: 500 },
    );
  }
}
