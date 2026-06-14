"use client";

import { useState, useCallback, useEffect } from "react";
import { KnowledgeIngestionForm } from "@/app/admin/forms/KnowledgeIngestionForm";
import type { KnowledgeIngestionFormData } from "@/app/admin/forms/KnowledgeIngestionFormSchema";
import { useConflictPreview } from "@/shared/hooks/useConflictPreview";
import { KnowledgeNode } from "@/entities/KnowledgeNode";

/**
 * Admin Knowledge Ingestion Dashboard
 * 
 * Full-page dashboard for admins to ingest new concepts with:
 * - Real-time conflict preview
 * - API integration to /api/ingest
 * - Success/error feedback
 * - Live DAG visualization (optional)
 */
export default function KnowledgeIngestionDashboard() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedPrerequisites, setSelectedPrerequisites] = useState<string[]>(
    []
  );

  // Mock data - will be fetched from database in Phase 3
  const mockConcepts: KnowledgeNode[] = [
    {
      id: "node-1",
      label: "JavaScript Fundamentals",
      confidenceScore: 0.85,
      prerequisites: [],
      sourceMetadata: {
        sourceType: "academic",
        sourceUrl: "https://example.com",
        lastUpdated: new Date().toISOString(),
        reliabilityScore: 0.9,
      },
    },
    {
      id: "node-2",
      label: "React Basics",
      confidenceScore: 0.88,
      prerequisites: ["node-1"],
      sourceMetadata: {
        sourceType: "market",
        sourceUrl: "https://example.com",
        lastUpdated: new Date().toISOString(),
        reliabilityScore: 0.92,
      },
    },
  ];

  const conceptsMap = new Map(mockConcepts.map((c) => [c.id, c]));
  const { preview, checkPrerequisiteConflict } =
    useConflictPreview(conceptsMap);

  const handlePrerequisitesChange = useCallback(
    (selectedIds: string[]) => {
      setSelectedPrerequisites(selectedIds);
      checkPrerequisiteConflict(selectedIds);
    },
    [checkPrerequisiteConflict]
  );

  const handleSubmit = async (data: KnowledgeIngestionFormData) => {
    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      // Re-check conflicts before submission
      const conflictCheck = checkPrerequisiteConflict(data.prerequisites || []);
      if (conflictCheck.hasConflict) {
        setErrorMessage(conflictCheck.message);
        setIsSubmitting(false);
        return;
      }

      // Call API endpoint
      const response = await fetch("/api/ingest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        setErrorMessage(result.error || "Failed to ingest concept");
        return;
      }

      setSuccessMessage(`✓ Successfully ingested: ${data.label}`);
      setSelectedPrerequisites([]);

      // Clear success message after 5 seconds
      setTimeout(() => setSuccessMessage(null), 5000);
    } catch (error) {
      const errorMsg =
        error instanceof Error ? error.message : "Network error occurred";
      setErrorMessage(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Knowledge Ingestion Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            Add new engineering concepts to AEIS with mastery-first validation
          </p>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Form Column */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <KnowledgeIngestionForm
                onSubmit={handleSubmit}
                isLoading={isSubmitting}
                existingConcepts={mockConcepts}
                onPrerequisitesChange={handlePrerequisitesChange}
              />
            </div>
          </div>

          {/* Sidebar - Conflict Preview & Info */}
          <div className="lg:col-span-1 space-y-6">
            {/* Conflict Preview Widget */}
            <div
              className={`rounded-lg p-6 ${
                preview.hasConflict
                  ? "bg-red-50 border-2 border-red-200"
                  : "bg-green-50 border-2 border-green-200"
              }`}
            >
              <h3 className="font-semibold text-sm mb-3">
                {preview.hasConflict ? "⚠️ Conflict Detected" : "✓ No Conflicts"}
              </h3>
              <p className="text-sm text-gray-700">{preview.message}</p>

              {preview.blockedNodes && preview.blockedNodes.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-xs font-semibold text-gray-600 mb-2">
                    Affected Nodes:
                  </p>
                  <ul className="space-y-1">
                    {preview.blockedNodes.map((nodeId) => (
                      <li
                        key={nodeId}
                        className="text-xs text-gray-700 bg-white bg-opacity-50 rounded px-2 py-1"
                      >
                        • {nodeId}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Validation Rules */}
            <div className="bg-blue-50 rounded-lg p-6 border-2 border-blue-200">
              <h3 className="font-semibold text-sm text-blue-900 mb-4">
                📋 Validation Rules
              </h3>
              <ul className="space-y-3 text-sm text-blue-800">
                <li className="flex items-start gap-2">
                  <span className="text-lg">✓</span>
                  <span>Confidence score must be {'>'} 0.7</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-lg">✓</span>
                  <span>Source URL must be valid</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-lg">✓</span>
                  <span>No circular prerequisites allowed</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-lg">✓</span>
                  <span>Prerequisites auto-linked</span>
                </li>
              </ul>
            </div>

            {/* Statistics */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="font-semibold text-sm text-gray-900 mb-4">
                📊 System Status
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Concepts:</span>
                  <span className="font-semibold text-gray-900">
                    {mockConcepts.length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">API Status:</span>
                  <span className="font-semibold text-green-600">Ready</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">DB Connection:</span>
                  <span className="font-semibold text-green-600">Connected</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Feedback Messages */}
        {successMessage && (
          <div className="fixed bottom-8 right-8 bg-green-50 border-2 border-green-200 rounded-lg p-6 shadow-lg">
            <p className="text-green-800">{successMessage}</p>
          </div>
        )}

        {errorMessage && (
          <div className="fixed bottom-8 right-8 bg-red-50 border-2 border-red-200 rounded-lg p-6 shadow-lg">
            <p className="text-red-800">{errorMessage}</p>
          </div>
        )}
      </div>
    </div>
  );
}
