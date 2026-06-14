"use client";

import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  KnowledgeIngestionFormSchema,
  KnowledgeIngestionFormData,
} from "./KnowledgeIngestionFormSchema";
import { KnowledgeNode } from "@/entities/KnowledgeNode";

export interface KnowledgeIngestionFormProps {
  onSubmit: (data: KnowledgeIngestionFormData) => Promise<void>;
  isLoading?: boolean;
  existingConcepts?: KnowledgeNode[];
  onPrerequisitesChange?: (selectedIds: string[]) => void;
}

export function KnowledgeIngestionForm({
  onSubmit,
  isLoading = false,
  existingConcepts = [],
  onPrerequisitesChange,
}: KnowledgeIngestionFormProps) {
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm({
    resolver: zodResolver(KnowledgeIngestionFormSchema),
  });

  const confidenceScore = watch("confidenceScore");
  const prerequisites = watch("prerequisites");

  // Trigger live preview callback when prerequisites change
  const handlePrerequisitesChange = (selectedIds: string[]) => {
    setValue("prerequisites", selectedIds);
    onPrerequisitesChange?.(selectedIds);
  };

  const handleFormSubmit = async (data: any) => {
    try {
      setError(null);
      await onSubmit(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to ingest knowledge"
      );
    }
  };

  return (
    <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
      {error && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-700 border border-red-200">
          ❌ {error}
        </div>
      )}

      {/* Concept Name */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Concept Name *
        </label>
        <input
          {...register("label")}
          type="text"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="e.g., React Hooks Advanced Patterns"
        />
        {errors.label && (
          <p className="mt-1 text-sm text-red-600">{errors.label.message}</p>
        )}
      </div>

      {/* Confidence Score */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Confidence Score *
          {confidenceScore && (
            <span className="ml-2 text-xs font-normal text-blue-600 bg-blue-50 px-2 py-1 rounded">
              {confidenceScore.toFixed(2)}
            </span>
          )}
        </label>
        <input
          {...register("confidenceScore", { valueAsNumber: true })}
          type="number"
          step="0.01"
          min="0.71"
          max="1"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="0.85"
        />
        {errors.confidenceScore && (
          <p className="mt-1 text-sm text-red-600">
            {errors.confidenceScore.message}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-500">
          Must be {'>'} 0.7 (mastery threshold)
        </p>
      </div>

      {/* Source Type */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Source Type *
        </label>
        <select
          {...register("sourceType")}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <option value="">Select source type...</option>
          <option value="academic">Academic Research</option>
          <option value="market">Market Data</option>
          <option value="other">Other</option>
        </select>
        {errors.sourceType && (
          <p className="mt-1 text-sm text-red-600">
            {errors.sourceType.message}
          </p>
        )}
      </div>

      {/* Source URL */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Source URL *
        </label>
        <input
          {...register("sourceUrl")}
          type="url"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="https://example.com/resource"
        />
        {errors.sourceUrl && (
          <p className="mt-1 text-sm text-red-600">
            {errors.sourceUrl.message}
          </p>
        )}
      </div>

      {/* Reliability Score */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Reliability Score (Optional)
        </label>
        <input
          {...register("reliabilityScore", { valueAsNumber: true })}
          type="number"
          step="0.01"
          min="0"
          max="1"
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="0.85"
        />
      </div>

      {/* Prerequisites */}
      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Prerequisites (Optional)
        </label>
        <select
          multiple
          value={prerequisites || []}
          onChange={(e) => {
            const selectedIds = Array.from(e.target.selectedOptions, (option) =>
              option.value
            );
            handlePrerequisitesChange(selectedIds);
          }}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          {existingConcepts.map((concept) => (
            <option key={concept.id} value={concept.id}>
              {concept.label} (confidence: {concept.confidenceScore})
            </option>
          ))}
        </select>
        {errors.prerequisites && (
          <p className="mt-1 text-sm text-red-600">
            {errors.prerequisites.message}
          </p>
        )}
        <p className="mt-2 text-xs text-gray-500">
          Hold Ctrl/Cmd to select multiple prerequisites
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-3 text-white font-semibold hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
      >
        {isLoading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent"></span>
            Ingesting...
          </span>
        ) : (
          "Ingest Knowledge"
        )}
      </button>
    </form>
  );
}
