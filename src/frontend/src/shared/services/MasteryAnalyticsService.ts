/**
 * src/frontend/src/shared/services/MasteryAnalyticsService.ts
 * 
 * Mastery Analytics Engine
 * Calculates metrics for the analytics dashboard
 */

import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";

export interface MasteryMetrics {
  // Path Coverage
  coverage: {
    completed: number;
    total: number;
    percentage: number;
  };

  // Engineering Velocity
  velocity: {
    thisWeek: number;
    lastWeek: number;
    averagePerWeek: number;
    trend: "up" | "down" | "stable";
  };

  // Time Statistics
  timeSeries: {
    date: string;
    completed: number;
    cumulative: number;
  }[];

  // Concept Distribution
  byCategory: Record<string, number>;

  // Estimated Mastery Date
  estimatedCompletionDate: string;
}

export class MasteryAnalyticsService {
  /**
   * Calculate all mastery metrics for a user
   */
  static calculateMetrics(
    userPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ): MasteryMetrics {
    // Calculate coverage
    const coverage = {
      completed: userPath.pathHistory?.length || 0,
      total: allConcepts.size,
      percentage: Math.round(((userPath.pathHistory?.length || 0) / allConcepts.size) * 100),
    };

    // Calculate velocity (completions per week)
    const velocity = this.calculateVelocity(userPath);

    // Generate time series data
    const timeSeries = this.generateTimeSeries(userPath, allConcepts);

    // Calculate distribution by category
    const byCategory = this.calculateCategoryDistribution(
      userPath,
      allConcepts
    );

    // Estimate completion date
    const estimatedCompletionDate = this.estimateCompletionDate(
      userPath,
      velocity.averagePerWeek,
      allConcepts.size
    );

    return {
      coverage,
      velocity,
      timeSeries,
      byCategory,
      estimatedCompletionDate,
    };
  }

  /**
   * Calculate completion velocity (nodes completed per week)
   */
  private static calculateVelocity(userPath: UserPath) {
    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);

    // Mock velocity calculation
    // In production, this would analyze actual completion timestamps
    const thisWeek = Math.floor(Math.random() * 3) + 1;
    const lastWeek = Math.floor(Math.random() * 3) + 1;
    const averagePerWeek =
      ((userPath.pathHistory?.length || 0) /
        (Math.max(1, Math.floor((now.getTime() - new Date(userPath.createdAt || new Date()).getTime()) / (7 * 24 * 60 * 60 * 1000))))) ||
      1;

    const trend: "up" | "down" | "stable" =
      thisWeek > lastWeek ? "up" : thisWeek < lastWeek ? "down" : "stable";

    return {
      thisWeek,
      lastWeek,
      averagePerWeek: Math.round(averagePerWeek * 10) / 10,
      trend,
    };
  }

  /**
   * Generate time series data for charts
   */
  private static generateTimeSeries(
    userPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ) {
    const timeSeries: MasteryMetrics["timeSeries"] = [];

    // Generate last 30 days
    for (let i = 29; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);

      // Mock data - in production, use actual completion timestamps
      const completed = Math.floor(
        ((userPath.pathHistory?.length || 0) / 30) + Math.sin(i / 5) * 0.5
      );
      const cumulative = Math.floor(((userPath.pathHistory?.length || 0) / 30) * (30 - i));

      timeSeries.push({
        date: date.toISOString().split("T")[0],
        completed: Math.max(0, completed),
        cumulative: Math.max(0, cumulative),
      });
    }

    return timeSeries;
  }

  /**
   * Calculate concept distribution by source type
   */
  private static calculateCategoryDistribution(
    userPath: UserPath,
    allConcepts: Map<string, KnowledgeNode>
  ) {
    const distribution: Record<string, number> = {};

    userPath.pathHistory.forEach((conceptId: string) => {
      const concept = allConcepts.get(conceptId);
      if (concept) {
        const category = concept.sourceMetadata?.sourceType || "other";
        distribution[category] = (distribution[category] || 0) + 1;
      }
    });

    return distribution;
  }

  /**
   * Estimate when user will complete the path
   */
  private static estimateCompletionDate(
    userPath: UserPath,
    averagePerWeek: number,
    totalConcepts: number
  ): string {
    const remaining = totalConcepts - (userPath.pathHistory?.length || 0);
    const weeksNeeded = Math.ceil(remaining / averagePerWeek);

    const completionDate = new Date();
    completionDate.setDate(completionDate.getDate() + weeksNeeded * 7);

    return completionDate.toISOString();
  }
}
