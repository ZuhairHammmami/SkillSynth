/**
 * src/frontend/src/app/components/LearningInterventionUI.tsx
 * 
 * Learning Intervention Alert
 * Displayed when a user is stuck on a concept for >48 hours
 * Presents intervention options to help them progress
 */

"use client";

import { useState } from "react";
import {
  StuckDetectionResult,
  LearningInterventionOption,
} from "@/shared/services/StuckProtocolService";

interface LearningInterventionUIProps {
  stuckDetection: StuckDetectionResult;
  onInterventionSelected: (intervention: LearningInterventionOption) => void;
  onDismiss: () => void;
}

/**
 * Alert card for when user is stuck
 */
export function LearningInterventionUI({
  stuckDetection,
  onInterventionSelected,
  onDismiss,
}: LearningInterventionUIProps) {
  const [selectedIntervention, setSelectedIntervention] =
    useState<LearningInterventionOption | null>(null);

  if (!stuckDetection.isStuck) {
    return null; // Don't show if not stuck
  }

  const { hoursSpent, hoursOverThreshold, currentConcept, interventionOptions } =
    stuckDetection;

  return (
    <div className="fixed bottom-4 right-4 max-w-md z-50 animate-in slide-in-from-bottom-4">
      <div className="bg-white border-l-4 border-red-500 rounded-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-50 to-orange-50 p-4 border-b border-red-200">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <h3 className="text-sm font-bold text-red-900 flex items-center gap-2">
                🔴 Learning Stuck Alert
              </h3>
              <p className="text-xs text-red-700 mt-1">
                You&apos;ve been on <span className="font-semibold">&quot;{currentConcept?.label}&quot;</span> for{" "}
                <span className="font-bold">{hoursSpent} hours</span>
              </p>
            </div>
            <button
              onClick={onDismiss}
              className="text-red-400 hover:text-red-600 text-lg"
              aria-label="Dismiss"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Message */}
        <div className="p-4 bg-white">
          <p className="text-sm text-gray-700 mb-4">
            We notice you&apos;ve been working on this concept for a while. Let us help you
            move forward! Select an intervention below:
          </p>

          {/* Intervention Options */}
          <div className="space-y-2">
            {interventionOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => {
                  setSelectedIntervention(option);
                  onInterventionSelected(option);
                }}
                className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition-colors group"
              >
                <div className="flex items-start gap-3">
                  <span className="text-lg mt-0.5">{option.icon}</span>
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-gray-900 group-hover:text-blue-900">
                      {option.title}
                    </h4>
                    <p className="text-xs text-gray-600 mt-0.5">
                      {option.description}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Footer with Info */}
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
          <p className="text-xs text-gray-600">
            💡 <span className="font-medium">Tip:</span> Most learners complete this concept with
            help or a different approach. You&apos;ve got this!
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Inline intervention suggestion (shows during learning)
 */
export function StuckIndicator({
  hoursSpent,
  status,
  onGetHelp,
}: {
  hoursSpent: number;
  status: string;
  onGetHelp: () => void;
}) {
  if (hoursSpent < 48) {
    return null;
  }

  const isExtremelyStuck = hoursSpent >= 96;
  const isSeverelyStuck = hoursSpent >= 72;

  return (
    <div
      className={`p-4 rounded-lg border ${
        isExtremelyStuck
          ? "bg-red-50 border-red-300 text-red-900"
          : isSeverelyStuck
          ? "bg-orange-50 border-orange-300 text-orange-900"
          : "bg-yellow-50 border-yellow-300 text-yellow-900"
      }`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-lg">
            {isExtremelyStuck ? "🔴" : isSeverelyStuck ? "🟠" : "🟡"}
          </span>
          <span className="text-sm font-semibold">{status}</span>
        </div>
        <button
          onClick={onGetHelp}
          className={`text-xs font-bold px-3 py-1.5 rounded transition-colors ${
            isExtremelyStuck
              ? "bg-red-200 hover:bg-red-300 text-red-900"
              : isSeverelyStuck
              ? "bg-orange-200 hover:bg-orange-300 text-orange-900"
              : "bg-yellow-200 hover:bg-yellow-300 text-yellow-900"
          }`}
        >
          Get Help →
        </button>
      </div>
    </div>
  );
}

/**
 * Card showing available interventions with expected outcomes
 */
export function InterventionSuggestions({
  interventions,
  onSelect,
}: {
  interventions: LearningInterventionOption[];
  onSelect: (intervention: LearningInterventionOption) => void;
}) {
  return (
    <div className="space-y-3">
      <h3 className="font-semibold text-gray-900 text-sm">Available Options</h3>
      {interventions.map((intervention) => (
        <div
          key={intervention.id}
          className="border border-gray-200 rounded-lg p-4 hover:border-blue-400 hover:bg-blue-50 cursor-pointer transition-all"
          onClick={() => onSelect(intervention)}
        >
          <div className="flex items-start gap-3">
            <span className="text-2xl">{intervention.icon}</span>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 text-sm">
                {intervention.title}
              </h4>
              <p className="text-xs text-gray-600 mt-1">
                {intervention.description}
              </p>
              <div className="mt-2 pt-2 border-t border-gray-200">
                <p className="text-xs text-gray-700">
                  <span className="font-medium">Expected outcome:</span>{" "}
                  {intervention.expectedOutcome}
                </p>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
