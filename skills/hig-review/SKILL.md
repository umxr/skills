---
name: hig-review
description: Review an iOS app's entire UI and interactions against Apple's Human Interface Guidelines, propose brand-preserving changes for approval, then implement them with subagents. Use when asked to audit or fix an app for HIG compliance, native iOS feel or iOS accessibility.
argument-hint: "[scope, e.g. 'onboarding checkout' — empty = whole app]"
disable-model-invocation: true
---

# HIG review (brand-preserving)

Bring this app's **UI and every interaction** in line with Apple's Human Interface Guidelines (HIG), so it feels native, accessible and predictable **without diluting its brand**. The deliverable is **the implemented changes**, not a report.

**Scope:** `$ARGUMENTS` (trimmed). Empty = the whole app.

**Process:**
1. **Review.** Produce `.hig-review/HIG_REVIEW.md`, an internal task list for you and your subagents, not a document for me.
2. **Propose.** Present the planned changes to me and **stop until I approve or amend it**.
3. **Implement** the approved plan with subagents.
4. **Verify** the changes and report back.

**Until I approve the plan:** write only under `.hig-review/` and do not modify app code.

---

## Rules (follow these above everything else)

1. **Coverage is exhaustive, reporting is deduplicated.** Review every screen, sheet and state in scope. An issue that appears on many screens is reported **once**, at the component or token level that causes it.
2. **Evidence or it isn't a finding.** Each finding needs a `file:line` from a Read or Grep you ran **this session**, a quote of the offending code (≤2 lines) or a screenshot path, and a source quote from `.hig-review/sources.md`. If you can't produce both, log it as `uncertain`.
3. **Cite the real source.** HIG rules cite the HIG page. Contrast ratios cite WCAG. Login and account-deletion rules cite the App Store Review Guidelines. Never cite rules from memory. Fetch them first (Phase 1).
4. **Brand isn't a problem to fix.** Don't recommend making the app look like stock iOS. Apply the brand tests below to every finding before classifying it.
5. **Static review is labelled.** Anything about feel, timing, gesture conflicts or performance that you didn't observe in a running app gets `Confidence: static`. Don't present it as fact.
6. **Don't skip silently.** If you can't review something, log `skipped: <reason>` in the inventory.
7. **Approval gate.** No app code changes before I've approved or amended the Phase 5 proposal. After that, implement only what's in the approved `HIG_REVIEW.md`.

---

## The brand principle

The HIG wants brand expression: voice, colour, custom fonts, imagery, motion. But it wants that expression to **defer to content and not change platform behaviour**. Per HIG *Branding*:
- accent colour is applied judiciously (primary actions, selection, status), not painted on every control;
- custom fonts suit headlines, while body text stays highly legible and supports Dynamic Type and Bold Text;
- logos aren't repeated throughout the UI, and the launch screen isn't used for branding.

**Appearance can carry the brand. Behaviour follows the platform.**

### Brand tests (apply in order)
1. **Is it really brand?** It must come from the token system or brand guidelines and be used consistently. A one-off value that bypasses the tokens is drift, so classify it as **Fix**.
2. **Does it change behaviour?** If a custom element looks different but behaves like its native equivalent (swipe-back, scroll-to-top, VoiceOver traits, Dynamic Type, hit area), it's **Keep**. If it changes what users can predict or do, it can't be Keep.
3. **Does it pass accessibility?** Brand never excuses contrast, Dynamic Type, VoiceOver or Reduce Motion failures. These are **Fix** or **Adapt**, never Keep.
4. **Is it a signature brand element?** If the compliant fix would alter a named brand asset or signature interaction (custom tab bar, celebration animation, brand-coloured chrome), it's **Discuss**. Give two options and your recommendation.

| Bucket | Meaning | Must include |
|---|---|---|
| **Fix** | HIG or accessibility issue; the fix doesn't touch brand identity | file:line, change |
| **Adapt** | Issue whose fix must be expressed in the brand's style | the brand token or component the fix uses |
| **Keep** | Non-standard but legitimate brand expression | where the brand intent comes from (token or guideline) |
| **Discuss** | Real tension between brand and HIG | 2 options, trade-offs, your recommendation |

Don't raise "adopt system materials or Liquid Glass" as a finding on its own. Flag custom chrome only when it fails to **behave** natively, or when it breaks the HIG's materials guidance in a way users would notice.

---

## Workflow

Keep state on disk so large apps don't overflow context and an interrupted run can resume. If `.hig-review/` already exists, resume from it:
- If the `HIG_REVIEW.md` plan status is `proposed`, re-present Phase 5 and wait.
- If it's `approved`, continue Phase 6 from tasks not yet `done`.

### Phase 0: Discover
Write `.hig-review/inventory.md`:
- **Stack:** framework (SwiftUI / UIKit / React Native / Expo / Flutter), navigation library, styling system, min iOS version and SDK, supported devices and orientations.
- **Brand summary:** 3–5 bullets drawn from the tokens/theme files and any brand guidelines (colours incl. dark variants, type scale and fonts, spacing, radii, iconography, illustration, motion, haptics, voice). This is what you must preserve.
- **Navigation map:** tabs, stacks, modals, deep links, and how each screen is reached and dismissed.
- **Screen table:** one row per screen, sheet, alert and state (loading, empty, error, offline and permission-denied **only where that state can occur**). Columns: `path | flow | status: pending`.
- **Interaction inventory:** every tappable or gesture-driven element, form, list action, refresh, keyboard flow, haptic and animation, with file references.
- **Shared components and tokens:** buttons, inputs, headers, cards, list rows, tab bar, sheets. Most fixes will land here.

### Phase 1: Sources
Read `references/hig-sources.md` and follow it. Write `.hig-review/sources.md`: for each checklist area, the source URL plus 2–5 verbatim quotes you'll cite. This is the only place findings may quote from.

### Phase 2: Run the app (if possible)
If `xcrun` is available (macOS):
1. Build and boot: `npx expo run:ios` / `xcodebuild` + `xcrun simctl`.
2. Reach each screen via `xcrun simctl openurl booted <deeplink>`, a Maestro flow, or manual navigation.
3. Screenshot every screen in its default variant: `xcrun simctl io booted screenshot .hig-review/shots/before/<screen>-<variant>.png`, then Read the image. These are the baselines for Phase 7, so never overwrite them.
4. Extra variants for key screens:
   - `xcrun simctl ui booted appearance dark`
   - `xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`
   - `xcrun simctl ui booted increase_contrast enabled`
   - small (iPhone SE) and large devices; iPad if supported.

If the build fails twice or takes more than ~10 minutes, stop trying, review statically and mark affected findings `Confidence: static`. Don't use web or Playwright previews as a stand-in for iOS behaviour.

### Phase 3: Review by flow
Review against `references/checklist.md`. Record findings using the schema in `references/task-format.md`.
- Group screens into flows of ≤8 screens (e.g. onboarding, auth, core task, purchase, settings).
- For more than ~10 screens, **spawn one subagent per flow** (in parallel where possible). Give each: the brand summary and brand tests, `sources.md`, its screen list, the paths to `references/checklist.md` and `references/task-format.md` (subagents read them directly), and this rule: *"You are read-only: write only `.hig-review/findings/<flow>.md`. Never edit app code."* Each returns a count by severity plus any `skipped: <reason>` rows.
- Review shared components and tokens once, in their own pass (`findings/components.md`).
- The main agent alone updates `inventory.md` (`reviewed` or `skipped: <reason>`). **Don't start Phase 4 while any row is `pending`.**

### Phase 4: Build the task list
Deduplicate. Merge issues seen on 3+ screens into a single component- or token-level finding listing the affected screens. Then turn findings into tasks in `.hig-review/HIG_REVIEW.md` (format in `references/task-format.md`).

### Phase 5: Propose (approval gate)
Present the plan to me in chat. Keep it scannable. Don't paste `HIG_REVIEW.md`.
1. **Headline:** total tasks by severity, files and components touched, and anything that will visibly change the look.
2. **Planned changes,** grouped by component/token (one line each: task ID, what changes, screens affected). Fix and Adapt items are listed together, and Adapt items say which brand token or component they use.
3. **Decisions needed:** each Discuss item with its options and your recommendation.
4. **Kept on purpose:** brand choices you're leaving alone, one line each.
5. **Out of scope / uncertain:** items you won't touch without device checks or more info.

Then ask me (use AskUserQuestion if available): **approve all**, or tell you what to change.
- **If I approve all:** Discuss items take your recommended option. Set plan status to `approved` and proceed to Phase 6.
- **If I request changes** (drop, add, re-scope, pick a different Discuss option, keep something as brand): update `HIG_REVIEW.md` to match. Briefly confirm the delta in one or two lines, set plan status to `approved`, and proceed to Phase 6. Don't re-ask unless my changes are ambiguous or conflict with each other.

Never start Phase 6 until I've approved all or requested changes. If my reply is a question, a "no" or a "wait", answer it and stay in Phase 5.

### Phase 6: Implement
**Setup**
- Run `git status`. If there are uncommitted changes, stop and ask me.
- Add `.hig-review/` to `.git/info/exclude`.
- Create branch `hig-fixes/<YYYY-MM-DD>`. Never commit to the default branch.

**Waves**
- Run in order: **tokens/theme → shared components → screen-specific tasks.**
- A task starts only when everything in its `Depends on` is `done`.
- If a dependency is `blocked`, mark its dependents `blocked: depends on HIG-xxx`.
- Tokens and theme files are done by one agent before anything else starts.

**Subagents**
- Within a wave, parallelise with **non-overlapping file ownership:** each subagent gets a batch of tasks plus an explicit list of files it owns, and edits nothing else.
- Give each subagent:
  - the brand summary and brand tests;
  - `sources.md`;
  - the "Kept on purpose" list;
  - its tasks (copied from `HIG_REVIEW.md`);
  - its owned file list;
  - these rules: fix the root cause at the lowest shared level; no unrelated refactors; don't change brand token values unless an approved task says so.
- Each subagent:
  - implements its tasks;
  - runs lint and related tests **on its own files only** (e.g. `jest --findRelatedTests <files>`);
  - reports typecheck errors outside its files without fixing them;
  - **does not commit and does not edit `HIG_REVIEW.md`;**
  - returns `task ID → done | blocked: <reason> → files changed`.

**Main agent only**
- After each wave, run the full typecheck, lint and tests.
- Commit each task serially with `git add <that task's files>` (never `git add -A`), message `hig: <ID> <summary>`.
- Update `Owner`/`Status` in `HIG_REVIEW.md`.

**Scope control**
- If a task turns out bigger or riskier than planned (e.g. a dependency upgrade or a navigation rewrite), mark it `blocked` and continue. Don't improvise a larger change.

**Native config**
- *Expo:* if `ios/` is generated (Continuous Native Generation (CNG) / gitignored), put native changes (Info.plist, icons, launch screen, purpose strings) in `app.json` / `app.config.*` or a config plugin, never in `ios/`. Native changes need `npx expo prebuild` plus a rebuild, not a Metro reload.

### Phase 7: Verify and hand back
- Run the full typecheck, lint and test suite.
- If the app runs, rebuild and re-screenshot affected screens to `.hig-review/shots/after/` in the same variants as Phase 2. Check every task's acceptance criteria, and confirm nothing regressed in brand appearance (compare before and after screenshots).
- Reopen any task that fails verification and fix it.
- Final message to me:
  - what changed (by area);
  - before/after screenshot paths for visible changes;
  - blocked or skipped tasks and why;
  - items needing an on-device check;
  - the branch name.

  Keep it short. `HIG_REVIEW.md` holds the detail.

---

## Reference files
- `references/checklist.md`: the 13-area review checklist plus stack-specific lookups. Read before Phase 3.
- `references/hig-sources.md`: how to fetch the HIG (JSON endpoints, slugs) and which sources to cite. Read in Phase 1.
- `references/task-format.md`: finding schema, severity, confidence and the `HIG_REVIEW.md` task format. Read before Phase 3.
