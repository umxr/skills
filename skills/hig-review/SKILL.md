---
name: hig-review
description: Review an iOS app's entire UI and interactions against Apple's Human Interface Guidelines, propose brand-preserving changes for approval, then implement them. A review orchestrator agent runs specialist subagents (one per HIG area), and an implementation orchestrator runs the fixes, so the main conversation stays light. Use when asked to audit or fix an app for HIG compliance, native iOS feel or iOS accessibility.
argument-hint: "[scope, e.g. 'onboarding checkout' — empty = whole app]"
disable-model-invocation: true
---

# HIG review (brand-preserving, orchestrated)

Bring this app's **UI and every interaction** in line with Apple's Human Interface Guidelines (HIG), so it feels native, accessible and predictable **without diluting its brand**. The deliverable is **the implemented changes**, not a report.

**Scope:** `$ARGUMENTS` (trimmed). Empty = the whole app.

## Who does what

A full review reads hundreds of files, fetches many HIG pages and takes many screenshots. If all of that ran in the main conversation, its context would fill up long before the work was done. So the work runs in agents, and the main conversation only coordinates:

```
Main conversation (you)        status checks, approval gate, final hand-back
├─ Review orchestrator         Phases 0–4 → writes the plan, returns the proposal
│   └─ Area specialists ×5     one per HIG area group, read-only, report to the orchestrator
└─ Implementation orchestrator Phases 6–7 → implements, verifies, returns the report
    └─ Implementers            one per batch of tasks, each owns separate files
```

Subagents can't ask the user anything (Claude Code removes `AskUserQuestion` from them). That is why the approval gate sits in the main conversation, between the two orchestrators, and why there are two orchestrators rather than one.

**Your job in the main conversation** is small on purpose:
- start the orchestrators and wait for them;
- present the proposal and collect approval;
- check git before implementation starts;
- relay the final report.

Don't read app code, fetch HIG pages, take screenshots or edit app files yourself. The orchestrators do that, and they keep their working state on disk in `.hig-review/`. If you do their work, you lose the benefit of the split.

**Until the user approves the plan,** nothing writes outside `.hig-review/`, and no agent modifies app code (see `references/principles.md`, rule 7).

## Paths you pass to agents

- `SKILL_DIR`: this skill's base directory (shown when the skill loaded). Agents read their briefs from it, so always pass the absolute path.
- `PROJECT_DIR`: the app's repo root (the current working directory).
- `SCOPE`: the trimmed `$ARGUMENTS`, or `whole app`.

## Step 1: Check state and resume

Look at `.hig-review/` with `ls` only. Don't read the large files.

| What exists | Go to |
|---|---|
| nothing, or no `proposal.md` | Step 2 (the review orchestrator resumes a partial review by itself) |
| `proposal.md`, no `approval.md` | Step 3 (read `proposal.md` and present it again) |
| `approval.md`, no `report.md` | Step 4 (the implementation orchestrator resumes from tasks not yet `done`) |
| `report.md` | Step 5 (read it and present it; ask whether to start a fresh review) |

## Step 2: Run the review orchestrator

Spawn one `general-purpose` agent with this prompt (fill in the paths):

> You are the HIG review orchestrator. Read `<SKILL_DIR>/agents/review-orchestrator.md` and follow it exactly.
> SKILL_DIR: `<SKILL_DIR>` · PROJECT_DIR: `<PROJECT_DIR>` · SCOPE: `<SCOPE>`
> You can't ask the user anything. When you need a decision, record it as a Discuss item or an open question in the proposal.
> Return only the proposal text described in the brief.

Tell the user in one line that the review is running and what will come back. Then wait for the result. Don't start review work of your own while it runs.

When the result arrives, check that `.hig-review/proposal.md` and `.hig-review/HIG_REVIEW.md` exist. If the orchestrator failed or stopped early, tell the user what it reported and offer to run it again. It resumes from its files.

## Step 3: Propose (approval gate)

Present the proposal to the user as the orchestrator returned it (or from `proposal.md` on resume). It's already written for a person: headline, planned changes, decisions needed, kept on purpose, out of scope / uncertain. Don't paste `HIG_REVIEW.md`.

Then ask (use AskUserQuestion if available): **approve all**, or say what to change.

- **Approve all:** Discuss items take the recommended option.
- **Changes requested** (drop, add, re-scope, pick a different Discuss option, keep something as brand): confirm the delta back in one or two lines. Ask again only if the changes are ambiguous or conflict with each other.
- **A question, a "no" or a "wait":** answer it and stay in Step 3. The gate stays closed.

When the user has approved or requested changes, write `.hig-review/approval.md`:

```
Decision: approve all | approve with changes
Date: <YYYY-MM-DD>
User's words: <verbatim reply>
Changes:
- <one line per change, e.g. "drop HIG-014", "HIG-021 → option B", "keep custom tab bar as brand">
```

Don't edit `HIG_REVIEW.md` yourself. The implementation orchestrator applies `approval.md` to it first, so the plan and the approval can't drift apart.

## Step 4: Run the implementation orchestrator

**Git preflight first** (you own this because it can need the user): run `git status --porcelain`, ignoring `.hig-review/`. If there are uncommitted changes, stop and ask the user how to proceed. Don't stash or commit them yourself.

Then spawn one `general-purpose` agent:

> You are the HIG implementation orchestrator. Read `<SKILL_DIR>/agents/implementation-orchestrator.md` and follow it exactly.
> SKILL_DIR: `<SKILL_DIR>` · PROJECT_DIR: `<PROJECT_DIR>`
> The git working tree was clean when you started. You can't ask the user anything: when a task needs a decision, mark it `blocked: <question>` and continue.
> Return only the final report described in the brief.

Tell the user in one line that implementation is running. Then wait.

## Step 5: Hand back

Relay the orchestrator's final report (also in `.hig-review/report.md`):
- what changed (by area);
- before/after screenshot paths for visible changes;
- blocked or skipped tasks and why, including any `blocked: <question>` items that need the user's answer;
- items needing an on-device check;
- the branch name.

Keep it short. `HIG_REVIEW.md` holds the detail. If tasks are blocked on questions, ask them now. Once the user answers, update `approval.md` and run Step 4 again; the orchestrator picks up only the open tasks.

## Files in this skill

- `agents/review-orchestrator.md`: Phases 0–4. Discovery, sources, simulator runs, specialists, dedup, plan, proposal.
- `agents/area-specialist.md`: the brief for each read-only area specialist.
- `agents/implementation-orchestrator.md`: Phases 6–7. Branch, waves, commits, verification, report.
- `agents/implementer.md`: the brief for each implementer subagent.
- `references/principles.md`: rules, the brand principle and the brand tests. Every agent reads it.
- `references/checklist.md`: the 13-area review checklist plus stack-specific lookups.
- `references/hig-sources.md`: how to fetch the HIG and which sources to cite.
- `references/task-format.md`: finding schema, severity, confidence and the `HIG_REVIEW.md` task format.
