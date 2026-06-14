/**
 * src/frontend/src/shared/services/MasteryProgressionService.ts
 * 
 * Live Mastery Engine
 * Handles real-time mastery progression, DAG recalculation, and node unlocking
 * 
 * Features:
 * - Mark concepts as completed
 * - Instantly recalculate DAG accessibility
 * - Return newly unlocked nodes to UI
 * - Persist changes to database
 */

import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { UserPath } from "@/entities/UserPath";
import { PathResolverService, type LearningPathDAG } from "./PathResolver";

export interface NodeCompletionResult {
  success: boolean;
  completedNode: KnowledgeNode;
  newlyAccessibleNodes: KnowledgeNode[];
  updatedDAG: LearningPathDAG | null;
  error?: string;
}

export interface ProgressionUpdate {
  userId: string;
  completedNodeId: string;
  timestamp: string;
}

export class MasteryProgressionService {
  /**
   * Mark a concept as completed and recalculate accessibility
   *
   * This function:
   * 1. Validates the node can be completed (already accessible)
   * 2. Updates user_mastery table with new path history
   * 3. Recalculates the DAG to identify newly accessible nodes
   * 4. Returns the updated state to the UI
   *
   * @param userId - The user's Supabase auth.uid()
   * @param nodeId - ID of the concept to mark as completed
   * @param currentUserPath - Current user mastery state
   * @param allConcepts - All available knowledge concepts
   * @returns NodeCompletionResult with new accessible nodes
   */
  static async completeNode(
    userId: string,
    nodeId: string,
    currentUserPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ): Promise<NodeCompletionResult> {
    try {
      // Step 1: Validate the node exists and is accessible
      const node = allConcepts.get(nodeId);

      if (!node) {
        return {
          success: false,
          completedNode: null as any,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: `Concept ${nodeId} not found`,
        };
      }

      // Step 2: Check if user can complete this node (it must be accessible)
      const currentDAG = PathResolverService.resolvePath(
        currentUserPath,
        allConcepts
      );

      if (!currentDAG.success || !currentDAG.dag) {
        return {
          success: false,
          completedNode: node,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: "Failed to calculate current DAG state",
        };
      }

      const currentNode = currentDAG.dag.allNodes.get(nodeId);

      if (!currentNode) {
        return {
          success: false,
          completedNode: node,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: `Node ${nodeId} not found in current DAG`,
        };
      }

      // Node must either be accessible or already completed
      if (!currentNode.isAccessible && !currentNode.isCompleted) {
        return {
          success: false,
          completedNode: node,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: "Cannot complete node: prerequisites not met",
        };
      }

      // Step 3: Add node to path history if not already there
      const newPathHistory = Array.from(
        new Set([...currentUserPath.pathHistory, nodeId])
      );

      // Create updated user path
      const updatedUserPath: UserPath = {
        ...currentUserPath,
        pathHistory: newPathHistory,
        currentNode: nodeId,
        updatedAt: new Date().toISOString(),
      };

      // Step 4: Persist to database
      const persistResult = await this.persistProgressionUpdate(
        userId,
        nodeId,
        newPathHistory
      );

      if (!persistResult.success) {
        return {
          success: false,
          completedNode: node,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: `Failed to persist progress: ${persistResult.error}`,
        };
      }

      // Step 5: Recalculate DAG with new completion
      const newDAGResult = PathResolverService.resolvePath(
        updatedUserPath,
        allConcepts
      );

      if (!newDAGResult.success || !newDAGResult.dag) {
        return {
          success: false,
          completedNode: node,
          newlyAccessibleNodes: [],
          updatedDAG: null,
          error: "Failed to recalculate DAG",
        };
      }

      // Step 6: Identify newly accessible nodes
      const newlyAccessible = this.identifyNewlyAccessibleNodes(
        currentDAG.dag,
        newDAGResult.dag,
        allConcepts
      );

      // Success! Return the result
      return {
        success: true,
        completedNode: node,
        newlyAccessibleNodes: newlyAccessible,
        updatedDAG: newDAGResult.dag,
      };
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : "Unknown error";

      return {
        success: false,
        completedNode: null as any,
        newlyAccessibleNodes: [],
        updatedDAG: null,
        error: errorMessage,
      };
    }
  }

  /**
   * Persist progression update to database
   * Updates the user_mastery table with the new path history
   */
  private static async persistProgressionUpdate(
    userId: string,
    completedNodeId: string,
    pathHistory: string[]
  ): Promise<{ success: boolean; error?: string }> {
    try {
      // TODO: Replace with actual Supabase update
      // This would be:
      // const { error } = await supabase
      //   .from('user_mastery')
      //   .update({
      //     current_node_id: completedNodeId,
      //     path_history: pathHistory,
      //     updated_at: new Date().toISOString(),
      //   })
      //   .eq('user_id', userId);

      // Mock implementation
      const response = await fetch("/api/mastery/progress", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          userId,
          completedNodeId,
          pathHistory,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        return {
          success: false,
          error: error.error || `HTTP ${response.status}`,
        };
      }

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  /**
   * Compare old and new DAG to find newly accessible nodes
   * These are nodes that were blocked before but are now accessible
   */
  private static identifyNewlyAccessibleNodes(
    oldDAG: LearningPathDAG,
    newDAG: LearningPathDAG,
    allConcepts: Map<string, KnowledgeNode>
  ): KnowledgeNode[] {
    const newlyAccessible: KnowledgeNode[] = [];

    for (const [nodeId, newNode] of newDAG.allNodes) {
      const oldNode = oldDAG.allNodes.get(nodeId);

      // Node was blocked but is now accessible (and not already completed)
      if (
        oldNode &&
        !oldNode.isAccessible &&
        newNode.isAccessible &&
        !newNode.isCompleted
      ) {
        const concept = allConcepts.get(nodeId);
        if (concept) {
          newlyAccessible.push(concept);
        }
      }
    }

    return newlyAccessible;
  }

  /**
   * Get completion statistics for a user
   * Useful for analytics and progress tracking
   */
  static getCompletionStats(userPath: UserPath, allConcepts: Map<string, KnowledgeNode>) {
    const completed = userPath.pathHistory.length;
    const total = allConcepts.size;
    const percentage = Math.round((completed / total) * 100);

    return {
      completed,
      total,
      remaining: total - completed,
      percentage,
      startedAt: userPath.createdAt,
      lastUpdatedAt: userPath.updatedAt,
    };
  }
}
