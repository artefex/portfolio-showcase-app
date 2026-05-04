import type { z } from "zod";

import type {
  chatRequestSchema,
  cookwareResultSchema,
  donePayloadSchema,
  sseEventSchema,
} from "./schemas";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  metadata?: {
    toolsUsed?: string[];
    cookwareCheck?: CookwareResult;
  };
}

export type ChatRequest = z.input<typeof chatRequestSchema>;
export type CookwareResult = z.infer<typeof cookwareResultSchema>;
export type SSEEvent = z.infer<typeof sseEventSchema>;
export type DonePayload = z.infer<typeof donePayloadSchema>;
