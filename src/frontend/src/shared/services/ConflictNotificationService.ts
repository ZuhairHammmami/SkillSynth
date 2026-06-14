"use client";

import { toast } from "sonner";
// Would call backend API in production
// import { ConflictCheckerService, type ConflictCheckResult } from "../../../../services/shared/conflict-checker/ConflictCheckerService";
import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";

// Stub implementation - would call backend API in production
interface ConflictCheckResult {
  hasConflict: boolean;
  conflictingNodes: string[];
  message: string;
  blockedBy?: string[];
  reason?: string;
}

const ConflictCheckerService = {
  checkNodeTransition: (_userPath: UserPath, _targetNodeId: string, _allConcepts: Map<string, KnowledgeNode>): ConflictCheckResult => ({
    hasConflict: false,
    conflictingNodes: [],
    message: "OK"
  }),
  validateSkillOverrides: (_userPath: UserPath, _allConcepts: Map<string, KnowledgeNode>): ConflictCheckResult => ({
    hasConflict: false,
    conflictingNodes: [],
    message: "OK"
  }),
  getBlockedNodes: (_userPath: UserPath, _allConcepts: Map<string, KnowledgeNode>): Array<{ nodeId: string; reason: string; blockedBy: string[] }> => []
};

export interface ConflictNotification {
  id: string;
  type: "warning" | "error" | "info";
  title: string;
  message: string;
  conflictingNodes?: string[];
  timestamp: Date;
}

/**
 * ConflictNotificationService
 * 
 * Handles detection and notification of prerequisite conflicts,
 * circular dependencies, and skill override violations.
 * Integrates with the UI toast notification system.
 */
export class ConflictNotificationService {
  private static notifications: Map<string, ConflictNotification> = new Map();

  /**
   * Check for conflicts when a user attempts to access a node
   * Displays appropriate toast notifications
   */
  static checkNodeAccessAndNotify(
    nodeId: string,
    userPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ): boolean {
    try {
      const result = ConflictCheckerService.checkNodeTransition(
        userPath,
        nodeId,
        allConcepts
      );

      if (result.hasConflict) {
        this.notifyConflict(result);
        return false;
      }

      return true;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      toast.error("Conflict Check Failed", {
        description: errorMsg,
      });
      return false;
    }
  }

  /**
   * Check skill overrides and notify of any violations
   */
  static checkSkillOverridesAndNotify(
    overrides: Map<string, number>,
    userPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ): boolean {
    try {
      const result = ConflictCheckerService.validateSkillOverrides(
        userPath,
        allConcepts
      );

      if (result.hasConflict) {
        this.notifyOverrideConflict(result);
        return false;
      }

      toast.success("Skill Overrides Applied", {
        description: "Your override preferences have been validated and applied.",
      });

      return true;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      toast.error("Override Validation Failed", {
        description: errorMsg,
      });
      return false;
    }
  }

/**
   * Check for blocked nodes and return their IDs
   */
  static getBlockedNodeIds(
    userPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ): string[] {
    try {
      const blockedNodes = ConflictCheckerService.getBlockedNodes(
        userPath,
        allConcepts
      );

      if (blockedNodes.length > 0) {
        const nodeIds = blockedNodes.map((n) => n.nodeId);
        this.notifyBlockedNodes(blockedNodes);
        return nodeIds;
      }

      return [];
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      toast.error("Failed to check blocked nodes", {
        description: errorMsg,
      });
      return [];
    }
  }

  /**
   * Notify about a conflict
   */
  private static notifyConflict(conflict: ConflictCheckResult): void {
    const notification: ConflictNotification = {
      id: `conflict-${Date.now()}`,
      type: "warning",
      title: "Prerequisites Not Met",
      message: this.buildConflictMessage(conflict),
      conflictingNodes: conflict.blockedBy,
      timestamp: new Date(),
    };

    this.storeNotification(notification);

    toast.warning("Cannot Access This Concept", {
      description: notification.message,
      duration: 5000,
      action: {
        label: "View Blocked",
        onClick: () => {
          // Navigate to blocked concept details
          window.location.href = `/mastery-path`;
        },
      },
    });
  }

  /**
   * Notify about override conflicts
   */
  private static notifyOverrideConflict(conflict: ConflictCheckResult): void {
    const notification: ConflictNotification = {
      id: `override-conflict-${Date.now()}`,
      type: "error",
      title: "Skill Override Conflict",
      message: this.buildOverrideConflictMessage(conflict),
      conflictingNodes: conflict.blockedBy,
      timestamp: new Date(),
    };

    this.storeNotification(notification);

    toast.error("Override Cannot Be Applied", {
      description: notification.message,
      duration: 6000,
    });
  }

  /**
   * Notify about blocked nodes
   */
  private static notifyBlockedNodes(blockedNodes: Array<{ nodeId: string; reason: string; blockedBy: string[] }>): void {
    if (blockedNodes.length === 0) return;

    const nodeCount = blockedNodes.length;
    const allBlockedBy = blockedNodes.flatMap((n) => n.blockedBy);
    const notification: ConflictNotification = {
      id: `blocked-nodes-${Date.now()}`,
      type: "info",
      title: "Concepts Locked",
      message: `You have ${nodeCount} concept${nodeCount > 1 ? "s" : ""} locked by prerequisites.`,
      conflictingNodes: allBlockedBy,
      timestamp: new Date(),
    };

    this.storeNotification(notification);

    toast.info("Some Concepts Are Locked", {
      description: `${nodeCount} concept${nodeCount > 1 ? "s" : ""} require prerequisite completion.`,
      duration: 4000,
    });
  }

  /**
   * Build a human-readable conflict message
   */
  private static buildConflictMessage(conflict: ConflictCheckResult): string {
    if (!conflict.blockedBy || conflict.blockedBy.length === 0) {
      return "This concept cannot be accessed at this time.";
    }

    if (conflict.blockedBy.length === 1) {
      return `Complete the prerequisite concept first to unlock this.`;
    }

    const blockedBy = conflict.blockedBy || [];
    return `${blockedBy.length} prerequisite${blockedBy.length > 1 ? "s" : ""} must be completed first.`;
  }

  /**
   * Build a human-readable override conflict message
   */
  private static buildOverrideConflictMessage(conflict: ConflictCheckResult): string {
    if (conflict.reason) {
      return conflict.reason;
    }
    return "This override violates the mastery-first principles and cannot be applied.";
  }

  /**
   * Store notification in memory for later retrieval
   */
  private static storeNotification(notification: ConflictNotification): void {
    this.notifications.set(notification.id, notification);

    // Auto-cleanup old notifications after 10 minutes
    setTimeout(() => {
      this.notifications.delete(notification.id);
    }, 10 * 60 * 1000);
  }

  /**
   * Get all stored notifications
   */
  static getNotifications(): ConflictNotification[] {
    return Array.from(this.notifications.values());
  }

  /**
   * Clear all notifications
   */
  static clearNotifications(): void {
    this.notifications.clear();
  }

  /**
   * Get notifications of a specific type
   */
  static getNotificationsByType(type: "warning" | "error" | "info"): ConflictNotification[] {
    return Array.from(this.notifications.values()).filter((n) => n.type === type);
  }

  /**
   * Count active conflicts
   */
  static getActiveConflictCount(): number {
    return this.notifications.size;
  }
}
