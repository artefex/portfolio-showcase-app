# Recipe Assistant Showcase

A sanitized public portfolio project that demonstrates a streaming AI recipe
assistant built with a FastAPI backend, a LangGraph workflow, and a Next.js chat
frontend.

This repository contains neutral demo content only. It does not include client
data, proprietary branding, private domains, analytics IDs, credentials, or
production deployment targets.

## What This Demonstrates

- A small monorepo with separate `backend` and `frontend` applications.
- A LangGraph workflow with classification, reasoning, optional tool use,
  cookware validation, and deterministic response formatting.
- Server-Sent Events from FastAPI to a typed Next.js client.
- Runtime validation with Pydantic and Zod.
- Testable service boundaries with mock LLM services in the backend tests.
- Docker Compose setup for local full-stack development.

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend | FastAPI, Pydantic, Server-Sent Events |
| AI workflow | LangGraph, LangChain service protocols |
| LLM provider | Anthropic via `langchain-anthropic` |
| Search tool | Tavily via LangChain community tools |
| Frontend | Next.js 16, React 19, TypeScript |
| Styling | Tailwind CSS, shadcn/ui-style primitives |
| Validation | Pydantic, Zod |
| Tests | Pytest, Vitest, Testing Library |
| Containers | Docker, Docker Compose |

## Key Features

- Classifies incoming messages as cooking-related or out of scope.
- Streams assistant responses to the browser as tokens arrive.
- Lets the reasoning model call a search tool when current information is useful.
- Checks generated recipes against a demo cookware list.
- Sends conversation history so follow-up questions can be interpreted in context.
- Provides a debug stream for graph node transitions when `debug=true`.

## Architecture Notes

The backend builds a LangGraph state machine from injected service protocols. LLM
dependent nodes depend on narrow interfaces, which keeps node logic easy to test
with mock services.

```text
User message
  -> classify_query
  -> refuse_query | reasoning
  -> tools? -> reasoning
  -> cookware_check?
  -> format_response
  -> SSE done event
```

Important modules:

- `backend/main.py`: FastAPI app and SSE event formatting.
- `backend/graphs/recipe_graph.py`: LangGraph topology and routing.
- `backend/nodes/`: graph node implementations.
- `backend/services/`: provider-backed and mock service implementations.
- `backend/prompts/`: prompt templates loaded at runtime.
- `frontend/components/`: chat UI components.
- `frontend/lib/api.ts`: streaming SSE client.
- `frontend/lib/schemas.ts`: client-side runtime schemas.

## Environment Variables

Copy the example file before running the backend:

```bash
cp backend/.env.example backend/.env
```

`backend/.env` is ignored by git. Use placeholder-free real values only in your
local environment.

| Variable | Required | Description |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | Yes for live LLM responses | Provider key used only by the backend. |
| `TAVILY_API_KEY` | Optional | Enables search tool calls. Without it, the graph still runs without search. |
| `BACKEND_PORT` | Optional | Backend port, defaults to `8000`. |
| `NEXT_PUBLIC_API_URL` | Optional | Frontend API base URL, defaults to `http://localhost:8000`. |

## Setup

### Docker

```bash
cp backend/.env.example backend/.env
# Add local API keys to backend/.env
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API docs: http://localhost:8000/docs

### Local Development

Run the backend:

```bash
cd backend
python -m pip install -e ".[dev]"
python -m uvicorn main:app --reload --port 8000
```

Run the frontend:

```bash
cd frontend
npm install
npm run dev
```

## Useful Commands

Backend:

```bash
cd backend
python -m pytest tests -v
```

Frontend:

```bash
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

## API Examples

Cooking query:

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What can I cook with eggs, cheese, and butter?"}'
```

Out-of-scope query:

```bash
curl -N -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who won the game last night?"}'
```

Debug stream:

```bash
curl -N -X POST "http://localhost:8000/api/chat?debug=true" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I make a stovetop pasta dish?"}'
```

## Demo Data Note

The cookware list in `backend/tools/cookware.py` is intentionally hardcoded demo
data. It is included to show how the graph validates generated recipes against a
user constraint without requiring a database.

## Screenshots

The `screenshots/` directory contains sanitized demo captures of local app
states. Review or regenerate them before publishing if the UI changes.

## Security And Privacy

This is a sanitized portfolio version. No client data, private project names,
production secrets, analytics IDs, private URLs, or proprietary assets are
included.

Runtime secrets belong in ignored `.env` files or a deployment secret manager.
The frontend receives only `NEXT_PUBLIC_*` values and never receives provider API
keys.

## License

No open-source license is included. Add one only after confirming that all code
and assets are approved for public licensing.
