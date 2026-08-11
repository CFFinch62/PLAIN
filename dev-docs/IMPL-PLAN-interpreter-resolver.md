# PLAIN Language — Interpreter Resolver / Slot-Indexed Variables Implementation Plan

**Created:** 2026-08-11
**Status:** 📋 SCOPED, NOT STARTED — a smaller mitigation (see §4) already landed and captured part of the win; this plan covers the remaining, larger piece
**Goal:** Eliminate the name-based `Environment` chain walk as a runtime cost for variable access, the largest remaining interpreter-level performance bottleneck confirmed by CPU profiling

---

## 1. Motivation

`plain_euler/LANGUAGE_LIMITATIONS.md` (in the sibling `PROJECT_EULER` repo) closed out a full solution-code algorithm review with an explicit verdict: PLAIN's average solution time (~1.7s) is not good enough on its own, and real interpreter-level work — not more solution-code tuning — was flagged as a hard requirement for the next phase. This document is that investigation's output: real profiling data, what was already fixed, and a scoped plan for the piece that wasn't.

This is the same class of problem Quick's own resolver (Phase 5 of that project) was built to solve, and the same anti-pattern already diagnosed in FORGE's pre-fix interpreter (a hashmap-keyed environment chain, re-hashed on every variable read). The difference — and the reason this isn't a direct port of Quick's approach — is PLAIN ships a real REPL (`internal/repl/`) and an IDE debugger with a live "variables" panel built directly on enumerating scopes by name at arbitrary breakpoints (`internal/runtime/debugger.go`). Quick has neither. Any resolver design here has to keep that working, which Quick's design never had to consider.

## 2. What profiling actually found

Methodology: a standalone Go program (not committed — built ad hoc against `internal/lexer`/`internal/parser`/`internal/runtime`, `runtime/pprof.StartCPUProfile` around a single `Eval` call) profiled two cases — a synthetic 5,000,000-iteration `loop ... if ...` isolation case, and the real `plain_euler/solution10.plain` (nested loops + conditionals, representative of typical Euler-style code). Both agreed.

**Before any fix**, on `solution10.plain` (real numbers from `go tool pprof -top`):

| Function | Cumulative % of total CPU time |
|---|---|
| `Environment.Get` | 29.89% |
| `evalIdentifier` (calls Get) | 33.26% |
| `runtime.mallocgc` (Go's allocator) | ~36% (across `mallocgc`/`mallocgcTiny`/`mallocgcSmallScanNoHeader`) |
| `aeshashbody` (Go's map hash function) | 9.47% flat |
| `mapaccess2_faststr` / `mapassign_faststr` | 28.00% / ~16% cumulative |

Root cause, confirmed by reading `internal/runtime/environment.go` and `evaluator.go` before any change: `Environment` was `map[string]Value` plus a parent pointer. Two compounding problems:

1. `NewEnclosedEnvironment` allocated a fresh map **eagerly** on every block entry (every `if`, every loop body) — including blocks that never declare a single local variable of their own (an `if` body that only assigns to an *outer* variable never calls `Define`, so the map was allocated, hashed into zero times, and discarded). This is the common case in real code.
2. Every variable **read** (`Get`) walks the parent chain, doing a real Go map lookup (hash + bucket probe) at every level, even though real scopes typically hold only a handful of variables — map overhead is not worth paying at that size.

## 3. Full fix (this plan): compile-time slot resolution

The complete fix, mirroring Quick's Phase 5: add a resolution pass that assigns every variable declaration a fixed `(depth, slot)` index at analysis time, annotate every identifier reference with its resolved index, and replace name-based lookup at runtime with direct array indexing — O(1), no hashing, no string comparison, no per-block allocation for scopes whose size is known ahead of time.

### 3.1 Where it plugs in

`internal/analyzer/` already does a real semantic-analysis pass with its own scope-tracking (`internal/scope/`, parent-chained `Scope` with a `map[string]*Symbol`) — enforcing PLAIN's no-shadowing rule, mutability checks, etc. This is the natural place to *also* assign slot indices, not a new pass built from scratch. Concretely:

- `internal/scope.Symbol` gains a `Slot int` field (and the enclosing `Scope` gains a slot counter, incrementing per `Define`).
- The AST (`internal/ast/`) needs each `*ast.Identifier` (and `VarStatement`/`FxdStatement` declaration sites) annotated with its resolved `(depth, slot)` — likely as new fields on the identifier node, filled in during the analyzer pass, mirroring how Quick's `resolved_kind`/`resolved_index` fields were added directly to AST nodes rather than a side table.
- **PLAIN's no-shadowing rule is a genuine simplification here** relative to a language that allows it: within one function/task, a name always refers to the same single declaration, so there's no Quick-style "which of several shadowed slots" ambiguity to resolve — every reference to a name resolves to exactly one slot for that name's whole lexical scope.

### 3.2 Runtime representation

Replace (or add alongside, see §3.4) the current `Environment` with a fixed-size, pre-sized `[]Value` per call frame, indexed directly by the resolved slot number — the same shape as Quick's per-call `locals` window, adapted for a tree-walking (not bytecode) interpreter: no compiled chunk to size the array from ahead of time, so the analyzer pass needs to compute each function/task body's `max_locals` (highest slot number used across every block within it, not summed — blocks that don't overlap in lifetime can reuse slot numbers as long as no reference confusion results, matching how Quick's own resolver reasoned about this) and the evaluator allocates that array once per call.

### 3.3 The REPL/debugger constraint (the real scope-adder)

This is the piece Quick's own Phase 5 never had to solve:

- **REPL** (`internal/repl/`): each line typed is evaluated incrementally against a *persistent* environment that grows indefinitely across the session — there's no fixed "compile once, then run" boundary the way a batch-executed `.plain` file has. A pure slot-indexed scheme assumes a closed, known-in-advance variable set per scope; the REPL's top-level (module) scope violates that by design. Likely resolution: keep the **module/global scope name-keyed** (exactly like Quick already does — "globals are one flat table" — Quick's own resolver never slot-indexes globals either, only function-locals), and only slot-index **function/task-local and block scopes**, which *are* closed and known once a task body is fully parsed. This should cover the actual hot path (loop bodies, block-local variables) without needing to solve REPL-incremental-globals as part of this work at all.
- **Debugger** (`internal/runtime/debugger.go`): `sendVariables()`, `GetAllVariables()`, and `collectOuterVars()` all currently enumerate a scope's variables by name for the IDE's live "variables" panel at a breakpoint (already adapted once this session, see §4 — they now call `Environment.snapshot()` instead of ranging over the old raw map field directly). A slot-indexed local frame has no names at runtime unless something preserves them. Needed: the analyzer pass must also emit, per function/task, a `[]string` (slot index → name) table alongside the resolved AST, so the debugger can still reconstruct `name -> value` pairs from `(frame []Value, names []string)` for display purposes. This is pure metadata, never touched on the hot path, so it costs nothing at runtime except at an actual breakpoint.

### 3.4 Suggested incremental path (don't attempt as one big-bang change)

1. Add slot assignment to `internal/analyzer/` for task-local scopes only (parameters + `var`/`fxd` declarations inside one task body, including nested blocks), leaving module-level globals exactly as they are today (name-keyed, via the already-landed `Environment` from §4).
2. Add the parallel slot-index → name table per task, for debugger use.
3. Introduce a new runtime frame type (e.g. `LocalFrame`) alongside the existing `Environment`, used only for task-local scope; module/global scope keeps using `Environment` unchanged.
4. Update `evalIdentifier`/`evalAssignStatement`/`evalVarStatement`/`evalFxdStatement` to check the identifier's resolved kind (global vs. local-slot) and dispatch to the right storage — same shape as Quick's `RESOLVED_LOCAL`/`RESOLVED_GLOBAL` split in `compile.c`.
5. Update `internal/runtime/debugger.go`'s three variable-enumeration call sites to read from `(LocalFrame, names []string)` when inspecting a local scope, falling back to the existing `Environment.snapshot()` path for module/global scope.
6. Re-run the same profiling methodology from §2 against the same two test cases (the synthetic isolation case and `solution10.plain`) to confirm the remaining ~16% `Environment.Get`/`Set` cost (see §4) is actually gone, not just moved — this project's own established discipline (see `plain_euler/LANGUAGE_LIMITATIONS.md`'s "speculative before/after numbers... were wrong every single time" lesson) applies here as much as to solution-code fixes.
7. Full regression: `go test ./...`, plus every `plain_euler/*.plain` solution re-verified against its known-correct answer (only 2 of 100 use `attempt`/`handle` at all, per a grep done this session — most of the corpus is exactly the loop/conditional-heavy code this change targets).

### 3.5 Scope estimate

Bigger than §4's mitigation by a wide margin — touches `internal/analyzer/` (new pass logic), `internal/ast/` (new fields), `internal/runtime/evaluator.go` (every statement/expression that reads or writes a variable), and `internal/runtime/debugger.go` (three call sites, metadata-only). Comparable to Quick's Phase 5 + relevant parts of Phase 6/7 combined, done against a much larger (16.8k-line vs. Quick's ~4.9k-line) and already-shipped codebase with a real IDE/debugger surface depending on current behavior — budget accordingly, and don't attempt it as a single uninterrupted session.

## 4. Already done: the cheap mitigation (2026-08-11)

Landed the same session this plan was written, as a **prerequisite low-risk step**, not a replacement for §3. Captured a real, measured chunk of the win with a self-contained change:

- `internal/runtime/environment.go`: replaced `store map[string]Value` with a lazily-grown, linear-scan `names []string` / `values []Value` pair. Nil until first `Define` (no allocation for blocks that never declare a local — the common case), and a plain string-equality scan beats Go's map for the handful of entries a typical scope actually holds. **Public API (`Get`/`Set`/`Define`) is unchanged**, so nothing outside this file needed to change except three call sites in `internal/runtime/debugger.go` and one in `evaluator.go` (module import namespace export) that directly ranged over the old `store` map field for the IDE's live variables panel and module export list — now go through a new `Environment.snapshot()` helper (builds a `map[string]Value` on demand, cold-path only, never on the hot execution path).
- **Measured, not assumed**: ~24% faster on both the synthetic loop+if isolation case (1.589s → 1.215s) and the real `solution10.plain` (4.015s → 3.043s). Re-profiling after confirms the map-hashing/allocation overhead (`aeshashbody`, most of the `mallocgc` family) is gone from the top-20 CPU consumers entirely. `Environment.Get`+`Set` combined dropped from ~30%+4% to ~11.65%+4.07% cumulative — real, but that residual is exactly the parent-chain-walk cost only §3's slot resolution can eliminate.
- Full test suite (`go test ./...`) passes; debugger variable-panel behavior preserved (same name→value shape via `snapshot()`, just not on the hot path anymore).

## 5. Also fixed this session, unrelated to performance

`internal/runtime/evaluator.go`'s `evalAttemptStatement` previously ran `stmt.Handlers[0]` unconditionally on any error, regardless of whether its `Pattern` actually matched — LANGUAGE-REFERENCE.md §10.2's whole "Pattern Matching Handlers" feature (multiple `handle "specific text"` clauses matched in declared order) was silently non-functional. Also fixed: a bare `handle err` (no `as TYPE`) left `err` unbound (see `dev-docs/defects_found_during_tutorial_creation.md` Defect 3 — was only half-fixed; `handle err as string` worked, bare `handle err` didn't). Both fixed together since the bare-identifier case was really a symptom of pattern matching never being implemented. See that file's Defect 3 update for the full writeup; not a performance item, noted here only because it touched the same function this plan also touches (`evalAttemptStatement`), so a future resolver pass should be aware `ErrorName`-bound handler variables are locals scoped to just the handler body, needing the same slot treatment as any other block-local.
