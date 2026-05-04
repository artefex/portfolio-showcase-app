import { describe, expect, it, vi } from "vitest";

import { streamChat } from "@/lib/api";

function createMockResponse(body: string): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(body));
      controller.close();
    },
  });
  return new Response(stream, {
    status: 200,
    headers: { "Content-Type": "text/event-stream" },
  });
}

describe("streamChat", () => {
  it("calls fetch with correct params", async () => {
    const mockFetch = vi.fn().mockResolvedValue(
      createMockResponse("event: done\ndata: {\"final_response\": \"test\", \"tools_used\": [], \"cookware_check\": null}\n\n"),
    );
    global.fetch = mockFetch;

    await streamChat({ message: "test" }, vi.fn(), vi.fn(), vi.fn(), vi.fn());

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/chat"),
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
      }),
    );
  });

  it("calls onToken for token events", async () => {
    const body = "event: token\ndata: {\"content\": \"Hello\"}\n\nevent: done\ndata: {\"final_response\": \"Hello\", \"tools_used\": [], \"cookware_check\": null}\n\n";
    global.fetch = vi.fn().mockResolvedValue(createMockResponse(body));

    const onToken = vi.fn();
    await streamChat({ message: "test" }, onToken, vi.fn(), vi.fn(), vi.fn());

    expect(onToken).toHaveBeenCalledWith("Hello");
  });

  it("calls onDone for done events", async () => {
    const body = 'event: done\ndata: {"final_response": "Done!", "tools_used": [], "cookware_check": null}\n\n';
    global.fetch = vi.fn().mockResolvedValue(createMockResponse(body));

    const onDone = vi.fn();
    await streamChat({ message: "test" }, vi.fn(), vi.fn(), onDone, vi.fn());

    expect(onDone).toHaveBeenCalledWith(expect.objectContaining({ final_response: "Done!" }));
  });

  it("calls onError on server error", async () => {
    global.fetch = vi.fn().mockResolvedValue(new Response(null, { status: 500 }));

    const onError = vi.fn();
    await streamChat({ message: "test" }, vi.fn(), vi.fn(), vi.fn(), onError);

    expect(onError).toHaveBeenCalledWith(expect.stringContaining("500"));
  });
});
