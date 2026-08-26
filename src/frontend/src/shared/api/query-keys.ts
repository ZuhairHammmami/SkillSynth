/**
 * Centralized Query Key Factory for React Query
 * 
 * This ensures consistency across the application and prevents cache collisions.
 * Each query key is a unique identifier that React Query uses to manage cache.
 * 
 * Using a factory pattern makes it easy to:
 * - Invalidate specific query types
 * - Maintain consistency across the codebase
 * - Enable type-safe query operations
 */

export const queryKeys = {
  // ==================== User & Auth ====================
  user: {
    all: ['user'] as const,
    current: () => [...queryKeys.user.all, 'current'] as const,
    profile: () => [...queryKeys.user.all, 'profile'] as const,
  },

  // ==================== Learning Paths ====================
  paths: {
    all: ['paths'] as const,
    lists: () => [...queryKeys.paths.all, 'list'] as const,
    list: (filters?: { status?: string; category?: string }) =>
      [...queryKeys.paths.lists(), { ...filters }] as const,
    details: () => [...queryKeys.paths.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.paths.details(), id] as const,
    progress: () => [...queryKeys.paths.all, 'progress'] as const,
    progressByPath: (pathId: string) =>
      [...queryKeys.paths.progress(), pathId] as const,
  },

  // ==================== Wizard / Path Generation ====================
  wizard: {
    all: ['wizard'] as const,
    options: () => [...queryKeys.wizard.all, 'options'] as const,
    generateOptions: (goal?: string) =>
      [...queryKeys.wizard.options(), { goal }] as const,
    templates: () => [...queryKeys.wizard.all, 'templates'] as const,
    assessment: () => [...queryKeys.wizard.all, 'assessment'] as const,
  },

  // ==================== Assessments ====================
  assessments: {
    all: ['assessments'] as const,
    lists: () => [...queryKeys.assessments.all, 'list'] as const,
    list: (pathId?: string) =>
      [...queryKeys.assessments.lists(), pathId] as const,
    details: () => [...queryKeys.assessments.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.assessments.details(), id] as const,
    results: () => [...queryKeys.assessments.all, 'results'] as const,
    resultsByPath: (pathId: string) =>
      [...queryKeys.assessments.results(), pathId] as const,
  },

  // ==================== Analytics ====================
  analytics: {
    all: ['analytics'] as const,
    dashboard: () => [...queryKeys.analytics.all, 'dashboard'] as const,
    skillGrowth: () => [...queryKeys.analytics.all, 'skill-growth'] as const,
    pathProgress: () => [...queryKeys.analytics.all, 'path-progress'] as const,
    pathProgressById: (pathId: number) =>
      [...queryKeys.analytics.pathProgress(), pathId] as const,
    learningVelocity: () => [...queryKeys.analytics.all, 'learning-velocity'] as const,
  },

  // ==================== Student Hooks & SSE Compat Keys ====================
  // Emit the exact cache-key strings used by the student hooks and the
  // SSE invalidation map so adoption never renames live cache entries.
  compat: {
    profile: () => ['profile'] as const,
    dashboard: () => ['dashboard'] as const,
    pathAll: () => ['path'] as const,
    pathDetail: (id: number) => ['path', id] as const,
    analyticsDashboard: () => ['analyticsDashboard'] as const,
    skillGrowth: () => ['skillGrowth'] as const,
    wizardOptions: () => ['wizardOptions'] as const,
    learningAnalysis: () => ['learningAnalysis'] as const,
  },
} as const;

/**
 * Helper function to invalidate related queries
 * Usage in mutation success callbacks:
 * 
 * onSuccess: (data) => {
 *   queryClient.invalidateQueries({
 *     queryKey: queryKeys.paths.all,
 *   });
 * }
 */
