# Findings and task format

## Finding schema

`ID | Sev | Conf | Bucket | Component/Token | Affected screens | Issue | Evidence (file:line + quote or screenshot) | Source (URL + quote) | Fix (brand-expressed) | Effort S/M/L`

**Severity** (impact × reach):
- **Blocker:** breaks a core flow, likely App Review rejection, or makes a flow unusable with VoiceOver or at large text sizes.
- **Major:** users in a core flow will notice or get stuck.
- **Minor:** noticeable but has a workaround, or sits off the core path.
- **Polish:** only a designer would notice. **Cap at 10.** Drop anything with no user impact.
- Raise severity one level for core flows (onboarding, primary task, purchase).

**Confidence:**
- `verified`: seen running or in a screenshot.
- `static`: inferred from code.
- `uncertain`: couldn't confirm. Listed separately, not in the main table.

---

## `.hig-review/HIG_REVIEW.md` format (agent-facing task list)

Written for agents to execute from. Terse and structured, no prose for humans.

1. **Context:** stack, brand summary, brand tests reference, branch name, and plan status (`proposed`, then `approved` along with a summary of my changes).
2. **Tasks,** ordered by dependency (tokens → components → screens), each as:
   ```
   ### HIG-012 [ ] Sev: Major | Conf: static | Bucket: Adapt | Effort: S
   Component/Token: PrimaryButton
   Screens: Home, Checkout, Settings (+11)
   Issue: no pressed state; hit area 36pt
   Evidence: src/components/PrimaryButton.tsx:42 `<View style={styles.btn}>`
   Source: https://developer.apple.com/design/human-interface-guidelines/buttons ("…")
   Change: wrap in Pressable with brand `colors.primaryPressed`; minHeight 44
   Acceptance: pressed state visible; ≥44pt hit area; VoiceOver role=button
   Depends on: HIG-003
   Owner: — | Status: todo
   ```
3. **Decisions:** Discuss items, with the options, the recommendation and (after approval) the chosen option.
4. **Kept on purpose:** brand choices left alone, with their brand source. Agents must not touch these.
5. **Uncertain / needs device check:** logged, not actioned.
6. **Flow walkthrough notes:** for each key flow, the script *happy path → slow network → failure → background mid-flow → back out → VoiceOver pass*, referencing task IDs.
7. **Coverage:** the inventory with final review statuses.
