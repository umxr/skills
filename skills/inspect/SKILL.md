---
name: inspect
description: Inspect an entire codebase end to end — single projects, monorepos (pnpm/npm/yarn/bun workspaces, Turborepo, Nx, Lerna, Rush, Cargo, Go and uv workspaces, Gradle, Maven, Bazel) and polyglot repos — and write an evidence-backed report of what it is, how the pieces fit together, how to build/run/test it, and what looks wrong (security, broken workspace config, dependency drift and cycles, untested or dead code, CI gaps). Use this whenever someone wants to understand, audit, map, onboard onto, or get "the lay of the land" of a whole repository or a large part of one, even if they don't say "inspect" — e.g. "how is this repo put together", "I just joined, walk me through this codebase", "what's in this monorepo and how do the packages connect", "review the whole project for problems", or before a big change to a system they don't know yet.
argument-hint: "[path] [focus, e.g. 'reconciliation logic' or 'security'] — empty = whole repo, general inspection"
---

# Inspect a codebase

Produce an accurate, evidence-backed picture of a whole codebase: what it is, how it is laid out, how the parts connect at build time **and at runtime**, how to build/run/test it, and what is wrong or risky. The deliverable is a report file plus a short chat summary.

**Arguments:** `$ARGUMENTS`. A leading path is the root to inspect (default: the current working directory, or the git toplevel if you are inside one and the user said "the repo"). Anything else is a **focus**: a subsystem, a concern (security, performance, testability) or a goal ("I need to change X next sprint"). No focus means a general inspection.

## Principles (why the steps look the way they do)

- **Evidence over impressions.** Every factual claim about the code should be traceable to a file (and line, for findings). Readers will act on this report; a confident wrong statement costs them more than an honest "not verified". Separate what you confirmed by reading from what you infer.
- **Read-only by default.** Don't install dependencies, run builds, start services, or touch the network unless the user asked. Cheap, side-effect-free commands (`git log`, `ls`, `cat`, the inventory script) are fine. You are describing the repo, not changing it — the only file you write inside it is the report.
- **Coverage before depth.** It is easy to spend the whole budget on the first interesting package and never look at the rest. Map everything first (the inventory does this in seconds), then go deep where it matters — the focus, the core path, and anything the inventory flagged.
- **Runtime wiring matters as much as manifests.** Manifests show who imports whom. They don't show that the Go gateway talks to the Rust relay over TCP, or that two apps share a database. Look for those links (URLs/hosts in env vars, docker-compose, shared schemas/protos, queue names, HTTP clients) — that's usually what a newcomer most needs.
- **Never echo secret values.** If you find credentials, name the file, line and kind of secret, and mask the value.

## Workflow

### 1. Inventory (deterministic, fast)

Run the bundled script against the root. Write the JSON outside the repo so the working tree stays clean:

```bash
python3 <skill-dir>/scripts/inventory.py <root> --json "${TMPDIR:-/tmp}/inspect-inventory.json"
```

It prints a Markdown summary: shape (single project / monorepo / multi-project / polyglot), languages and size, tooling markers (CI, Docker, linters, version pins), declared workspaces and **workspace problems** (patterns that match nothing, members without manifests, crates or Go modules left out of the workspace), every package with its scripts/entry points/test count, the **internal dependency graph** (as Mermaid) with **cycles** and packages nothing depends on, **version drift** of external deps across packages, conflicting pins between manifests of one project, largest files, TODO/FIXME counts, git history and churn, and **possible secrets** (masked).

Treat the flags as leads, not conclusions: the script uses heuristics. Each flag you report must be confirmed by reading the file it points at (e.g. a "cycle" might be a devDependency only; a "secret" might be an obvious placeholder; "not depended on" is normal for apps and CLIs but suspicious for a library).

If the script fails (unusual Python, odd layout), carry on manually with `git ls-files`, manifests and `find` — don't stop.

### 2. Orient

Read, in this order and only as much as needed: root README and any `CLAUDE.md`/`AGENTS.md`/`CONTRIBUTING.md`/`ARCHITECTURE.md`/`docs/` index; root manifests and workspace config (`package.json`, `pnpm-workspace.yaml`, `turbo.json`, `nx.json`, `Cargo.toml`, `go.work`, `pyproject.toml`, `settings.gradle`…); CI workflows; `docker-compose`/Dockerfiles/deploy config. From these, write down the **units** you will inspect:

- **Monorepo / multi-project:** one unit per package/project (group tiny ones — e.g. three 20-line config packages — into one unit).
- **Single project:** one unit per top-level source area (e.g. `api/`, `services/`, `db/`, `integrations/`, `cli`), plus tests and infra.

### 3. Inspect each unit

For every unit, find out:

1. **Purpose** — one or two sentences, in the repo's own terms.
2. **Entry points** — servers, CLIs, `main`s, exported library surface, scheduled jobs, handlers/routes.
3. **Internal structure** — the few modules that matter and how control/data flows through them.
4. **Dependencies** — internal (other units: imports and runtime calls) and external (frameworks, DBs, queues, third-party APIs; env vars it reads).
5. **Build / run / test** — the actual commands from its manifest/Makefile, and whether tests exist and look meaningful (skipped or trivial tests count as "no real coverage").
6. **Problems** — with `file:line` evidence: security (unauthenticated mutations, injection, unverified webhooks/tokens, committed secrets), correctness (race/tie/double-processing bugs, protocol mismatches between units, missing timeouts), hygiene (drift, cycles, dead packages, broken workspace config, conflicting pins), test/CI gaps.

**Small repos** (roughly < 150 code files): do this yourself, unit by unit.

**Larger repos or many packages:** delegate units to parallel subagents so your own context stays free for synthesis. Give each one the brief in `agents/unit-inspector.md` plus: the root, its unit path(s), the inventory rows for those units, the focus (if any), and the list of sibling units (so it can name cross-unit links). Send them all in one message so they run concurrently; group small units so you launch at most ~8. Use a read-only agent type if one is available (e.g. `Explore`), otherwise a general-purpose one told not to modify files. If subagents aren't available, work through units yourself, smallest-first, writing notes as you go.

### 4. Cross-cutting pass

Now look across units — this is where most of the report's value is:

- **How it fits together:** trace one or two real request/data paths end to end (e.g. browser → web app → API client → API → DB; CLI → core lib → network). Note runtime links manifests don't show. When two units talk, check that both sides agree (framing, schema, auth expectations, ports/env var names).
- **Confirm or dismiss every inventory flag** by reading the evidence.
- **Build & CI reality:** does CI build/test every unit and every language? Do declared scripts exist where the task runner expects them (e.g. a `turbo run typecheck` with packages that lack a `typecheck` script)? Do Dockerfiles and the manifests they install from agree?
- **Config & secrets:** list env vars the system needs and where they're read; note committed `.env` files and hard-coded fallbacks (masked).

### 5. Focus deep-dive (only when a focus was given)

Still map the whole repo (briefly), but spend most of the depth on the focus. For a "I need to change X" focus, the reader needs: where X lives and every caller of it (API, CLI, jobs); the data it reads/writes; its invariants and the known bugs/edge cases in it right now; which tests cover it (and what they miss); config that changes its behaviour; and a concrete "before you change it" checklist.

### 6. Write the report

Write it to `CODEBASE_REPORT.md` at the inspected root unless the user named another path. Don't commit it. Use this structure; drop sections that genuinely don't apply (e.g. "Packages" for a single project) rather than padding them:

```markdown
# <Project name> — codebase inspection
_<date> · <git commit or "not a git repo"> · scope: <root> · focus: <focus or "general">_

## TL;DR
3–6 bullets: what it is, its shape, the most important things to know, the top risks.

## What it is
One short paragraph.

## Layout
Shape (single / monorepo with <tool> / polyglot), a table of units: path · name · kind (app/service/lib/tool) · language · purpose · tests? — and for multi-unit repos the dependency graph (Mermaid), with runtime links drawn differently from import links (e.g. dashed).

## How it fits together
The real request/data flows, step by step, naming files. Call out cross-unit contracts and whether both sides agree.

## Tech stack
Languages, frameworks, data stores, infra, tooling — with versions where pinned.

## Build, run, test
Exact commands (from the repo, not guessed), what each needs (env vars, services), and what CI actually runs vs. what it skips.

## Configuration & external services
Env vars (name · where read · purpose), external systems, secrets handling.

## Packages (multi-unit repos)
A short subsection per unit: purpose, entry points, key files, notable issues.

## Focus: <focus>   (only if a focus was given)

## Findings
| # | Severity | Area | Finding | Evidence | Suggested fix |
Severity: **High** = exploitable, data loss/corruption, or breaks prod/CI; **Medium** = real bug or risk with limited blast radius, or hygiene that will bite soon; **Low** = cleanup. Order by severity. Mark anything inferred but not confirmed as "(unconfirmed)".

## Where to start
A reading order for a newcomer (5–10 files), and who/what to ask about unclear areas.

## Not covered / open questions
What you didn't inspect or couldn't verify (and why), and questions for the team.
```

Keep it skimmable: tables and short bullets over long prose; link files as relative paths (`apps/api/src/server.ts:12`).

### 7. Reply

In chat, give the TL;DR (the same bullets), the top findings, and the report path. Don't paste the whole report.

## Scale notes

- **Very large repos** (inventory says TRUNCATED, or > ~5k code files): inventory with a higher `--max-files` if feasible; otherwise inspect top-level areas and say in "Not covered" what was sampled rather than read.
- **Generated/vendored code** (lockfiles, `dist/`, `vendor/`, codegen output, migrations): describe it, don't review it line by line.
- **Git submodules / symlinked upstream code:** note them as external; don't review them as first-party unless asked.
- **Inspecting a subdirectory** of a bigger repo: the script scopes git history to that directory; mention the parent repo in the header.
