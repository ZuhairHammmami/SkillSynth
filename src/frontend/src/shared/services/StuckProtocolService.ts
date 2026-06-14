/**
 * src/frontend/src/shared/services/StuckProtocolService.ts
 * 
 * Stuck Protocol - Learning Intervention Detection
 * Detects when users spend >48 hours on a single node without completion
 * Triggers automated learning interventions to help them progress
 * 
 * Features:
 * - Track time spent on individual nodes
 * - Detect 48+ hour threshold
 * - Generate simplified learning paths
 * - Recommend interventions (get help, skip, alternative path)
 */

import { StuckTracking, LearningIntervention } from "@/entities/Assessment";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { v4 as uuidv4 } from "uuid";

export interface StuckDetectionResult {
  isStuck: boolean;
  hoursSpent: number;
  hoursOverThreshold: number; // Hours beyond 48h threshold
  currentConcept: KnowledgeNode | null;
  interventionOptions: LearningInterventionOption[];
}

export interface LearningInterventionOption {
  id: string;
  type: "learning_intervention" | "skip_option" | "alternative_path";
  title: string;
  description: string;
  action: string;
  icon: string;
  expectedOutcome: string;
}

export class StuckProtocolService {
  private static readonly STUCK_THRESHOLD_HOURS = 48;

  /**
   * Check if a user is stuck on a node
   * 
   * @param trackingData User's stuck tracking record
   * @param currentConcept The concept they're working on
   * @returns Detection result with intervention options if stuck
   */
  static detectStuck(
    trackingData: StuckTracking | null,
    currentConcept: KnowledgeNode | null
  ): StuckDetectionResult {
    if (!trackingData || !currentConcept) {
      return {
        isStuck: false,
        hoursSpent: 0,
        hoursOverThreshold: 0,
        currentConcept: null,
        interventionOptions: [],
      };
    }

    const startTime = new Date(trackingData.nodeStartTime || new Date().toISOString());
    const now = new Date();
    const hoursSpent = (now.getTime() - startTime.getTime()) / (1000 * 60 * 60);
    const isStuck = hoursSpent >= this.STUCK_THRESHOLD_HOURS;
    const hoursOverThreshold = Math.max(0, hoursSpent - this.STUCK_THRESHOLD_HOURS);

    const interventionOptions = isStuck
      ? this.generateInterventionOptions(currentConcept, hoursSpent)
      : [];

    return {
      isStuck,
      hoursSpent: Math.round(hoursSpent),
      hoursOverThreshold: Math.round(hoursOverThreshold),
      currentConcept,
      interventionOptions,
    };
  }

  /**
   * Generate intervention options based on concept and time spent
   * @private
   */
  private static generateInterventionOptions(
    concept: KnowledgeNode,
    hoursSpent: number
  ): LearningInterventionOption[] {
    const options: LearningInterventionOption[] = [];

    // Always offer learning intervention
    options.push({
      id: uuidv4(),
      type: "learning_intervention",
      title: "🎓 Get Learning Intervention",
      description:
        "Access alternative explanations and guided practice tailored to your learning style",
      action: "Request AI-powered tutoring explanation of this concept",
      icon: "📚",
      expectedOutcome:
        "Gain new perspective and unlock the concept with personalized guidance",
    });

    // After 72 hours, offer skip option
    if (hoursSpent >= 72) {
      options.push({
        id: uuidv4(),
        type: "skip_option",
        title: "⏭️ Skip This Concept (Not Recommended)",
        description:
          "Temporarily skip this concept and come back later. This may block some advanced paths.",
        action: "Skip this node and mark for review",
        icon: "⏭️",
        expectedOutcome:
          "Continue learning, but some skills may be unavailable until you master this",
      });
    }

    // After 96 hours, offer alternative path
    if (hoursSpent >= 96) {
      options.push({
        id: uuidv4(),
        type: "alternative_path",
        title: "🛤️ Take Alternative Learning Path",
        description:
          "Jump to a related concept that builds similar skills through a different approach",
        action: "Switch to alternative skill path",
        icon: "🛤️",
        expectedOutcome:
          "Build parallel skills and potentially circle back to this concept later with better foundation",
      });
    }

    return options;
  }

  /**
   * Calculate a simplified subpath for users stuck on a complex concept
   * 
   * Returns a shorter path with intermediate concepts that build up to the original
   * 
   * @param conceptId The concept user is stuck on
   * @param allConcepts All available concepts
   * @returns Array of concept IDs forming a simplified path
   */
  static generateSimplifiedSubpath(
    conceptId: string,
    allConcepts: Map<string, KnowledgeNode>
  ): string[] {
    const concept = allConcepts.get(conceptId);
    if (!concept) return [conceptId];

    // Return the immediate prerequisites as a simplified path
    const simplifiedPath = concept.prerequisites || [];

    // Limit to top 3 most fundamental prerequisites
    return simplifiedPath.slice(0, 3);
  }

  /**
   * Record that an intervention was triggered
   * 
   * @param userId User who is stuck
   * @param conceptId Concept they're stuck on
   * @param intervention The intervention option selected
   * @param hoursSpent Total hours spent on this concept
   * @returns Intervention record
   */
  static createInterventionRecord(
    userId: string,
    conceptId: string,
    intervention: LearningInterventionOption,
    hoursSpent: number
  ): LearningIntervention {
    return {
      id: uuidv4(),
      userId,
      conceptId,
      interventionType: intervention.type === "learning_intervention" ? "hint" : 
                        intervention.type === "skip_option" ? "prerequisite-review" :
                        intervention.type === "alternative_path" ? "alternative-explanation" : "hint",
      content: intervention.description,
      triggerReason: "stuck_48h",
      hoursSpent,
      failedAttempts: 0, // Would be populated from assessment results
      interventionAccepted: true,
      actionTaken: intervention.action,
      createdAt: new Date().toISOString(),
    };
  }

  /**
   * Track when user starts working on a node
   * 
   * @param userId User ID
   * @param conceptId Concept ID
   * @returns StuckTracking record
   */
  static initializeNodeTracking(
    userId: string,
    conceptId: string
  ): StuckTracking {
    return {
      userId,
      conceptId,
      stuckCount: 0,
      stuckTime: "",
      triggers: [],
      nodeStartTime: new Date().toISOString(),
    };
  }

  /**
   * Check if intervention was successful (user completed node after intervention)
   * 
   * @param intervention The intervention that was applied
   * @param completedSuccessfully Whether the user completed the node
   * @returns Quality assessment of intervention effectiveness
   */
  static assessInterventionEffectiveness(
    intervention: LearningIntervention,
    completedSuccessfully: boolean
  ): { effective: boolean; message: string } {
    if (completedSuccessfully) {
      return {
        effective: true,
        message: `✓ Intervention successful! The ${intervention.interventionType} helped you make progress.`,
      };
    }

    return {
      effective: false,
      message:
        "Consider trying a different intervention approach or reaching out for direct support.",
    };
  }

  /**
   * Get the textual status of a stuck node
   * 
   * @param hoursSpent Hours the user has been stuck
   * @returns Human-readable status
   */
  static getStuckStatus(hoursSpent: number): string {
    if (hoursSpent < 24) {
      return "⏱️ Normal pace";
    } else if (hoursSpent < 48) {
      return "⚠️ Taking time";
    } else if (hoursSpent < 72) {
      return "🔴 Stuck (48h+)";
    } else if (hoursSpent < 96) {
      return "🔴 Severely stuck (72h+)";
    } else {
      return "🔴 Critical (96h+)";
    }
  }
}
