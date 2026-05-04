import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ChatInput } from "@/components/ChatInput";

describe("ChatInput", () => {
  it("calls onSend on form submit", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled={false} />);

    const input = screen.getByPlaceholderText(/recipe/i);
    fireEvent.change(input, { target: { value: "How do I cook pasta?" } });
    fireEvent.submit(input.closest("form")!);

    expect(onSend).toHaveBeenCalledWith("How do I cook pasta?");
  });

  it("is disabled when loading", () => {
    render(<ChatInput onSend={vi.fn()} disabled={true} />);

    const input = screen.getByPlaceholderText(/recipe/i);
    expect(input).toBeDisabled();
  });

  it("clears input after submit", () => {
    const onSend = vi.fn();
    render(<ChatInput onSend={onSend} disabled={false} />);

    const input = screen.getByPlaceholderText(/recipe/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "test" } });
    fireEvent.submit(input.closest("form")!);

    expect(input.value).toBe("");
  });
});
