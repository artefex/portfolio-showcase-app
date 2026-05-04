"use client";

export function LoadingIndicator() {
  return (
    <div className="flex items-center gap-1 p-2 text-sm text-muted-foreground">
      <span className="animate-pulse">Thinking...</span>
    </div>
  );
}
