/**
 * src/frontend/src/shared/services/SkillGapAnalyzerService.ts
 * 
 * Skill Gap Analysis
 * Identifies weak prerequisites that block advanced learning
 * 
 * Features:
 * - Detect prerequisites with low reliability scores
 * - Map which advanced skills are blocked by weak prerequisites
 * - Prioritize weak skills for review
 * - Generate recommendations for improvement
 */

import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { UserPath } from "@/entities/UserPath";
import { SkillGap } from "@/entities/Assessment";

export interface WeakSkill {
  skillId: string;
  skillLabel: string;
  reliabilityScore: number; // 0-1, where < 0.8 is considered "weak"
  blockedCount: number; // How many advanced skills are blocked by this
  blockedSkills: string[]; // IDs of blocked skills
  priority: "critical" | "high" | "medium"; // Based on blocked count and reliability
  recommendedAction: string;
}

export interface SkillGapAnalysis {
  hasGaps: boolean;
  weakSkills: WeakSkill[];
  totalBlockedSkills: number;
  overallReliability: number; // Average reliability of prerequisites
  recommendations: string[];
}

export class SkillGapAnalyzerService {
  /**
   * Analyze skill gaps based on user's mastery history and concept prerequisites
   * 
   * @param userPath User's learning journey
   * @param allConcepts All available concepts
   * @param masteredConceptIds Concepts user has already mastered
   * @returns Detailed skill gap analysis
   */
  static analyzeSkillGaps(
    userPath: UserPath | null,
    allConcepts: Map<string, KnowledgeNode>,
    masteredConceptIds: string[] = []
  ): SkillGapAnalysis {
    if (!userPath || allConcepts.size === 0) {
      return {
        hasGaps: false,
        weakSkills: [],
        totalBlockedSkills: 0,
        overallReliability: 1.0,
        recommendations: [],
      };
    }

    const weakSkills: WeakSkill[] = [];
    const skillGapMap = new Map<string, SkillGap>(); // Map skillId -> SkillGap

    // Analyze each mastered concept
    for (const masteredId of masteredConceptIds) {
      const concept = allConcepts.get(masteredId);
      if (!concept) continue;

      // Get this concept's prerequisites
      const prerequisites = concept.prerequisites || [];

      for (const prereqId of prerequisites) {
        const prereqConcept = allConcepts.get(prereqId);
        if (!prereqConcept) continue;

         // Check if prerequisite reliability is weak (< 0.8)
        const reliabilityScore = prereqConcept.sourceMetadata?.reliabilityScore || 0;

        if (reliabilityScore < 0.8) {
          // This is a weak prerequisite
          if (!skillGapMap.has(prereqId)) {
            skillGapMap.set(prereqId, {
              id: "",
              conceptId: prereqId,
              gapScore: 1 - reliabilityScore,
              recommendedResources: [],
              prerequisitesNeeded: [],
              blockedAdvancedSkills: [],
              reliabilityScore,
              lastAssessmentDate: null,
              recommendationStatus: "pending",
              createdAt: new Date().toISOString(),
              updatedAt: new Date().toISOString(),
            });
          }

           // Add this concept to blocked skills list
           const gap = skillGapMap.get(prereqId)!;
           if (!gap.blockedAdvancedSkills?.includes(masteredId)) {
             (gap.blockedAdvancedSkills = gap.blockedAdvancedSkills || []);
             gap.blockedAdvancedSkills.push(masteredId);
           }
        }
      }
    }

    // Convert map to WeakSkill array with priority
    for (const [skillId, gap] of skillGapMap.entries()) {
      const concept = allConcepts.get(skillId);
      if (!concept) continue;

       const blockedCount = gap.blockedAdvancedSkills?.length || 0;
       let priority: "critical" | "high" | "medium" = "medium";

       if ((gap.reliabilityScore || 0) < 0.5 || blockedCount >= 5) {
         priority = "critical";
       } else if ((gap.reliabilityScore || 0) < 0.65 || blockedCount >= 3) {
         priority = "high";
       }

       weakSkills.push({
         skillId,
         skillLabel: concept.label || concept.title || "",
         reliabilityScore: gap.reliabilityScore || 0,
         blockedCount,
         blockedSkills: gap.blockedAdvancedSkills || [],
         priority,
         recommendedAction: this.generateRecommendation(
           gap.reliabilityScore || 0,
           blockedCount
         ),
       });
    }

    // Sort by priority (critical > high > medium) and blocked count
    weakSkills.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2 };
      const priorityDiff =
        priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return b.blockedCount - a.blockedCount;
    });

     // Calculate overall reliability
    const allReliabilityScores = Array.from(allConcepts.values())
      .filter((c) => masteredConceptIds.includes(c.id))
      .map((c) => c.sourceMetadata?.reliabilityScore || 0);
    const overallReliability =
      allReliabilityScores.length > 0
        ? allReliabilityScores.reduce((a, b) => a + b, 0) /
          allReliabilityScores.length
        : 1.0;

    // Generate recommendations
    const recommendations = this.generateRecommendations(weakSkills, overallReliability);

    return {
      hasGaps: weakSkills.length > 0,
      weakSkills,
      totalBlockedSkills: weakSkills.reduce((sum, s) => sum + s.blockedCount, 0),
      overallReliability,
      recommendations,
    };
  }

  /**
   * Generate specific recommendation for a skill based on reliability and impact
   * @private
   */
  private static generateRecommendation(
    reliabilityScore: number,
    blockedCount: number
  ): string {
    if (reliabilityScore < 0.5) {
      return "⚠️ Requires immediate review - foundation is unstable";
    } else if (reliabilityScore < 0.65) {
      return "🔧 Review recommended before advancing further";
    } else if (blockedCount >= 5) {
      return "📚 Important prerequisite - consider a refresher";
    } else if (blockedCount >= 3) {
      return "→ Optional review to strengthen foundation";
    } else {
      return "✓ Adequate foundation, no immediate action needed";
    }
  }

  /**
   * Generate overall recommendations for the user
   * @private
   */
  private static generateRecommendations(
    weakSkills: WeakSkill[],
    overallReliability: number
  ): string[] {
    const recommendations: string[] = [];

    if (weakSkills.length === 0) {
      recommendations.push(
        "✓ Your foundation is solid! Continue with advanced concepts."
      );
      return recommendations;
    }

    // Find critical gaps
    const criticalGaps = weakSkills.filter((s) => s.priority === "critical");
    if (criticalGaps.length > 0) {
      recommendations.push(
        `⚠️ ${criticalGaps.length} critical skill gap(s) detected. Review these before advancing.`
      );
    }

    // Check overall reliability
    if (overallReliability < 0.7) {
      recommendations.push(
        "📊 Your overall foundation reliability is below 70%. Consider taking a skill assessment test."
      );
    }

    if (weakSkills.length > 5) {
      recommendations.push(
        "🎯 Consider slowing down and consolidating your knowledge before tackling new concepts."
      );
    } else if (weakSkills.length > 0) {
      recommendations.push(
        `Take time to strengthen ${weakSkills.length} weak skill${weakSkills.length > 1 ? "s" : ""}. They're blocking your progress.`
      );
    }

    return recommendations;
  }

  /**
   * Get skills that should be reviewed before advancing to a specific concept
   * 
   * @param conceptId The concept user wants to learn
   * @param allConcepts All available concepts
   * @param weakSkillIds IDs of weak skills
   * @returns Array of concepts that should be reviewed first
   */
  static getPrerequisitesForReview(
    conceptId: string,
    allConcepts: Map<string, KnowledgeNode>,
    weakSkillIds: string[]
  ): KnowledgeNode[] {
    const concept = allConcepts.get(conceptId);
    if (!concept) return [];

    const prerequisites = concept.prerequisites || [];
    return prerequisites
      .map((id: string) => allConcepts.get(id))
      .filter(
        (prereq): prereq is KnowledgeNode =>
          prereq !== undefined && weakSkillIds.includes(prereq.id)
      );
  }
}
