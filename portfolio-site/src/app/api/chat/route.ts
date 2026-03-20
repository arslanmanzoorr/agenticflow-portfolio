import { NextRequest } from "next/server";
import { projects } from "@/data/projects";
import { services } from "@/data/services";
import { testimonials } from "@/data/testimonials";

function buildPortfolioContext(): string {
  let ctx = `## About Arslan Manzoor\n`;
  ctx += `- Title: AI Automation Engineer\n`;
  ctx += `- Brand: AgenticFlow\n`;
  ctx += `- Specialties: Agentic AI workflows, n8n pipeline automation, Python APIs, intelligent integrations\n`;
  ctx += `- Value proposition: Eliminates 20+ hours of manual work per week through AI automation\n`;
  ctx += `- Status: Available for new projects\n\n`;

  ctx += `## Services Offered (${services.length})\n`;
  for (const s of services) {
    ctx += `- **${s.title}**: ${s.description}\n`;
  }
  ctx += `\n`;

  ctx += `## Projects Portfolio (${projects.length} projects)\n`;
  for (const p of projects) {
    ctx += `- **${p.title}** [${p.category}] — ${p.tagline} | Tools: ${p.tools.join(", ")}${p.featured ? " | ⭐ Featured" : ""}\n`;
  }
  ctx += `\n`;

  ctx += `## Client Testimonials (${testimonials.length})\n`;
  for (const t of testimonials) {
    ctx += `- **${t.name}** (${t.role}, ${t.company}): "${t.text.slice(0, 120)}..."\n`;
  }
  ctx += `\n`;

  ctx += `## Technical Skills\n`;
  const allTools = [...new Set(projects.flatMap((p) => p.tools))];
  ctx += `- Tools & Platforms: ${allTools.join(", ")}\n`;
  ctx += `- Core: n8n, Python, FastAPI, OpenAI, Apify, Airtable, HubSpot, Shopify\n`;
  ctx += `- AI/ML: GPT-4, Claude, LangChain, autonomous agents\n`;
  ctx += `- Infrastructure: Docker, webhooks, REST APIs, WebSockets\n`;

  return ctx;
}

function createSystemPrompt(context: string): string {
  return `You are Arslan's AI portfolio assistant embedded on his website. You help visitors learn about Arslan's work, services, and expertise in AI automation.

## Your Role
- Answer questions about Arslan's projects, services, and technical skills
- Help potential clients understand which service fits their needs
- Provide details about specific projects when asked
- Be friendly, professional, and concise
- Encourage visitors to reach out via the Contact page for custom work

## Guidelines
- Keep responses under 200 words unless asked for details
- Use markdown formatting (bold, lists) for readability
- Reference specific projects and data when relevant
- If asked about pricing, say to reach out via the Contact page for a custom quote
- Be enthusiastic about automation and AI — reflect Arslan's passion
- If asked something outside your knowledge, direct them to the Contact page

## Portfolio Data
${context}`;
}

export async function POST(req: NextRequest) {
  try {
    const { message, history = [] } = await req.json();

    if (!message || typeof message !== "string") {
      return Response.json({ error: "Message is required" }, { status: 400 });
    }

    const apiKey = process.env.OPENROUTER_API_KEY;
    if (!apiKey) {
      return Response.json(
        {
          error: "Chat not configured",
          message: "Set OPENROUTER_API_KEY in .env.local to enable the AI chatbot",
        },
        { status: 503 }
      );
    }

    const model = process.env.OPENROUTER_MODEL || "anthropic/claude-sonnet-4";
    const context = buildPortfolioContext();
    const systemPrompt = createSystemPrompt(context);

    const messages = [
      { role: "system", content: systemPrompt },
      ...history.slice(-20),
      { role: "user", content: message },
    ];

    const response = await fetch(
      "https://openrouter.ai/api/v1/chat/completions",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${apiKey}`,
          "HTTP-Referer": "https://arslanmanzoor.dev",
          "X-Title": "Arslan Portfolio",
        },
        body: JSON.stringify({
          model,
          messages,
          stream: true,
          max_tokens: 800,
          temperature: 0.7,
        }),
      }
    );

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`OpenRouter API error (${response.status}): ${error}`);
    }

    // Stream the response back via SSE
    const encoder = new TextEncoder();
    const readable = new ReadableStream({
      async start(controller) {
        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines.pop() || "";

            for (const line of lines) {
              const trimmed = line.trim();
              if (!trimmed || !trimmed.startsWith("data: ")) continue;

              const data = trimmed.slice(6);
              if (data === "[DONE]") {
                controller.enqueue(encoder.encode("data: [DONE]\n\n"));
                continue;
              }

              try {
                const parsed = JSON.parse(data);
                const content = parsed.choices?.[0]?.delta?.content;
                if (content) {
                  controller.enqueue(
                    encoder.encode(
                      `data: ${JSON.stringify({ content })}\n\n`
                    )
                  );
                }
              } catch {
                // skip malformed chunks
              }
            }
          }
        } catch (err) {
          controller.enqueue(
            encoder.encode(
              `data: ${JSON.stringify({ error: (err as Error).message })}\n\n`
            )
          );
        } finally {
          controller.close();
        }
      },
    });

    return new Response(readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  } catch (err) {
    console.error("[CHAT] Error:", (err as Error).message);
    return Response.json(
      { error: "Chat failed", message: (err as Error).message },
      { status: 500 }
    );
  }
}

export async function GET() {
  const configured = !!process.env.OPENROUTER_API_KEY;
  return Response.json({
    configured,
    model: process.env.OPENROUTER_MODEL || "anthropic/claude-sonnet-4",
  });
}
