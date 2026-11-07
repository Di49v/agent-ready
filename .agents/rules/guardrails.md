---
trigger: always_on
---

# AgentReady Lab - Workspace Engineering Guidelines

Please follow these workspace conventions for modular architecture, git hygiene, and manual terminal control:

## 1. TERMINAL EXECUTION GUIDELINES
- Do not invoke bash, PowerShell, or terminal execution tools (`run_command`, `execute_command`).
- You CAN and SHOULD create folders and files directly using your native editor file-creation/editing tools.
- Whenever a command needs to be run (installing packages with `uv` or `npm`, running `pytest`, starting `uvicorn`, or running `git`), print the exact command inside a `### Manual Terminal & Git Steps` section at the end of your response and wait for the user to paste the terminal output back.

## 2. PRIVACY & SECRET ISOLATION + KEY SHARDING
- NEVER attempt to read, open, grep, or create `.env` or any real credential file.
- Whenever you introduce a new configuration variable, add a placeholder entry to `.env.example` and ask the user to add the real value to their local `.env`.
- All LLM calls must route through `backend/app/core/key_shard.py` (`get_sharded_gemini_key()`) using the `GEMINI_API_KEYS` comma-separated pool and `GEMINI_MODEL` (default `gemini-3.8-flash`).

## 3. BLAST-RADIUS CONTROL (NO RUSHING, NO MULTI-LINE DELETIONS)
- Implement ONLY the single task or step explicitly requested by the user in the current turn.
- Modify or create AT MOST 2 to 5 files per turn (unless explicitly asked to scaffold empty boilerplate files).
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

## 7. LIVING DOCUMENTATION & DIAGRAMS
- Maintain architectural clarity by updating or creating `docs/ARCHITECTURE.md`, `README.md`, and `docs/SETUP.md` alongside major feature completions.
- Use Mermaid.js (`mermaid` code blocks) within markdown files to visually map out state machines, data flows, and multi-agent orchestrations.
- Ensure any new environment variables or setup steps are instantly reflected in `docs/SETUP.md`.

## 8. PRESCRIPTIVE FRONTEND DESIGN SYSTEM ("SWISS PRECISION TELEMETRY")

Follow these exact visual, typographic, and layout rules across all frontend components:

### A. Exposed Hairline Grid & Tonal Surfaces (Zero Floating Card Clutter)
- **Exposed 1px Structural Grid:** Group related panels inside a flush container using `grid gap-px bg-white/[0.07] border border-white/[0.07] rounded-lg overflow-hidden`. Each child cell uses a solid dark background (`bg-[#0D0F14]`), creating crisp 1px architectural hairlines between panels instead of floating cards with messy margins.
- **3-Tier Surface Depth (No Heavy Drop Shadows):**
  - **Canvas Background:** `#08090C` (Obsidian Carbon)
  - **Primary Panel Surface:** `#0D0F14` (Graphite Slate)
  - **Interactive / Elevated Surface:** `#13161F` with a 1px top-edge specular highlight (`shadow-[inset_0_1px_0_0_rgba(255,255,255,0.06)]`)
- **Subtle Dot-Matrix Backdrop:** Apply a faint radial dot pattern on the main canvas (`bg-[radial-gradient(#ffffff0a_1px,transparent_1px)] [background-size:16px_16px]`) so the workbench feels like an engineering instrument.

### B. Strict Typographic Hierarchy & Tabular Monospace Data
- **Display & Section Headings:** `Geist` or `Inter`, `font-medium` (never heavy cartoon bold), tight tracking `tracking-[-0.02em]`, color `#F3F4F6`.
- **Instrument Micro-Labels:** All panel headers, column labels, and metadata tags MUST use `font-mono text-[11px] uppercase tracking-[0.08em] text-zinc-400`.
- **Financials, IDs, Latencies & Scores:** MUST use `font-mono tabular-nums` (`JetBrains Mono`) so numbers never jitter horizontally during live SSE updates.

### C. Semantic Signal Discipline (Dark Surfaces + Crisp Micro-Indicators)
- Never paint entire card backgrounds bright red or green. Keep panel surfaces dark (`#0D0F14`) and indicate state using:
  - **Status Dot:** `h-1.5 w-1.5 rounded-full` (`bg-emerald-400` for Pass/Guarded, `bg-rose-500` for Violation, `bg-amber-400` for Fault Injected, `bg-cyan-400` for Active Stream).
  - **Pill Badge:** `px-2 py-0.5 text-[11px] font-mono rounded border` (`bg-rose-500/10 text-rose-400 border-rose-500/20` for Failures; `bg-emerald-500/10 text-emerald-400 border-emerald-500/20` for Guarded; `bg-amber-500/10 text-amber-300 border-amber-500/20` for Chaos Faults).

### D. Tangible E-Commerce Context Next to Wire Telemetry
- Never show raw API endpoints (`/v2/checkout/orders`) in isolation. Always pair protocol telemetry with a visual **Channel3 Product & Cart Receipt Card** showing:
  1. Product thumbnail/icon, title, and selected variant pill (e.g., `Brooks Ghost 16 · Size 8 · $120.00`).
  2. **Approved Human Intent vs. Wire Payload Diff:** Visually show transformations side by side (e.g., Approved `$150.00` $\rightarrow$ Tampered Wire Payload `$1.50` in crimson strikethrough, or `1x Approved Cart` $\rightarrow$ `2x Duplicate Capture ($240.00)`).

### E. Choreographed Micro-Motion
- Use fast, physical easing (`transition-all duration-150 ease-[cubic-bezier(0.22,1,0.36,1)]`). Avoid bouncy spring animations.
- Use a `2px` horizontal progress bar at the top of active persona cells and AG Grid `enableCellChangeFlash={true}` when ledger rows update.