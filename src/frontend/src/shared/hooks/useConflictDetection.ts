"use client";

import { useCallback } from "react";
import { ConflictNotificationService } from "@/shared/services/ConflictNotificationService";
// Would call backend API in production
// import { ConflictCheckerService } from "../../../../services/shared/conflict-checker/ConflictCheckerService";
import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";

/**
 * Hook for using conflict detection and notifications in components
 */
export function useConflictDetection() {
  /**
   * Check if a user can access a specific node
   */
  const canAccessNode = useCallback(
    (
      nodeId: string,
      userPath: UserPath,
      allConcepts: Map<string, KnowledgeNode>
    ): boolean => {
      return ConflictNotificationService.checkNodeAccessAndNotify(
        nodeId,
        userPath,
        allConcepts
      );
    },
    []
  );

  /**
   * Attempt to access a node with full validation and notification
   */
  const attemptNodeAccess = useCallback(
    (
      nodeId: string,
      userPath: UserPath,
      allConcepts: Map<string, KnowledgeNode>,
      onSuccess?: () => void,
      onFailure?: (message: string) => void
    ): boolean => {
      const canAccess = ConflictNotificationService.checkNodeAccessAndNotify(
        nodeId,
        userPath,
        allConcepts
      );

      if (canAccess) {
        onSuccess?.();
      } else {
        onFailure?.("Cannot access this concept due to unmet prerequisites");
      }

      return canAccess;
    },
    []
  );

  /**
   * Get all currently blocked nodes
   */
  const getBlockedNodes = useCallback(
    (userPath: UserPath, allConcepts: Map<string, KnowledgeNode>): string[] => {
      return ConflictNotificationService.getBlockedNodeIds(
        userPath,
        allConcepts
      );
    },
    []
  );

  /**
   * Validate skill overrides
   */
  const validateOverrides = useCallback(
    (
      overrides: Map<string, number>,
      userPath: UserPath,
      allConcepts: Map<string, KnowledgeNode>
    ): boolean => {
      return ConflictNotificationService.checkSkillOverridesAndNotify(
        overrides,
        userPath,
        allConcepts
      );
    },
    []
  );

  /**
   * Get active notification count
   */
  const getConflictCount = useCallback(() => {
    return ConflictNotificationService.getActiveConflictCount();
  }, []);

  /**
   * Get all notifications
   */
  const getNotifications = useCallback(() => {
    return ConflictNotificationService.getNotifications();
  }, []);

  /**
   * Get warnings specifically
   */
  const getWarnings = useCallback(() => {
    return ConflictNotificationService.getNotificationsByType("warning");
  }, []);

  /**
   * Get errors specifically
   */
  const getErrors = useCallback(() => {
    return ConflictNotificationService.getNotificationsByType("error");
  }, []);

  return {
    canAccessNode,
    attemptNodeAccess,
    getBlockedNodes,
    validateOverrides,
    getConflictCount,
    getNotifications,
    getWarnings,
    getErrors,
  };
}
