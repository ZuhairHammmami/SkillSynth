/**
 * src/frontend/src/shared/hooks/useNodeCompletion.ts
 * 
 * Node Completion Hook
 * Handles marking concepts as completed and updating the UI in real-time
 * 
 * Usage:
 * const { completeNode, isUpdating, error } = useNodeCompletion(userPath, allConcepts);
 * await completeNode(nodeId);
 */

import { useCallback, useState } from "react";
import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { MasteryProgressionService, type NodeCompletionResult } from "@/shared/services/MasteryProgressionService";

interface UseNodeCompletionResult {
  completeNode: (nodeId: string) => Promise<NodeCompletionResult>;
  isUpdating: boolean;
  error: string | null;
  lastCompleted: NodeCompletionResult | null;
}

/**
 * Hook to handle node completion with real-time DAG updates
 */
export function useNodeCompletion(
  userPath: UserPath | null,
  allConcepts: Map<string, KnowledgeNode> | null
): UseNodeCompletionResult {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastCompleted, setLastCompleted] = useState<NodeCompletionResult | null>(
    null
  );

  const completeNode = useCallback(
    async (nodeId: string): Promise<NodeCompletionResult> => {
      // Validate preconditions
      if (!userPath) {
        const result: NodeCompletionResult = {
          success: false,
          completedNode: null as any,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: "User path not loaded",
        };
        setError(result.error || null);
        return result;
      }

      if (!allConcepts || allConcepts.size === 0) {
        const result: NodeCompletionResult = {
          success: false,
          completedNode: null as any,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: "Concepts not loaded",
        };
        setError(result.error || null);
        return result;
      }

      try {
        setIsUpdating(true);
        setError(null);

        // Call MasteryProgressionService
        const result = await MasteryProgressionService.completeNode(
          userPath.user_id || userPath.userId || '',
          nodeId,
          userPath,
          allConcepts
        );

        setLastCompleted(result);

        if (!result.success) {
          setError(result.error || "Failed to complete node");
        }

        return result;
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "Unknown error occurred";

        setError(errorMessage);

        const result: NodeCompletionResult = {
          success: false,
          completedNode: null as any,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: errorMessage,
        };

        return result;
      } finally {
        setIsUpdating(false);
      }
    },
    [userPath, allConcepts]
  );

  return {
    completeNode,
    isUpdating,
    error,
    lastCompleted,
  };
}
