---
trigger: always_on
---

# AgentReady Lab — Strict Workspace Engineering Rules

You are collaborating with a developer who values modular architecture, strict git hygiene, manual terminal control, and zero destructive edits. Follow every rule below without exception:

## 1. NO TERMINAL EXECUTION (HARD LOCK)
- NEVER invoke bash, PowerShell, or terminal execution tools (`run_command`, `execute_command`, etc.).
- You CAN and SHOULD create folders and files directly using your native editor file-creation/editing tools.
- Whenever a command needs to be run (installing packages with `uv` or `npm`, running `pytest`, starting `uvicorn`, or running `git`), print the exact command inside a `### Manual Terminal & Git Steps` section at the end of your response and wait for the user to paste the terminal output back.

## 2. PRIVACY & SECRET ISOLATION + KEY SHARDING
- NEVER attempt to read, open, grep, or create `.env` or any real credential file.
- Whenever you introduce a new configuration variable, add a placeholder entry to `.env.example` and ask the user to add the real value to their local `.env`.
- All LLM calls must route through `backend/app/core/key_shard.py` (`get_sharded_gemini_key()`) using the `GEMINI_API_KEYS` comma-separated pool and `GEMINI_MODEL` (default `gemini-3.8-flash`).

## 3. BLAST-RADIUS CONTROL (NO RUSHING, NO MULTI-LINE DELETIONS)
- Implement ONLY the single task or step explicitly requested by the user in the current turn.
- Modify or create AT MOST 2 to 3 files per turn (unless explicitly asked to scaffold empty boilerplate files).
- NEVER delete existing functions, comments, imports, or logic unless explicitly instructed or required. Never use lazy placeholders like `// ... existing code ...` that overwrite working lines.
- Keep every source file modular.

## 4. SURGICAL EDITS & MODULAR ARCHITECTURE (NO RUSHING)
- Execute ONLY the single task ID requested from `docs/ROADMAP.md` in each turn (touching 1–4 files per turn unless scaffolding empty folders).
- Keep code modular by responsibility (separate routers, schemas, services, and UI components). Do not artificially split cohesive logic just to hit an arbitrary line count, but ALWAYS use `replace_file_content` with exact `StartLine` and `EndLine` ranges when editing existing files—never overwrite a file with `// ... rest of code ...` placeholders or delete working lines.

## 5. TECH STACK & CODING STANDARDS
- Backend (`backend/`): Python 3.11+, FastAPI, `uv` package manager, `uvicorn`, Pydantic v2, `httpx` (async), SQLAlchemy/asyncpg (or Prisma), `pytest`.
- Frontend (`frontend/`): Next.js (App Router), TypeScript, Tailwind CSS, AG Grid (`ag-grid-react` Community/Studio).
- MCP Server (`mcp/`): Thin wrapper over `/v1/*` API plus `@paypal/agent-toolkit` integration.
- Error Responses: Strictly follow RFC 9457 (`application/problem+json`).
- Sandbox Lock: Hard-pin PayPal calls to `https://api-m.sandbox.paypal.com`.

## 6. MANDATORY END-OF-TURN HANDSHAKE
End every response with this exact checklist:
1. **Files Changed:** Bullet list of the 1–3 files created/updated.
2. **Roadmap Sync:** Which checkbox in `docs/ROADMAP.md` was completed.
3. **Run & Test Commands:** Exact `uv run ...` or `npm ...` command for the user to run and what log output to paste back.
4. **Git Commands:** Exact `git checkout -b ...`, `git add ...`, and `git commit -m "..."` command for this atomic change.