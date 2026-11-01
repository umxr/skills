# HIG sources

- HIG pages render client-side, so HTML fetches return only metadata. Fetch the JSON instead:
  `https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<slug>.json`
  For the human-readable link in `HIG_REVIEW.md` Source lines, use `https://developer.apple.com/design/human-interface-guidelines/<slug>`.
- Known slugs: `branding, accessibility, layout, color, materials, typography, app-icons, gestures, buttons, tab-bars, toolbars, search-fields, sheets, alerts, action-sheets, playing-haptics`. For other topics (dark mode, SF Symbols, launching, onboarding, managing accounts, privacy, sidebars, menus, context menus, text fields, motion, feedback, loading, modality, writing, inclusion, right-to-left), find the slug via `foundations.json`, `components.json` or `patterns.json` under the same base path.
- Note the current design language for the app's SDK: Liquid Glass applies from iOS 26, and apps built with the iOS 27 SDK can't opt out via `UIDesignRequiresCompatibility`.
- App Store Review Guidelines: https://developer.apple.com/app-store/review/guidelines/ (4.8 login services, 5.1.1(v) account deletion). WCAG 2.2 for contrast.
