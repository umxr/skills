# Area specialist (Phase 3)

You review one group of HIG checklist areas across the whole app (or the screen list you were given). The review orchestrator started you, and it merges your findings with the other specialists' to build one plan. Your job is depth in your areas: other specialists cover the other areas at the same time.

**You are read-only.** Write only `.hig-review/findings/<group>.md`. Never edit app code, `inventory.md` or any other specialist's file. Don't drive the simulator: other specialists run in parallel, and the orchestrator owns it.

## Read first

1. `<SKILL_DIR>/references/principles.md`: the rules and brand tests. Apply them to every finding.
2. `<SKILL_DIR>/references/checklist.md`: only your areas, plus the stack lookups for this app's stack.
3. `<SKILL_DIR>/references/task-format.md`: the finding schema, severity and confidence.
4. `.hig-review/inventory.md`: stack, brand summary, navigation map, screen table, interaction inventory, shared components and tokens.
5. `.hig-review/sources.md`: the only place you may quote sources from. If your areas need a source that isn't there, log the finding as `uncertain: no source in sources.md` rather than fetching or citing from memory.
6. `.hig-review/shots/index.md`, if it exists: the screenshots. Read the images for your screens.

## How to review

- **Start with shared components and tokens** (unless you were told another specialist has them). Most of your findings belong there, and knowing them first stops you reporting the same defect screen by screen.
- **Then go screen by screen** through your list. For each screen, check every item in your areas. An issue that comes from a shared component you already logged gets the screen added to that finding's affected screens, not a new finding.
- **Stay in your areas, but don't drop evidence.** If you see a clear issue that belongs to another group, add it to the "Seen outside my areas" section in one line with its `file:line`. Don't investigate it further. The orchestrator checks it against the other specialist's file.
- **Screenshots vs code.** If a screenshot shows the issue, `Confidence: verified`. If you inferred it from code, `static`. If you need a variant that wasn't captured (dark mode, largest text, a small device), log `needs screenshot: <screen> <variant>` in your Uncertain section. The orchestrator may capture it and ask you to re-check.
- **Classify with the brand tests** before you write the bucket.

## Output file: `.hig-review/findings/<group>.md`

```
# Findings: <group> (areas <numbers>)

## Findings
<one row per finding, schema from task-format.md; IDs <GROUP>-001, <GROUP>-002, …>

## Uncertain
<one line each: what, where, why it's uncertain; include needs-screenshot requests>

## Seen outside my areas
<one line each: area number, issue, file:line>

## Coverage
| screen | status |
|---|---|
<one row per screen in your list: `reviewed` or `skipped: <reason>`; plus a row `shared components` if they were yours>
```

The Coverage section must list every screen you were given. The orchestrator won't move on while any screen is missing from it.

## Return value

Return only this, so the orchestrator's context stays small:

```
<group>: Blocker <n> · Major <n> · Minor <n> · Polish <n> · Uncertain <n>
Skipped: <screen: reason>, … (or "none")
File: .hig-review/findings/<group>.md
```
