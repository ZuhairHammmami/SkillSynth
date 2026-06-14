"use client";

import { useState, useEffect } from "react";
import { toast } from "sonner";
import { PathResolverService, type LearningPathDAG, type DAGNode } from "@/shared/services/PathResolver";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { UserPath } from "@/entities/UserPath";
import { useConflictDetection } from "@/shared/hooks/useConflictDetection";
import { DAGErrorBoundary } from "@/app/components/ErrorBoundary";

/**
 * Visual component for rendering a single DAG node
 */
function DAGNodeComponent({
  node,
  isHighlighted,
  onNodeClick,
}: {
  node: DAGNode;
  isHighlighted: boolean;
  onNodeClick: (node: DAGNode) => void;
}) {
  return (
    <button
      onClick={() => onNodeClick(node)}
      className={`relative flex flex-col items-center justify-center rounded-lg border-2 px-4 py-3 text-sm font-medium transition-all cursor-pointer hover:shadow-md ${
        node.isCompleted
          ? "border-green-500 bg-green-50 text-green-900 hover:bg-green-100"
          : node.isAccessible
            ? isHighlighted
              ? "border-blue-600 bg-blue-100 text-blue-900 shadow-lg"
              : "border-blue-400 bg-blue-50 text-blue-900 hover:bg-blue-100"
            : "border-gray-300 bg-gray-100 text-gray-600 opacity-60 cursor-not-allowed hover:opacity-70"
      }`}
      disabled={!node.isAccessible && !node.isCompleted}
    >
      <div className="font-semibold">{node.label}</div>
      <div className="mt-1 text-xs opacity-75">
        Confidence: {(node.confidenceScore * 100).toFixed(0)}%
      </div>
      {node.isCompleted && <div className="mt-1 text-xs font-bold">✓ Completed</div>}
      {!node.isAccessible && node.blockedBy.length > 0 && (
        <div className="mt-1 text-xs">
          🔒 Blocked by {node.blockedBy.length} prerequisite{node.blockedBy.length > 1 ? "s" : ""}
        </div>
      )}
    </button>
  );
}

/**
 * Visual component for rendering the DAG layers
 */
function DAGVisualization({
  dag,
  userPath,
  allConcepts,
}: {
  dag: LearningPathDAG;
  userPath: UserPath;
  allConcepts: Map<string, KnowledgeNode>;
}) {
  const [highlightedPath, setHighlightedPath] = useState<Set<string>>(
    new Set(dag.shortestPath.map((n) => n.id))
  );
  const { attemptNodeAccess } = useConflictDetection();

  const handleNodeClick = (node: DAGNode) => {
    if (node.isCompleted) {
      toast.info("Concept Completed", {
        description: `You have already completed ${node.label}.`,
      });
      return;
    }

    if (!node.isAccessible) {
      // Use conflict detection which will show appropriate toast
      attemptNodeAccess(node.id, userPath, allConcepts, undefined, (message) => {
        // Detailed error already shown by the hook
      });
      return;
    }

    // Node is accessible but not completed
    toast.success("Ready to Learn", {
      description: `Start learning ${node.label} now!`,
      action: {
        label: "Begin",
        onClick: () => {
          // Navigate to learning module
          window.location.href = `/learn/${node.id}`;
        },
      },
    });
  };

  return (
    <div className="space-y-8 rounded-lg bg-gradient-to-b from-gray-50 to-gray-100 p-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900">Your Learning Path</h2>
        <p className="mt-2 text-gray-600">
          {dag.completionPercentage}% complete • ~{Math.ceil(dag.estimatedTimeToMastery)} hours to mastery
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mx-auto max-w-md">
        <div className="flex justify-between text-xs text-gray-600">
          <span>Progress</span>
          <span>{dag.completionPercentage}%</span>
        </div>
        <div className="mt-2 h-2 overflow-hidden rounded-full bg-gray-300">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
            style={{ width: `${dag.completionPercentage}%` }}
          />
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-3 gap-4 rounded-lg bg-white p-4">
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded border-2 border-green-500 bg-green-50" />
          <span className="text-sm text-gray-700">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded border-2 border-blue-400 bg-blue-50" />
          <span className="text-sm text-gray-700">Accessible</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-4 w-4 rounded border-2 border-gray-300 bg-gray-100 opacity-60" />
          <span className="text-sm text-gray-700">Blocked</span>
        </div>
      </div>

      {/* Layers */}
      <div className="space-y-8">
        {dag.layers.map((layer, layerIndex) => (
          <div key={layerIndex} className="space-y-3">
            <div className="text-sm font-semibold text-gray-600">
              Level {layerIndex} {layerIndex === 0 ? "(Foundations)" : `(Prerequisites fulfilled)`}
            </div>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {layer.map((node) => (
                <div
                  key={node.id}
                  onMouseEnter={() => {
                    if (node.dependents.length > 0) {
                      setHighlightedPath(new Set([node.id, ...node.dependents]));
                    }
                  }}
                  onMouseLeave={() => setHighlightedPath(new Set(dag.shortestPath.map((n) => n.id)))}
                >
                  <DAGNodeComponent
                    node={node}
                    isHighlighted={highlightedPath.has(node.id)}
                    onNodeClick={handleNodeClick}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Shortest Path Recommendation */}
      {dag.shortestPath.length > 0 && (
        <div className="rounded-lg border-2 border-purple-200 bg-purple-50 p-4">
          <h3 className="font-semibold text-purple-900">Recommended Learning Sequence</h3>
          <div className="mt-3 flex flex-wrap gap-2">
            {dag.shortestPath.map((node, idx) => (
              <div key={node.id} className="flex items-center gap-2">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-purple-600 text-xs font-bold text-white">
                  {idx + 1}
                </div>
                <span className="text-sm text-purple-900">{node.label}</span>
                {idx < dag.shortestPath.length - 1 && (
                  <span className="ml-1 text-purple-400">→</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistics */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg bg-white p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {Array.from(dag.allNodes.values()).filter((n) => n.isCompleted).length}
          </div>
          <div className="text-sm text-gray-600">Completed Concepts</div>
        </div>
        <div className="rounded-lg bg-white p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Array.from(dag.allNodes.values()).filter((n) => n.isAccessible && !n.isCompleted).length}
          </div>
          <div className="text-sm text-gray-600">Ready to Learn</div>
        </div>
        <div className="rounded-lg bg-white p-4 text-center">
          <div className="text-2xl font-bold text-gray-600">
            {Array.from(dag.allNodes.values()).filter((n) => !n.isAccessible).length}
          </div>
          <div className="text-sm text-gray-600">Locked Concepts</div>
        </div>
      </div>
    </div>
  );
}

/**
 * Mastery Path Page - Shows the user's learning journey with Visual DAG
 */
export default function MasteryPathPage() {
  const [dag, setDAG] = useState<LearningPathDAG | null>(null);
  const [userPath, setUserPath] = useState<UserPath | null>(null);
  const [allConcepts, setAllConcepts] = useState<Map<string, KnowledgeNode> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPath = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // TODO: Fetch real user data and concepts from database
        // For now, using mock data
        const mockConcepts = new Map<string, KnowledgeNode>([
          [
            "js-basics",
            {
              id: "js-basics",
              label: "JavaScript Fundamentals",
              confidenceScore: 0.95,
              prerequisites: [],
              sourceMetadata: {
                sourceType: "academic",
                sourceUrl: "https://example.com/js",
                lastUpdated: new Date().toISOString(),
                reliabilityScore: 0.9,
              },
            },
          ],
          [
            "ts-essentials",
            {
              id: "ts-essentials",
              label: "TypeScript Essentials",
              confidenceScore: 0.92,
              prerequisites: ["js-basics"],
              sourceMetadata: {
                sourceType: "market",
                sourceUrl: "https://example.com/ts",
                lastUpdated: new Date().toISOString(),
                reliabilityScore: 0.85,
              },
            },
          ],
          [
            "react-basics",
            {
              id: "react-basics",
              label: "React Basics",
              confidenceScore: 0.88,
              prerequisites: ["js-basics"],
              sourceMetadata: {
                sourceType: "academic",
                sourceUrl: "https://example.com/react",
                lastUpdated: new Date().toISOString(),
                reliabilityScore: 0.9,
              },
            },
          ],
          [
            "react-advanced",
            {
              id: "react-advanced",
              label: "React Advanced Patterns",
              confidenceScore: 0.82,
              prerequisites: ["react-basics", "ts-essentials"],
              sourceMetadata: {
                sourceType: "market",
                sourceUrl: "https://example.com/react-adv",
                lastUpdated: new Date().toISOString(),
                reliabilityScore: 0.8,
              },
            },
          ],
          [
            "node-backend",
            {
              id: "node-backend",
              label: "Node.js Backend",
              confidenceScore: 0.85,
              prerequisites: ["js-basics"],
              sourceMetadata: {
                sourceType: "academic",
                sourceUrl: "https://example.com/node",
                lastUpdated: new Date().toISOString(),
                reliabilityScore: 0.88,
              },
            },
          ],
        ]);

        // Mock user path (completed js-basics)
        const mockUserPath: UserPath = {
          id: "path-123",
          user_id: "user-123",
          userId: "user-123",
          title: "JavaScript Mastery",
          pathName: "JavaScript Mastery",
          goalConceptId: "js-advanced",
          nodes: [],
          currentNode: "js-basics",
          pathHistory: ["js-basics"],
          completedAssessments: [],
          skillOverrides: {},
          progress: 25,
          created_at: new Date().toISOString(),
          createdAt: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };

        setAllConcepts(mockConcepts);
        setUserPath(mockUserPath);

        const result = PathResolverService.resolvePath(mockUserPath, mockConcepts);

        if (result.success && result.dag) {
          setDAG(result.dag);
        } else {
          setError(result.error || "Failed to resolve learning path");
          toast.error("Failed to load mastery path", {
            description: result.error,
          });
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : "Unknown error";
        setError(errorMessage);
        toast.error("Error loading mastery path", {
          description: errorMessage,
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadPath();
  }, []);

  return (
    <div className="mx-auto max-w-6xl py-12 px-4">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900">Mastery Path</h1>
        <p className="mt-2 text-lg text-gray-600">
          Your personalized learning journey to engineering mastery
        </p>
      </div>

      {isLoading && (
        <div className="flex justify-center py-12">
          <div className="text-lg text-gray-500">Loading your learning path...</div>
        </div>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 p-4 text-red-700">
          <p className="font-semibold">Error loading path</p>
          <p className="mt-1 text-sm">{error}</p>
        </div>
      )}

      {dag && userPath && allConcepts && (
        <DAGErrorBoundary>
          <DAGVisualization dag={dag} userPath={userPath} allConcepts={allConcepts} />
        </DAGErrorBoundary>
      )}
    </div>
  );
}
