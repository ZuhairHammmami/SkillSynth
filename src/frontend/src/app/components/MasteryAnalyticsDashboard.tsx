/**
 * src/frontend/src/app/components/MasteryAnalyticsDashboard.tsx
 * 
 * Mastery Statistics Dashboard
 * Visualizes user's learning progress with analytics, including Skill Gap analysis
 */

"use client";

import { useMemo } from "react";
import { UserPath } from "@/entities/UserPath";
import { KnowledgeNode } from "@/entities/KnowledgeNode";
import { MasteryAnalyticsService, type MasteryMetrics } from "@/shared/services/MasteryAnalyticsService";
import { SkillGapAnalyzerService, type SkillGapAnalysis } from "@/shared/services/SkillGapAnalyzerService";

interface MasteryAnalyticsDashboardProps {
  userPath: UserPath | null;
  allConcepts: Map<string, KnowledgeNode> | null;
}

/**
 * Skill Gap Visualizer - Shows weak prerequisites blocking advancement
 */
function SkillGapVisualizer({ analysis }: { analysis: SkillGapAnalysis }) {
  if (!analysis.hasGaps) {
    return (
      <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-6 border border-emerald-200">
        <div className="flex items-start gap-4">
          <div className="text-3xl">✓</div>
          <div>
            <h3 className="text-lg font-bold text-emerald-900 mb-2">
              Strong Foundation
            </h3>
            <p className="text-sm text-emerald-700">
              No skill gaps detected. Your prerequisites are solid and ready for advanced concepts!
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Recommendations Alert */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
        <div className="flex items-start gap-3">
          <span className="text-xl mt-0.5">⚠️</span>
          <div>
            <h4 className="font-semibold text-amber-900 mb-3">
              Skill Gaps Detected
            </h4>
            <ul className="space-y-2">
              {analysis.recommendations.map((rec, idx) => (
                <li key={idx} className="text-sm text-amber-800 flex items-start gap-2">
                  <span className="text-amber-600 mt-0.5">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Weak Skills List */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-900 text-sm uppercase">
          Skills Needing Review ({analysis.weakSkills.length})
        </h4>
        {analysis.weakSkills.map((skill) => {
          const priorityStyles = {
            critical: "bg-red-50 border-red-200 hover:bg-red-100",
            high: "bg-orange-50 border-orange-200 hover:bg-orange-100",
            medium: "bg-yellow-50 border-yellow-200 hover:bg-yellow-100",
          };

          const priorityBadge = {
            critical: <span className="text-xs font-bold px-2 py-1 rounded bg-red-200 text-red-900">CRITICAL</span>,
            high: <span className="text-xs font-bold px-2 py-1 rounded bg-orange-200 text-orange-900">HIGH</span>,
            medium: <span className="text-xs font-bold px-2 py-1 rounded bg-yellow-200 text-yellow-900">MEDIUM</span>,
          };

          return (
            <div
              key={skill.skillId}
              className={`border rounded-lg p-4 transition-colors ${priorityStyles[skill.priority]}`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <h5 className="font-semibold text-gray-900 text-sm">
                    {skill.skillLabel}
                  </h5>
                  <p className="text-xs text-gray-600 mt-1">
                    {skill.recommendedAction}
                  </p>
                </div>
                {priorityBadge[skill.priority]}
              </div>

              {/* Reliability Score Bar */}
              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-700">
                    Reliability
                  </span>
                  <span className="text-xs font-bold text-gray-900">
                    {(skill.reliabilityScore * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all ${
                      skill.reliabilityScore < 0.5
                        ? "bg-red-500"
                        : skill.reliabilityScore < 0.7
                        ? "bg-orange-500"
                        : "bg-yellow-500"
                    }`}
                    style={{ width: `${skill.reliabilityScore * 100}%` }}
                  />
                </div>
              </div>

              {/* Impact Info */}
              <div className="text-xs text-gray-600">
                <span className="font-medium">Blocking</span>: {skill.blockedCount} advanced skill
                {skill.blockedCount !== 1 ? "s" : ""}
              </div>
            </div>
          );
        })}
      </div>

      {/* Overall Reliability Gauge */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-semibold text-gray-900">
            Foundation Strength
          </span>
          <span className="text-lg font-bold text-gray-900">
            {(analysis.overallReliability * 100).toFixed(0)}%
          </span>
        </div>
        <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all ${
              analysis.overallReliability < 0.6
                ? "bg-red-500"
                : analysis.overallReliability < 0.8
                ? "bg-orange-500"
                : "bg-emerald-500"
            }`}
            style={{ width: `${analysis.overallReliability * 100}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {analysis.overallReliability < 0.6
            ? "⚠️ Foundation needs strengthening"
            : analysis.overallReliability < 0.8
            ? "→ Room for improvement"
            : "✓ Strong foundation"}
        </p>
      </div>
    </div>
  );
}

/**
 * Velocity Chart - Shows tasks completed per week
 */
function VelocityChart({ thisWeek, lastWeek }: { thisWeek: number; lastWeek: number }) {
  const max = Math.max(thisWeek, lastWeek, 5);

  return (
    <div className="space-y-4">
      {/* This Week */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">This Week</span>
          <span className="text-2xl font-bold text-blue-600">{thisWeek}</span>
        </div>
        <div className="h-8 bg-gray-100 rounded-lg overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all"
            style={{ width: `${(thisWeek / max) * 100}%` }}
          />
        </div>
      </div>

      {/* Last Week */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Last Week</span>
          <span className="text-2xl font-bold text-gray-600">{lastWeek}</span>
        </div>
        <div className="h-8 bg-gray-100 rounded-lg overflow-hidden">
          <div
            className="h-full bg-gray-400 transition-all"
            style={{ width: `${(lastWeek / max) * 100}%` }}
          />
        </div>
      </div>
    </div>
  );
}

/**
 * Mastery Heatmap - Visual representation of skill density
 */
function MasteryHeatmap({
  byCategory,
  total,
}: {
  byCategory: Record<string, number>;
  total: number;
}) {
  const categories = Object.entries(byCategory).map(([cat, count]) => ({
    category: cat.charAt(0).toUpperCase() + cat.slice(1),
    count,
    percentage: Math.round((count / total) * 100),
  }));

  if (categories.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No completion data yet</p>
      </div>
    );
  }

  // Color map for heatmap
  const getHeatmapColor = (percentage: number) => {
    if (percentage >= 60) return "bg-red-600";
    if (percentage >= 40) return "bg-orange-500";
    if (percentage >= 20) return "bg-yellow-500";
    return "bg-blue-500";
  };

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      {categories.map(({ category, count, percentage }) => (
        <div key={category} className="text-center">
          <div
            className={`w-full h-20 rounded-lg mb-2 flex items-center justify-center text-white font-bold text-lg shadow-sm hover:shadow-md transition-shadow cursor-pointer ${getHeatmapColor(
              percentage
            )}`}
          >
            {count}
          </div>
          <div className="text-xs font-medium text-gray-700">{category}</div>
          <div className="text-xs text-gray-500">{percentage}%</div>
        </div>
      ))}
    </div>
  );
}

/**
 * Main Dashboard Component
 */
export function MasteryAnalyticsDashboard({
  userPath,
  allConcepts,
}: MasteryAnalyticsDashboardProps) {
  const metrics = useMemo<MasteryMetrics | null>(() => {
    if (!userPath || !allConcepts || allConcepts.size === 0) {
      return null;
    }

    return MasteryAnalyticsService.calculateMetrics(userPath, allConcepts);
  }, [userPath, allConcepts]);

  // Calculate skill gaps
  const skillGapAnalysis = useMemo<SkillGapAnalysis>(() => {
    if (!userPath || !allConcepts || allConcepts.size === 0) {
      return {
        hasGaps: false,
        weakSkills: [],
        totalBlockedSkills: 0,
        overallReliability: 1.0,
        recommendations: [],
      };
    }

    return SkillGapAnalyzerService.analyzeSkillGaps(
      userPath,
      allConcepts,
      userPath.pathHistory // Use path history as mastered concepts
    );
  }, [userPath, allConcepts]);

  if (!metrics) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>Loading analytics...</p>
      </div>
    );
  }

  const estimatedDate = new Date(metrics.estimatedCompletionDate);
  const weeksRemaining = Math.ceil(
    (estimatedDate.getTime() - Date.now()) / (7 * 24 * 60 * 60 * 1000)
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-gray-200 pb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Mastery Analytics</h2>
        <p className="text-gray-600">
          Your learning journey in numbers. Keep pushing to reach mastery!
        </p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Path Coverage */}
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border border-blue-200">
          <div className="text-sm font-semibold text-blue-600 uppercase tracking-wide mb-2">
            Path Coverage
          </div>
          <div className="text-4xl font-bold text-blue-900 mb-1">
            {metrics.coverage.percentage}%
          </div>
          <p className="text-sm text-blue-700">
            {metrics.coverage.completed} of {metrics.coverage.total} concepts
          </p>
        </div>

        {/* Engineering Velocity */}
        <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-6 border border-emerald-200">
          <div className="text-sm font-semibold text-emerald-600 uppercase tracking-wide mb-2">
            Weekly Velocity
          </div>
          <div className="text-4xl font-bold text-emerald-900 mb-1">
            {metrics.velocity.thisWeek}
          </div>
          <p className="text-sm text-emerald-700">
            concepts this week{" "}
            {metrics.velocity.trend === "up" && "📈"}
            {metrics.velocity.trend === "down" && "📉"}
            {metrics.velocity.trend === "stable" && "→"}
          </p>
        </div>

        {/* Average Velocity */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 border border-purple-200">
          <div className="text-sm font-semibold text-purple-600 uppercase tracking-wide mb-2">
            Average Velocity
          </div>
          <div className="text-4xl font-bold text-purple-900 mb-1">
            {metrics.velocity.averagePerWeek}
          </div>
          <p className="text-sm text-purple-700">concepts per week</p>
        </div>

        {/* Estimated Completion */}
        <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-6 border border-amber-200">
          <div className="text-sm font-semibold text-amber-600 uppercase tracking-wide mb-2">
            Completion Est.
          </div>
          <div className="text-2xl font-bold text-amber-900 mb-1">
            {weeksRemaining} weeks
          </div>
          <p className="text-xs text-amber-700">
            ~{estimatedDate.toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Velocity Section */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-6">
              Engineering Velocity
            </h3>
            <VelocityChart
              thisWeek={metrics.velocity.thisWeek}
              lastWeek={metrics.velocity.lastWeek}
            />
            <p className="text-xs text-gray-500 mt-6 italic">
              Complete more concepts each week to accelerate your mastery journey
            </p>
          </div>
        </div>

        {/* Coverage Section */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-6">Path Coverage</h3>

            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Domain Mastery
                </span>
                <span className="text-sm font-bold text-gray-900">
                  {metrics.coverage.percentage}%
                </span>
              </div>
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all"
                  style={{ width: `${metrics.coverage.percentage}%` }}
                />
              </div>
            </div>

            {/* Milestone badges */}
            <div className="space-y-2 mt-6">
              <div className="text-xs font-semibold text-gray-600 uppercase">
                Milestones Reached
              </div>
              <div className="flex flex-wrap gap-2">
                {[25, 50, 75, 100].map((milestone) => (
                  <span
                    key={milestone}
                    className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${
                      metrics.coverage.percentage >= milestone
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-gray-100 text-gray-500"
                    }`}
                  >
                    {milestone}%
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Heatmap Section */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
            <h3 className="text-lg font-bold text-gray-900 mb-6">
              Mastery Heatmap
            </h3>
            <MasteryHeatmap
              byCategory={metrics.byCategory}
              total={metrics.coverage.completed}
            />
            <p className="text-xs text-gray-500 mt-6 italic">
              Darker colors indicate higher density of skills acquired
            </p>
          </div>
        </div>
      </div>

      {/* Time Series Preview (Future Enhancement) */}
      <div className="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <h3 className="text-lg font-bold text-gray-900 mb-4">
          30-Day Trend (Preview)
        </h3>
        <div className="h-40 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <p className="text-gray-600 text-sm">
              📊 Trend visualization coming soon
            </p>
            <p className="text-gray-500 text-xs mt-2">
              Track your daily completion rate over time
            </p>
          </div>
        </div>
      </div>

      {/* Skill Gap Analyzer Section */}
      <div>
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Skill Gap Analysis</h2>
          <p className="text-gray-600">
            Weak prerequisites blocking your advancement. Address these to unlock faster progress.
          </p>
        </div>
        <SkillGapVisualizer analysis={skillGapAnalysis} />
      </div>
    </div>
  );
}
