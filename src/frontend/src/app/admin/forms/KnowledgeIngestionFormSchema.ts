import { z } from "zod";

export const KnowledgeIngestionFormSchema = z.object({
  label: z.string().min(1, "Concept name is required"),
  confidenceScore: z
    .number()
    .gt(0.7, "Confidence score must be greater than 0.7")
    .lte(1, "Confidence score must be at most 1"),
  sourceType: z.enum(["academic", "market", "other"]),
  sourceUrl: z.string().url("Must be a valid URL"),
  reliabilityScore: z.number().min(0).max(1).optional(),
  prerequisites: z.array(z.string().uuid()).default([]),
});

export type KnowledgeIngestionFormData = z.infer<
  typeof KnowledgeIngestionFormSchema
>;
