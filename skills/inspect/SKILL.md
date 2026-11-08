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
- **Leave the repo exactly as you found it.** The only file you add is the report. Many "harmless" commands write files: `go list`/`go build` create `go.work.sum`, `pytest` leaves `__pycache__`, `cargo` writes `target/` and `Cargo.lock`, package managers write lockfiles and `node_modules`. So inside the repo, stick to reading (`git`, `ls`, `cat`, `grep`, the inventory script). If running something would confirm a claim, do it in a throwaway copy (see step 4).
- **Proportionate and prioritised.** The reader should get the picture in about ten minutes. Scale the report to the repo (a 200-line repo doesn't need 20 KB), keep sections that aren't the focus short, and make the order of urgency obvious — reserve **High** for things that are genuinely urgent, so the top of the list means something.
- **Coverage before depth.** It is easy to spend the whole budget on the first interesting package and never look at the rest. Map everything first (the inventory does this in seconds), then go deep where it matters — the focus, the core path, and anything the inventory flagged.
- **Runtime wiring matters as much as manifests.** Manifests show who imports whom. They don't show that the Go gateway talks to the Rust relay over TCP, or that two apps share a database. Look for those links (URLs/hosts in env vars, docker-compose, shared schemas/protos, queue names, HTTP clients) — that's usually what a newcomer most needs.
- **Never echo secret values — but don't undersell them either.** Name the file, line and kind of secret, and mask the whole value — no prefixes, suffixes or lengths (`postgres://harbor_admin:****@harbor-prod-db…`, `CARRIER_WEBHOOK_SECRET=****`); the host and variable name carry the meaning. Then judge whether it looks real: production-looking hosts (`prod`, cloud DB endpoints), `live` key prefixes and non-placeholder values mean "treat as leaked: rotate it, and remember it stays in git history even after deletion". Say that plainly rather than asking whether it might be real.

## Workflow

### 1. Inventory (deterministic, fast)

Run the bundled script against the root. Write the JSON outside the repo so the working tree stays clean:

```bash
python3 <skill-dir>/scripts/inventory.py <root> --json "${TMPDIR:-/tmp}/inspect-inventory.json"
```

It prints a Markdown summary: shape (single project / monorepo / multi-project / polyglot), languages and size, tooling markers (CI, Docker, linters, version pins), declared workspaces and **workspace problems** (patterns that match nothing, members without manifests, crates or Go modules left out of the workspace), every package with its scripts/entry points/test count, the **internal dependency graph** (as Mermaid) with **cycles** and packages nothing depends on, **version drift** of external deps across packages, conflicting pins between manifests of one project, **build/ship risks** (missing lockfiles under `--frozen-lockfile`, `tsc` without a tsconfig, Go modules without `go.sum`, Docker `COPY . .` with no `.dockerignore`, compose services with no Dockerfile, ecosystems or turbo tasks CI never runs), largest files, TODO/FIXME counts, git history and churn, and **possible secrets** (masked).

Treat the flags as leads, not conclusions: the script uses heuristics. Each flag you report must be confirmed by reading the file it points at (e.g. a "cycle" might be a devDependency only; a declared dependency might never actually be imported; a "secret" might be an obvious placeholder; "not depended on" is normal for apps and CLIs but suspicious for a library).

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
- **Does it actually work as committed?** Newcomers assume the main branch builds and runs; tell them where it doesn't. Check: CI builds/tests every unit and language; lockfiles exist where installs demand them; configs referenced by scripts exist (tsconfig, eslint, migrations); built output can load what it imports (e.g. `main` pointing at `.ts` source of a sibling package); Dockerfiles and compose contexts exist and can see what they copy; entry points really do what they claim (a server that never listens, a CLI that prints and exits, a migration that's empty).
- **Config & secrets:** list env vars the system needs and where they're read; note committed `.env` files and hard-coded fallbacks (masked, with your verdict on whether they look real).
- **Optional: verify in a throwaway copy.** When a claim is load-bearing ("the Rust workspace doesn't build", "a null due date crashes the run") and the toolchain is already installed, you can confirm it by running the relevant build/test offline in a copy: `cp -R <root> "${TMPDIR:-/tmp}/inspect-verify"`, run there, then delete the copy. Skip this if the user asked you not to run things, if it would need to download dependencies, or if it would take more than a couple of minutes. Mark each finding as confirmed (by reading or by running) or "(unconfirmed)".

### 5. Focus deep-dive (only when a focus was given)

Still map the whole repo, but briefly — most of the depth goes to the focus. For a "I need to change X" focus, the reader needs: where X lives and every caller of it (API, CLI, jobs); the data it reads/writes; its current behaviour stated precisely (a small table of cases beats prose); its invariants and the known bugs/edge cases right now; which tests cover it (and what they miss); config that changes its behaviour; and a concrete "before you change it" checklist about X itself. Service-wide problems that merely affect X (no CI, broken migrations, a leaked key) go in Findings, with a one-line pointer from the focus section, not in the checklist.

### 6. Write the report

Write it to `CODEBASE_REPORT.md` at the inspected root unless the user named another path. Don't commit it. Use this structure; drop sections that genuinely don't apply (e.g. "Packages" for a single project) rather than padding them:

```markdown
# <Project name> — codebase inspection
_<date> · <git commit or "not a git repo"> · scope: <root> · focus: <focus or "general">_

## TL;DR
3–6 bullets: what it is, its shape, the most important things to know — ending with **Fix first:** the 1–3 most urgent findings by number.

## What it is
One short paragraph.

## Layout
Shape (single / monorepo with <tool> / polyglot), a table of units: path · name · kind (app/service/lib/tool) · language · purpose · tests? — and for multi-unit repos the dependency graph (Mermaid): solid arrows for imports you saw in code, dashed for runtime links (HTTP/TCP/DB/env var), and declared-but-unused dependencies labelled as such.

## How it fits together
The real request/data flows, step by step, naming files. Call out cross-unit contracts and whether both sides agree.

## Tech stack
Languages, frameworks, data stores, infra, tooling — with versions where pinned.

## Build, run, test
Exact commands (from the repo, not guessed), what each needs (env vars, services), whether it works as committed, and what CI actually runs vs. what it skips. If something doesn't build as committed, add the shortest recipe that works today (e.g. "remove X from members, then …"), marked as a workaround.

## Configuration & external services
Env vars (name · where read · purpose), external systems, secrets handling.

## Packages (multi-unit repos)
A short subsection per unit: purpose, entry points, key files, notable issues.

## Focus: <focus>   (only if a focus was given)

## Findings
| # | Severity | Area | Finding | Evidence | Suggested fix |
Use exactly these severities: **High** = exploitable, leaked credentials, data loss/corruption, or breaks prod/CI/the build; **Medium** = real bug or risk with limited blast radius, or hygiene that will bite soon; **Low** = cleanup. Order by severity; every High cites `file:line`. Mark anything inferred but not confirmed as "(unconfirmed)".

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
