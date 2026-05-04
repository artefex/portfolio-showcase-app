"use client";

import { useEffect, useRef, useState } from "react";

import { streamChat } from "@/lib/api";
import type { DonePayload, Message } from "@/lib/types";

import { ChatInput } from "./ChatInput";
import { ChatMessage } from "./ChatMessage";
import { ErrorBanner } from "./ErrorBanner";
import { LoadingIndicator } from "./LoadingIndicator";

const WELCOME_MESSAGE: Message = {
  id: "welcome",
  role: "assistant",
  content:
    "Welcome! Ask me about recipes, cooking techniques, or ingredient ideas.",
  timestamp: new Date(),
};

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    const assistantId = crypto.randomUUID();
    const assistantMessage: Message = {
      id: assistantId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      isStreaming: true,
    };

    setMessages((prev) => [...prev, assistantMessage]);

    // Build conversation history (exclude welcome message and the empty streaming message)
    const history = messages
      .filter((msg) => msg.id !== "welcome" && msg.content && !msg.isStreaming)
      .map((msg) => ({ role: msg.role, content: msg.content }));

    try {
      await streamChat(
        { message: content, history },
        // onToken
        (token) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? { ...msg, content: msg.content + token }
                : msg,
            ),
          );
        },
        // onNode
        () => {},
        // onDone
        (response: DonePayload) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? {
                    ...msg,
                    content: response.final_response || msg.content,
                    isStreaming: false,
                    metadata: {
                      toolsUsed: response.tools_used,
                      cookwareCheck: response.cookware_check ?? undefined,
                    },
                  }
                : msg,
            ),
          );
        },
        // onError
        (errorMsg) => {
          setError(errorMsg);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId
                ? { ...msg, isStreaming: false, content: msg.content || "An error occurred." }
                : msg,
            ),
          );
        },
      );
    } catch {
      setError("Failed to connect to the server.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex w-full max-w-2xl flex-col rounded-lg border shadow-sm" style={{ height: "70vh" }}>
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {isLoading && messages[messages.length - 1]?.content === "" && (
          <LoadingIndicator />
        )}
        <div ref={messagesEndRef} />
      </div>
      {error && <ErrorBanner message={error} />}
      <div className="border-t p-4">
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
}
