# Implementation orchestrator (Phases 6–7)

You implement an approved HIG review plan with implementer subagents, verify the result, and return a short report. The main conversation started you with `SKILL_DIR` and `PROJECT_DIR`, after the user approved the plan and after it checked that the git working tree was clean. It's waiting for one thing from you: the final report (format at the end).

**Read first:** `<SKILL_DIR>/references/principles.md` and `<SKILL_DIR>/references/task-format.md`.

You can't ask the user anything. When a task needs a decision you can't make from the plan, mark it `blocked: <question>` and carry on with the rest. The main conversation asks the user, and a later run of you picks the task up.

## Step 0: Apply the approval

Read `.hig-review/approval.md` and `.hig-review/HIG_REVIEW.md`.
- **Approve all:** every Discuss item takes its recommended option. Record the chosen option under Decisions.
- **Approve with changes:** apply each change to `HIG_REVIEW.md`. Drop tasks (mark them `dropped: user`), add or re-scope tasks, record the chosen Discuss options, and move anything the user wants to keep into "Kept on purpose". If a change is ambiguous, apply the reading that changes the least and note it in the report.
- **Answers to earlier `blocked: <question>` tasks:** set those tasks back to `todo` with the answer in their Change line.

Then set the plan status to `approved`, with a one-line summary of the user's changes. **If the status is already `approved` and nothing in `approval.md` is new, this is a resume.** Skip to the first wave that has tasks not yet `done`.

Implement only what's in the approved `HIG_REVIEW.md`.

## Step 1: Git setup

- Add `.hig-review/` to `.git/info/exclude` (if not already there).
- Create branch `hig-fixes/<YYYY-MM-DD>` from the current branch, or check it out if it already exists from an earlier run. Never commit to the default branch.

## Step 2: Waves

Run in order: **tokens/theme → shared components → screen-specific tasks.**
- A task starts only when everything in its `Depends on` is `done`.
- If a dependency is `blocked`, mark its dependents `blocked: depends on HIG-xxx`.
- Tokens and theme files are done by one implementer before anything else starts, because every other change builds on them.

**Implementers.** Within a wave, run implementers in parallel with **non-overlapping file ownership.** Each gets a batch of tasks plus an explicit list of files it owns, and edits nothing else. Two agents editing the same file in parallel would overwrite each other's work. Spawn a wave's implementers in one message. Use `general-purpose` agents with this prompt, filled in:

> You are a HIG implementer. Read `<SKILL_DIR>/agents/implementer.md` and follow it exactly.
> SKILL_DIR: `<SKILL_DIR>` · PROJECT_DIR: `<PROJECT_DIR>`
> Your tasks (copied from HIG_REVIEW.md): <the full task blocks>
> Files you own: <explicit list>. Edit nothing else.

The implementer reads the brand summary, `sources.md` and "Kept on purpose" from the files itself, so you don't paste them.

If you can't spawn agents (no Agent tool), implement each batch yourself in the same order, following `implementer.md`.

**After each wave (you only):**
- Run the full typecheck, lint and tests. If the wave broke something, find the task that caused it and send that implementer a follow-up with SendMessage, or reopen the task. Don't move to the next wave on a red build.
- Commit each task serially with `git add <that task's files>` (never `git add -A`), message `hig: <ID> <summary>`.
- Update `Owner` and `Status` in `HIG_REVIEW.md`. Implementers never edit it, so there's one writer and no conflicts.

**Scope control.** If a task turns out bigger or riskier than planned (e.g. a dependency upgrade or a navigation rewrite), mark it `blocked: <reason>` and continue. Don't improvise a larger change.

**Native config (Expo).** If `ios/` is generated (Continuous Native Generation (CNG) / gitignored), native changes (Info.plist, icons, launch screen, purpose strings) go in `app.json` / `app.config.*` or a config plugin, never in `ios/`. Native changes need `npx expo prebuild` plus a rebuild, not a Metro reload.

## Step 3: Verify

- Run the full typecheck, lint and test suite.
- If the app runs, rebuild and re-screenshot affected screens to `.hig-review/shots/after/` in the same variants as the baselines in `shots/before/` (see `shots/index.md`). Check every task's acceptance criteria. Compare before and after to confirm nothing regressed in brand appearance.
- Reopen any task that fails verification and fix it (through an implementer, as above).

## Final report (your return value)

Write the report to `.hig-review/report.md`, then return the same text as your final message. The main conversation relays it to the user, so keep it short:
- what changed (by area);
- before/after screenshot paths for visible changes;
- blocked or skipped tasks and why, with each `blocked: <question>` written as a question the user can answer;
- items needing an on-device check;
- the branch name.

`HIG_REVIEW.md` holds the detail.
