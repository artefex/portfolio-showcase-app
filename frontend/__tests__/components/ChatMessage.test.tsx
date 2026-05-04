import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ChatMessage } from "@/components/ChatMessage";

describe("ChatMessage", () => {
  it("renders user message content", () => {
    render(
      <ChatMessage
        message={{
          id: "1",
          role: "user",
          content: "How do I make pasta?",
          timestamp: new Date(),
        }}
      />,
    );
    expect(screen.getByText("How do I make pasta?")).toBeInTheDocument();
  });

  it("renders assistant message content", () => {
    render(
      <ChatMessage
        message={{
          id: "2",
          role: "assistant",
          content: "Here is a recipe for pasta.",
          timestamp: new Date(),
        }}
      />,
    );
    expect(screen.getByText(/Here is a recipe/)).toBeInTheDocument();
  });

  it("shows streaming indicator when streaming", () => {
    render(
      <ChatMessage
        message={{
          id: "3",
          role: "assistant",
          content: "Streaming...",
          timestamp: new Date(),
          isStreaming: true,
        }}
      />,
    );
    expect(screen.getByTestId("streaming-cursor")).toBeInTheDocument();
  });
});
