import { NotificationService } from "./NotificationService";

/**
 * Example usage of NotificationService
 * This demonstrates how to integrate SendGrid notifications in the AEIS system
 */

export async function exampleNotificationUsage() {
  // Example 1: Send knowledge ingestion notification
  await NotificationService.notifyKnowledgeIngestion(
    "admin@aeis.dev",
    "React Hooks Fundamentals",
    "success"
  );

  // Example 2: Notify user of prerequisite conflict
  await NotificationService.notifyPrerequisiteConflict(
    "user@aeis.dev",
    "Advanced React Patterns",
    ["React Fundamentals", "Component Lifecycle"]
  );

  // Example 3: Send system-wide alert
  await NotificationService.sendSystemAlert(
    ["admin1@aeis.dev", "admin2@aeis.dev"],
    "High Confidence Threshold Alert",
    "A concept with confidence score below 0.7 was detected in the pipeline."
  );
}
