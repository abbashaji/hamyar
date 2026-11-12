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

## 11.43 Numerals

Three contexts, one rule each [D]:

| Context | Digits | Why |
| --- | --- | --- |
| Display of a number the system formats (balance, price, count, time left, version of a parameter) | `latin` or `persian` per the member's `digits` setting | Readability (FD§10, prompt F) |
| Typed input in a numeric field | Either digit set accepted, converted to ASCII before anything leaves the field | A member should not have to switch keyboards |
| Storage, API, exports, logs, hashes, IDs, clipboard of content | ASCII digits `0` to `9` only | S0.6: amounts are base-10 integer strings, timestamps are RFC 3339; one canonical form keeps hashes and comparisons stable |

**Digit sets.** `latin` is U+0030 to U+0039. `persian` is the Extended Arabic-Indic digits U+06F0 to U+06F9 (`۰۱۲۳۴۵۶۷۸۹`). The Arabic-Indic digits U+0660 to U+0669 are never produced, because the forms of four, five and six differ from the Persian ones; they are accepted on input and converted. [D]

**Default.** `fa` uses `i18n.digits_default_fa`, initially `persian` [A][H]: the hypothesis is that Persian readers prefer Persian digits in a Persian interface; it is tested in the Phase 1 interviews (FD§9) and replaced by the measured majority (`P1M`); the kill criterion (a share of interviewees who switch to `latin` in the first session) is set by the founders in the pre-registration (`FND`). `en` uses `latin`. The member can change it in settings at any time. [D]

**The formatter works on values, never on strings** [D]

```
fn fmt_number(value, opts, ctx):            # value: integer or exact decimal, never a float
    sign, int_part, frac = split(value, opts.decimals)
    sep_group = '٬' if ctx.digits == 'persian' else ','
    sep_dec   = '٫' if ctx.digits == 'persian' else '.'
    s = group(int_part, size=3, sep=sep_group) + ((sep_dec + frac) if frac else '')
    if ctx.digits == 'persian': s = map_digits(s, '0123456789' -> '۰۱۲۳۴۵۶۷۸۹')
    return isolate(sign + s, dir='ltr', mode=ctx.mode)   # S11.45: one LTR unit per number
```

The separators follow the digit set, not the locale. Platform number formatting MAY be used where it gives exactly this output [V: support on the target phones]; otherwise the bundled formatter is used. Every formatted number is one LTR isolate, so its display does not depend on the surrounding text direction or on the mixed bidi classes of digits and separators [D]. A ratio is shown as a decimal, never as a percent (`0.87`, not `87%`), which avoids a percent-sign placement problem and matches the FD figures [D].

**Amounts and ratios** [D]

- Credit amounts come from `_ucr` integers (S0.6): balances are shown rounded down, prices rounded up, to `ui.credit.display_decimals` places; a whole number of credits is shown without decimals.
- Ratios come from `_ppm` integers and are shown to `ui.ratio.display_decimals` places, rounded half away from zero (the FD§3.3 example shows 869,565 ppm as `0.870`).
- Counts are integers. Grouping separators are used from four digits up.
- A value that the system could not compute is shown as an em dash with an accessible label, never as `0`.

**Where the digit mapping is never applied** [D]: free text of any kind (prompt text, requester data, template bodies, submitted results, glossary terms, reviewer notes); the recovery key, invite and device-link codes; IDs (`job_...`), hashes, keys, URLs, e-mail addresses, version strings; code blocks; JSON. Copy buttons that copy a number from the UI copy the ASCII form. The mapping is a property of the formatter that produced the number, so text a person typed cannot be changed by it. Literal digits in notice copy are avoided altogether (S11.50).

**Input parsing** [D]

```
fn parse_decimal(raw):                           # numeric fields; returns Decimal or a field error
    s = trim(raw)
    s = map U+0660..U+0669 and U+06F0..U+06F9 to '0'..'9'
    s = replace '٫' with '.' ; replace '٬' with ','
    s = remove U+200E, U+200F, U+200C, U+00A0, U+202F, and ASCII space   # paste residue and grouping spaces
    if s matches ^[0-9]+(\.[0-9]+)?$:            ok
    elif s matches ^[0-9]{1,3}(,[0-9]{3})+(\.[0-9]+)?$:   s = remove ','   # ',' only as a grouping mark
    else: return error VALIDATION_FAILED, field code 'number_format'
    return Decimal(s)
```

A comma is never read as a decimal point, because `1,5` read as `15` would silently change an amount. The field echoes the parsed value in the display form before the member confirms anything that moves credit (job size, reservation size, escrow confirmation). The server validates the ASCII value again and never parses Persian digits (S0.11). [D]

**Ordered lists** use a CSS counter style defined in the stylesheet (`system: numeric`, symbols `۰` to `۹`) when `digits` is `persian`, and `decimal` otherwise; no external resource is involved. Sorting, search and filtering operate on the ASCII values. [D]

## 11.44 Dates, times and calendars

**Storage and wire** [D]: UTC `timestamptz` and RFC 3339 with `Z`; durations in integer seconds (S0.6). The server never stores, accepts or emits a Jalali string. Conversion to a display calendar happens only on the client.

**Calendars** [D]: `calendar` is `jalali` or `gregorian` (S0.8.6). `fa` defaults to `jalali`, `en` to `gregorian`. With `i18n.dual_calendar_detail` true (FD§10), every detail view shows the primary calendar first and the other calendar second, plus the ISO instant. Lists and cards show the primary calendar only.

**Display patterns** (example instant `2026-11-11T09:30:00Z` shown in the zone `UTC`; the Jalali values are computed examples that the golden table of this section must confirm [V])

| Context | `fa`, `jalali`, `persian` digits | `en`, `gregorian`, `latin` digits |
| --- | --- | --- |
| Short date | `۱۴۰۵/۰۸/۲۰` | `11 Nov 2026` |
| Long date | `چهارشنبه ۲۰ آبان ۱۴۰۵` | `Wednesday 11 November 2026` |
| Date and time (24-hour clock) | `۲۰ آبان ۱۴۰۵، ۰۹:۳۰` | `11 Nov 2026, 09:30` |
| Other calendar line in a detail view | `۱۱ نوامبر ۲۰۲۶` (digit set of the member) | `20 Aban 1405` |
| ISO line in a detail view | `2026-11-11T09:30:00Z` (always ASCII) | same |
| Duration | number plus `ثانیه`, `دقیقه`, `ساعت` or `روز` | number plus `s`, `min`, `h` or `d` words in full |
| Credit expiry | the absolute date, then the days left | the same order |

The clock is 24-hour in both locales [A] (no AM and PM markers to translate). Relative wording (`in 3 hours`) is used only for countdowns and for times less than one day away or past; everything else is absolute. [D]

**Names for the fallback formatter and for tests** [D]

| No. | Jalali month, `fa` | Jalali month, `en` | Gregorian month, `fa` |
| --- | --- | --- | --- |
| 1 | فروردین | Farvardin | ژانویه |
| 2 | اردیبهشت | Ordibehesht | فوریه |
| 3 | خرداد | Khordad | مارس |
| 4 | تیر | Tir | آوریل |
| 5 | مرداد | Mordad | مه |
| 6 | شهریور | Shahrivar | ژوئن |
| 7 | مهر | Mehr | ژوئیه |
| 8 | آبان | Aban | اوت |
| 9 | آذر | Azar | سپتامبر |
| 10 | دی | Dey | اکتبر |
| 11 | بهمن | Bahman | نوامبر |
| 12 | اسفند | Esfand | دسامبر |

Weekdays in `fa`, Saturday first: `شنبه`, `یکشنبه`, `دوشنبه`, `سه‌شنبه`, `چهارشنبه`, `پنجشنبه`, `جمعه`. Jalali months 1 to 6 have 31 days, months 7 to 11 have 30 days, month 12 has 29 days, or 30 in a leap year. [V: names and spellings checked by a native-speaking reviewer; stored in the copy review record of S11.53]

**Calendar library requirement** (the library is chosen by the stack in S4.*; this is the requirement) [D]

1. Convert between a UTC instant and a Jalali or Gregorian calendar date, in a given IANA zone, correctly for at least 2026-01-01 to 2040-12-31 [A]; the range covers every date the system can show (credit lifetime, reservations, quotes; S0.10).
2. The official Jalali calendar defines leap years astronomically; arithmetic algorithms approximate it and may differ for some years [V]. The library MUST pass a golden table of boundary dates (the first day of each Jalali year, the last day of each leap Esfand, month boundaries, and the Gregorian dates around them) in CI. Who supplies and signs the table, and its source, is [V]: a native-speaking reviewer records it as a test fixture with its source reference.
3. Prefer the platform calendar support (`Intl` with the Persian calendar) where present [V: support on the target phones]; always bundle an arithmetic fallback (S0.6). Both are self-hosted, make no network request and count against `ui.budget.js_bytes`.
4. Pure functions; no hidden clock; time comes from the server-supplied instant (S11.49).
5. A date typed or picked by the member is converted to a UTC instant or window on the client and sent as RFC 3339; the UI shows the resulting UTC window in both calendars before confirmation.

**Time zone** [D]: the device zone by default, overridden by an IANA zone chosen in settings, never from an IP address (S0.6). Offsets and daylight-saving rules for any country come from the tz database on the device and are not written into this spec or the code [V]. Detail views show the offset in force at that instant.

**Period boundaries and labels** [D]

- Rate limits, the monthly mint cap and daily jobs use UTC boundaries (S0.6). A cap period is therefore labeled `UTC month` (`ماه میلادی به وقت UTC`) and never with a Jalali month name, because the boundaries differ and a Jalali label would mislead. The screen shows the start and end of the period, and any reset time, in the member's calendar and zone next to the UTC value.
- Weekly aggregates on public pages (S12.*, S13.*) use fixed UTC weeks and say so; the member's week start (`i18n.week_start_fa`, `saturday` [V]) affects only calendar pickers and personal views.
- Countdowns (lease time left) are rendered from the server's `expires_at`; see S11.49 for clock-skew handling.

**Date input and pickers** [D]: every date field names its calendar in its label; the text field parses only the selected calendar, and the year must fall in a plausible window for it (otherwise the error is `VALIDATION_FAILED` with a field code, shown from a copy key); the picker is keyboard operable, its month grid follows the reading direction, and its week starts on `i18n.week_start_fa` for `jalali` and on the member's regional default otherwise [V].

## 11.45 Mixed-direction text

Prompts, requester data, pasted answers, glossary terms and reviewer notes mix Persian, English, digits, code and URLs in any order. Policy: **never alter what a person wrote or what a template says; only isolate it for display.** [D]

**Where mixed text appears** [D]: the cell card and the expanded full prompt (template body plus data slots, FD§5.5); the paste-back box; submitted results in reviewer and requester views; glossary terms (translation jobs, S8.*); the deliverable preview; dynamic placeholders inside notice copy; admin and log views.

| Rule | Decision | Test |
| --- | --- | --- |
| Content is never altered | Stored text is exactly what was pasted or authored: no Unicode normalization, no trimming, no digit mapping, no ZWNJ removal, no inserted direction marks. Hashes are over raw bytes (S0.6). Only comparison keys are folded (`fold_fa`, below). | AC-i18n-15 |
| Isolation units | Block-level foreign text is split into paragraphs at line breaks, each a separate element with `dir=auto`. Inline dynamic text is wrapped in `<bdi>` in markup. In plain-text contexts (page title, `aria-label`, `alt`, toast text) the renderer wraps dynamic text in U+2068 and U+2069 (first-strong isolate) and LTR tokens in U+2066 and U+2069. Preformatted text keeps its line breaks and is rendered per line with `dir=auto`. | AC-i18n-14 |
| Declared language wins | If a template slot or output field declares its language (a BCP 47 tag from a closed list), the renderer sets `lang` and `dir` from it and uses `dir=auto` only for undeclared or mixed text. `dir=auto` follows the first strong character, so a Persian paragraph that starts with a Latin word would otherwise render left to right. Requirement on S8.*: slots and output fields carry `lang`. | AC-i18n-14 |
| LTR tokens | Code, URLs, hashes, IDs, e-mail addresses and keys render in an `dir=ltr` isolate in the monospace stack (S11.46) and are never mirrored. Code blocks scroll horizontally. | AC-i18n-14 |
| Fixing punctuation | A sentence-final mark next to an opposite-direction word is fixed by isolating that word, never by inserting direction marks into the content. | AC-i18n-14 |
| Invisible controls are made visible | In the expanded prompt and in reviewer and requester result views, U+202A to U+202E, U+2066 to U+2069, U+200B, U+2060 and U+FEFF are always shown as labeled markers. U+200C, U+200D, U+200E and U+200F (legitimate in Persian text) are shown as markers only when the member turns on *show invisible characters*. Markers come from CSS-generated content or `user-select: none` elements, so they are never in a copied range. | AC-i18n-16 |
| Screening | Embedding and override controls (U+202A to U+202E) and isolate controls (U+2066 to U+2069) in requester input or in a submission are flagged, because they can make text read differently from what it is (the same class of trick as source-code spoofing). The action is `screen.bidi_control_action`, initially `flag_for_review`; for a submission, a flag means `submission.quarantined` (S9.*). U+200C, U+200D, U+200E and U+200F are not flagged. | AC-i18n-17 |
| Copy buttons | *Copy prompt* writes exactly the stored prompt text to the clipboard: no marks added or removed, no digit mapping, no trailing characters. Copying a UI-originated number or string writes the raw form without isolates. | AC-i18n-15 |
| Paste-back | The field's content is sent exactly as it is in the field, without trimming. The server judges length and schema on the raw text (S9.*). | AC-i18n-15 |
| Placeholders in notices | The renderer escapes dynamic text first, then isolates it (below). Numbers come from the formatter (S11.43). | AC-i18n-14 |
| Prefilled links | Where a registry entry says prefill is supported, the prompt is percent-encoded from its UTF-8 bytes unchanged. Encoded length is computed by actually encoding, and if it exceeds `adapter.max_url_chars` (a per-service value, [V]) or `adapter.copy_only` is true, the adapter falls back to copy-only. For planning: every non-ASCII byte becomes three characters (`%XX`), a Persian letter is two bytes, so a Persian prompt expands up to six URL characters per letter; a prompt of `cell.envelope.max_input_chars` (4,000, initial configurable default) Persian letters can reach about 24,000 URL characters, so copy-only is the expected path for Persian prompts. | AC-i18n-15 |

```
fn render(key, params, ctx, mode):                 # mode: 'markup' | 'plain'
    tpl = copy[key][ctx.locale] or fallback(key, ctx)        # S11.41
    for p in placeholders(tpl):
        v = params[p.name]
        if p.type in {number, credits, ratio, duration, date, datetime}:
            s = format(v, ctx)                               # S11.43, S11.44; already one LTR unit
        elif p.type in {text, service, topic}:
            s = escape(v)                                    # untrusted text: escape, then isolate
            s = isolate(s, dir='auto', mode=mode, lang=known_lang(v))
        tpl = substitute(tpl, p, s)
    return tpl
fn isolate(s, dir, mode, lang=None):
    if mode == 'markup': return '<bdi' + (' dir=ltr' if dir == 'ltr' else '') + lang_attr(lang) + '>' + s + '</bdi>'
    return ('\u2066' if dir == 'ltr' else '\u2068') + s + '\u2069'
```

**Comparison folding** (used by automatic checks, glossary matching and duplicate detection in S8.* and S9.*; the original text is never overwritten) [D]

```
fn fold_fa(text, opts):
    t = NFC(text)
    t = map U+0660..U+0669 and U+06F0..U+06F9 to '0'..'9'
    t = replace U+064A and U+0649 with U+06CC ; replace U+0643 with U+06A9   # Arabic yeh, kaf to Persian forms
    t = remove U+0640                                                        # tatweel
    if opts.strip_marks: t = remove U+064B..U+0652 and U+0670               # vowel marks
    if opts.zwnj == 'space': t = replace U+200C with U+0020
    elif opts.zwnj == 'none': t = remove U+200C
    if opts.collapse_ws: t = collapse runs of whitespace to one space
    return t                                                                 # a key, never shown, never stored over the original
```

Each comparator declares its `opts`; whether `zwnj` is folded is a per-template decision because *می‌کنم* and *می کنم* are both seen in real text [A].

## 11.46 Fonts

| Topic | Decision |
| --- | --- |
| Hosting | Fonts are WOFF2 files served from the application's own origin or its storage interface (S4.*). No third-party font service, stylesheet, script, CDN or analytics request is made by any member or public page (FD§10 cautions on blocked resources; prompt I). `ui.font.third_party_allowed` is the constant `false`; the content security policy (S10.*) blocks other origins; a CI test fails on any request to another origin (AC-i18n-18). [D] |
| Family | The stylesheet names one alias, `Hamyar Sans`, mapped to the bundled files, so the family can change without touching components. The final family is chosen by the designer from candidates whose license permits redistribution and subsetting; candidates, unverified: Vazirmatn, Noto Sans Arabic, Noto Naskh Arabic [V: license text and glyph coverage, checked by a reviewer; the license file and the check date are stored beside the font files in the repository]. [D] |
| Coverage | Must cover: Persian letters including پ چ ژ گ ک ی; hamza and the combining hamza above (U+0654) used for the ezafe; the digits U+06F0 to U+06F9; ، ؛ ؟ « » ٫ ٬; U+200C to U+200F; Basic Latin; common general punctuation. [D] |
| Subsetting | A build step subsets by `unicode-range` so that `en` pages do not download Arabic-script ranges and `fa` pages download Latin only if the face contains it. The subset MUST keep the OpenType layout tables that Arabic-script shaping needs (at least `ccmp`, `locl`, `isol`, `init`, `medi`, `fina`, `rlig`, `liga`, `calt`, `mark`, `mkmk`, `kern`); stripping them breaks letter joining. A render test on joined words and on a ZWNJ pair is part of CI (AC-i18n-19). [D] |
| Weights and styles | Two weights (`ui.font.max_weights`, initial configurable default 2: regular and bold). No italic; `font-synthesis` is off, so a missing style is not faked. [D] |
| Loading | Preload only the regular face of the active locale on first screens; hashed file names with long immutable caching [A]; `font-display: swap` so text is never invisible; metric overrides to limit layout shift where the browser supports them [V]. [D] |
| Fallback stack | The default Persian stack ends in system faces and a generic family (`ui.font.fa_stack`, S11.55). Which system faces render Persian on the target phones is [V] (G2, FD§8.3). A prompt that contains letters outside the subset (Kurdish, Urdu, Arabic) must still render in a fallback face and never as empty boxes (AC-i18n-20). [D] |
| Monospace | A system monospace stack for codes, keys and code blocks; always `dir=ltr`. The recovery key is shown in groups of four characters, as an LTR isolate, with no digit mapping; on input, hyphens, spaces and case are ignored; paste is never blocked. Its alphabet and length belong to S10.*, which SHOULD avoid visually ambiguous characters. [D] |
| Budget | Total font bytes are capped by `ui.budget.fonts_bytes` (initial configurable default 80,000, replaced by the measured subset sizes, `TEC`). [D] |

## 11.47 English

English is a full locale, not a fallback. [D]

- Same keys, same screens, same flows as `fa`; the layout is checked in both directions (S11.42).
- Digits `latin` and calendar `gregorian` by default, with the Jalali date shown as a second line in detail views (S11.44). Jalali month names in English are the transliterations in S11.44.
- Plain, short sentences; the same terms in the same meaning every time (S11.53 glossary); no idioms, humor or abbreviations in notices.
- Counted nouns have `one` and `other` plural forms in `en`; Persian uses the singular noun after a number, so a Persian key has a single form [A].
- Dates are unambiguous (`11 Nov 2026`), never `11/11/26`. The clock is 24-hour (S11.44).
- English is written first for counsel to read and Persian is written natively, not machine-translated; which language prevails if they ever differ is a legal question that this spec does not decide and no precedence clause is written [V: counsel; recorded in the counsel memo]. [A]
- A member can read both languages of any notice side by side on the public notices page (S11.52).

## 11.48 Accessibility

**Target** [A]: WCAG 2.2 level AA on every member, requester, reviewer, operator and public screen, in both locales. This is a declared target, not a claim that it has been reached; reaching it is shown by the audit in the last row of the table below. The owner decision that could overturn it (a different level, or a lower level for operator tools) is listed in S3.*. One deviation is known and stated openly (row 2.2.1).

| Success criterion (WCAG 2.2) | Decision |
| --- | --- |
| 1.1.1 Non-text content | Every icon that carries meaning has a text alternative from a copy key; decorative icons are hidden from assistive technology. No text is baked into images (S11.42). |
| 1.3.1, 1.3.2 Structure and order | Landmarks, one `h1` per screen, ordered headings, labeled controls, table headers. The cell card is one `article` with the declarations (purpose, license, sensitivity, service, template, expected time) in a description list. DOM order equals reading order in both directions. |
| 1.3.4 Orientation | No orientation lock. |
| 1.4.1 Use of color | Status (accepted, rejected, flagged, expired) is never color alone; each has a word and a shape. |
| 1.4.3, 1.4.11 Contrast | Text at least 4.5:1 (3:1 for large text); borders, icons and focus indicators at least 3:1, in light and dark themes. |
| 1.4.4, 1.4.10 Resize and reflow | Usable at 200% text zoom and at a 320 CSS pixel width without two-dimensional scrolling, except for code blocks and data tables, which scroll inside their own container. |
| 1.4.12 Text spacing | Nothing is lost when a user stylesheet increases line, paragraph and word spacing. Letter spacing is never applied to Arabic-script text (S11.42). |
| 1.4.13 Content on hover or focus | Dismissible, hoverable, persistent. |
| 2.1.1, 2.1.2 Keyboard | Everything is operable by keyboard; nothing traps focus. The language switch, the prompt expansion, copy, paste-back and Submit are reachable in a short tab sequence. |
| 2.2.1 Timing adjustable (known deviation) | A lease has a server-enforced time limit (`lease.timeout_s`) that exists so that cells are not hoarded. WCAG asks that a user can extend a limit many times; the product allows `lease.max_extensions` (initial configurable default 1) extensions of `lease.extend_s`. The deviation is mitigated by: a warning at `ui.lease.warn_remaining_s`; a default limit of ten times the expected time per cell (`lease.timeout_s` is 10 x 120 s, S0.10); a free decline at any moment; an immediate re-lease of the next cell; and local draft preservation (S11.49). The deviation is listed in the accessibility statement. [A][V: whether the essential-limit exception applies is for the accessibility auditor] |
| 2.2.2, 2.3.1, 2.3.3 Motion | Nothing blinks or flashes. Animation honors `prefers-reduced-motion`; the counter and progress indicators work without motion. |
| 2.4.1, 2.4.2, 2.4.6 Navigation | Skip-to-content link; localized page titles (dynamic parts isolated, S11.45); descriptive headings and labels. |
| 2.4.3, 2.4.7, 2.4.11 Focus | Logical focus order; a visible focus indicator on every control; focused elements are never hidden under sticky bars. |
| 2.5.1, 2.5.2 Pointer gestures | No gesture is required (no path-based gestures); swipes and carousels have buttons. Actions fire on release and can be cancelled. |
| 2.5.3 Label in name | A control's accessible name starts with its visible Persian or English label. |
| 2.5.8 Target size | Targets are at least `ui.a11y.min_target_css_px` (initial configurable default 44; the WCAG 2.2 minimum is 24). |
| 3.1.1, 3.1.2 Language | `lang` on the root and `lang` on every inline passage in the other language, so that speech output switches voice (S11.45). Persian speech availability differs by device [V: target phones]; no function depends on audio. |
| 3.2.2 On input | Changing the language, digits or calendar setting changes only the display and never submits or navigates. |
| 3.3.1 to 3.3.4 Errors | An error summary at the top receives focus, links to each field, and names the problem and the fix from `details.copy_key` and `details.fields[].path` (S0.11). Screens that move credit (escrow confirmation, reservation, cancellation) show a review step and can be reversed or cancelled where the ledger allows (S6.*). |
| 3.3.7 Redundant entry | Nothing already entered is asked again; the paste-back draft survives reload and re-lease (S11.49). |
| 3.3.8 Accessible authentication | No cognitive test, no transcription. The recovery key field accepts paste and password managers; its grouping, hyphens and case are tolerated (S11.46). |
| 4.1.2, 4.1.3 Name, role, value; status messages | Standard controls; custom ones carry ARIA roles. Result feedback (accepted, rejected, balance changed, draft saved, offline) is announced politely by a status region. The lease countdown is not announced every second: only at `ui.lease.warn_remaining_s` and at expiry. |
| Mandatory prompt expansion (FD§5.5) | While a first-use or non-default prompt is unexpanded, Copy and Open stay focusable with `aria-disabled=true` and an adjacent explanation linked by `aria-describedby`; they are not removed from the tab order and not conveyed by color alone. Expanding moves focus to the start of the expanded text and announces it. |
| Plain language | Notices follow the copy rules of S11.50: short sentences, one idea each, the actor named. |
| Verification | An automated rules engine runs in CI on every screen in both locales (a failure fails the build); a manual pass with keyboard only, 200% zoom, and a screen reader on a real Android and a real iOS phone, in `fa` and in `en`, is a `LaunchGateItem` under G2 with evidence attached (S14.*). An accessibility statement page with a way to report problems exists before launch [A]. Automated checks find only part of the problems; the manual pass is not optional. |

## 11.49 Low-bandwidth behavior and offline-tolerant paste-back

The design assumes slow, lossy and sometimes blocked connections without assuming any statistic about them. Reachability from Iran is [V] (FD§8.3 G2) and is measured, not assumed. [D]

**Rules** [D]

- **No third-party requests** from any member or public page: no CDN, font, script, style, tracker, map, embed, avatar or analytics service. The content security policy (S10.*) allows the page origin and the API origin only. A CI test loads every screen with all other origins blocked and fails on any attempt (AC-i18n-28). Opening a service in another tab is a member action and is not part of a page load.
- **No heavy assets:** no video, no raster hero images; icons are one inline SVG sprite; share cards (S12.*) are generated only on explicit request and are outside the flows of this part.
- **Notices and public pages work without JavaScript and without an identity:** the notices (S11.51) are static pages readable before an identity exists, in both languages; the first-contribution flow needs JavaScript because keys are generated and used on the device (S10.*).
- **UTF-8 JSON is sent raw**, not ASCII-escaped: an escaped Persian letter costs six bytes against two. Text responses are compressed (brotli or gzip).
- **Caching:** static assets have hashed names and immutable caching [A]; authenticated responses are `no-store` and public ones follow S0.11.7.
- **Polling, not sockets:** public counters refresh every `public.counter_refresh_s`; polling pauses while the tab is hidden and backs off on failure. Where the browser signals a data-saver preference, optional refreshes and animations stop [V: browser support].
- **Only the active locale's strings** are loaded; the other locale loads on switch. The consent manifest (S11.50) is small and carries hashes, not texts.
- **Retries** use the same `Idempotency-Key` and exponential backoff with jitter: `delay_n = min(ui.retry.max_delay_s, ui.retry.base_delay_s x 2^(n-1)) x u`, with `u` uniform in [0.5, 1.0], and `Retry-After` wins when larger. After `ui.retry.max_attempts` the client stops retrying by itself and offers a manual retry.

**Budgets** (every one is an `initial configurable default` or a formula; each is enforced in CI against the build and replaced by measurement on real phones and networks, `TEC`)

| Parameter | Value | Derivation |
| --- | --- | --- |
| `ui.budget.js_bytes` | 100,000 | initial configurable default, compressed, whole first-contribution flow including the calendar and number formatters |
| `ui.budget.css_bytes` | 20,000 | initial configurable default, compressed |
| `ui.budget.fonts_bytes` | 80,000 | initial configurable default, compressed |
| `ui.budget.first_load_bytes` | 204,096 | js + css + fonts + 4,096 for markup and the icon sprite = 100,000 + 20,000 + 80,000 + 4,096 |
| `ui.budget.cell_card_bytes` | 16,096 | `cell.envelope.max_input_chars` x 3 (worst-case UTF-8 bytes per character, as in S0.10) + 4,096 metadata = 4,000 x 3 + 4,096 |
| `ui.budget.repeat_view_bytes` | 65,248 | cell card + `cell.envelope.max_submission_bytes` + 16,384 for balance and status calls = 16,096 + 32,768 + 16,384 |
| `ui.budget.test_profile` | downlink 400 kbit/s, round trip 400 ms | initial configurable default for the test harness only; it is a test input, not a claim about any real network |
| `ui.budget.first_interactive_s` | 7 | `ceil(first_load_bytes x 8 / (downlink_kbps x 1000) + 6 x rtt_s)` = `ceil(204,096 x 8 / 400,000 + 6 x 0.4)` = `ceil(4.08 + 2.4)`; six round trips for name lookup, connection, handshake, markup, style and script [A] |

**Server time and countdowns** [D]. The client never trusts its own wall clock (S0.6). Lease responses carry `expires_at` and `server_time` (requirement on S15.*); the client keeps a monotonic clock and an offset:

```
sent_at = mono_now() ; response arrives at recv_at = mono_now()
offset  = server_time - (sent_at + recv_at) / 2          # server minus client monotonic time
remaining(now_mono) = expires_at - (now_mono + offset)
```

The displayed countdown is advisory; the server decides (`reject.lease_expired`, S9.*).

**Offline-tolerant paste-back drafts** [D]

The member copies a prompt, presses Send in the service, and pastes the answer back. Pasting must not be lost to a dropped connection, and the platform never submits for the member and never touches the service page (ground rule 3; FD Principle 3).

| Client-local state | Meaning | Leaves the state when |
| --- | --- | --- |
| `empty` | Nothing pasted for this lease | text is typed or pasted: `drafting` |
| `drafting` | Text exists; saved to device storage keyed by lease id; never sent | Submit pressed: `queued`; time-to-live, lease end or *clear local data*: purged |
| `queued` | Submit was pressed; a key was generated; waiting for a connection or a retry timer | connection or timer: `sending`; lease end plus `lease.submit_grace_s` passes: `expired_local` |
| `sending` | One request in flight with the stored `Idempotency-Key` | 2xx: `acked`; network error, timeout, 5xx: `queued` (backoff); 429: `queued` after `Retry-After`; 410 `LEASE_EXPIRED` or 409 `LEASE_CONFLICT`: `expired_local`; 400, 413 or 422: `drafting` with the error shown and the text kept |
| `acked` (terminal) | The server stored the outcome (S9.*) | the draft is purged at once |
| `expired_local` (terminal) | The cell can no longer be accepted from this lease | the text is kept until the draft time-to-live so the member can copy it out; then purged |

These are client UI states, not domain states of S0.9; they emit no event and are not logged on the server. [D]

```
fn on_submit_press(lease_id):                    # only a person's press starts this; no auto-submit on paste
    d = store.get(lease_id)
    if utf8_bytes(d.text) > cfg.cell_envelope_max_submission_bytes: show copy_key for size; return   # server is authoritative (413)
    d.key = new_idempotency_key()                # S0.11.5; a new key per press, reused by every retry of this press
    d.state = 'queued'; store.put(d)             # persisted before any network call
    schedule(try_send, now)
fn try_send(d):
    if server_now() > d.expires_at + cfg.lease_submit_grace_s: d.state = 'expired_local'; return
    resp = POST /v1/leases/{d.lease_id}/submission   with the raw text, the lease nonce, Idempotency-Key d.key   # body per S15.*, S9.*
    match resp: 2xx -> purge(d); show accepted_or_checking | 410, 409 -> d.state = 'expired_local'
                | 400, 413, 422 -> d.state = 'drafting' ; show errors | 429, 5xx, network -> backoff(d)
```

Storage and privacy [D]:

- A draft record holds the pasted text, the lease id, the lease nonce, the key and timestamps, in device storage (IndexedDB preferred). It is purged on acknowledgement, at the lease end plus the time-to-live `ui.draft.ttl_s`, on *clear local data*, and when the identity is closed. *Clear local data* never deletes the member's key silently; deleting the key is a separate, confirmed action defined in S10.*.
- The draft contains output of a service for a cell of data classed S0 or S1 (S0.8.1); it is still readable by anyone who can inspect the device, and the notices say so (`copy.offline.draft_local_only`, `copy.safety.iran_notice.body`).
- If storage is unavailable (private browsing) or full, drafts live in memory only, the field keeps its text, and a status message says that reloading will lose it. Nothing is silently dropped.
- Two tabs: the draft is keyed by lease, the last write wins, and a `storage` event refreshes the other tab.
- A service worker MAY cache the application shell and the notices for offline reading. It never caches API responses beyond the cell card of an active lease, which follows the same time-to-live. [A]

## 11.50 Copy system

**Storage and delivery** [D]. Copy is a set of versioned resource files shipped with the front-end build, one record per key, not rows in the database and not editable by the parameter editor: legal text changes only by a reviewed release. The build also emits a `copy_manifest` (key, version, hash, review status) that the API reads. Keys follow S0.5: `copy.<area>.<key>`, with an optional last segment (`.title`, `.body`, `.chip`, `.ack`).

```
copy_entry:
  key:            copy.<area>.<key>[.<part>]
  fa:             text                       # Persian first
  en:             text | {one, other}        # plural forms only where a count is shown
  promise:        bool                       # true when the key holds a promise-like sentence
  placeholders:   [ {name, type} ]           # identical set in fa and en
  review_status:  copy_review_status
  reviewed:       {fa_by, en_by, legal_ref, at}   # opaque admin ids and a memo reference
  version:        int                        # +1 on every text change
  hash:           sha256:<hex> over RFC 8785 canonical JSON of {key, fa, en, version}   # S0.6
```

**Review status** `copy_review_status` [D][A] (the value `needs_human_and_legal_review` is the marker of S0.5; the others are added here, `ISS-118`):

| Value | Meaning | Allowed next values |
| --- | --- | --- |
| `needs_human_and_legal_review` | Initial value of every row; any text change returns here. Shown to no member of a launched system. | `human_reviewed` |
| `human_reviewed` | A native-speaking reviewer for each language recorded that the text passes the checklist of S11.53 | `legal_reviewed`, `needs_human_and_legal_review` |
| `legal_reviewed` | Counsel's memo is referenced in `reviewed.legal_ref` [V] | `approved`, `needs_human_and_legal_review` |
| `approved` | Two distinct admins signed off (the rule of `launch.min_signoffs`, S14.*) | `withdrawn`, `needs_human_and_legal_review` |
| `withdrawn` | Taken out of use; the key is not deleted | none |

Changing the text of either language resets both to `needs_human_and_legal_review`, so the two languages never drift apart under an old approval. [D]

**Promise-like sentence** [D]: any sentence in which Hamyar, a reviewer or the operator says what it does, does not do, or will do, or what will happen in the future (including *we do not collect*). Every such sentence says *declared* (`اعلام‌شده` in Persian) in the sentence itself, so that the reader sees that it is a stated policy and not a guarantee (FD Principle 11). A key containing one has `promise: true`.

**Writing rules for both languages** [D]

- Short sentences, one idea each, the actor named, active voice, second person (`شما` in Persian, never the informal form).
- No legal conclusion (what a law or a terms-of-service clause means) and no statement about a provider's terms; such a dependence is a registry value rendered as a placeholder or stays [V].
- No provider name, no law name, no URL inside a notice.
- No absolute about something the project cannot show; *never* appears only inside a sentence that also says declared.
- No tip for getting around a limit; no politics; no humor.
- Any number that comes from a parameter is a placeholder (registry in S11.52). Literal digits do not appear in Persian copy.
- Paragraph break `¶`, list item `•` and placeholder `{name}` are the only markup. No HTML, no Markdown.
- Persian orthography and terminology follow S11.53.

**Copy checks in CI** (they fail the build; AC-i18n-31, AC-i18n-32)

| Check | Rule |
| --- | --- |
| Complete | Every key has `fa`, `en`, `promise`, a status and a placeholder list; both languages have the same placeholder set |
| Declared | A key with `promise: true` contains `اعلام‌شده` (also in its ezafe forms) in `fa` and `declared` in `en` |
| No guarantee claims | The words *guarantee*, *guaranteed*, *تضمین* and *ضمانت* occur only in negated or contrasting sentences from an allowlist kept with the key (for example *not a guarantee*, *تضمین نیست*) |
| Persian characters | No Arabic yeh or kaf (U+064A, U+0643); no Arabic-Indic digits; no ASCII digits and no Latin punctuation `, ; ?` outside placeholders and the allowlisted tokens (for example `IP`) |
| ZWNJ | No *می* or *نمی* followed by a space and a letter; no space before the plural suffix *ها*; both are written with ZWNJ |
| Direction controls | No bidi controls other than U+200C and U+200D in copy |
| No markup | No `<`, no URL, no Markdown |
| Status | A key whose text changed without a version bump or a status reset fails |

## 11.51 The notices: keyed copy table

The table lists the copy of every policy, privacy and risk notice required by prompt scope F. Columns: `key`; `FA` (Persian first); `EN`; `review status`. The machine value of the review status of every row is `needs_human_and_legal_review` (S11.50), written in the last column as *needs human and legal review*. All rows have `promise: true` unless the text contains no promise-like sentence. `¶` is a paragraph break and `•` a list item. [D]

No text below has been checked by a lawyer, a safety advisor or a native-speaking reviewer. The wording of the contributor waiver and of every statement about law, terms or safety is a draft for counsel and for a qualified safety advisor [V: counsel in the operator's jurisdiction, FD§8.3 G0; a person qualified to advise on safety, FD§8.3 G1].

### 11.51.A Account risk

| key | FA | EN | review status |
| --- | --- | --- | --- |
| `copy.risk.account_notice.title` | خطر برای حساب‌های خودتان | Risk to your own accounts | needs human and legal review |
| `copy.risk.account_notice.body` | همیار از شما می‌خواهد با حساب شخصی خودتان در یک سرویس هوش مصنوعی، کارهای کوچکی به نام «سلول کار» را برای دیگران انجام دهید. هر سرویس شرایط استفادهٔ خودش را دارد. ممکن است آن شرایط چنین کاری را مجاز ندانند، بدون اطلاع قبلی تغییر کنند، یا در محل زندگی شما به شکل دیگری اعمال شوند. اگر سرویسی تشخیص دهد که شرایط آن را نقض کرده‌اید، ممکن است حساب شما را محدود یا مسدود کند. همیار نمی‌تواند جلوی این اتفاق را بگیرد، از طرف شما پیگیری نمی‌کند و هیچ سرویسی را کنترل نمی‌کند. ¶ • اعلام‌شده: هر سرویس تنها وقتی در همیار عرضه می‌شود که یک بازبین شرایط آن را ثبت کرده و نسخهٔ تاریخ‌دارش را ذخیره کرده باشد. این بازبینی اعلام‌شده است و تضمین نمی‌کند که سرویس کار شما را بپذیرد. • اعلام‌شده: دکمهٔ ارسال را همیشه خودتان می‌زنید. همیار هرگز گذرواژه‌تان را نمی‌خواهد، به حساب شما وصل نمی‌شود و صفحهٔ گفتگوی شما را نمی‌خواند. • اعلام‌شده: می‌توانید از هر سلول کار انصراف دهید و هر زمان که خواستید کنار بگذارید، بدون هیچ جریمه‌ای. • پیش از استفاده از هر سرویس، شرایط آن را خودتان بخوانید. اگر مطمئن نیستید، از آن استفاده نکنید. | Hamyar asks you to use your own account on a third-party AI service to do small tasks, called cells, for other people. That service has its own terms. Those terms may not allow this, may change without notice, or may be applied differently where you live. If a service decides that you broke its terms, it may limit or suspend your account. Hamyar cannot prevent that, cannot follow up with the service for you and does not control any service. ¶ • Declared: a service is offered in Hamyar only when a reviewer has recorded its terms and saved a dated copy. This is a declared review, not a guarantee that the service will accept what you do. • Declared: you press Send yourself every time. Hamyar never asks for your password, never connects to your account and never reads your chat page. • Declared: you may decline any cell and stop at any time, without penalty. • Read the terms of a service yourself before you use it. If you are not sure, do not use it. | needs human and legal review |
| `copy.risk.service_review_line` | شرایط این سرویس آخرین بار در {review_date} بازبینی شده است. این بازبینی اعلام‌شده است و تضمین نیست. | The terms of this service were last reviewed on {review_date}. This is a declared review, not a guarantee. | needs human and legal review |

### 11.51.B Privacy

| key | FA | EN | review status |
| --- | --- | --- | --- |
| `copy.privacy.pseudonymity_notice.title` | همیار چه چیزی را جمع‌آوری می‌کند و چه چیزی را نه | What Hamyar collects and what it does not | needs human and legal review |
| `copy.privacy.pseudonymity_notice.body_collected` | اعلام‌شده: همیار یک کلید عمومی را که دستگاه شما می‌سازد ذخیره می‌کند تا بدون نام، شما را بشناسد. ¶ • اعلام‌شده: سوابق اعتبار شما، نتیجه‌هایی که ارسال می‌کنید، انتخاب‌های شما و گزارش‌ها یا درخواست‌های بازبینی‌ای که ثبت می‌کنید ذخیره می‌شود. • اعلام‌شده: برای جلوگیری از سوءاستفاده فقط هش کلیددار شناسه‌های دستگاه و شبکه به‌مدت {ip_hash_ttl_days} روز نگهداری می‌شود و نشانی IP خام شما هرگز ذخیره نمی‌شود. • اعلام‌شده: متن هر کار و نتیجه‌های آن {job_payload_days} روز پس از پایان کار حذف می‌شود؛ هش‌ها و سوابق فاقد اطلاعات شخصی باقی می‌مانند. • ثبت نشانی ایمیل اختیاری است. اعلام‌شده: همیار فقط در صورتی ایمیل شما را نگه می‌دارد که خودتان آن را اضافه کنید. | Declared: Hamyar stores a public key that your device creates, so that it can recognise you without a name. ¶ • Declared: it stores your credit records, the results you submit, your opt-in choices, and any reports or appeals you file. • Declared: to limit abuse it stores only keyed hashes of device and network identifiers, for {ip_hash_ttl_days} day(s), and never your raw network address. • Declared: the text of a job and of its results is deleted {job_payload_days} days after the job ends; hashes and records without personal data remain. • An e-mail address is optional. Declared: Hamyar stores one only if you choose to add it. | needs human and legal review |
| `copy.privacy.pseudonymity_notice.body_not_collected` | اعلام‌شده: همیار نام واقعی، شمارهٔ تلفن یا هیچ مدرک هویتی از شما نمی‌خواهد. ¶ • اعلام‌شده: گذرواژه یا نشست ورود شما در هیچ سرویسی را ذخیره نمی‌کند و متن صفحهٔ گفتگوی شما را نگه نمی‌دارد. • اعلام‌شده: محل اعضا را نمایش نمی‌دهد و از ردیاب یا کوکی شخص ثالث استفاده نمی‌کند. • اعلام‌شده: درخواست‌دهندگان هرگز نمی‌بینند چه کسی سلول کار را انجام داده است. | Declared: Hamyar does not ask for your real name, phone number or any identity document. ¶ • Declared: it does not store your password or session for any service, and it does not keep the text of your chat page. • Declared: it does not show where members are, and it does not use third-party trackers or cookies. • Declared: requesters never see who completed a cell. | needs human and legal review |
| `copy.privacy.pseudonymity_notice.body_limits` | آنچه همیار نمی‌تواند وعده دهد: ¶ • همیار «با نام مستعار» است، نه «ناشناس». ما وعده نمی‌دهیم که هیچ‌کس نتواند شما را شناسایی کند. • ارائه‌دهندهٔ میزبانی همیار و شبکه‌هایی که میان دستگاه شما و همیار قرار دارند ممکن است ببینند که دستگاه شما به همیار وصل شده است، هرچند طبق سیاست اعلام‌شدهٔ ما، نشانی خام شبکه ذخیره نمی‌شود. • اگر کسی با اختیار قانونی یا دسترسی فیزیکی داده‌ای بخواهد یا دستگاهی را بردارد، نتیجه به قانون و به چیزی که وجود دارد بستگی دارد. اعلام‌شده: ما تا جای ممکن کم نگه می‌داریم تا چیز کمتری برای تحویل وجود داشته باشد. • همیار نمی‌تواند اطلاعاتی را که خودتان بیرون از همیار منتشر می‌کنید کنترل کند. | What Hamyar cannot promise: ¶ • Hamyar is pseudonymous, not anonymous. We do not promise that nobody can identify you. • The provider that hosts Hamyar, and the networks between your device and Hamyar, may be able to see that your device connected, even though our declared policy is not to store raw network addresses. • If someone with legal power or physical access asks for data or takes a device, the outcome depends on the law and on what exists to be taken. Declared: we keep as little as we can, so that there is less to hand over. • Hamyar cannot control what other people do with information that you share outside Hamyar. | needs human and legal review |

### 11.51.C Safety of members in Iran

The notice is shown to every new member and does not depend on any guess about location: Hamyar never infers where a member is (S0.6, S10.*). It is also on the public notices page. [D]

| key | FA | EN | review status |
| --- | --- | --- | --- |
| `copy.safety.iran_notice.title` | یادداشتی ساده دربارهٔ ایمنی شخصی | A plain note on personal safety | needs human and legal review |
| `copy.safety.iran_notice.body` | اگر در ایران هستید، یا در جایی که مشارکت می‌تواند خطرناک باشد، پیش از عضویت این یادداشت را بخوانید. اعلام‌شده: همیار تلاش نمی‌کند بفهمد شما کجا هستید و این یادداشت را به همهٔ اعضای جدید نشان می‌دهد. ¶ مشارکت ممکن است برای شما خطر شخصی داشته باشد؛ این به محل زندگی شما، قانون همان‌جا و شرایط سرویس‌هایی که استفاده می‌کنید بستگی دارد. همیار نمی‌تواند این را به‌جای شما ارزیابی کند و مشاورهٔ حقوقی نمی‌دهد. ¶ • همیار «با نام مستعار» است، نه «ناشناس». اعلام‌شده: ما تا جای ممکن کمترین اطلاعات را جمع می‌کنیم. وعده نمی‌دهیم که هیچ‌کس نتواند شما را شناسایی کند. • هر چیزی که در یک کار، گزارش یا درخواست بازبینی می‌نویسید ممکن است کسانی آن را بخوانند که ما کنترلی بر آن‌ها نداریم. نام، راه‌های تماس یا هر چیزی را که بتواند خودتان یا دیگری را شناسایی کند ننویسید. • هر چیزی که روی دستگاه شما ذخیره شود، مثل پیش‌نویس‌ها، برای هرکس که بتواند از دستگاه استفاده کند یا آن را بررسی کند قابل دیدن است. هر زمان می‌توانید آن را پاک کنید. • همیار از شما نمی‌خواهد و به شما توصیه نمی‌کند که محدودیتی را دور بزنید یا شرایط استفادهٔ سرویسی را نقض کنید. اگر سرویسی برای شما در دسترس یا مجاز نیست، از آن استفاده نکنید. • اعلام‌شده: همیار محل اعضا را نمایش نمی‌دهد و مدرک هویتی نمی‌خواهد. • می‌توانید از هر سلول کار انصراف دهید، کنار بگذارید یا حساب خود را ببندید. اگر احساس امنیت نمی‌کنید، کنار گذاشتن انتخابی معقول است. | If you are in Iran, or anywhere else where taking part may be risky, please read this note before you join. Declared: Hamyar does not try to work out where you are, and it shows this note to every new member. ¶ Taking part may carry personal risk, depending on where you are, what the law says there, and what the services you use allow. Hamyar cannot judge this for you and gives no legal advice. ¶ • Hamyar is pseudonymous, not anonymous. Declared: we collect as little as we can. We do not promise that nobody can identify you. • Anything you write in a job, a report or an appeal may be read by people we do not control. Do not include your name, your contacts or anything that could identify you or another person. • Anything saved on your device, such as drafts, can be seen by anyone who can use or inspect that device. You can clear it at any time. • Hamyar does not ask or advise you to get around any restriction or to break any service's terms. If a service is not available or not allowed for you, do not use it. • Declared: Hamyar does not show where members are, and it does not require an identity document. • You may decline any cell, stop, or close your account at any time. If you do not feel safe, stopping is a reasonable choice. | needs human and legal review |

### 11.51.D Open license, declared not guaranteed, credit is not money

| key | FA | EN | review status |
| --- | --- | --- | --- |
| `copy.license.downstream_uncontrolled.title` | مجوز باز: استفادهٔ بعدی از نتیجه‌ها خارج از کنترل است | Open license: downstream use is uncontrolled | needs human and legal review |
| `copy.license.downstream_uncontrolled.body` | نتیجهٔ کارهایی که با مجوز باز منتشر می‌شوند را هر کسی می‌تواند کپی، بازاستفاده و اقتباس کند، برای هر استفاده‌ای که آن مجوز اجازه می‌دهد؛ حتی استفاده‌هایی که همیار اعلام یا تأیید نکرده است. ¶ • اعلام‌شده: درخواست‌دهنده هدف و مجوز را اعلام می‌کند. هدف اعلام‌شده، درخواست‌دهنده و خود همیار را مقید می‌کند، نه کسانی را که بعدها نتیجهٔ منتشرشده را می‌خوانند. • اعلام‌شده: همیار برای هیچ نتیجه‌ای ادعای مالکیت ندارد. با مشارکت، ادعاهای شخصی خودتان را همان‌طور که در شرایط مشارکت‌کنندگان آمده است کنار می‌گذارید. • همیار نمی‌تواند ببیند یا جلوگیری کند که پس از انتشار با متن منتشرشده چه می‌شود. | Results of jobs published under an open license can be copied, reused and adapted by anyone, for any use that the license allows, including uses that Hamyar did not declare or approve. ¶ • Declared: a requester declares a purpose and a license. The declared purpose binds the requester and Hamyar itself, not the people who later read an open result. • Declared: Hamyar claims no ownership of any result. By taking part you give up your own claims, as described in the contributor terms. • Hamyar cannot see or stop what happens to openly published text after it is published. | needs human and legal review |
| `copy.license.downstream_uncontrolled.chip` | مجوز باز: هر کسی می‌تواند از آن استفاده کند | Open license: anyone may reuse this | needs human and legal review |
| `copy.declared.not_guaranteed.title` | اعلام‌شده، نه تضمین‌شده | Declared, not guaranteed | needs human and legal review |
| `copy.declared.not_guaranteed.body` | بسیاری از چیزها در همیار را افراد اعلام می‌کنند. درخواست‌دهنده هدف، مجوز و حساسیت کار را اعلام می‌کند. مشارکت‌کننده گزارش می‌دهد که نتیجه را کدام سرویس و مدل ساخته است. بازبین در یک تاریخ اعلام می‌کند که یک قالب یا سرویس بازبینی شده است. ¶ • اعلام‌شده: همیار این اعلام‌ها را تا جایی که از نظر فنی ممکن است بررسی می‌کند. با این حال، اعلام، تضمین نیست و همیار نمی‌تواند آنچه را که بیرون از همیار رخ می‌دهد ببیند. • اعلام‌شده: زمان‌هایی که برای تکمیل کار اعلام می‌شود، بازه‌هایی بر پایهٔ ظرفیت اندازه‌گیری‌شده است و وعدهٔ تکمیل فوری یا قطعی نیست. • اعلام‌شده: عددهای منتشرشده همان‌هایی است که در تاریخِ نمایش‌داده‌شده اندازه‌گیری شده‌اند. ممکن است تغییر کنند و تغییرشان از پیش در سابقهٔ تغییرات اعلام می‌شود. | Many things in Hamyar are declared by people. A requester declares the purpose, license and sensitivity of a job. A volunteer reports which service and model produced a result. A reviewer declares, on a date, that a template or a service has been reviewed. ¶ • Declared: Hamyar checks these declarations as far as is technically possible. A declaration is still not a guarantee, and Hamyar cannot observe what happens outside Hamyar. • Declared: quoted times are windows based on measured capacity. They are not a promise of instant or certain completion. • Declared: published numbers are those measured on the date shown. They can change, with advance notice in the change log. | needs human and legal review |
| `copy.declared.window_quote` | بازهٔ اعلام‌شده: حدود {window}. این بازه بر پایهٔ ظرفیت اندازه‌گیری‌شده است و تضمین نیست. | Declared window: about {window}. This is based on measured capacity and is not a guarantee. | needs human and legal review |
| `copy.declared.reported_service` | سرویس و مدل را مشارکت‌کننده گزارش کرده است و راستی‌آزمایی نشده است. | The service and model are reported by the volunteer and have not been verified. | needs human and legal review |
| `copy.credit.not_money.title` | اعتبار، پول نیست | Credit is not money | needs human and legal review |
| `copy.credit.not_money.body` | اعتبار در همیار واحد حسابِ کارهایی است که بررسی و پذیرفته شده‌اند. اعتبار پول نیست، دارایی نیست و حقِ وعده‌داده‌شده‌ای هم به شمار نمی‌رود. ¶ • اعلام‌شده: اعتبار فقط با انجام کار جابه‌جا می‌شود. نه خرید و فروش می‌شود، نه مستقیم برای عضو دیگری فرستاده می‌شود و نه با پول مبادله می‌شود. • اعلام‌شده: اعتبار تاریخ انقضا دارد و هر موجودی تاریخ‌های انقضای خود را نشان می‌دهد. اعتبارِ حاصل از کار {credit_lifetime_days} روز ماندگار است، مگر آنکه قوانین با اطلاع قبلی در سابقهٔ تغییرات عوض شوند. • اعلام‌شده: قیمت هر کار پیش از تأیید درخواست‌دهنده نشان داده می‌شود و کار فقط وقتی پذیرفته می‌شود که ظرفیت اعلام‌شده اجازه بدهد. • همیار دربارهٔ اینکه قانون با اعتبار چگونه رفتار می‌کند هیچ ادعایی ندارد. | Credit in Hamyar is a unit of account for work that has been checked and accepted. It is not money, not property and not a promised entitlement. ¶ • Declared: credit moves only through completed work. It is not bought or sold, it is not sent directly to another member, and it is not exchanged for money. • Declared: credit expires, and each balance shows its expiry dates. Credit earned by work lasts {credit_lifetime_days} days, unless the rules change with advance notice in the change log. • Declared: the price of a job is shown before the requester confirms, and a job is accepted only when the declared capacity allows it. • Hamyar makes no statement about how any law treats credit. | needs human and legal review |
