/**
 * src/frontend/src/shared/hooks/useMasteryPath.ts
 * 
 * Identity Handshake Hook
 * Fetches user mastery data and identifies starting point in the learning path
 * 
 * Usage:
 * const { userPath, startingNodes, isLoading, error } = useMasteryPath();
 */

import { useEffect, useState, useCallback } from "react";
import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { PathResolverService } from "@/shared/services/PathResolver";

interface MasteryPathHookResult {
  userPath: UserPath | null;
  startingNodes: KnowledgeNode[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook to fetch user mastery data and calculate their starting point
 */
export function useMasteryPath(concepts: Map<string, KnowledgeNode> | null): MasteryPathHookResult {
  const [userPath, setUserPath] = useState<UserPath | null>(null);
  const [startingNodes, setStartingNodes] = useState<KnowledgeNode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch user mastery data from the Identity Handshake endpoint
  const fetchUserMastery = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch("/api/mastery/user-path", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.error || `Failed to fetch user mastery: ${response.status}`
        );
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Failed to initialize user mastery");
      }

      // Map API response to UserPath entity
      const mappedUserPath: UserPath = {
        id: data.data.id,
        user_id: data.data.userId,
        userId: data.data.userId,
        title: data.data.pathName || data.data.title || '',
        pathName: data.data.pathName || data.data.title || '',
        goalConceptId: data.data.goalConceptId,
        nodes: [],
        currentNode: data.data.currentNodeId,
        pathHistory: data.data.pathHistory || [],
        completedAssessments: [],
        skillOverrides: data.data.customSkillOverrides || {},
        progress: data.data.progress || 0,
        created_at: data.data.createdAt,
        createdAt: data.data.createdAt,
        updated_at: data.data.updatedAt,
        updatedAt: data.data.updatedAt,
      };

      setUserPath(mappedUserPath);

      // Calculate starting nodes if concepts are available
      if (concepts && concepts.size > 0) {
        const rootNodes = Array.from(concepts.values()).filter(
          (concept) => concept.prerequisites.length === 0
        );

        setStartingNodes(rootNodes);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error";
      setError(errorMessage);
      console.error("[useMasteryPath Error]", errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [concepts]);

  // Fetch on mount
  useEffect(() => {
    fetchUserMastery();
  }, [fetchUserMastery]);

  return {
    userPath,
    startingNodes,
    isLoading,
    error,
    refetch: fetchUserMastery,
  };
}
