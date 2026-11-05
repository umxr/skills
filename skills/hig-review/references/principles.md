# Principles: rules, brand principle, brand tests

Every agent in this review reads this file: the orchestrators, the area specialists and the implementers. The rules hold no matter which phase you're in.

## Rules (follow these above everything else)

1. **Coverage is exhaustive, reporting is deduplicated.** Review every screen, sheet and state in scope. An issue that appears on many screens is reported **once**, at the component or token level that causes it.
2. **Evidence or it isn't a finding.** Each finding needs a `file:line` from a Read or Grep you ran **yourself in this run**, a quote of the offending code (≤2 lines) or a screenshot path, and a source quote from `.hig-review/sources.md`. If you can't produce both, log it as `uncertain`.
3. **Cite the real source.** HIG rules cite the HIG page. Contrast ratios cite WCAG. Login and account-deletion rules cite the App Store Review Guidelines. Never cite rules from memory. They are fetched once, into `sources.md`, in Phase 1.
4. **Brand isn't a problem to fix.** Don't recommend making the app look like stock iOS. Apply the brand tests below to every finding before classifying it.
5. **Static review is labelled.** Anything about feel, timing, gesture conflicts or performance that wasn't observed in a running app gets `Confidence: static`. Don't present it as fact.
6. **Don't skip silently.** If you can't review something, log `skipped: <reason>`.
7. **Approval gate.** No app code changes before the user has approved or amended the proposal. Only the main conversation can talk to the user, so only it collects approval. After approval, implement only what's in the approved `HIG_REVIEW.md`.

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
