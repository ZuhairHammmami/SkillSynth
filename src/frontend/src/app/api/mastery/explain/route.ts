/**
 * src/frontend/src/app/api/mastery/explain/route.ts
 * 
 * Alternative Explanation API
 * AI-Powered Content Synthesis using LLM
 * 
 * POST /api/mastery/explain
 * Generates alternative explanations when users struggle with concepts
 * Triggered after 2 failed assessment attempts
 */

import { NextRequest, NextResponse } from "next/server";

interface ExplainRequestBody {
  userId: string;
  conceptId: string;
  attemptNumber: number; // Number of failed attempts
  difficulty?: "beginner" | "intermediate" | "advanced";
  masteredPrerequisites?: string[]; // Concepts user has already mastered
}

interface ExplainResponse {
  success: boolean;
  data?: {
    explanationId: string;
    conceptId: string;
    explanation: string;
    difficulty: string;
    followUpQuestion?: string;
  };
  error?: string;
}

/**
 * POST /api/mastery/explain
 * Generate an alternative explanation for a struggling learner
 * 
 * Request Body:
 * {
 *   userId: UUID,
 *   conceptId: UUID,
 *   attemptNumber: number (should be 2 or more),
 *   difficulty: 'beginner' | 'intermediate' | 'advanced',
 *   masteredPrerequisites: [UUID, UUID, ...]
 * }
 */
export async function POST(
  request: NextRequest
): Promise<NextResponse<ExplainResponse>> {
  let body: ExplainRequestBody = {} as ExplainRequestBody;
  try {
    body = await request.json();

    // Validate required fields
    if (!body.userId || !body.conceptId) {
      return NextResponse.json(
        {
          success: false,
          error: "Missing required fields: userId, conceptId",
        },
        { status: 400 }
      );
    }

    // Only generate alternative explanations after 2+ failed attempts
    if ((body.attemptNumber || 0) < 2) {
      return NextResponse.json(
        {
          success: false,
          error:
            "Alternative explanations available after 2 failed attempts",
        },
        { status: 400 }
      );
    }

    // Verify user authorization
    const authenticatedUserId = request.headers.get("x-user-id");
    if (authenticatedUserId && authenticatedUserId !== body.userId) {
      return NextResponse.json(
        {
          success: false,
          error: "Unauthorized: User ID mismatch",
        },
        { status: 403 }
      );
    }

    // Generate alternative explanation using LLM
    const explanation = await generateAlternativeExplanation({
      conceptId: body.conceptId,
      userId: body.userId,
      difficulty: body.difficulty || "intermediate",
      masteredPrerequisites: body.masteredPrerequisites || [],
    });

    // Store explanation in database for caching
    const explanationId = await storeExplanation(
      body.conceptId,
      body.userId,
      explanation.text,
      explanation.difficulty
    );

    console.log(
      `[Alternative Explanation Generated] User: ${body.userId}, Concept: ${body.conceptId}, Attempt: ${body.attemptNumber}`
    );

    return NextResponse.json(
      {
        success: true,
        data: {
          explanationId,
          conceptId: body.conceptId,
          explanation: explanation.text,
          difficulty: explanation.difficulty,
          followUpQuestion: explanation.followUpQuestion,
        },
      },
      { status: 200 }
    );
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error";

    console.error("[Explanation Generation Error]", errorMessage);

    // Graceful degradation: return a helpful fallback explanation
    const conceptId = body?.conceptId || "unknown";
    const difficulty = body?.difficulty || "intermediate";
    const fallbackExplanation = generateFallbackExplanation(conceptId, difficulty);

    const explanationId = `fallback_${Date.now()}`;

    return NextResponse.json(
      {
        success: true,
        data: {
          explanationId,
          conceptId,
          explanation: fallbackExplanation.text,
          difficulty: fallbackExplanation.difficulty,
          followUpQuestion: fallbackExplanation.followUpQuestion,
          provider: "fallback" as string,
        },
      },
      { status: 200 }
    );
  }
}

function generateFallbackExplanation(conceptId: string, difficulty: string) {
  const text = `Let's explore "${conceptId}" together. 

${conceptId} is an important concept in software development. Think of it as a pattern or technique that helps you solve common problems more efficiently. 

The best way to learn it is to:
1. Understand the problem it solves
2. See simple examples in action
3. Practice with increasingly complex scenarios
4. Build real projects using it

💡 For more information, try searching for "${conceptId}" on MDN Web Docs, freeCodeCamp, or YouTube.`;

  return {
    text,
    difficulty,
    followUpQuestion: `What specific aspect of ${conceptId} would you like to understand better?`,
  };
}

interface GenerateExplanationParams {
  conceptId: string;
  userId: string;
  difficulty: string;
  masteredPrerequisites: string[];
}

interface GeneratedExplanation {
  text: string;
  difficulty: string;
  followUpQuestion?: string;
}

/**
 * Generate alternative explanation using Hybrid LLM Provider
 * 
 * Uses either Ollama (local) or OpenAI based on configuration
 * Supports runtime switching for privacy and cost optimization
 * 
 * Provider Strategy:
 * 1. Try local Ollama (Mistral/Llama3) for privacy and cost
 * 2. Fallback to OpenAI if local is unavailable or disabled
 * 3. Always use OpenAI for complex explanations when needed
 */
async function generateAlternativeExplanation(
  params: GenerateExplanationParams
): Promise<GeneratedExplanation> {
  try {
    // Dynamic provider selection from environment or request context
    const useLocal = process.env.LLM_PROVIDER !== "openai-only";
    const forceProvider = process.env.LLM_FORCE_PROVIDER as "local" | "openai" | undefined;

    // Fetch from hybrid provider
    // Note: In production, import HybridLLMProvider from "@/services/HybridLLMProvider"
    // For now, using a simpler inline implementation that mirrors the service

    const explanation = await generateExplanationViaHybridProvider({
      conceptId: params.conceptId,
      difficulty: params.difficulty as any,
      masteredPrerequisites: params.masteredPrerequisites,
      attemptNumber: 2, // Since we're called after 2+ failed attempts
      useLocal: useLocal && forceProvider !== "openai",
    });

    return explanation;
  } catch (error) {
    console.error("[Explanation Generation Error]", error);
    throw new Error(
      `Failed to generate explanation: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}

/**
 * Hybrid provider explanation generation (Phase 4.0)
 * Attempts local first, falls back to OpenAI
 */
async function generateExplanationViaHybridProvider(options: {
  conceptId: string;
  difficulty: string;
  masteredPrerequisites: string[];
  attemptNumber: number;
  useLocal: boolean;
}): Promise<GeneratedExplanation> {
  const prerequisites =
    options.masteredPrerequisites.length > 0
      ? options.masteredPrerequisites.join(", ")
      : "none";

  const prompt = `You are an expert programming tutor. A student is struggling to understand "${options.conceptId}".
They have already mastered: ${prerequisites}
They have failed ${options.attemptNumber} attempts.

Generate a clear, ${options.difficulty}-level explanation that:
1. Connects to their existing knowledge
2. Uses analogies from their mastered topics
3. Provides a practical, working example
4. Is easy to understand

Keep it concise (2-3 paragraphs). End with a follow-up question.`;

  // Try local provider first if enabled
  if (options.useLocal && process.env.OLLAMA_BASE_URL) {
    try {
      console.log(`[Hybrid Provider] Attempting local generation for concept: ${options.conceptId}`);

      const response = await fetch(`${process.env.OLLAMA_BASE_URL}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: process.env.OLLAMA_MODEL || "mistral",
          prompt,
          stream: false,
          temperature: 0.7,
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (response.ok) {
        const data = await response.json();
        const text = data.response || "";

        console.log(
          `[Ollama Explanation] Concept: ${options.conceptId}, Model: ${process.env.OLLAMA_MODEL}`
        );

        return {
          text,
          difficulty: options.difficulty,
          followUpQuestion: `How would you apply this concept of ${options.conceptId} in a real-world project?`,
          provider: "local",
          generationTimeMs: 0,
        };
      }

      console.warn(`[Ollama] Request failed with status ${response.status}, falling back to OpenAI`);
    } catch (error) {
      console.warn(
        `[Hybrid Provider] Local generation failed, falling back to OpenAI: ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
    }
  }

  // Fallback to OpenAI
  return await generateExplanationViaOpenAI(
    options.conceptId,
    prompt,
    options.difficulty
  );
}

/**
 * OpenAI explanation generation
 */
async function generateExplanationViaOpenAI(
  conceptId: string,
  prompt: string,
  difficulty: string
): Promise<GeneratedExplanation> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    throw new Error("OpenAI API key not configured in environment variables");
  }

  try {
    const response = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`,
      },
      body: JSON.stringify({
        model: process.env.OPENAI_MODEL || "gpt-4",
        messages: [{ role: "user", content: prompt }],
        temperature: 0.7,
        max_tokens: 500,
      }),
      signal: AbortSignal.timeout(15000),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(
        `OpenAI API error: ${response.status} - ${error.error?.message || response.statusText}`
      );
    }

    const data = await response.json();
    const text = data.choices?.[0]?.message?.content || "";

    console.log(`[OpenAI Explanation] Concept: ${conceptId}, Model: ${process.env.OPENAI_MODEL}`);

    return {
      text,
      difficulty,
      followUpQuestion: `How would you apply this concept of ${conceptId} in a real-world project?`,
      provider: "openai",
      generationTimeMs: 0,
    };
  } catch (error) {
    throw new Error(
      `OpenAI explanation generation failed: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}

interface GeneratedExplanation {
  text: string;
  difficulty: string;
  followUpQuestion?: string;
  provider: "local" | "openai";
  generationTimeMs: number;
}

/**
 * Store explanation in alternative_explanations table
 * 
 * TODO: Replace with actual Supabase insert
 */
async function storeExplanation(
  conceptId: string,
  userId: string,
  explanationText: string,
  difficulty: string
): Promise<string> {
  try {
    // TODO: Insert into alternative_explanations table
    // const { data, error } = await supabase
    //   .from('alternative_explanations')
    //   .insert([{
    //     concept_id: conceptId,
    //     generated_by_user_id: userId,
    //     explanation_text: explanationText,
    //     difficulty_level: difficulty,
    //     model_used: 'openai-gpt-4',
    //     created_at: new Date().toISOString()
    //   }])
    //   .select();

    console.log(
      `[Explanation Stored] Concept: ${conceptId}, Difficulty: ${difficulty}`
    );

    return `explanation_${Date.now()}`;
  } catch (error) {
    throw new Error(
      `Failed to store explanation: ${
        error instanceof Error ? error.message : "Unknown error"
      }`
    );
  }
}
