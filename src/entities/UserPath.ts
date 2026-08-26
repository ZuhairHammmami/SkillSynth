import { z } from "zod";

export const UserPathSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  currentNode: z.string().uuid(),
  pathHistory: z.array(z.string().uuid()),
  allowedPaths: z.array(z.string().uuid()),
  customSkillOverrides: z.record(z.string(), z.any()), // Record of skillId to override config
});

export type UserPath = z.infer<typeof UserPathSchema>;