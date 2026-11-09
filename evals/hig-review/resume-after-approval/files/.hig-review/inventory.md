# Inventory

**Stack:** Expo SDK 54, React Native 0.81, React Navigation 7 (native-stack + bottom-tabs with custom tabBar), StyleSheet + `src/theme/tokens.ts`. iOS 17.0+, iPhone only, portrait.
App not run: no simulator on this machine. Review is static.

**Brand summary**
- Fern green `colors.primary` is the single accent (primary actions, selection). Cream `colors.background` canvas. All colours from `src/theme/tokens.ts`, with dark variants.
- Recoleta for headlines (`type.display`, `type.title`); system font for body.
- The Leaf Bar (`src/components/BrandTabBar.tsx`) is the signature custom tab bar (docs/brand.md).
- Warm, short, playful voice. Gentle spring on add-to-cart; respects Reduce Motion.

**Navigation map:** Onboarding (gate) → Main tabs (Home, Cart, Profile; Leaf Bar) · Home → Product (push) · Cart → Checkout (modal).

| path | flow | structure | interaction | visual | accessibility | platform |
|---|---|---|---|---|---|---|
| src/screens/OnboardingScreen.tsx | onboarding | reviewed | reviewed | reviewed | reviewed | reviewed |
| src/screens/HomeScreen.tsx | core | reviewed | reviewed | reviewed | reviewed | reviewed |
| src/screens/ProductScreen.tsx | core | reviewed | reviewed | reviewed | reviewed | reviewed |
| src/screens/CartScreen.tsx | purchase | reviewed | reviewed | reviewed | reviewed | reviewed |
| src/screens/CheckoutScreen.tsx | purchase | reviewed | reviewed | reviewed | reviewed | reviewed |
| src/screens/ProfileScreen.tsx | settings | reviewed | reviewed | reviewed | reviewed | reviewed |

**Shared components and tokens:** `src/theme/tokens.ts`, `src/components/PrimaryButton.tsx`, `src/components/IconButton.tsx`, `src/components/BrandTabBar.tsx`.
