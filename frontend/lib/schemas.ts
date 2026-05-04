import { z } from "zod";

export const chatMessageSchema = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string(),
});

export const chatRequestSchema = z.object({
  message: z.string().min(1).max(2000),
  history: z.array(chatMessageSchema).default([]),
  conversation_id: z.string().optional(),
});

export const cookwareResultSchema = z.object({
  sufficient: z.boolean(),
  missing: z.array(z.string()),
  suggestions: z.string(),
});

export const donePayloadSchema = z.object({
  final_response: z.string(),
  tools_used: z.array(z.string()),
  cookware_check: cookwareResultSchema.nullable(),
});

export const sseEventSchema = z.object({
  event: z.enum(["token", "node", "tool", "cookware", "done", "error", "debug"]),
  data: z.record(z.string(), z.unknown()),
});
