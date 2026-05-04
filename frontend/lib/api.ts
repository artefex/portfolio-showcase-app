import { API_URL } from "./constants";
import { chatRequestSchema, donePayloadSchema } from "./schemas";
import type { ChatRequest, DonePayload } from "./types";

export async function streamChat(
  request: ChatRequest,
  onToken: (token: string) => void,
  onNode: (node: string, status: string) => void,
  onDone: (response: DonePayload) => void,
  onError: (error: string) => void,
): Promise<void> {
  const validated = chatRequestSchema.parse(request);
  const response = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validated),
  });

  if (!response.ok) {
    onError(`Server error: ${response.status}`);
    return;
  }

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    let currentEvent = "";
    for (const line of lines) {
      if (line.startsWith("event: ")) {
        currentEvent = line.slice(7);
      } else if (line.startsWith("data: ")) {
        const data = JSON.parse(line.slice(6));
        switch (currentEvent) {
          case "token":
            onToken(data.content);
            break;
          case "node":
            onNode(data.node, data.status);
            break;
          case "done":
            onDone(donePayloadSchema.parse(data));
            break;
          case "error":
            onError(data.message);
            break;
        }
      }
    }
  }
}
