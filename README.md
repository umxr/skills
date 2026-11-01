# skills

Claude skills by [@umxr](https://github.com/umxr).

| Skill | What it does |
|---|---|
| [`hig-review`](skills/hig-review/SKILL.md) | Reviews an iOS app's entire UI and interactions against Apple's Human Interface Guidelines, proposes brand-preserving changes for your approval, then implements them with subagents. |

## Install

**Claude Code (all projects):**

```sh
git clone https://github.com/umxr/skills ~/src/umxr-skills
mkdir -p ~/.claude/skills
cp -R ~/src/umxr-skills/skills/hig-review ~/.claude/skills/
```

**Claude Code (one project):** copy `skills/hig-review` into the project's `.claude/skills/` directory.

**Claude apps:** zip the `skills/hig-review` folder and upload it under Settings → Capabilities → Skills.

## Usage

```
/hig-review                     # whole app
/hig-review onboarding checkout # specific flows
```

`hig-review` only runs when you invoke it (`disable-model-invocation: true`), because a full review and implementation is a long, expensive run.

### Flow

1. **Review.** Inventories every screen, fetches the current HIG, and reviews by flow (with subagents on larger apps). It writes its working state to `.hig-review/`, so it can resume if interrupted.
2. **Propose.** Presents the planned changes, any brand decisions it needs from you, and what it's deliberately leaving alone. Then it waits.
3. **Implement.** After you approve (or amend the plan), it creates a `hig-fixes/<date>` branch and implements in waves (tokens → components → screens), with parallel subagents that each own separate files.
4. **Verify.** Runs typecheck, lint and tests, compares before and after simulator screenshots when the app can run, then reports back.

## Layout

```
skills/<skill-name>/
  SKILL.md          # core instructions (loaded when the skill runs)
  references/       # detail loaded only when needed
```
