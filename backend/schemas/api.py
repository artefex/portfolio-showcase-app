from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    history: list[ChatMessage] = Field(default_factory=list, description="Previous conversation messages")
    conversation_id: str | None = Field(None, description="Optional conversation ID for context")


class CookwareResult(BaseModel):
    sufficient: bool
    missing: list[str] = []
    suggestions: str = ""


class DebugEntry(BaseModel):
    node: str
    reasoning: str
    timestamp: str


class ChatResponse(BaseModel):
    response: str
    is_cooking_related: bool
    tools_used: list[str] = []
    cookware_check: CookwareResult | None = None
    debug: list[DebugEntry] | None = None
