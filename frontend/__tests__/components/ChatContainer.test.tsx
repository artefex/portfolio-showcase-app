import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ChatContainer } from "@/components/ChatContainer";

describe("ChatContainer", () => {
  it("renders welcome message", () => {
    render(<ChatContainer />);
    expect(screen.getByText(/welcome|cooking|recipe/i)).toBeInTheDocument();
  });

  it("renders the chat input", () => {
    render(<ChatContainer />);
    expect(screen.getByPlaceholderText(/recipe/i)).toBeInTheDocument();
  });
});
