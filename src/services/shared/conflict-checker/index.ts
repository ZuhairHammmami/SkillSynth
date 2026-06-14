import { ConflictCheckerService } from "./ConflictCheckerService";

/**
 * Example usage of ConflictCheckerService
 * Demonstrates prerequisite validation and conflict detection
 */

export async function exampleConflictCheckerUsage() {
  // Example: Check node transition
  // This would be used in the User Path Editor to validate moves

  const mockUserPath = {
    id: "user-path-123",
    userId: "user-456",
    currentNode: "node-1",
    pathHistory: ["node-1", "node-2"],
    allowedPaths: ["node-1", "node-2", "node-3", "node-4"],
    customSkillOverrides: {},
  };

  const mockAllNodes = new Map([
    [
      "node-1",
      {
        id: "node-1",
        label: "JavaScript Basics",
        confidenceScore: 0.85,
        prerequisites: [],
        sourceMetadata: {
          sourceType: "academic" as const,
          sourceUrl: "https://example.com",
          lastUpdated: new Date().toISOString(),
          reliabilityScore: 0.9,
        },
      },
    ],
    [
      "node-2",
      {
        id: "node-2",
        label: "React Fundamentals",
        confidenceScore: 0.88,
        prerequisites: ["node-1"],
        sourceMetadata: {
          sourceType: "market" as const,
          sourceUrl: "https://example.com",
          lastUpdated: new Date().toISOString(),
          reliabilityScore: 0.92,
        },
      },
    ],
    [
      "node-3",
      {
        id: "node-3",
        label: "Advanced React",
        confidenceScore: 0.82,
        prerequisites: ["node-2"],
        sourceMetadata: {
          sourceType: "academic" as const,
          sourceUrl: "https://example.com",
          lastUpdated: new Date().toISOString(),
          reliabilityScore: 0.88,
        },
      },
    ],
  ]);

  // Check if user can move to node-3
  const result = ConflictCheckerService.checkNodeTransition(
    mockUserPath,
    "node-3",
    mockAllNodes
  );

  console.log("Transition check:", result);
  // Output: { hasConflict: false, conflictingNodes: [], message: "Transition is allowed" }

  // Get all blocked nodes for the user
  const blockedNodes = ConflictCheckerService.getBlockedNodes(
    mockUserPath,
    mockAllNodes
  );

  console.log("Blocked nodes:", blockedNodes);
}
