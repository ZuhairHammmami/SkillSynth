/**
 * src/frontend/src/app/learn/[conceptId]/page.tsx
 * 
 * Deep Focus Learning Room
 * A distraction-free interface for immersive learning
 * 
 * Design Philosophy:
 * - Minimalist, zen-like aesthetic
 * - Content is the primary focus
 * - Elegant typography and whitespace
 * - Single, clear call-to-action
 * - Soft, sophisticated color palette
 */

"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { toast } from "sonner";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { UserPath } from "@/entities/UserPath";
import { useMasteryPath } from "@/shared/hooks/useMasteryPath";
import { useNodeCompletion } from "@/shared/hooks/useNodeCompletion";
import Link from "next/link";
import { ErrorBoundary } from "@/app/components/ErrorBoundary";

// Mock data generator - replace with real data fetching
function getMockConcept(id: string): KnowledgeNode {
  const concepts: Record<string, KnowledgeNode> = {
    "js-basics": {
      id: "js-basics",
      label: "JavaScript Fundamentals",
      confidenceScore: 0.95,
      prerequisites: [],
      sourceMetadata: {
        sourceType: "academic",
        sourceUrl: "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        lastUpdated: new Date().toISOString(),
        reliabilityScore: 0.95,
      },
    },
    "react-basics": {
      id: "react-basics",
      label: "React Basics",
      confidenceScore: 0.88,
      prerequisites: ["js-basics"],
      sourceMetadata: {
        sourceType: "academic",
        sourceUrl: "https://react.dev",
        lastUpdated: new Date().toISOString(),
        reliabilityScore: 0.92,
      },
    },
    "state-management": {
      id: "state-management",
      label: "State Management",
      confidenceScore: 0.85,
      prerequisites: ["react-basics"],
      sourceMetadata: {
        sourceType: "market",
        sourceUrl: "https://react.dev/learn/managing-state",
        lastUpdated: new Date().toISOString(),
        reliabilityScore: 0.88,
      },
    },
  };

  return concepts[id] || concepts["js-basics"];
}

/**
 * Prerequisite History Breadcrumb
 */
function PrerequisiteHistory({
  prerequisites,
  completed,
}: {
  prerequisites: string[];
  completed: string[];
}) {
  return (
    <div className="mb-8 flex items-center gap-2 text-sm">
      <div className="text-gray-400">Learning Path:</div>
      {prerequisites.length === 0 ? (
        <span className="text-gray-600 italic">No prerequisites</span>
      ) : (
        <div className="flex flex-wrap gap-2">
          {prerequisites.map((prereq, idx) => (
            <div key={prereq} className="flex items-center gap-2">
              <div
                className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                  completed.includes(prereq)
                    ? "bg-emerald-50 text-emerald-700"
                    : "bg-gray-100 text-gray-600"
                }`}
              >
                <span
                  className={`inline-block w-1.5 h-1.5 rounded-full ${
                    completed.includes(prereq) ? "bg-emerald-500" : "bg-gray-400"
                  }`}
                />
                {prereq}
              </div>
              {idx < prerequisites.length - 1 && (
                <span className="text-gray-300">→</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Content Frame
 * Displays concept content from external source
 */
function ContentFrame({
  sourceUrl,
  title,
  isLoading,
}: {
  sourceUrl: string;
  title: string;
  isLoading: boolean;
}) {
  return (
    <div className="relative w-full h-full rounded-xl overflow-hidden bg-white border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-b from-white to-gray-50 z-10">
          <div className="text-center">
            <div className="mb-4 w-12 h-12 rounded-full border-2 border-gray-200 border-t-gray-900 animate-spin mx-auto" />
            <p className="text-sm text-gray-600">Loading {title}...</p>
          </div>
        </div>
      )}

      {/* Note: In production, this would be an iframe that loads the source_url */}
      <div className="w-full h-full p-12 bg-gradient-to-br from-white via-gray-50 to-white overflow-auto">
        <div className="prose prose-sm max-w-none text-gray-700 leading-relaxed">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">{title}</h2>

          <div className="space-y-4 text-sm text-gray-600">
            <p>
              This is where the concept content would be loaded from{" "}
              <code className="bg-gray-100 px-2 py-1 rounded text-xs font-mono">
                {sourceUrl}
              </code>
            </p>

            <p className="text-xs text-gray-500 italic">
              In production, this would render an iframe or fetched content from
              the source URL. For demonstration, educational content from the
              specified source would appear here.
            </p>

            <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-100">
              <p className="text-xs text-blue-700">
                💡 <strong>Tip:</strong> Take notes, pause frequently, and
                actively engage with the material. Real mastery comes from
                focused, deliberate practice.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Master Skill Completion Button
 */
function MasterSkillButton({
  conceptId,
  conceptLabel,
  onComplete,
  isLoading,
  isCompleted,
}: {
  conceptId: string;
  conceptLabel: string;
  onComplete: () => Promise<void>;
  isLoading: boolean;
  isCompleted: boolean;
}) {
  return (
    <button
      onClick={onComplete}
      disabled={isLoading || isCompleted}
      className={`w-full py-4 px-6 rounded-xl font-semibold text-lg transition-all ${
        isCompleted
          ? "bg-emerald-50 text-emerald-700 cursor-default border-2 border-emerald-200"
          : isLoading
            ? "bg-gray-100 text-gray-600 cursor-wait"
            : "bg-gradient-to-r from-blue-600 to-blue-700 text-white hover:shadow-lg hover:-translate-y-1"
      }`}
    >
      <div className="flex items-center justify-center gap-2">
        {isCompleted ? (
          <>
            <span className="text-xl">✓</span>
            <span>Mastered: {conceptLabel}</span>
          </>
        ) : isLoading ? (
          <>
            <div className="w-4 h-4 rounded-full border-2 border-gray-400 border-t-gray-800 animate-spin" />
            <span>Marking as Mastered...</span>
          </>
        ) : (
          <>
            <span>Master Skill</span>
            <span className="text-xl">→</span>
          </>
        )}
      </div>
    </button>
  );
}

/**
 * Main Learning Room Component
 */
export default function LearningRoomPage() {
  const params = useParams();
  const router = useRouter();
  const conceptId = params.conceptId as string;

  // State
  const [concept, setConcept] = useState<KnowledgeNode | null>(null);
  const [isContentLoading, setIsContentLoading] = useState(true);
  const [isCompleted, setIsCompleted] = useState(false);
  const [allConcepts, setAllConcepts] = useState<Map<string, KnowledgeNode> | null>(null);

  // Hooks
  const { userPath, isLoading: isUserPathLoading } = useMasteryPath(allConcepts);
  const { completeNode, isUpdating: isCompletionLoading, error: completionError } = useNodeCompletion(
    userPath,
    allConcepts
  );

  // Initialize concept
  useEffect(() => {
    if (!conceptId) return;

    // Load the specific concept
    const mockConcept = getMockConcept(conceptId);
    setConcept(mockConcept);

    // Load all concepts for path calculation
    const allConceptsMap = new Map([
      [mockConcept.id, mockConcept],
      [getMockConcept("js-basics").id, getMockConcept("js-basics")],
      [getMockConcept("react-basics").id, getMockConcept("react-basics")],
      [getMockConcept("state-management").id, getMockConcept("state-management")],
    ]);

    setAllConcepts(allConceptsMap);
    setIsContentLoading(false);

    // Simulate content loading
    const timer = setTimeout(() => {
      setIsContentLoading(false);
    }, 800);

    return () => clearTimeout(timer);
  }, [conceptId]);

  // Check if concept is already completed
  useEffect(() => {
    if (userPath && concept) {
      setIsCompleted(userPath.pathHistory.includes(concept.id));
    }
  }, [userPath, concept]);

  // Handle skill mastery
  const handleMasterSkill = async () => {
    if (!userPath || !concept) {
      toast.error("Cannot mark as complete", {
        description: "User data or concept not loaded",
      });
      return;
    }

    const result = await completeNode(concept.id);

    if (result.success) {
      setIsCompleted(true);
      toast.success("🎉 Concept Mastered!", {
        description: `You've completed ${concept.label}. ${
          result.newlyAccessibleNodes.length > 0
            ? `${result.newlyAccessibleNodes.length} new concept(s) unlocked!`
            : ""
        }`,
        action: {
          label: "Continue Learning",
          onClick: () => router.push("/mastery-path"),
        },
      });
    } else {
      toast.error("Could not mark as complete", {
        description: result.error || "Unknown error occurred",
      });
    }
  };

  // Loading state
  if (isUserPathLoading || !concept || !userPath) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="mb-4 w-12 h-12 rounded-full border-2 border-gray-200 border-t-gray-900 animate-spin mx-auto" />
          <p className="text-gray-600">Initializing learning room...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Header - Minimal Navigation */}
      <div className="sticky top-0 z-50 border-b border-gray-100 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            href="/mastery-path"
            className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors flex items-center gap-2"
          >
            <span>←</span>
            <span>Back to Path</span>
          </Link>

          <div className="text-xs text-gray-500">
            {userPath.pathHistory.length} concepts mastered
          </div>
        </div>
      </div>

      {/* Main Content */}
      <ErrorBoundary componentName="LearningRoom" fallback={(error, retry) => (
        <div className="max-w-6xl mx-auto px-6 py-12">
          <div className="rounded-lg bg-red-50 p-8 text-center">
            <h2 className="text-2xl font-bold text-red-900 mb-4">Learning Room Temporarily Unavailable</h2>
            <p className="text-red-700 mb-6">The learning content couldn&apos;t load. Your progress is saved.</p>
            <button onClick={retry} className="px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-colors">
              Retry
            </button>
          </div>
        </div>
      )}>
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Prerequisite History */}
        <PrerequisiteHistory
          prerequisites={concept.prerequisites}
          completed={userPath.pathHistory}
        />

        {/* Concept Title */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-3">
            {concept.label}
          </h1>
          <p className="text-gray-600">
            Level {concept.prerequisites?.length || 0} • Confidence:{" "}
            <span className="font-semibold text-gray-900">
              {((concept.confidenceScore || 0) * 100).toFixed(0)}%
            </span>
          </p>
        </div>

        {/* Learning Room - Content Area */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 mb-12">
          {/* Main Content Frame */}
          <div className="lg:col-span-3 flex flex-col">
            <ContentFrame
              sourceUrl={concept.sourceMetadata?.sourceUrl || ""}
              title={concept.label || ""}
              isLoading={isContentLoading}
            />
          </div>

          {/* Sidebar - Progress & Actions */}
          <div className="lg:col-span-1 flex flex-col gap-6">
            {/* Stats Card */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
              <div className="text-3xl font-bold text-blue-900 mb-2">
                {((userPath.pathHistory.length / 10) * 100).toFixed(0)}%
              </div>
              <p className="text-sm text-blue-700">
                Path to Mastery
              </p>
            </div>

            {/* Info Card */}
            <div className="bg-gray-50 rounded-xl p-4 text-sm space-y-3 border border-gray-100">
              <div>
                <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                  Prerequisites
                </div>
                <div className="text-gray-700">
                  {concept.prerequisites.length === 0
                    ? "None - Start here!"
                    : concept.prerequisites.join(", ")}
                </div>
              </div>

              <div>
                <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                  Source
                </div>
                <div className="text-gray-700 line-clamp-1">
                  {concept.sourceMetadata?.sourceType || "unknown"}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Master Skill Button - Full Width */}
        <MasterSkillButton
          conceptId={concept.id}
          conceptLabel={concept.label || ""}
          onComplete={handleMasterSkill}
          isLoading={isCompletionLoading}
          isCompleted={isCompleted}
        />

        {/* Error Message */}
        {completionError && (
          <div className="mt-6 p-4 bg-red-50 rounded-lg border border-red-200 text-red-700 text-sm">
            {completionError}
          </div>
        )}
      </div>
      </ErrorBoundary>
    </div>
  );
}
