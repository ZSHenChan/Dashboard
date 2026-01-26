import { GoogleGenAI } from "@google/genai";

// Ensure you have GOOGLE_API_KEY in your .env.local file
const ai = new GoogleGenAI({ apiKey: process.env.GOOGLE_API_KEY });

export async function POST(req: Request) {
  try {
    const { systemPrompt, userPrompt, model, config, image } = await req.json();

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const parts: any[] = [{ text: userPrompt }];

    if (image) {
      // image.data should be the raw base64 string (without "data:image/png;base64," prefix)
      parts.push({
        inlineData: {
          mimeType: image.mimeType,
          data: image.data,
        },
      });
    }
    // 1. Initialize the stream
    // Note: We use generateContentStream instead of generateContent
    const streamResult = await ai.models.generateContentStream({
      model: model || "gemini-3-pro-preview",
      config: {
        systemInstruction: systemPrompt,
        ...config,
      },
      contents: [
        {
          role: "user",
          parts: parts,
        },
      ],
    });

    // 2. Create a ReadableStream to pipe data to the frontend
    const stream = new ReadableStream({
      async start(controller) {
        const encoder = new TextEncoder();
        try {
          // Iterate over the async generator from Google SDK
          for await (const chunk of streamResult) {
            const text = chunk.text;
            if (text) {
              controller.enqueue(encoder.encode(text));
            }
          }
        } catch (err) {
          controller.error(err);
        } finally {
          controller.close();
        }
      },
    });

    // 3. Return the stream response
    return new Response(stream, {
      headers: {
        "Content-Type": "text/plain; charset=utf-8",
      },
    });
  } catch (error) {
    console.error("API Error:", error);
    return new Response(
      JSON.stringify({ error: "Failed to generate content" }),
      {
        status: 500,
      },
    );
  }
}
