"use client";

import { useState } from "react";
import Markdown from "react-markdown";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Message } from "@/lib/types";

interface ChatMessageProps {
  message: Message;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button
      variant="ghost"
      size="xs"
      onClick={handleCopy}
      className="mt-1 opacity-0 transition-opacity group-hover/message:opacity-100"
      aria-label="Copy to clipboard"
    >
      {copied ? "Copied!" : "Copy"}
    </Button>
  );
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`group/message flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      <Card
        className={`max-w-[80%] ${
          isUser
            ? "border-transparent bg-primary text-primary-foreground"
            : "bg-muted/50"
        }`}
      >
        <CardContent>
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose prose-sm dark:prose-invert max-w-none">
              <Markdown>{message.content}</Markdown>
            </div>
          )}
          {message.isStreaming && (
            <span
              data-testid="streaming-cursor"
              className="ml-1 inline-block h-4 w-1 animate-pulse bg-current"
            />
          )}
        </CardContent>
        {!isUser && message.content && !message.isStreaming && (
          <div className="flex justify-end px-4 pb-2">
            <CopyButton text={message.content} />
          </div>
        )}
      </Card>
    </div>
  );
}
