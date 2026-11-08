# skills

Claude skills by [@umxr](https://github.com/umxr).

| Skill | What it does |
|---|---|
| [`hig-review`](skills/hig-review/SKILL.md) | Reviews an iOS app's entire UI and interactions against Apple's Human Interface Guidelines, proposes brand-preserving changes for your approval, then implements them with subagents. |
| [`inspect`](skills/inspect/SKILL.md) | Inspects a whole codebase — single project, monorepo or polyglot. Writes a reusable `CONTEXT.md` (layout, how the pieces connect, build/run/test, config, gotchas) and a complete, evidence-backed `CODEBASE_REPORT.md` of what looks wrong. |
| [`security-audit`](https://github.com/cloudflare/security-audit-skill/tree/main/skills/security-audit) | Cloudflare's source-first security audit: recon, coverage-led hunting, independent validation, and structured findings. Pulled from upstream (see [Upstream skills](#upstream-skills)). |

## Install

**Claude Code (all projects):**

```sh
git clone --recurse-submodules https://github.com/umxr/skills ~/src/umxr-skills
mkdir -p ~/.claude/skills
cp -RL ~/src/umxr-skills/skills/hig-review ~/.claude/skills/
```

Replace `hig-review` with any skill name from the table. Use `-L` so `cp` follows the symlinks that upstream skills use.

**Claude Code (one project):** copy `skills/<skill-name>` into the project's `.claude/skills/` directory.

**Claude apps:** zip the `skills/<skill-name>` folder and upload it under Settings → Capabilities → Skills.

## Usage

```
/hig-review                     # whole app
/hig-review onboarding checkout # specific flows
```

```
/inspect                        # whole repo, general inspection
/inspect services/api           # one path
/inspect reconciliation logic   # whole repo, deep-dive on a focus
```

`hig-review` only runs when you invoke it (`disable-model-invocation: true`), because a full review and implementation is a long, expensive run.

### Flow

The heavy work runs in agents, so your main conversation stays light. It only coordinates and asks for your approval.

1. **Review.** A review orchestrator agent inventories every screen, fetches the current HIG and takes simulator screenshots. Then it sends five area specialists in parallel (structure, interaction, visual, accessibility, platform), and each one reviews the whole app through its lens. The orchestrator merges their findings into one plan. All working state goes to `.hig-review/`, so a run can resume if interrupted.
2. **Propose.** The main conversation presents the planned changes, any brand decisions it needs from you, and what it's deliberately leaving alone. Then it waits. This step stays in the main conversation because subagents can't ask you questions.
3. **Implement.** After you approve (or amend the plan), an implementation orchestrator creates a `hig-fixes/<date>` branch and implements in waves (tokens → components → screens), with parallel implementers that each own separate files.
4. **Verify.** The implementation orchestrator runs typecheck, lint and tests, and compares before and after simulator screenshots when the app can run. The main conversation relays its short report.

Nested agents need Claude Code's default spawn depth (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` of 2 or more). With nesting turned off, the orchestrators do the specialist and implementer work themselves, one step at a time.

### How `/inspect` works

1. **Inventory.** A bundled, standard-library-only script (`scripts/inventory.py`) maps the repo in seconds. It finds languages and size, workspaces (pnpm/npm/yarn/bun, Turborepo, Nx, Lerna, Rush, Cargo, Go, uv, Gradle, Maven, Bazel), every package, and the internal dependency graph. It flags cycles, workspace globs that match nothing, crates or modules left out of their workspace, version drift, build/ship risks (missing lockfiles, `tsc` with no tsconfig, Docker `COPY . .` with no `.dockerignore`, CI that skips a language), possible secrets (masked) and git churn.
2. **Inspect.** Claude reads each unit: purpose, entry points, dependencies, env vars, tests. On large repos, parallel subagents do this (`agents/unit-inspector.md`).
3. **Connect.** A cross-cutting pass traces real request paths and checks the contracts between units. It also checks whether the repo actually builds as committed, sometimes by running a build in a throwaway copy. Apart from the files below, the repo is never modified.
4. **Write it down.** Two files at the repo root, neither committed:
   - **`CONTEXT.md`** holds the durable understanding: layout and dependency graph, how requests flow, build/run/test commands and whether they work, env vars, conventions and gotchas, a glossary, a reading order, and a dated "Known issues" snapshot linking to the findings. Larger monorepos also get a `CONTEXT.md` in each substantive package, with the root file as the map. Keep it, commit it, or point your `CLAUDE.md`/`AGENTS.md` at it so future sessions start with the context. Claude offers to add that pointer.
   - **`CODEBASE_REPORT.md`** holds the complete findings, not abridged. It has a TL;DR ending in "Fix first", then one entry per finding with location, evidence (including what was confirmed by running in a throwaway copy) and a fix, plus the focus deep-dive and anything not covered. Secret values are always masked, and a bundled check (`scripts/check_secrets.py`) verifies no file leaks any part of one before Claude replies.

   The chat reply stays short: the TL;DR, what to fix first, and the file paths.

## Upstream skills

Some skills come from other repos. This repo does not keep a copy of them. Each upstream repo is a git submodule in `vendor/`, and `skills/<skill-name>` is a symlink into it.

| Skill | Source |
|---|---|
| `security-audit` | [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) (MIT) |

Dependabot checks the submodules each week and opens a PR when an upstream skill changes. To pull the latest versions by hand:

```sh
git submodule update --init --remote
git add vendor && git commit -m "Update upstream skills"
```

## Layout

```
skills/<skill-name>/
  SKILL.md          # core instructions (loaded when the skill runs)
  references/       # detail loaded only when needed
  agents/           # subagent briefs
  scripts/          # bundled helpers
  evals/            # test cases (claude plugin eval layout)
```
