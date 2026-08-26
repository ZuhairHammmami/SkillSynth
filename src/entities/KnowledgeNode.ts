import { z } from "zod";

export const SourceMetadataSchema = z.object({
  sourceType: z.enum(["academic", "market", "other"]),
  sourceUrl: z.string().url(),
  lastUpdated: z.string().datetime(),
  reliabilityScore: z.number().min(0).max(1),
});

export const KnowledgeNodeSchema = z.object({
  id: z.string().uuid(),
  label: z.string(),
  confidenceScore: z.number().gt(0.7), // strictly > 0.7
  prerequisites: z.array(z.string().uuid()), // UUIDs of other KnowledgeNodes
  sourceMetadata: SourceMetadataSchema,
});

export type KnowledgeNode = z.infer<typeof KnowledgeNodeSchema>;