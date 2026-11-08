# CODEBASE_REPORT.md format

The report is the complete record of the inspection: every finding with its evidence, the focus deep-dive, what was verified and how, and what wasn't covered. It is meant to be read in full when someone acts on it, and skimmed from the top otherwise — so put the conclusion first and keep the body complete. Don't trim findings to save space; trim repetition.

The report doesn't re-describe the codebase. Layout, flows, commands and configuration live in `CONTEXT.md`; the report links there (`see [CONTEXT.md § How it fits together](./CONTEXT.md#how-it-fits-together)`) and adds only what's needed to understand a finding.

```markdown
# <Project name> — codebase inspection
_<date> · <commit or "not a git repo"> · scope: <root> · focus: <focus or "general"> · context: [CONTEXT.md](./CONTEXT.md)_

## TL;DR
3–6 bullets: what it is and the state it's in — ending with **Fix first:** the 1–3 most urgent findings by number.

## Findings
A summary table first, then one subsection per finding.

| # | Severity | Area | Finding | Status |
|---|---|---|---|---|
| 1 | High | Security | Production DB credentials committed in `apps/api/.env` | confirmed (read) |

### 1. <Finding title> — High
- **Where:** `file:line` (every location)
- **What:** what the code does, precisely.
- **Why it matters:** the concrete consequence (who can do what, what breaks, when).
- **Evidence:** the lines that show it; for "confirmed by running", the command and its result.
- **Fix:** the smallest change that addresses it, and anything that must change with it.

<Anchor each subsection so CONTEXT.md can link to it: put `<a id="1"></a>` on the line before the heading.>

## Focus: <focus>   (only if a focus was given)
Where it lives and every caller; the data it reads and writes; its current behaviour stated precisely (a table of cases beats prose); invariants and known bugs/edge cases (link to findings by number rather than re-explaining); test coverage and gaps; config that changes its behaviour; and a "before you change it" checklist about the focus itself.

## Verification
What was confirmed by running, in a throwaway copy, and how: command → result. What was only read.

## Not covered / open questions
What wasn't inspected or couldn't be verified, and why. Questions for the team.
```

## Severity

Use exactly these: **High** = exploitable, leaked credentials, data loss or corruption, or it breaks prod, CI or the build; **Medium** = a real bug or risk with limited blast radius, or hygiene that will bite soon; **Low** = cleanup. Order by severity. Reserve High for what's genuinely urgent so the top of the list means something. Every finding cites `file:line`. Mark anything inferred but not confirmed as "(unconfirmed)".

## Style

- Say each thing once: a problem is explained in exactly one subsection; everywhere else refers to it by number.
- Low findings can share one subsection as a list of one-liners (each still with `file:line`).
- Link files as relative paths (`apps/api/src/server.ts:12`).
