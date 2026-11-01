# HIG review checklist

Skip areas that don't apply, and say so in one line.

**1. Navigation & structure**
- Tab bar for top-level peers, not actions.
- Concise nav titles; large titles where they help.
- Standard Back chevron, no custom "Back" text.
- Swipe-back works on every pushed screen and isn't blocked by custom gestures.
- No dead ends; tab state preserved.
- Search placed per HIG *Search fields* (as a tab, in a toolbar, or inline).
- Deep links into the middle of a stack still have a sensible back path.

**2. Modality**
- Sheets for focused tasks, full screen only when justified.
- Grabber on resizable sheets; one consistent Cancel/Done pattern.
- One sheet at a time, no sheet-on-sheet without reason.
- Discarding unsaved changes is confirmed with an action sheet.
- No alert over a sheet that's mid-dismiss.

**3. Layout & adaptivity**
- Safe areas, Dynamic Island, home indicator.
- Consistent margins.
- Layout holds from iPhone SE to Pro Max.
- On iPad, layout follows size classes (not device checks) and supports resizable windows and tab bar → sidebar.
- No clipping at large text sizes.
- Right-to-left mirroring if localised for RTL languages.

**4. Touch & controls**
- Hit targets ≥44×44pt (check `hitSlop`/padding, not the visual size). Under 28×28pt is a Blocker.
- One or two prominent buttons per view (heuristic, not a hard rule); a destructive action is never the primary button.
- Custom controls behave like their native equivalents.
- Text fields: keyboard type, return key, `textContentType` / autofill (passwords, one-time codes, email, address), secure entry.

**5. Typography**
- Every style maps to a Dynamic Type text style, including brand fonts (`UIFontMetrics`, `relativeTo:`, or RN `allowFontScaling`, with `maxFontSizeMultiplier` only where justified).
- Text scales to at least 200%; at the largest accessibility size, as much text shows as at the largest standard size.
- Bold Text is respected.
- No fixed-height text containers.

**6. Colour & materials**
- Brand colours are semantic tokens with light, dark and Increase Contrast variants.
- Contrast meets WCAG AA in both modes: 4.5:1 for text up to 17pt, 3:1 for 18pt+ or bold, 3:1 for essential non-text UI (WCAG 1.4.11).
- Colour is never the only signal.
- Accent colour is used judiciously.
- On iOS 26+: no opaque or brand-filled backgrounds behind system bars (use the scroll edge effect), and no glass in the content layer. Reduce Transparency is respected.

**7. Iconography & imagery**
- Icons are SF Symbols, or brand icons with matching optical weight and alignment. Brand icons aren't a finding just for not being SF Symbols.
- Tab bar icons prefer filled symbols.
- Meaningful images are labelled; decorative ones are hidden from VoiceOver.
- The app icon is a layered icon (Icon Composer) with Default, Dark, Clear and Tinted appearances for iOS 26+.

**8. Interactions** (the core of this review)
- *Feedback:* pressed states on everything tappable; response within ~100ms; progress for anything slower; optimistic UI rolls back on failure; no layout shift when content loads.
- *Scroll:* tab re-tap scrolls to top or pops to root; status-bar tap scrolls to top; large titles collapse correctly; scroll position is kept on back and tab switch; custom headers don't break pull-to-refresh.
- *Gesture conflicts:* carousels or pagers vs swipe-back; sheet drag vs inner scroll; maps vs scroll; long-press vs scroll. Every custom gesture has a visible alternative.
- *Lists:* swipe actions, context menus and long-press where users expect them; share sheet for sharing.
- *Keyboard:* never covers the focused field or the primary CTA; dismisses on drag or tap-outside; return advances between fields; sensible autofocus.
- *Focus:* after a sheet or alert closes, VoiceOver focus returns to the control that opened it; sensible focus after a delete.
- *Safety:* double-submit protection on forms and payments; a disabled state while requests are in flight; undo preferred over confirming every action.
- *Alerts & action sheets:* alerts are rare, with short titles and at most 3 buttons, and the cancel button is titled "Cancel". Action sheets are for choices tied to an action the user started, with destructive options marked and Cancel separate.
- *Haptics:* purposeful and consistent with system semantics (notification success/warning/error, impact, selection); never the only feedback; no haptic spam.
- *Lifecycle:* state survives backgrounding, calls, Control Center and process kill (state restoration); half-filled forms persist; sensitive screens are obscured in the app switcher; audio interruptions are handled.

**9. Motion**
- Purposeful, quick, interruptible; input isn't blocked during transitions.
- Consistent curves and durations; transitions express hierarchy (push vs present).
- Reduce Motion gives a cross-fade or no motion.
- No dropped frames in long lists (image decoding, cell layout).

**10. States**
- Loading, empty (explanation plus next action), error (what happened plus how to recover), offline and permission-denied, **only where that state can actually happen**.

**11. Accessibility**
- VoiceOver: labels, hints, traits/roles, logical order, grouping, custom actions for swipe/long-press, announcements for dynamic changes.
- Voice Control: visible labels match accessible names.
- Full Keyboard Access where relevant.
- Increase Contrast, Bold Text, Reduce Motion, Reduce Transparency.

**12. Launch, onboarding, accounts & privacy**
- Launch screen is nearly identical to the first screen, with no text or logos.
- Onboarding is short and skippable; sign-in is delayed until needed.
- If third-party login is offered, an equivalent privacy-preserving option exists (App Review 4.8; Sign in with Apple satisfies it).
- Passkeys preferred where possible.
- In-app account deletion exists if accounts exist (App Review 5.1.1(v)).
- Permissions are requested in context, with specific purpose strings.

**13. Writing**
- Clear, consistent terminology and capitalisation; verbs on buttons.
- Inclusive language.
- Brand voice is welcome, but errors and destructive confirmations stay plain.

**Stack lookups**
- *React Native/Expo:* `accessibilityLabel/Role/State`, `accessible` grouping, `allowFontScaling` / `maxFontSizeMultiplier`, `PlatformColor` / `useColorScheme`, `react-native-safe-area-context`, native-stack (not JS stack) for native transitions and swipe-back, `KeyboardAvoidingView` / keyboard controller, `expo-haptics`, `Pressable` `hitSlop`.
- *SwiftUI/UIKit:* `Font` text styles / `UIFontMetrics`, asset-catalog colour sets with appearances, `.accessibility*` modifiers, `.sensoryFeedback` / `UIFeedbackGenerator`, `accessibilityReduceMotion`, `presentationDetents`, `NavigationStack`, scene state restoration.
