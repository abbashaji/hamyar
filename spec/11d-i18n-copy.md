# 11. Experiences, part d: Persian first, accessibility, low bandwidth and notices copy

*Spec part 11d (the fourth file of part 11) · written against Founding Document draft v0.1 (FD) · vocabulary from `spec/00-conventions.md` (S0), used exactly. Nothing here is legal advice. Every notice in S11.51 needs human and legal review before any member can see it; none of it has been read by a lawyer, a safety advisor or a native-speaking reviewer.*

## 11.40 Scope, status and how to read this part

This part completes the last bullet of prompt scope F: Persian first (full RTL, numerals, Jalali and Gregorian dates, mixed-direction text, fonts), English, accessibility, low-bandwidth behavior, and the copy of every policy, privacy and risk notice in both languages. Screens, states and flows live in the other files of S11; this file sets the cross-cutting rules that every screen obeys, and it owns the notice texts. [D]

| Prompt item (scope F) | Where decided |
| --- | --- |
| Full RTL | S11.42 |
| Persian numerals option; storage always ASCII digits | S11.43 |
| Jalali and Gregorian dates; UTC storage | S11.44 |
| Mixed-direction text in prompts and outputs; clipboard | S11.45 |
| Fonts | S11.46 |
| English | S11.47 |
| Accessibility | S11.48 |
| Low-bandwidth behavior; offline-tolerant paste-back drafts | S11.49 |
| Copy of all notices: keyed table, review process | S11.50 to S11.53 |
| Acceptance criteria (Given / When / Then) | S11.54 |
| New parameters | S11.55 |
| Assumptions, items to verify, requirements on other parts | S11.56, S11.57 |

**Reading rules** [D]

- Persian first: wherever a table lists both locales, `fa` comes before `en`.
- MUST, MUST NOT, SHOULD and MAY carry their RFC 2119 meaning (S0.2). Evidence tags are those of S0.2; `[A]` assumptions are collected in S11.56.
- Persian text uses the zero-width non-joiner (ZWNJ, U+200C) where Persian orthography needs it, for example after the verb prefix and before the plural suffix. It is invisible; a file where it is missing is wrong, not different.
- Every number is derived by a formula shown next to it or labeled `initial configurable default` and listed in S11.55. Copy contains no hard-coded number that comes from a parameter (S11.50).
- Heading numbers of this file start at 11.40 so that they cannot collide with the other files of S11 [A]; see `ISS-117`.

**The decisions of this part in one table** [D]

| Decision | Section |
| --- | --- |
| Locale, digits, calendar and time zone are four independent settings kept on the device; the API is language-neutral and returns copy keys, never prose | S11.41 |
| Layout uses logical CSS only; direction is set once at the root and changed only by isolates around foreign text | S11.42, S11.45 |
| Persian digits exist only at the display edge; storage, API, exports, hashes and the clipboard carry ASCII digits and byte-exact text | S11.43, S11.45 |
| Jalali is the primary display calendar for `fa`, Gregorian is shown in detail views; the server never sees a Jalali string; cap periods are labeled in UTC, never with Jalali month names | S11.44 |
| Text from other people is never altered, only isolated; invisible bidi controls inside it are made visible and screened | S11.45 |
| Fonts are self-hosted and subset with shaping tables intact, with system fallbacks; no third-party font, script or style request on any member page | S11.46, S11.49 |
| WCAG 2.2 level AA is the declared target [A], with one known deviation (lease timing) stated openly | S11.48 |
| Budgets are initial configurable defaults enforced in CI; a paste-back draft stays on the device and is sent only after an explicit Submit | S11.49, S11.55 |
| Notices are one keyed table in `fa` and `en`, every row `needs human and legal review`; each promise-like sentence says declared (`اعلام‌شده`) | S11.50 to S11.53 |

## 11.41 Locale model

Supported locales are the `locale` enum of S0.8.6 (`fa`, `en`), listed in `i18n.supported_locales`; the default is `i18n.default_locale` (`fa`). [D]

**Four independent display settings** [D]

| Setting | Values | Default for `fa` | Default for `en` | Kept | Effect of a change |
| --- | --- | --- | --- | --- | --- |
| `locale` | `fa`, `en` | see first-visit rule | see first-visit rule | on the device | Immediate re-render; no reload; no input lost |
| `digits` | `latin`, `persian` | `i18n.digits_default_fa` (`persian` [A][H]) | `i18n.digits_default_en` (`latin`) | on the device | Display only (S11.43) |
| `calendar` | `jalali`, `gregorian` | `i18n.calendar_default_fa` (`jalali`) | `i18n.calendar_default_en` (`gregorian`) | on the device | Display only (S11.44) |
| `time_zone` | an IANA zone | the device zone | the device zone | on the device | Display only; never inferred from an IP address (S0.6) |

The four settings are independent: a member may use `en` with Persian digits, or `fa` with Gregorian dates. They are stored on the device, not on the server, to collect less [D]; if S15.* offers a member settings resource, these four fields are the only i18n fields in it [A].

**First-visit rule** [D]

```
fn initial_locale(stored, nav_languages, cfg):
    if stored.locale in cfg.supported_locales: return stored.locale
    if cfg.first_visit_locale_from_browser:            # i18n.first_visit_locale_from_browser
        for tag in nav_languages:                      # the browser's own preference order
            if tag startswith 'fa': return 'fa'
            if tag startswith 'en': return 'en'
    return cfg.default_locale                          # 'fa': Persian first
```

The preference list is read on the client only and is never sent to the server. [D]

**Rules** [D]

- A language switch is present on every screen, including error, offline and consent screens. Its labels are the endonyms `فارسی` and `English`, each carrying its own `lang`, so that it is readable whatever the current locale.
- Switching language keeps the state: pasted draft text, scroll position, expanded sections (including a mandatory prompt expansion), and focus. It never navigates away.
- Public pages are addressable per locale with a path prefix `/fa/` or `/en/` [A]. The API is not: it is language-neutral. Error bodies carry `details.copy_key` (S0.11), and the client renders the text.
- Any human-authored, member-visible string that the system stores (template display name, topic category name, badge name, service display name, reviewer-written reject reason) MUST be stored as a `{fa, en}` pair or as a copy key. S5.*, S8.* and S7.* apply this to their fields.
- Missing-translation policy: static copy with a missing key in either locale fails the build (AC-i18n-31). For human-authored dynamic strings with a missing `fa` or `en`, the UI shows the other locale's text inside an element carrying its own `lang` and `dir` (never an empty string, never the raw key). No telemetry about missing strings is sent, to avoid collecting reading behavior.

## 11.42 Right-to-left rules

RTL is the primary layout, not a mirrored afterthought: the design is made in `fa` first and checked in `en` second. [D] Each rule is testable; the test cases are named in S11.54.

| Area | Rule | Test |
| --- | --- | --- |
| Direction source | The root element carries `lang` and `dir` set from the active locale (`fa` gives `dir=rtl`, `en` gives `dir=ltr`) before first paint; a switch updates both without reload. No component sets its own direction except the isolates of S11.45. | AC-i18n-01 |
| Logical properties | Layout CSS uses logical properties only: `margin-inline-start`, `padding-inline-end`, `inset-inline-start`, `border-start-start-radius`, `text-align: start` or `end`, `float: inline-start`. Physical `left` and `right` properties and values are forbidden outside the allowlist in the next row. A CI check fails the build on a violation. | AC-i18n-04 |
| Physical-direction allowlist | Allowed only for code blocks (always LTR), LTR-only tokens that set their own `dir` (S11.42 forms row), canvas or drawing code that works in coordinates, and operating-system safe-area insets. Each use carries a comment `physical-ok: <reason>` that the check reads. | AC-i18n-04 |
| Flex and grid | Use `flex` and `grid`, which follow direction. `row-reverse` and manual order swaps used to fake RTL are forbidden. | AC-i18n-04 |
| Alignment | Text aligns `start`. Centered text only for short single-line headings. Never `text-align` left or right. | AC-i18n-04 |
| Mirrored in RTL | Arrows and chevrons, back and forward, next and previous, disclosure triangles, progress bars and sliders (fill grows from the inline start), carousel and swipe order, list and tree indentation, stepper order, breadcrumbs, timelines, and the position of the primary action (at the inline end of a button row). Every icon in the sprite carries `mirror: true` or `mirror: false` in the icon manifest (default `false`); mirrored icons flip under `dir=rtl`. | AC-i18n-05 |
| Not mirrored | The brand mark, code, URLs, hashes, IDs, e-mail addresses, the order of digits inside a number, check marks, plus and minus signs, clock faces, the numeric axis of a chart. | AC-i18n-05 |
| Time axes | Time runs from the inline start to the inline end (right to left in `fa`), so that charts read like text [D]. Whether this reads naturally to Persian readers is [H], tested in the Phase 1 interviews (FD§9) with a 5-second read test; the kill criterion (a share of interviewees who misread the axis) is set by the founders in the pre-registration (`FND`); the fallback is a per-chart setting, not a redesign. | AC-i18n-05 |
| Operator diagrams | Any diagram the operator tools draw as a graph is an explicit `dir=ltr` figure whose text labels still follow S11.45. | AC-i18n-05 |
| Tables | Column order follows the reading direction; row headers sit at the inline start; numeric columns align `end` and use tabular figures where the font supports them [V]. | AC-i18n-04 |
| Forms | Labels above fields; helper and error text under the field; the required marker follows the end of the label; a checkbox or radio sits at the inline start of its label. | AC-i18n-22 |
| Free-text input | `dir=auto` plus a three-way direction toggle (auto, RTL, LTR) on the paste-back box, because a pasted answer may begin with a digit, a quote or a Latin word. The toggle is kept per field on the device only. | AC-i18n-14 |
| LTR-only fields | Recovery key, e-mail address, invite code, device-link code and URL fields set `dir=ltr`, `text-align: start`, `autocapitalize=off`, `autocorrect=off`, `spellcheck=false`. `text-align: start` resolves against the element's own `dir`, so no physical alignment is needed. | AC-i18n-14 |
| Numeric fields | `inputmode` is `numeric` or `decimal`, and the field is `dir=ltr`, so that digits and separators never reorder; the typed text is parsed by S11.43. | AC-i18n-08 |
| Punctuation and quotes | Persian copy uses « » ، ؛ ؟ and the Persian decimal and thousands separators (S11.43). Latin punctuation appears inside Persian sentences only inside an isolated Latin token. Brackets and parentheses are never swapped by hand; the bidi algorithm mirrors them. | AC-i18n-31 |
| ZWNJ and ZWJ | Inputs, storage and rendering keep U+200C and U+200D. No sanitizer, trimmer or normalizer removes them. Truncation with an ellipsis happens on extended grapheme cluster boundaries only. | AC-i18n-15 |
| Styling of Arabic-script text | No `letter-spacing` (it breaks cursive joining); no italic or synthetic italic; no `text-transform`; no justified text (no kashida support is assumed). Emphasis is by weight only. | AC-i18n-19 |
| Line breaking and height | No hard-coded line breaks in copy; `overflow-wrap: anywhere` for long unbroken tokens (keys, hashes); `hyphens: none` for Persian; no fixed-height or fixed-width container holds text; the `fa` line-height token is larger than the `en` token so that dots and descenders are not clipped (values are design tokens checked by the clipping test, not set here). | AC-i18n-20 |
| Scrolling and focus | Horizontally scrollable regions start at the inline start; scroll-into-view and focus logic use the inline axis. | AC-i18n-01 |
| Keyboard | Arrow keys keep their visual meaning; custom widgets (tabs, sliders, carousels) map ArrowLeft and ArrowRight to the visual direction and Home and End to the inline start and end; no shortcut depends on a physical key position. | AC-i18n-23 |
| Text in images | No text is baked into a bitmap. Any generated image (share card, S12.*) draws its text with the same font stack, direction and digit rules as the UI. | AC-i18n-18 |
| Emoji and symbols | Never the only carrier of meaning (S11.48); rendering varies by device [V]. | AC-i18n-22 |
| Exports | Downloads that contain text (provenance manifest, deliverables) are UTF-8, use ASCII digits and ISO dates (S0.6), and carry no direction marks added by the renderer. | AC-i18n-07 |
