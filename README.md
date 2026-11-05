# skills

Claude skills by [@umxr](https://github.com/umxr).

| Skill | What it does |
|---|---|
| [`hig-review`](skills/hig-review/SKILL.md) | Reviews an iOS app's entire UI and interactions against Apple's Human Interface Guidelines, proposes brand-preserving changes for your approval, then implements them with subagents. |
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

`hig-review` only runs when you invoke it (`disable-model-invocation: true`), because a full review and implementation is a long, expensive run.

### Flow

The heavy work runs in agents, so your main conversation stays light. It only coordinates and asks for your approval.

1. **Review.** A review orchestrator agent inventories every screen, fetches the current HIG and takes simulator screenshots. Then it sends five area specialists in parallel (structure, interaction, visual, accessibility, platform), and each one reviews the whole app through its lens. The orchestrator merges their findings into one plan. All working state goes to `.hig-review/`, so a run can resume if interrupted.
2. **Propose.** The main conversation presents the planned changes, any brand decisions it needs from you, and what it's deliberately leaving alone. Then it waits. This step stays in the main conversation because subagents can't ask you questions.
3. **Implement.** After you approve (or amend the plan), an implementation orchestrator creates a `hig-fixes/<date>` branch and implements in waves (tokens → components → screens), with parallel implementers that each own separate files.
4. **Verify.** The implementation orchestrator runs typecheck, lint and tests, and compares before and after simulator screenshots when the app can run. The main conversation relays its short report.

Nested agents need Claude Code's default spawn depth (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` of 2 or more). With nesting turned off, the orchestrators do the specialist and implementer work themselves, one step at a time.

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
```
