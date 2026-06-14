/**
 * src/frontend/src/shared/hooks/useMasteryData.ts
 * 
 * React Query Hooks for Mastery Data
 * Implements SWR pattern with automatic caching and deduplication
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { MasteryAnalyticsService } from "@/shared/services/MasteryAnalyticsService";

/**
 * Fetch user's mastery data
 * Cached for 5 minutes, stale-while-revalidate pattern
 */
export function useUserMastery(userId: string | undefined) {
  return useQuery({
    queryKey: ['mastery', 'user', userId || ""],
    queryFn: async (): Promise<UserPath> => {
      if (!userId) {
        throw new Error("User ID required");
      }

      const response = await fetch("/api/mastery/user-path", {
        headers: {
          "x-user-id": userId,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch user mastery");
      }

      const data = await response.json();

      if (!data.success) {
        throw new Error(data.error || "Failed to load user mastery");
      }

      return {
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
        skillOverrides: {},
        progress: data.data.progress || 0,
        created_at: data.data.createdAt,
        createdAt: data.data.createdAt,
        updated_at: data.data.updatedAt,
        updatedAt: data.data.updatedAt,
      };
    },
    enabled: !!userId,
    // Stale for 5 minutes
    staleTime: 5 * 60 * 1000,
    // Cache for 30 minutes
    gcTime: 30 * 60 * 1000,
  });
}

/**
 * Fetch all concepts
 * Cached for 1 hour (rarely changes)
 */
export function useConcepts() {
  return useQuery({
    queryKey: ['mastery', 'concepts'],
    queryFn: async (): Promise<Map<string, KnowledgeNode>> => {
      // TODO: Replace with actual API call
      // const response = await fetch("/api/concepts");
      // const data = await response.json();

      // Mock data for now
      const concepts = new Map<string, KnowledgeNode>([
        [
          "js-basics",
          {
            id: "js-basics",
            label: "JavaScript Fundamentals",
            confidenceScore: 0.95,
            prerequisites: [],
            sourceMetadata: {
              sourceType: "academic",
              sourceUrl: "https://developer.mozilla.org",
              lastUpdated: new Date().toISOString(),
              reliabilityScore: 0.95,
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
              sourceUrl: "https://react.dev",
              lastUpdated: new Date().toISOString(),
              reliabilityScore: 0.92,
            },
          },
        ],
      ]);

      return concepts;
    },
    staleTime: 60 * 60 * 1000, // 1 hour
    gcTime: 2 * 60 * 60 * 1000, // 2 hours
  });
}

/**
 * Fetch user's mastery analytics
 * Cached for 15 minutes
 */
export function useMasteryAnalytics(userId: string | undefined) {
  const { data: userPath } = useUserMastery(userId);
  const { data: concepts } = useConcepts();

  return useQuery({
    queryKey: ['mastery', 'analytics', userId || ""],
    queryFn: async () => {
      if (!userPath || !concepts) {
        return null;
      }

      return MasteryAnalyticsService.calculateMetrics(userPath, concepts);
    },
    enabled: !!userPath && !!concepts,
    staleTime: 15 * 60 * 1000, // 15 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Mutation to complete a node
 * Automatically invalidates related queries
 */
export function useCompleteNodeMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      userId,
      nodeId,
    }: {
      userId: string;
      nodeId: string;
    }) => {
      const response = await fetch("/api/mastery/progress", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-user-id": userId,
        },
        body: JSON.stringify({
          userId,
          completedNodeId: nodeId,
          pathHistory: [],
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to complete node");
      }

      return await response.json();
    },

    onSuccess: (_, { userId }) => {
      queryClient.invalidateQueries({ queryKey: ['mastery', 'progress', userId] });
      queryClient.invalidateQueries({ queryKey: ['mastery', 'analytics', userId] });
    },
  });
}

/**
 * Standalone query function for user mastery (used for prefetching)
 */
async function fetchUserMastery(userId: string): Promise<UserPath> {
  const response = await fetch("/api/mastery/user-path", {
    headers: { "x-user-id": userId },
  });
  if (!response.ok) throw new Error("Failed to fetch user mastery");
  const data = await response.json();
  if (!data.success) throw new Error(data.error || "Failed to load user mastery");
  return {
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
    skillOverrides: {},
    progress: data.data.progress || 0,
    created_at: data.data.createdAt,
    createdAt: data.data.createdAt,
    updated_at: data.data.updatedAt,
    updatedAt: data.data.updatedAt,
  };
}

/**
 * Prefetch queries for better performance
 * Call this when you know the user will need the data
 */
export function usePrefetchMasteryData(userId: string | undefined) {
  const queryClient = useQueryClient();

  return {
    prefetchUserMastery: () => {
      if (userId) {
        queryClient.prefetchQuery({
          queryKey: ['mastery', 'user', userId],
          queryFn: () => fetchUserMastery(userId),
        });
      }
    },

    prefetchConcepts: () => {
      queryClient.prefetchQuery({
        queryKey: ['mastery', 'concepts'],
        queryFn: async (): Promise<Map<string, KnowledgeNode>> => {
          return new Map<string, KnowledgeNode>([
            ["js-basics", {
              id: "js-basics",
              label: "JavaScript Fundamentals",
              confidenceScore: 0.95,
              prerequisites: [],
              sourceMetadata: {
                sourceType: "academic",
                sourceUrl: "https://developer.mozilla.org",
                lastUpdated: new Date().toISOString(),
                reliabilityScore: 0.95,
              },
            }],
            ["react-basics", {
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
            }],
          ]);
        },
      });
    },

    prefetchAnalytics: () => {
      if (userId) {
        queryClient.prefetchQuery({
          queryKey: ['mastery', 'analytics', userId],
          queryFn: async () => null,
        });
      }
    },

    prefetchAll: async () => {
      if (userId) {
        await Promise.all([
          queryClient.prefetchQuery({
            queryKey: ['mastery', 'user', userId],
            queryFn: () => fetchUserMastery(userId),
          }),
          queryClient.prefetchQuery({
            queryKey: ['mastery', 'concepts'],
            queryFn: async (): Promise<Map<string, KnowledgeNode>> => {
              return new Map<string, KnowledgeNode>([
                ["js-basics", {
                  id: "js-basics",
                  label: "JavaScript Fundamentals",
                  confidenceScore: 0.95,
                  prerequisites: [],
                  sourceMetadata: {
                    sourceType: "academic",
                    sourceUrl: "https://developer.mozilla.org",
                    lastUpdated: new Date().toISOString(),
                    reliabilityScore: 0.95,
                  },
                }],
                ["react-basics", {
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
                }],
              ]);
            },
          }),
        ]);
      }
    },
  };
}
