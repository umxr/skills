# HIG_REVIEW

## Context
Stack: Expo 54 / RN 0.81 / React Navigation 7. Brand summary: see inventory.md. Brand tests: references/principles.md.
Branch: hig-fixes/<date> (not created yet).
Plan status: proposed

## Tasks

### HIG-001 [ ] Sev: Major | Conf: static | Bucket: Fix | Effort: S
Component/Token: IconButton
Screens: Cart
Issue: icon-only button with 30×30pt hit area and no accessible name
Evidence: src/components/IconButton.tsx:20 `btn: { width: 30, height: 30, ...`
Source: https://developer.apple.com/design/human-interface-guidelines/buttons
Change: make the hit area at least 44×44pt (minWidth/minHeight 44, keep the 18pt glyph); add a required `accessibilityLabel` prop and `accessibilityRole="button"`; pass `accessibilityLabel="Remove <item name>"` from CartScreen
Acceptance: hit area ≥44pt; VoiceOver reads "Remove Oat latte, button"
Depends on: —
Owner: — | Status: todo

### HIG-002 [ ] Sev: Major | Conf: static | Bucket: Fix | Effort: S
Component/Token: Product screen navigation
Screens: Product
Issue: swipe-back disabled and custom "← Back" text replaces the standard back button
Evidence: App.tsx:43 `options={{ headerShown: false, gestureEnabled: false }}`; src/screens/ProductScreen.tsx:14 `← Back`
Source: https://developer.apple.com/design/human-interface-guidelines/gestures
Change: remove `gestureEnabled: false` and `headerShown: false` for Product so native-stack provides the standard back chevron and swipe-back; delete the custom back Pressable; header tint `colors.primary`, transparent header over `colors.background`
Acceptance: edge swipe pops Product; standard back chevron visible
Depends on: —
Owner: — | Status: todo

### HIG-003 [ ] Sev: Minor | Conf: static | Bucket: Fix | Effort: S
Component/Token: PrimaryButton usage
Screens: Product
Issue: one-off colour #FF6B00 on "Add to cart" bypasses tokens (brand test 1: drift)
Evidence: src/screens/ProductScreen.tsx:23 `color="#FF6B00"`
Source: https://developer.apple.com/design/human-interface-guidelines/branding
Change: remove the `color` prop so the button uses `colors.primary`
Acceptance: Add to cart uses Fern in light and dark mode
Depends on: HIG-002
Owner: — | Status: todo

## Decisions
None.

## Kept on purpose
- The Leaf Bar (src/components/BrandTabBar.tsx): signature brand element per docs/brand.md; behaves as tabs (role tab, selected state, labels).
- Recoleta headlines (type.display, type.title).

## Uncertain / needs device check
- Swipe-back feel after HIG-002: confirm on device.

## Coverage
See inventory.md (all reviewed).
