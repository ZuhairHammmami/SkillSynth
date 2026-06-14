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

  // ==================== Admin ====================
  admin: {
    all: ['admin'] as const,
    stats: () => [...queryKeys.admin.all, 'stats'] as const,
    users: {
      all: ['admin', 'users'] as const,
      list: (page?: number, pageSize?: number) =>
        [...queryKeys.admin.users.all, 'list', page, pageSize] as const,
      detail: (id: string) =>
        [...queryKeys.admin.users.all, 'detail', id] as const,
    },
    paths: {
      all: ['admin', 'paths'] as const,
      list: (page?: number, pageSize?: number) =>
        [...queryKeys.admin.paths.all, 'list', page, pageSize] as const,
      detail: (id: string) =>
        [...queryKeys.admin.paths.all, 'detail', id] as const,
    },
    resources: {
      all: ['admin', 'resources'] as const,
      list: () => [...queryKeys.admin.resources.all, 'list'] as const,
      detail: (id: string) =>
        [...queryKeys.admin.resources.all, 'detail', id] as const,
    },
    skills: {
      all: ['admin', 'skills'] as const,
      list: () => [...queryKeys.admin.skills.all, 'list'] as const,
      detail: (id: string) =>
        [...queryKeys.admin.skills.all, 'detail', id] as const,
    },
    categories: {
      all: ['admin', 'categories'] as const,
      list: () => [...queryKeys.admin.categories.all, 'list'] as const,
    },
    jobRoles: {
      all: ['admin', 'jobRoles'] as const,
      list: () => [...queryKeys.admin.jobRoles.all, 'list'] as const,
    },
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
