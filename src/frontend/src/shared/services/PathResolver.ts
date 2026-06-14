import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { UserPath } from "@/entities/UserPath";

/**
 * PathResolver - Dynamic Path Engine
 * 
 * Calculates the optimal "Shortest Path to Mastery" by analyzing the 
 * prerequisites tree in the database and returning a DAG (Directed Acyclic Graph)
 * representation of the user's learning journey.
 */

export interface DAGNode {
  id: string;
  label: string;
  confidenceScore: number;
  level: number; // 0 = root, 1 = first-level prereqs, etc.
  prerequisites: string[]; // IDs of prerequisite nodes
  dependents: string[]; // IDs of nodes that depend on this
  isCompleted: boolean;
  isAccessible: boolean;
  blockedBy: string[]; // If not accessible, which nodes block it
}

export interface LearningPathDAG {
  userId: string;
  rootNodes: DAGNode[]; // Nodes with no prerequisites
  allNodes: Map<string, DAGNode>;
  layers: DAGNode[][]; // Organized by dependency level
  shortestPath: DAGNode[];
  completionPercentage: number;
  estimatedTimeToMastery: number; // in hours
}

export interface PathResolverResult {
  success: boolean;
  dag?: LearningPathDAG;
  error?: string;
}

export class PathResolverService {
  /**
   * Resolve the shortest path to mastery for a user
   * @param userPath Current user mastery state
   * @param allConcepts All available knowledge concepts
   * @returns LearningPathDAG with shortest path calculation
   */
  static resolvePath(
    userPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ): PathResolverResult {
    try {
      // Step 1: Build the complete DAG from all concepts
      const dagNodes = this.buildDAGNodes(
        allConcepts,
        new Set(userPath.pathHistory)
      );

      // Step 2: Compute layers (dependency levels)
      const layers = this.computeLayers(dagNodes);

      // Step 3: Identify root nodes (no prerequisites)
      const rootNodes = dagNodes.filter((node) => node.prerequisites.length === 0);

      // Step 4: Calculate shortest path to completion
      const remainingConcepts = Array.from(allConcepts.values()).filter(
        (concept) => !userPath.pathHistory.includes(concept.id)
      );

      const shortestPath = this.calculateShortestPath(
        remainingConcepts,
        userPath.currentNode || "",
        dagNodes
      );

      // Step 5: Build the final DAG structure
      const dagMap = new Map(dagNodes.map((node) => [node.id, node]));

      const completionPercentage = Math.round(
        (userPath.pathHistory.length / allConcepts.size) * 100
      );

      const estimatedTimeToMastery = this.estimateTimeToMastery(
        remainingConcepts
      );

      return {
        success: true,
dag: {
           userId: userPath.user_id || userPath.userId || '',
          rootNodes,
          allNodes: dagMap,
          layers,
          shortestPath,
          completionPercentage,
          estimatedTimeToMastery,
        },
      };
    } catch (error) {
      return {
        success: false,
        error:
          error instanceof Error ? error.message : "Failed to resolve path",
      };
    }
  }

  /**
   * Build DAG nodes from all concepts
   */
  private static buildDAGNodes(
    allConcepts: Map<string, KnowledgeNode>,
    completedNodes: Set<string>
  ): DAGNode[] {
    const dagNodes: DAGNode[] = [];
    const nodeMap = new Map<string, DAGNode>();

    // First pass: create all nodes
    for (const [conceptId, concept] of allConcepts) {
      const dagNode: DAGNode = {
        id: conceptId,
        label: concept.label || "",
        confidenceScore: concept.confidenceScore || 0,
        level: 0, // Will be computed later
        prerequisites: concept.prerequisites || [],
        dependents: [],
        isCompleted: completedNodes.has(conceptId),
        isAccessible: false, // Will be computed
        blockedBy: [],
      };
      nodeMap.set(conceptId, dagNode);
      dagNodes.push(dagNode);
    }

    // Second pass: compute dependencies and accessibility
    for (const dagNode of dagNodes) {
      // Find dependents (nodes that have this node as prerequisite)
      for (const otherNode of dagNodes) {
        if (otherNode.prerequisites.includes(dagNode.id)) {
          dagNode.dependents.push(otherNode.id);
        }
      }

      // Compute accessibility
      if (dagNode.prerequisites.length === 0) {
        dagNode.isAccessible = true;
      } else {
        const unmetPrereqs = dagNode.prerequisites.filter(
          (prereqId) => !completedNodes.has(prereqId)
        );
        dagNode.isAccessible = unmetPrereqs.length === 0;
        dagNode.blockedBy = unmetPrereqs;
      }
    }

    return dagNodes;
  }

  /**
   * Compute layers (dependency levels) using topological sort
   */
  private static computeLayers(dagNodes: DAGNode[]): DAGNode[][] {
    const layers: DAGNode[][] = [];
    const processed = new Set<string>();

    let currentLayer = dagNodes.filter(
      (node) => node.prerequisites.length === 0
    );
    let layerIndex = 0;

    while (currentLayer.length > 0 && layerIndex < 100) {
      // Safety: max 100 layers
      layers.push([...currentLayer]);
      processed.forEach((id) => {
        // Mark as processed
      });
      currentLayer.forEach((node) => processed.add(node.id));

      // Find next layer: nodes whose prerequisites are all in processed set
      const nextLayer = dagNodes.filter(
        (node) =>
          !processed.has(node.id) &&
          node.prerequisites.every((prereqId) => processed.has(prereqId))
      );

      currentLayer = nextLayer;
      layerIndex++;
    }

    // Compute level for each node
    for (let i = 0; i < layers.length; i++) {
      layers[i].forEach((node) => {
        node.level = i;
      });
    }

    return layers;
  }

  /**
   * Calculate shortest path to mastery using BFS
   */
  private static calculateShortestPath(
    remainingConcepts: KnowledgeNode[],
    currentNodeId: string,
    dagNodes: DAGNode[]
  ): DAGNode[] {
    if (remainingConcepts.length === 0) {
      return [];
    }

    const shortestPath: DAGNode[] = [];
    const accessibleNodes = dagNodes.filter((node) => node.isAccessible);

    // Use BFS to find the shortest path through remaining concepts
    const queue: (string | undefined)[] = [currentNodeId];
    const visited = new Set<string>();

    while (queue.length > 0) {
      const nodeId = queue.shift();
      if (!nodeId || visited.has(nodeId)) continue;

      visited.add(nodeId);
      const node = dagNodes.find((n) => n.id === nodeId);

      if (node && node.dependents.length > 0) {
        const unvisitedDependents = node.dependents.filter(
          (depId) => !visited.has(depId)
        );

        for (const depId of unvisitedDependents) {
          queue.push(depId);
          const depNode = dagNodes.find((n) => n.id === depId);
          if (depNode && remainingConcepts.some((c) => c.id === depId)) {
            shortestPath.push(depNode);
          }
        }
      }
    }

    return shortestPath;
  }

  /**
   * Estimate time to mastery in hours
   */
  private static estimateTimeToMastery(
    remainingConcepts: KnowledgeNode[]
  ): number {
    // Estimate: 2 hours per concept on average
    // Multiply by confidence factor (higher confidence = less time needed)
    const baseHours = remainingConcepts.length * 2;
    const confidenceSum = remainingConcepts.reduce((sum, c) => sum + (c.confidenceScore || 0), 0);
    const confidenceFactor = remainingConcepts.length > 0 ? confidenceSum / remainingConcepts.length : 0.8;

    return Math.round(baseHours / confidenceFactor);
  }

  /**
   * Validate that a proposed path doesn't violate prerequisites
   */
  static validatePath(
    proposedPath: string[],
    allConcepts: Map<string, KnowledgeNode>
  ): { valid: boolean; reason?: string } {
    const visited = new Set<string>();

    for (const nodeId of proposedPath) {
      const concept = allConcepts.get(nodeId);
      if (!concept) {
        return { valid: false, reason: `Node ${nodeId} not found` };
      }

      // Check prerequisites
      for (const prereqId of concept.prerequisites) {
        if (!visited.has(prereqId)) {
          return {
            valid: false,
            reason: `Missing prerequisite ${prereqId} for ${nodeId}`,
          };
        }
      }

      visited.add(nodeId);
    }

    return { valid: true };
  }

  /**
   * Export DAG as JSON for visualization
   */
  static exportDAGAsJSON(dag: LearningPathDAG): string {
    return JSON.stringify(
      {
        userId: dag.userId,
        completionPercentage: dag.completionPercentage,
        estimatedTimeToMastery: dag.estimatedTimeToMastery,
        layers: dag.layers.map((layer) =>
          layer.map((node) => ({
            id: node.id,
            label: node.label,
            level: node.level,
            isCompleted: node.isCompleted,
            isAccessible: node.isAccessible,
          }))
        ),
        shortestPath: dag.shortestPath.map((node) => ({
          id: node.id,
          label: node.label,
          confidenceScore: node.confidenceScore,
        })),
      },
      null,
      2
    );
  }
}
