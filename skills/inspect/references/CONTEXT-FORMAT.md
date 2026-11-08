# CONTEXT.md format

`CONTEXT.md` is the durable half of an inspection: what someone (or an agent) needs to know to work in this codebase, written so it stays true until the code changes. It is meant to be kept, committed by the team if they like it, and read at the start of future work. The point-in-time judgements (what's wrong, how bad, how to fix) live in `CODEBASE_REPORT.md`; `CONTEXT.md` carries only a short, dated snapshot of them.

## Where the files go

- **Single project, or a small multi-unit repo** (roughly ≤ 5 substantive units): one `CONTEXT.md` at the inspected root.
- **Larger monorepo:** the root `CONTEXT.md` is the **map** — the whole-system picture plus a units table linking to a `CONTEXT.md` inside each substantive unit (`apps/api/CONTEXT.md`, `crates/relay-core/CONTEXT.md`). Group trivial units (config packages, tiny shared types) into the root file instead of giving each its own. Example/template and fixture packages get no file.

## Existing files

- If a `CONTEXT.md` already exists, read it first. Update the sections this format defines; keep everything else the team wrote, and never delete their content. If they contradict what the code shows, keep their text and add a dated note under it saying what the code does now.
- If the repo uses `GLOSSARY.md` / `GLOSSARY-MAP.md` (or `docs/adr/`) for its domain language and decisions, don't duplicate them: link to them from the Glossary section, and use their terms throughout.
- Re-running the inspection refreshes the header line and the Known issues snapshot; it doesn't start the file over.

## Root CONTEXT.md

```markdown
# <Project name>

_Context written by an inspection on <date> at <commit>. Findings and evidence: [CODEBASE_REPORT.md](./CODEBASE_REPORT.md)._

<One or two sentences: what this system is for, in the repo's own terms.>

## Layout
Shape (single project / <tool> monorepo / polyglot). A table of units — path · kind (app/service/lib/tool) · language · purpose (one line) · context file (if it has one). For multi-unit repos, a Mermaid graph: solid arrows for imports seen in code, dashed for runtime links (HTTP/TCP/DB/queue/env var).

## How it fits together
The real request/data flows, step by step, naming files. Cross-unit contracts (wire format, schema, auth, ports/env var names), and whether both sides currently agree.

## Build, run, test
Exact commands from the repo, what each needs (toolchains and pinned versions, services, network access during the build), and whether it works as committed. If something doesn't build today, the shortest workaround, marked as such. What CI runs, and what it skips — and where the documented contributor workflow (CONTRIBUTING, README) differs from what CI actually does.

## Configuration
Env vars: name · where read · purpose. External services. How secrets are supplied (never their values).

## Conventions and gotchas
Things that will surprise someone making a change: generated code and how to regenerate it, settings captured at import time, implicit ordering, packages consumed as source, a protocol that differs from what the name suggests, contribution rules (changesets, commit format, required checks), and any instructions the repo addresses to AI agents. Facts, not complaints.

## Glossary
Domain terms specific to this codebase, one line each (what it IS) — or a link to the existing GLOSSARY.md.

## Where to start
A reading order for a newcomer: 5–10 files, each with why.

## Known issues (snapshot at <commit>)
One line per High and Medium finding, worst first, each linking its number in the report: `- **High** Committed production DB credentials — [#1](./CODEBASE_REPORT.md#1)`. This is what goes stale first; it is here so a future reader or agent knows the landmines without reading the whole report.
```

## Per-unit CONTEXT.md (larger monorepos)

```markdown
# <unit name> (`<path>`)

_Part of <project>; system map in [../CONTEXT.md](../CONTEXT.md). Written <date> at <commit>._

<Purpose, one or two sentences.>

## Entry points
file — what it starts or exports.

## Key modules
file — role (the 3–8 a newcomer must know).

## Depends on / used by
Internal imports and runtime links in both directions, with the mechanism.

## Build, run, test
This unit's own commands and their state.

## Configuration
Env vars this unit reads.

## Gotchas
Unit-specific surprises.

## Known issues (snapshot at <commit>)
One-liners linking to the report.
```

## Style

- Present tense, factual, stable. "The gateway forwards the raw body over TCP to `RELAY_ADDR`" — not "I found that…".
- Every claim names a file. Tables and bullets over paragraphs.
- Mask secrets exactly as in the report.
- State-of-the-world claims ("fails as committed") carry the same confirmed/unconfirmed status as the report's matching finding, and link to it.
