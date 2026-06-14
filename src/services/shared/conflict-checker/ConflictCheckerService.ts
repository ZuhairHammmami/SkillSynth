import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";

export interface ConflictCheckResult {
  hasConflict: boolean;
  conflictingNodes: string[];
  message: string;
  blockedBy?: string[];
  reason?: string;
}

/**
 * ConflictChecker Service
 * Validates UserPath transitions against mandatory engineering prerequisites
 * Prevents users from skipping required skills in a learning path
 */
export class ConflictCheckerService {
  /**
   * Check if a user can transition to a new node
   * @param userPath Current user path state
   * @param targetNodeId UUID of the node the user wants to move to
   * @param allNodes All available knowledge nodes with prerequisite info
   * @returns ConflictCheckResult with conflict details
   */
  static checkNodeTransition(
    userPath: UserPath,
    targetNodeId: string,
    allNodes: Map<string, KnowledgeNode>
  ): ConflictCheckResult {
    const targetNode = allNodes.get(targetNodeId);

    if (!targetNode) {
      return {
        hasConflict: true,
        conflictingNodes: [],
        message: "Target node not found",
      };
    }

    // Check if user has completed all prerequisites
    const unmetPrerequisites = targetNode.prerequisites.filter(
      (prereqId) => !userPath.pathHistory.includes(prereqId)
    );

    if (unmetPrerequisites.length > 0) {
      return {
        hasConflict: true,
        conflictingNodes: unmetPrerequisites,
        message: `User must complete ${unmetPrerequisites.length} prerequisite(s) before accessing this node`,
      };
    }

    return {
      hasConflict: false,
      conflictingNodes: [],
      message: "Transition is allowed",
    };
  }

  /**
   * Validate custom skill overrides don't break prerequisite chains
   * @param userPath User path with custom overrides
   * @param allNodes All knowledge nodes
   * @returns ConflictCheckResult
   */
  static validateSkillOverrides(
    userPath: UserPath,
    allNodes: Map<string, KnowledgeNode>
  ): ConflictCheckResult {
    const overrideNodeIds = Object.keys(userPath.customSkillOverrides);
    const conflictingNodes: string[] = [];

    for (const nodeId of overrideNodeIds) {
      const node = allNodes.get(nodeId);
      if (!node) {
        conflictingNodes.push(nodeId);
        continue;
      }

      // If override is marked as "skipped", check if it breaks prerequisites for allowed paths
      const override = userPath.customSkillOverrides[nodeId];
      if (override?.skipped === true) {
        const dependentNodes = Array.from(allNodes.values()).filter((n) =>
          n.prerequisites.includes(nodeId)
        );

        const blockedDependents = dependentNodes.filter((dependent) =>
          userPath.allowedPaths.includes(dependent.id)
        );

        if (blockedDependents.length > 0) {
          conflictingNodes.push(nodeId);
        }
      }
    }

    if (conflictingNodes.length > 0) {
      return {
        hasConflict: true,
        conflictingNodes,
        message: `Skill overrides would block access to ${conflictingNodes.length} allowed path(s)`,
      };
    }

    return {
      hasConflict: false,
      conflictingNodes: [],
      message: "All skill overrides are valid",
    };
  }

  /**
   * Get all nodes that are currently blocked due to unmet prerequisites
   * @param userPath Current user path
   * @param allNodes All knowledge nodes
   * @returns Array of blocked node IDs with reasons
   */
  static getBlockedNodes(
    userPath: UserPath,
    allNodes: Map<string, KnowledgeNode>
  ): Array<{ nodeId: string; reason: string; blockedBy: string[] }> {
    const blockedNodes: Array<{
      nodeId: string;
      reason: string;
      blockedBy: string[];
    }> = [];

    for (const [nodeId, node] of allNodes) {
      // Skip if already completed
      if (userPath.pathHistory.includes(nodeId)) continue;

      // Check prerequisites
      const unmetPrereqs = node.prerequisites.filter(
        (prereqId) => !userPath.pathHistory.includes(prereqId)
      );

      if (unmetPrereqs.length > 0) {
        blockedNodes.push({
          nodeId,
          reason: `Blocked by ${unmetPrereqs.length} prerequisite(s)`,
          blockedBy: unmetPrereqs,
        });
      }
    }

    return blockedNodes;
  }
}
