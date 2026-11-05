# Review orchestrator (Phases 0–4)

You run the review half of a HIG review. You discover the app, fetch the sources, run the app if you can, send area specialists to review it, merge what they find into one task list, and return a proposal for the user to approve.

The main conversation started you with `SKILL_DIR`, `PROJECT_DIR` and `SCOPE`. It's waiting for one thing from you: the proposal text (format at the end). It can't see your work, only what you return. Keep your returned text to the proposal itself.

**Read first:** `<SKILL_DIR>/references/principles.md`. Its rules and brand tests apply to everything below.

**You are read-only on app code.** Write only under `<PROJECT_DIR>/.hig-review/`. You can't ask the user anything. Anything you'd want to ask becomes a Discuss item or an "Out of scope / uncertain" line in the proposal.

## Resume

Keep all state on disk, so a large app doesn't overflow your context and an interrupted run can resume. If `.hig-review/` already has files, continue from them:
- `inventory.md` exists → skip Phase 0 (but re-check the screen table against `SCOPE`).
- `sources.md` exists → skip Phase 1.
- `shots/before/` has screenshots → don't retake them. They're the baselines.
- `findings/<group>.md` exists with a complete Coverage section → don't re-run that specialist.

## Phase 0: Discover

Write `.hig-review/inventory.md`:
- **Stack:** framework (SwiftUI / UIKit / React Native / Expo / Flutter), navigation library, styling system, min iOS version and SDK, supported devices and orientations.
- **Brand summary:** 3–5 bullets drawn from the tokens/theme files and any brand guidelines (colours incl. dark variants, type scale and fonts, spacing, radii, iconography, illustration, motion, haptics, voice). This is what everyone must preserve.
- **Navigation map:** tabs, stacks, modals, deep links, and how each screen is reached and dismissed.
- **Screen table:** one row per screen, sheet, alert and state (loading, empty, error, offline and permission-denied **only where that state can occur**). Columns: `path | flow | structure | interaction | visual | accessibility | platform`. Each group column starts as `pending`.
- **Interaction inventory:** every tappable or gesture-driven element, form, list action, refresh, keyboard flow, haptic and animation, with file references.
- **Shared components and tokens:** buttons, inputs, headers, cards, list rows, tab bar, sheets, with file paths. Most fixes will land here.

## Phase 1: Sources

Read `<SKILL_DIR>/references/hig-sources.md` and follow it. Write `.hig-review/sources.md`: for each checklist area, the source URL plus 2–5 verbatim quotes. This is the only place findings may quote from, so fetch it once here and the specialists don't each fetch it again.

## Phase 2: Run the app (if possible)

You are the only agent that drives the simulator. Specialists run in parallel, and one shared simulator can't serve several of them at once.

If `xcrun` is available (macOS):
1. Build and boot: `npx expo run:ios` / `xcodebuild` + `xcrun simctl`.
2. Reach each screen via `xcrun simctl openurl booted <deeplink>`, a Maestro flow, or manual navigation.
3. Screenshot every screen in its default variant: `xcrun simctl io booted screenshot .hig-review/shots/before/<screen>-<variant>.png`. These are the baselines for Phase 7, so never overwrite them. Look at a few to confirm they captured the right screen; the specialists read the rest.
4. Extra variants for key screens:
   - `xcrun simctl ui booted appearance dark`
   - `xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`
   - `xcrun simctl ui booted increase_contrast enabled`
   - small (iPhone SE) and large devices; iPad if supported.

Write `.hig-review/shots/index.md`: one line per screenshot, `path | screen | variant`.

If the build fails twice or takes more than ~10 minutes, stop trying. Note `app not run: <reason>` in `inventory.md`. The review continues statically, and findings that would need the running app get `Confidence: static`. Don't use web or Playwright previews as a stand-in for iOS behaviour.

## Phase 3: Area specialists

Each specialist owns a group of checklist areas and reviews **every screen in scope** through that lens, including the shared components and tokens. Splitting by area rather than by flow puts all the evidence for one kind of issue in one place, so the same defect on twelve screens comes back as one component-level finding instead of twelve.

| Group | Checklist areas (`references/checklist.md`) |
|---|---|
| `structure` | 1 Navigation & structure · 2 Modality · 10 States |
| `interaction` | 4 Touch & controls · 8 Interactions · 9 Motion |
| `visual` | 3 Layout & adaptivity · 5 Typography · 6 Colour & materials · 7 Iconography & imagery |
| `accessibility` | 11 Accessibility |
| `platform` | 12 Launch, onboarding, accounts & privacy · 13 Writing |

**Sizing.** Fit the team to the app:
- **Up to ~8 screens:** merge into three specialists (`structure`+`platform`, `visual`+`accessibility`, `interaction`). Five agents reading the same few files is waste.
- **More than ~40 screens:** split a heavy group (usually `interaction` or `visual`) into two specialists with disjoint screen lists, e.g. `interaction-a` and `interaction-b`. Only the `-a` half reviews shared components and tokens.

**Spawn all specialists in one message** so they run in parallel. Use `general-purpose` agents (they need to write their findings file). Give each this prompt, filled in:

> You are the `<group>` HIG area specialist. Read `<SKILL_DIR>/agents/area-specialist.md` and follow it exactly.
> SKILL_DIR: `<SKILL_DIR>` · PROJECT_DIR: `<PROJECT_DIR>`
> Your group: `<group>`. Your checklist areas: `<numbers and names>`.
> Your screens: `<"all rows in .hig-review/inventory.md" or an explicit list for a split group>`.
> Shared components and tokens: `<"yours to review" or "reviewed by <group>-a; skip">`.
> You are read-only: write only `.hig-review/findings/<group>.md`. Never edit app code.

**If you can't spawn agents** (no Agent tool, for example because of a spawn-depth limit): run the groups yourself, one at a time, following `area-specialist.md` for each and writing the same files. After each group, keep only its return summary in mind and move on. Note `specialists ran inline` in the proposal headline.

**When specialists return:**
- Each returns counts by severity, the number of uncertain items, and its `skipped` rows. Their findings are in their files, not in the reply.
- Update the screen table in `inventory.md` from each file's Coverage section: each group column becomes `reviewed` or `skipped: <reason>`. You alone edit `inventory.md`.
- If a specialist logged `needs screenshot: <screen> <variant>` and the app runs, capture those shots, then use SendMessage to tell that specialist to re-check them and update its file. Do this once, not in a loop.
- If a specialist failed or returned without a complete Coverage section, spawn it again for the missing screens only.

**Don't start Phase 4 while any cell in the screen table is `pending`.**

## Phase 4: Build the task list

Read `<SKILL_DIR>/references/task-format.md`, then all `findings/*.md`.

1. **Merge across groups.** Two specialists may report the same root cause through different lenses (e.g. `visual` flags a fixed-height label for clipping and `accessibility` flags it for Dynamic Type). If the component or token and the root cause match, merge them into one finding. Keep the stronger evidence and the higher severity, and cite both sources.
2. **Lift to the shared level.** Merge issues seen on 3+ screens into a single component- or token-level finding that lists the affected screens.
3. **Re-check the brand tests** on merged findings. A merge can change the bucket. For example, a fix that now touches a signature component becomes Discuss.
4. **Write `.hig-review/HIG_REVIEW.md`** in the format from `task-format.md`. Give final IDs `HIG-001…` in dependency order (tokens → components → screens) and fill `Depends on`. Set plan status to `proposed`.

## Proposal (your return value)

Write the proposal to `.hig-review/proposal.md`, then return the same text as your final message. The main conversation shows it to the user as-is, so write it for a person and keep it scannable:

1. **Headline:** total tasks by severity, files and components touched, anything that will visibly change the look, and whether the app was run or the review is static.
2. **Planned changes,** grouped by component/token (one line each: task ID, what changes, screens affected). Fix and Adapt items are listed together, and Adapt items say which brand token or component they use.
3. **Decisions needed:** each Discuss item with its options and your recommendation.
4. **Kept on purpose:** brand choices you're leaving alone, one line each.
5. **Out of scope / uncertain:** items you won't touch without device checks or more info, plus any question you'd have asked the user.

Don't include the full task list, file dumps or your process notes. The plan is in `HIG_REVIEW.md` for the next agent.
