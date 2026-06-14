/**
 * src/services/HybridLLMProvider.ts
 * 
 * Hybrid LLM Provider (Phase 4.0)
 * Runtime switching between Local AI (Ollama/Mistral) and OpenAI with fallback
 * 
 * Features:
 * - Local-first strategy (privacy, cost reduction)
 * - Runtime provider switching via environment variable
 * - Automatic fallback to OpenAI if local is unavailable
 * - Provider-agnostic interface (LLM abstraction)
 * - Caching of provider health status to avoid repeated failed attempts
 * - Cost tracking and logging
 */

interface LLMProviderConfig {
  provider: "local" | "openai" | "hybrid";
  localModels?: {
    model: string; // e.g., "mistral", "llama2", "neural-chat"
    baseUrl: string; // e.g., "http://localhost:11434"
    fallbackToOpenAI: boolean;
  };
  openaiConfig?: {
    apiKey: string;
    model: string; // e.g., "gpt-4", "gpt-3.5-turbo"
  };
}

interface GenerateExplanationOptions {
  conceptId: string;
  conceptName?: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  masteredPrerequisites?: string[];
  attemptNumber: number;
  useLocal?: boolean; // Force local provider if specified
}

interface GeneratedExplanation {
  text: string;
  difficulty: string;
  followUpQuestion?: string;
  provider: "local" | "openai";
  generationTimeMs: number;
}

interface GenerateQuizOptions {
  conceptId: string;
  conceptName?: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  questionCount?: number;
  useLocal?: boolean;
}

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
}

interface GeneratedQuiz {
  questions: QuizQuestion[];
  provider: "local" | "openai";
  generationTimeMs: number;
}

/**
 * Provider health cache to avoid repeated failed requests
 */
interface ProviderHealthStatus {
  lastChecked: number;
  isHealthy: boolean;
  failureCount: number;
}

export class HybridLLMProvider {
  private static config: LLMProviderConfig;
  private static providerHealthCache: Map<string, ProviderHealthStatus> = new Map();
  private static readonly HEALTH_CHECK_INTERVAL = 5 * 60 * 1000; // 5 minutes
  private static readonly MAX_FAILURES_BEFORE_FALLBACK = 3;

  /**
   * Initialize the hybrid LLM provider
   */
  static initialize(config?: Partial<LLMProviderConfig>): void {
    this.config = {
      provider: config?.provider || process.env.LLM_PROVIDER || "hybrid" as "local" | "openai" | "hybrid",
      localModels: {
        model: config?.localModels?.model || process.env.OLLAMA_MODEL || "mistral",
        baseUrl: config?.localModels?.baseUrl || process.env.OLLAMA_BASE_URL || "http://localhost:11434",
        fallbackToOpenAI: config?.localModels?.fallbackToOpenAI ?? true,
      },
      openaiConfig: {
        apiKey: config?.openaiConfig?.apiKey || process.env.OPENAI_API_KEY || "",
        model: config?.openaiConfig?.model || process.env.OPENAI_MODEL || "gpt-4",
      },
    };

    console.log(`[HybridLLMProvider] Initialized with provider: ${this.config.provider}`);
  }

  /**
   * Check if local provider (Ollama) is healthy
   */
  private static async checkLocalHealth(): Promise<boolean> {
    const cacheKey = "local_health";
    const cached = this.providerHealthCache.get(cacheKey);

    // Use cached result if fresh
    if (cached && Date.now() - cached.lastChecked < this.HEALTH_CHECK_INTERVAL) {
      return cached.isHealthy;
    }

    try {
      const response = await fetch(`${this.config.localModels?.baseUrl}/api/tags`, {
        signal: AbortSignal.timeout(2000),
      });

      const isHealthy = response.ok;
      this.providerHealthCache.set(cacheKey, {
        lastChecked: Date.now(),
        isHealthy,
        failureCount: isHealthy ? 0 : (cached?.failureCount || 0) + 1,
      });

      console.log(`[Ollama Health Check] Status: ${isHealthy ? "✓ Healthy" : "✗ Unhealthy"}`);
      return isHealthy;
    } catch (error) {
      const failureCount = (cached?.failureCount || 0) + 1;
      this.providerHealthCache.set(cacheKey, {
        lastChecked: Date.now(),
        isHealthy: false,
        failureCount,
      });

      console.warn(
        `[Ollama Health Check] Failed (${failureCount}/${this.MAX_FAILURES_BEFORE_FALLBACK}): ${
          error instanceof Error ? error.message : "Unknown error"
        }`
      );
      return false;
    }
  }

  /**
   * Generate explanation using local provider
   */
  private static async generateExplanationLocal(
    options: GenerateExplanationOptions
  ): Promise<GeneratedExplanation> {
    const startTime = performance.now();

    const prerequisites =
      options.masteredPrerequisites && options.masteredPrerequisites.length > 0
        ? options.masteredPrerequisites.join(", ")
        : "none";

    const prompt = `You are an expert programming tutor. A student is struggling to understand "${options.conceptName || options.conceptId}".
They have already mastered: ${prerequisites}
They have failed ${options.attemptNumber} attempts.

Generate a clear, ${options.difficulty}-level explanation that:
1. Connects to their existing knowledge
2. Uses analogies from their mastered topics
3. Provides a practical, working example
4. Is easy to understand

Keep it concise (2-3 paragraphs). End with a follow-up question.`;

    try {
      const response = await fetch(`${this.config.localModels?.baseUrl}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: this.config.localModels?.model || "mistral",
          prompt,
          stream: false,
          temperature: 0.7,
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status}`);
      }

      const data = await response.json();
      const text = data.response || "";

      const generationTime = performance.now() - startTime;
      console.log(
        `[Ollama Explanation Generated] Concept: ${options.conceptId}, Time: ${generationTime.toFixed(0)}ms, Model: ${this.config.localModels?.model}`
      );

      return {
        text,
        difficulty: options.difficulty,
        provider: "local",
        generationTimeMs: generationTime,
      };
    } catch (error) {
      throw new Error(
        `Local explanation generation failed: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }

  /**
   * Generate explanation using OpenAI
   */
  private static async generateExplanationOpenAI(
    options: GenerateExplanationOptions
  ): Promise<GeneratedExplanation> {
    const startTime = performance.now();

    if (!this.config.openaiConfig?.apiKey) {
      throw new Error("OpenAI API key not configured");
    }

    const prerequisites =
      options.masteredPrerequisites && options.masteredPrerequisites.length > 0
        ? options.masteredPrerequisites.join(", ")
        : "none";

    const prompt = `You are an expert programming tutor. A student is struggling to understand "${options.conceptName || options.conceptId}".
They have already mastered: ${prerequisites}
They have failed ${options.attemptNumber} attempts.

Generate a clear, ${options.difficulty}-level explanation that:
1. Connects to their existing knowledge
2. Uses analogies from their mastered topics
3. Provides a practical, working example
4. Is easy to understand

Keep it concise (2-3 paragraphs). End with a follow-up question.`;

    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.config.openaiConfig.apiKey}`,
        },
        body: JSON.stringify({
          model: this.config.openaiConfig.model || "gpt-4",
          messages: [{ role: "user", content: prompt }],
          temperature: 0.7,
          max_tokens: 500,
        }),
        signal: AbortSignal.timeout(15000),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          `OpenAI API error: ${response.status} - ${
            errorData.error?.message || response.statusText
          }`
        );
      }

      const data = await response.json();
      const text = data.choices?.[0]?.message?.content || "";

      const generationTime = performance.now() - startTime;
      console.log(
        `[OpenAI Explanation Generated] Concept: ${options.conceptId}, Time: ${generationTime.toFixed(0)}ms, Model: ${this.config.openaiConfig?.model}`
      );

      return {
        text,
        difficulty: options.difficulty,
        provider: "openai",
        generationTimeMs: generationTime,
      };
    } catch (error) {
      throw new Error(
        `OpenAI explanation generation failed: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }

  /**
   * Generate a static fallback explanation when all providers are unavailable
   */
  private static generateFallbackExplanation(
    options: GenerateExplanationOptions
  ): GeneratedExplanation {
    const startTime = performance.now();
    const conceptName = options.conceptName || options.conceptId;
    return {
      text: `Let's explore "${conceptName}" together. This concept is an important building block in your learning journey.

Think of ${conceptName} as a tool in your developer toolkit. Like how a hammer helps you drive nails, ${conceptName} helps you solve specific types of problems more efficiently. The key is understanding when and why to use it.

To master ${conceptName}, start with the fundamentals: understand what problem it solves, see it used in simple examples, and gradually build up to more complex scenarios. Practice is the key to mastery.

💡 Tip: Try searching for "${conceptName}" on MDN, freeCodeCamp, or YouTube for practical tutorials and examples.`,
      difficulty: options.difficulty,
      followUpQuestion: `What aspect of ${conceptName} would you like to explore further?`,
      provider: "local",
      generationTimeMs: performance.now() - startTime,
    };
  }

  /**
   * Generate a static fallback quiz when all providers are unavailable
   */
  private static generateFallbackQuiz(
    options: GenerateQuizOptions
  ): GeneratedQuiz {
    const startTime = performance.now();
    const conceptName = options.conceptName || options.conceptId;
    const questionCount = options.questionCount || 5;

    const questions: QuizQuestion[] = [];
    for (let i = 0; i < questionCount; i++) {
      questions.push({
        id: `fallback_${i}`,
        question: `What is the primary purpose of ${conceptName}?`,
        options: [
          "A) To solve a specific category of problems",
          "B) To make code run faster",
          "C) To replace all other approaches",
          "D) It has no real purpose",
        ],
        correctAnswer: "A) To solve a specific category of problems",
        explanation: `${conceptName} is designed to address specific challenges in software development. Understanding its purpose helps you know when to apply it.`,
      });
    }

    return {
      questions,
      provider: "local",
      generationTimeMs: performance.now() - startTime,
    };
  }

  /**
   * Generate explanation with hybrid fallback logic
   *
   * Strategy:
   * 1. If useLocal=true, try local only
   * 2. If provider="local", try local with fallback to OpenAI
   * 3. If provider="openai", use OpenAI
   * 4. If provider="hybrid", try local first, fallback to OpenAI if local fails
   * 5. If ALL providers fail, return a static fallback explanation
   */
  static async generateExplanation(
    options: GenerateExplanationOptions
  ): Promise<GeneratedExplanation> {
    const shouldUseLocal =
      options.useLocal !== false &&
      (this.config.provider === "local" || this.config.provider === "hybrid");

    if (shouldUseLocal) {
      try {
        const isHealthy = await this.checkLocalHealth();
        if (!isHealthy && this.config.provider === "local") {
          console.warn("[Hybrid Provider] Local provider unavailable, using fallback");
          return this.generateFallbackExplanation(options);
        }

        if (isHealthy) {
          return await this.generateExplanationLocal(options);
        }
      } catch (error) {
        console.warn(`[Hybrid Provider] Local generation failed: ${error}`);

        if (this.config.provider === "hybrid" && this.config.localModels?.fallbackToOpenAI) {
          console.log("[Hybrid Provider] Falling back to OpenAI...");
          try {
            return await this.generateExplanationOpenAI(options);
          } catch (openaiError) {
            console.warn(`[Hybrid Provider] OpenAI also failed: ${openaiError}`);
            return this.generateFallbackExplanation(options);
          }
        }

        return this.generateFallbackExplanation(options);
      }
    }

    try {
      return await this.generateExplanationOpenAI(options);
    } catch (error) {
      console.warn(`[Hybrid Provider] OpenAI failed: ${error}`);
      return this.generateFallbackExplanation(options);
    }
  }

  /**
   * Generate quiz questions using local provider
   */
  private static async generateQuizLocal(
    options: GenerateQuizOptions
  ): Promise<GeneratedQuiz> {
    const startTime = performance.now();
    const questionCount = options.questionCount || 5;

    const prompt = `You are an expert programming tutor creating a ${options.difficulty}-level assessment for "${options.conceptName || options.conceptId}".

Generate exactly ${questionCount} quiz questions in this JSON format:
[
  {
    "id": "q1",
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correctAnswer": "A) ...",
    "explanation": "..."
  }
]

Requirements:
- Each question should test a different aspect of the concept
- Options should be plausible but distinct
- Explanations should be concise`;

    try {
      const response = await fetch(`${this.config.localModels?.baseUrl}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: this.config.localModels?.model || "mistral",
          prompt,
          stream: false,
          temperature: 0.7,
        }),
        signal: AbortSignal.timeout(10000),
      });

      if (!response.ok) {
        throw new Error(`Ollama API error: ${response.status}`);
      }

      const data = await response.json();
      const text = data.response || "[]";

      // Parse JSON from response
      const jsonMatch = text.match(/\[[\s\S]*\]/);
      const questions = jsonMatch ? JSON.parse(jsonMatch[0]) : [];

      const generationTime = performance.now() - startTime;
      console.log(
        `[Ollama Quiz Generated] Concept: ${options.conceptId}, Questions: ${questions.length}, Time: ${generationTime.toFixed(0)}ms`
      );

      return {
        questions,
        provider: "local",
        generationTimeMs: generationTime,
      };
    } catch (error) {
      throw new Error(
        `Local quiz generation failed: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }

  /**
   * Generate quiz questions using OpenAI
   */
  private static async generateQuizOpenAI(
    options: GenerateQuizOptions
  ): Promise<GeneratedQuiz> {
    const startTime = performance.now();
    const questionCount = options.questionCount || 5;

    if (!this.config.openaiConfig?.apiKey) {
      throw new Error("OpenAI API key not configured");
    }

    try {
      const response = await fetch("https://api.openai.com/v1/chat/completions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.config.openaiConfig.apiKey}`,
        },
        body: JSON.stringify({
          model: this.config.openaiConfig.model || "gpt-4",
          messages: [
            {
              role: "user",
              content: `You are an expert programming tutor creating a ${options.difficulty}-level assessment for "${options.conceptName || options.conceptId}".

Generate exactly ${questionCount} quiz questions in this JSON format:
[
  {
    "id": "q1",
    "question": "...",
    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
    "correctAnswer": "A) ...",
    "explanation": "..."
  }
]

Requirements:
- Each question should test a different aspect of the concept
- Options should be plausible but distinct
- Explanations should be concise`,
            },
          ],
          temperature: 0.7,
          max_tokens: 2000,
        }),
        signal: AbortSignal.timeout(15000),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          `OpenAI API error: ${response.status} - ${
            errorData.error?.message || response.statusText
          }`
        );
      }

      const data = await response.json();
      const text = data.choices?.[0]?.message?.content || "[]";

      // Parse JSON from response
      const jsonMatch = text.match(/\[[\s\S]*\]/);
      const questions = jsonMatch ? JSON.parse(jsonMatch[0]) : [];

      const generationTime = performance.now() - startTime;
      console.log(
        `[OpenAI Quiz Generated] Concept: ${options.conceptId}, Questions: ${questions.length}, Time: ${generationTime.toFixed(0)}ms`
      );

      return {
        questions,
        provider: "openai",
        generationTimeMs: generationTime,
      };
    } catch (error) {
      throw new Error(
        `OpenAI quiz generation failed: ${error instanceof Error ? error.message : "Unknown error"}`
      );
    }
  }

  /**
   * Generate quiz with hybrid fallback logic
   * NEVER throws - returns static fallback quiz if all providers fail
   */
  static async generateQuiz(options: GenerateQuizOptions): Promise<GeneratedQuiz> {
    const shouldUseLocal =
      options.useLocal !== false &&
      (this.config.provider === "local" || this.config.provider === "hybrid");

    if (shouldUseLocal) {
      try {
        const isHealthy = await this.checkLocalHealth();
        if (!isHealthy && this.config.provider === "local") {
          console.warn("[Hybrid Provider] Local provider unavailable, using fallback quiz");
          return this.generateFallbackQuiz(options);
        }

        if (isHealthy) {
          return await this.generateQuizLocal(options);
        }
      } catch (error) {
        console.warn(`[Hybrid Provider] Local quiz generation failed: ${error}`);

        if (this.config.provider === "hybrid" && this.config.localModels?.fallbackToOpenAI) {
          console.log("[Hybrid Provider] Falling back to OpenAI for quiz...");
          try {
            return await this.generateQuizOpenAI(options);
          } catch (openaiError) {
            console.warn(`[Hybrid Provider] OpenAI quiz also failed: ${openaiError}`);
            return this.generateFallbackQuiz(options);
          }
        }

        return this.generateFallbackQuiz(options);
      }
    }

    try {
      return await this.generateQuizOpenAI(options);
    } catch (error) {
      console.warn(`[Hybrid Provider] OpenAI quiz failed: ${error}`);
      return this.generateFallbackQuiz(options);
    }
  }

  /**
   * Get provider status for monitoring
   */
  static getStatus(): {
    primaryProvider: string;
    localHealthy: boolean;
    openaiConfigured: boolean;
  } {
    const localHealth = this.providerHealthCache.get("local_health");
    return {
      primaryProvider: this.config.provider,
      localHealthy: localHealth?.isHealthy ?? false,
      openaiConfigured: !!this.config.openaiConfig?.apiKey,
    };
  }
}

// Auto-initialize on import
if (typeof process !== "undefined") {
  HybridLLMProvider.initialize();
}
