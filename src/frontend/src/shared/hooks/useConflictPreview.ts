import { useCallback, useState } from "react";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
// Would call backend API in production
// import { ConflictCheckerService } from "../../../../services/shared/conflict-checker/ConflictCheckerService";

export interface ConflictWarning {
  hasConflict: boolean;
  conflictType: "circular" | "missing-prerequisite" | "none";
  message: string;
  blockedNodes?: string[];
}

/**
 * useConflictPreview Hook
 * 
 * Provides real-time conflict detection as the admin types prerequisites
 * Shows immediate visual warnings before form submission
 */
export function useConflictPreview(allConcepts: Map<string, KnowledgeNode>) {
  const [preview, setPreview] = useState<ConflictWarning>({
    hasConflict: false,
    conflictType: "none",
    message: "",
  });

  const checkPrerequisiteConflict = useCallback(
    (selectedPrerequisiteIds: string[]): ConflictWarning => {
      if (selectedPrerequisiteIds.length === 0) {
        return {
          hasConflict: false,
          conflictType: "none",
          message: "",
        };
      }

      // Check for circular references in selected prerequisites
      const circularCheck = checkForCircularPrerequisites(
        selectedPrerequisiteIds,
        allConcepts
      );

      if (circularCheck.hasCircular) {
        const warning: ConflictWarning = {
          hasConflict: true,
          conflictType: "circular",
          message: `⚠️ Circular reference detected: ${circularCheck.conflictingNodes.join(", ")}`,
          blockedNodes: circularCheck.conflictingNodes,
        };
        setPreview(warning);
        return warning;
      }

      // Check for missing prerequisites (prerequisites that aren't in system)
      const missingPrereqs = selectedPrerequisiteIds.filter(
        (id) => !allConcepts.has(id)
      );

      if (missingPrereqs.length > 0) {
        const warning: ConflictWarning = {
          hasConflict: true,
          conflictType: "missing-prerequisite",
          message: `⚠️ Unknown prerequisites: ${missingPrereqs.join(", ")}`,
          blockedNodes: missingPrereqs,
        };
        setPreview(warning);
        return warning;
      }

      // All clear
      const success: ConflictWarning = {
        hasConflict: false,
        conflictType: "none",
        message: `✓ ${selectedPrerequisiteIds.length} prerequisite(s) valid`,
      };
      setPreview(success);
      return success;
    },
    [allConcepts]
  );

  return { preview, checkPrerequisiteConflict };
}

/**
 * Check for circular references in prerequisites
 */
function checkForCircularPrerequisites(
  selectedPrerequisiteIds: string[],
  allConcepts: Map<string, KnowledgeNode>
): { hasCircular: boolean; conflictingNodes: string[] } {
  const visited = new Set<string>();
  const conflictingNodes: string[] = [];

  function traverse(nodeId: string, path: Set<string>): boolean {
    if (path.has(nodeId)) {
      conflictingNodes.push(nodeId);
      return true;
    }

    if (visited.has(nodeId)) {
      return false;
    }

    visited.add(nodeId);
    const concept = allConcepts.get(nodeId);

    if (concept && concept.prerequisites.length > 0) {
      const newPath = new Set(path);
      newPath.add(nodeId);

      for (const prereq of concept.prerequisites) {
        if (traverse(prereq, newPath)) {
          return true;
        }
      }
    }

    return false;
  }

  for (const nodeId of selectedPrerequisiteIds) {
    if (traverse(nodeId, new Set())) {
      return { hasCircular: true, conflictingNodes };
    }
  }

  return { hasCircular: false, conflictingNodes: [] };
}
