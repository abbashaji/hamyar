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

### 11.51.E Prompt-injection advice, decline, report and rejection

| key | FA | EN | review status |
| --- | --- | --- | --- |
| `copy.injection.advice.title` | پیش از زدن دکمهٔ ارسال | Before you press Send | needs human and legal review |
| `copy.injection.advice.body` | متنی که می‌خواهید کپی کنید حاوی داده‌هایی از یک شخص ناشناس است که درون یک قالب بازبینی‌شده قرار گرفته است. متنِ افراد ناشناس ممکن است دستورهایی داشته باشد که برای هدایت شما یا گفتگوی شما نوشته شده‌اند. ¶ • برای هر سلول کار یک گفتگوی تازه و تمیز شروع کنید. • هر جا که سرویس اجازه می‌دهد، حافظه و برنامه‌ها یا ابزارهای متصل را برای آن گفتگو خاموش کنید. • اگر چیزی غیرعادی به نظر می‌رسد، متن کامل درخواست را باز کنید و بخوانید. • تنها کار شما این است: متن را کپی کنید، ارسال را بزنید و متن پاسخ را برگردانید. اگر متن چیز دیگری از شما خواست، مثلاً باز کردن پیوند، دانلود فایل، اجرای کد، نصب چیزی یا دادن گذرواژه، انجامش ندهید و سلول کار را گزارش کنید. • اعلام‌شده: همیار ورودی‌ها را بازبینی می‌کند و نتیجه‌های مشکوک را علامت می‌زند. این کار خطر را کم می‌کند، اما از بین نمی‌برد. | The text you are about to copy contains data from a stranger, placed inside a reviewed template. Text from strangers can include instructions meant to steer you or your chat. ¶ • Use a new, clean chat for each cell. • Where the service lets you, turn off memory and connected apps or tools for that chat. • If anything looks unusual, expand and read the full prompt. • Your only job is to copy the prompt, press Send and paste back the text of the answer. If the text asks for anything else, such as opening a link, downloading a file, running code, installing something or sharing a password, do not do it, and report the cell. • Declared: Hamyar reviews inputs and flags suspicious results. This reduces the risk but does not remove it. | needs human and legal review |
| `copy.injection.clean_chat_hint.default` | گفتگوی تازه‌ای شروع کنید. اگر این سرویس حافظه یا برنامهٔ متصل دارد، برای این گفتگو آن‌ها را خاموش کنید. | Start a new chat. If this service has memory or connected apps, turn them off for this chat. | needs human and legal review |
| `copy.moderation.decline_explainer` | می‌توانید از هر سلول کار انصراف دهید. اعلام‌شده: انصراف جریمه ندارد، بر سطح اعتماد شما اثر نمی‌گذارد و زمان انتظاری هم ایجاد نمی‌کند. سلولِ منصرف‌شده به صف برمی‌گردد تا شخص دیگری آن را انجام دهد. اعلام‌شده: همیار تعداد انصراف‌ها را فقط برای فهمیدن اینکه کدام کارها باید بهتر شوند می‌شمارد. | You can decline any cell. Declared: declining has no penalty, does not affect your trust level and adds no waiting time. A declined cell returns to the queue for someone else. Declared: Hamyar counts declines only to learn which jobs need improving. | needs human and legal review |
| `copy.moderation.report_explainer` | اگر سلولی ناامن به نظر می‌رسد، چیزی بیشتر از کپی، ارسال و بازگرداندن متن می‌خواهد، به نظر می‌رسد اطلاعات شخصی دارد یا به هر شکل دیگری ایراد دارد، آن را گزارش کنید. ¶ • اعلام‌شده: یک بازبین هر گزارش را می‌بیند. هدف اعلام‌شده برای نخستین بررسی {report_triage_sla_days} روز است. • اعلام‌شده: درخواست‌دهنده نمی‌فهمد چه کسی گزارش داده است. • اعلام‌شده: گزارش‌ها تا {moderation_days} روز پس از رسیدگی نگه داشته می‌شوند و بعد به شمارش‌های کلی تقلیل می‌یابند. | Report a cell if it looks unsafe, asks for more than copying, pressing Send and returning text, seems to contain personal data, or is wrong in some other way. ¶ • Declared: a reviewer looks at every report. The declared target for a first look is {report_triage_sla_days} days. • Declared: the requester does not learn who reported. • Declared: reports are kept for {moderation_days} days after they are resolved, then reduced to counts. | needs human and legal review |
| `copy.moderation.rejection_explainer` | نتیجه‌ای که رد‌شده باشد اعتباری نمی‌آورد. اعلام‌شده: دلیل رد را می‌بینید و تا {appeal_window_days} روز می‌توانید درخواست بازبینی بدهید. بازبینی را کسی انجام می‌دهد که تصمیم اول را نگرفته است. | A rejected result earns no credit. Declared: you can see the reason, and you can ask for a review within {appeal_window_days} days. A reviewer who did not make the first decision looks at it. | needs human and legal review |

### 11.51.F Recovery key, consent and opt-in

| key | FA | EN | review status |
| --- | --- | --- | --- |
| `copy.identity.recovery_key_warning.title` | همین حالا کلید بازیابی خود را ذخیره کنید | Save your recovery key now | needs human and legal review |
| `copy.identity.recovery_key_warning.body` | این کلید تنها راه بازگرداندن هویت شما در همیار است، اگر این دستگاه یا اطلاعات آن را از دست بدهید. ¶ • این کلید فقط یک‌بار و همین‌جا نشان داده می‌شود. اعلام‌شده: همیار نسخه‌ای از آن نگه نمی‌دارد که بتواند دوباره به شما نشان دهد. • هرکس این کلید را داشته باشد می‌تواند هویت شما را تصاحب کند و اعتبار شما را خرج کند. آن را به کسی ندهید و برای کسی نفرستید. اعلام‌شده: تیم همیار هرگز آن را نمی‌خواهد. • آن را در جای امنی نگه دارید که با شرایط خودتان سازگار باشد. هر کسی که به محل نگهداری دسترسی داشته باشد می‌تواند نسخهٔ ذخیره‌شده را پیدا کند. • اگر آن را گم کنید، همیار نمی‌تواند هویت شما را برایتان بازگرداند. • اعلام‌شده: پس از بازیابی، هویتِ بازیابی‌شده تا {recovery_cooldown} نمی‌تواند کار شروع کند یا اعتبار خرج کند. این یک محدودیت برای جلوگیری از سوءاستفاده است. | This key is the only way to get your Hamyar identity back if you lose this device or its data. ¶ • It is shown once, here. Declared: Hamyar does not keep a copy that it can show you again. • Anyone who has this key can take over your identity and spend your credit. Do not share it, and do not send it to anyone. Declared: the Hamyar team never asks for it. • Keep it somewhere safe that fits your own situation. A saved copy can be found by anyone who can reach the place where you saved it. • If you lose it, Hamyar cannot restore your identity for you. • Declared: after a recovery, the recovered identity cannot start jobs or spend credit for {recovery_cooldown}. This is an abuse limit. | needs human and legal review |
| `copy.identity.recovery_key_warning.confirm` | کلید بازیابی‌ام را ذخیره کرده‌ام و می‌دانم همیار نمی‌تواند آن را برایم بازگرداند. | I have saved my recovery key. I understand that Hamyar cannot restore it for me. | needs human and legal review |
| `copy.consent.join.title` | پیش از عضویت | Before you join | needs human and legal review |
| `copy.consent.join.intro` | لطفاً یادداشت‌های بالا را بخوانید. هر کادر را فقط اگر برای شما درست است علامت بزنید. برای ادامه، همهٔ کادرها لازم است. | Please read the notes above. Tick each box only if it is true for you. You need all of them to continue. | needs human and legal review |
| `copy.consent.join.risk_ack` | یادداشت دربارهٔ خطر برای حساب‌های خودم را خوانده‌ام. می‌دانم ممکن است سرویسی حساب من را محدود یا مسدود کند و خودم تصمیم می‌گیرم که مشارکت کنم یا نه. | I have read the note on risks to my own accounts. I understand that a service may limit or suspend my account, and I decide for myself whether to take part. | needs human and legal review |
| `copy.consent.join.privacy_ack` | آنچه همیار جمع‌آوری می‌کند و آنچه نمی‌تواند وعده دهد را خوانده‌ام. می‌دانم همیار «با نام مستعار» است، نه «ناشناس». | I have read what Hamyar collects and what it cannot promise. I understand that Hamyar is pseudonymous, not anonymous. | needs human and legal review |
| `copy.consent.join.safety_ack` | یادداشت دربارهٔ ایمنی شخصی را خوانده‌ام. خودم تصمیم می‌گیرم که مشارکت برای من ایمن است یا نه. | I have read the note on personal safety. I decide for myself whether it is safe for me to take part. | needs human and legal review |
| `copy.consent.join.credit_ack` | می‌دانم اعتبار پول یا دارایی نیست، تاریخ انقضا دارد و زمان‌ها و عددهای اعلام‌شده تضمین نیستند. | I understand that credit is not money or property, that it expires, and that declared times and numbers are not guarantees. | needs human and legal review |
| `copy.consent.join.waiver` | ادعای شخصی خودم را نسبت به نتیجه‌هایی که ارسال می‌کنم، همان‌طور که در شرایط مشارکت‌کنندگان آمده است، کنار می‌گذارم. می‌دانم نتیجه‌های دارای مجوز باز را هر کسی می‌تواند دوباره استفاده کند. | I give up any claim of my own over the results I submit, as described in the contributor terms. I understand that openly licensed results can be reused by anyone. | needs human and legal review |
| `copy.consent.join.no_circumvention_ack` | می‌دانم همیار از من نمی‌خواهد محدودیتی را دور بزنم یا شرایط استفادهٔ سرویسی را نقض کنم، و نباید از سرویسی که برای من در دسترس یا مجاز نیست استفاده کنم. | I understand that Hamyar does not ask me to get around any restriction or to break a service's terms, and that I should not use a service that is not available or not allowed for me. | needs human and legal review |
| `copy.consent.join.age_confirmation` | تأیید می‌کنم که دست‌کم {min_age_years} سال دارم. | I confirm that I am at least {min_age_years} years old. | needs human and legal review |
| `copy.consent.join.continue` | موافقم و ادامه می‌دهم | Agree and continue | needs human and legal review |
| `copy.consent.optin.defaults_note` | اعلام‌شده: به‌طور پیش‌فرض فقط سلول‌هایی به شما نشان داده می‌شود که برای استفادهٔ شخصی یا انتشار باز هستند و داده‌های عمومی یا غیرحساس دارند. هر زمان می‌توانید انتخاب‌هایتان را عوض کنید. تغییرها بر سلول‌هایی که هنوز باز نکرده‌اید اعمال می‌شود. | Declared: by default you are shown only cells for personal use or open publication that use public or non-sensitive data. You can change your choices at any time. Changes apply to cells you have not opened yet. | needs human and legal review |
| `copy.consent.optin.sensitive_topic` | سلول‌هایی با این موضوع به من نشان داده شود: {topic}. ممکن است محتوای سخت یا ناراحت‌کننده داشته باشند. اعلام‌شده: این گزینه به‌طور پیش‌فرض خاموش است و هر زمان می‌توانید خاموشش کنید. | Show me cells on this topic: {topic}. They may contain difficult material. Declared: this is off by default, and you can turn it off at any time. | needs human and legal review |
| `copy.consent.optin.locked_purpose` | این نوع استفاده هنوز باز نشده است. اعلام‌شده: برای هر سرویس فقط پس از بازبینی شرایط آن باز می‌شود و تغییر در سابقهٔ تغییرات اعلام می‌شود. | This use is not open yet. Declared: it opens for a service only after that service's terms have been reviewed, and the change is announced in the change log. | needs human and legal review |

### 11.51.G No circumvention and offline drafts

| key | FA | EN | review status |
| --- | --- | --- | --- |
| `copy.policy.no_circumvention.title` | بدون دور زدن محدودیت‌ها | No circumvention | needs human and legal review |
| `copy.policy.no_circumvention.body` | اعلام‌شده: همیار هرگز از کسی نمی‌خواهد و به کسی توصیه نمی‌کند که محدودیت منطقه‌ای یا فنی را دور بزند یا شرایط استفادهٔ یک سرویس را نقض کند. ¶ • اعلام‌شده: هر سرویس فقط پس از آن در همیار به کار می‌رود که یک بازبین شرایط آن را ثبت کرده باشد. • اعلام‌شده: همیار راهکار دور زدن محدودیت‌ها را منتشر نمی‌کند و نمی‌تواند در مشکل‌هایی که از این کار پیش می‌آید کمک کند. • اگر سرویسی برای شما در دسترس نیست، یا برای شما یا برای کاری که می‌خواهید با آن بکنید مجاز نیست، از آن استفاده نکنید. پرسش دربارهٔ آنچه یک سرویس اجازه می‌دهد را باید از خود آن سرویس و از مشاورهٔ حقوقی صلاحیتدار پرسید. | Declared: Hamyar never asks or advises anyone to get around a regional or technical restriction, or to break the terms of a service. ¶ • Declared: a service is used in Hamyar only after a reviewer has recorded its terms. • Declared: Hamyar does not publish tips for getting around limits, and cannot help with problems that come from doing so. • If a service is not available to you, or not allowed for you or for what you would do with it, do not use it. Questions about what a service allows are for that service and for qualified legal advice. | needs human and legal review |
| `copy.offline.draft_local_only` | اعلام‌شده: متنی که چسبانده‌اید فقط روی همین دستگاه ذخیره می‌شود، تا وقتی که ارسال را بزنید، یا زمانِ سلول کار تمام شود، یا {draft_ttl}، هر کدام زودتر باشد. هر کسی که بتواند از این دستگاه استفاده کند آن را می‌بیند. همین حالا می‌توانید آن را پاک کنید. | Declared: your pasted text is saved only on this device, until you press Submit, until the cell's time runs out, or for {draft_ttl}, whichever comes first. Anyone who can use this device can see it. You can clear it now. | needs human and legal review |
| `copy.offline.submit_queued` | شما آفلاین هستید. ارسال شما روی همین دستگاه منتظر مانده است. اعلام‌شده: اگر زمان سلول کار تمام نشده باشد، با برگشتن اتصال فرستاده می‌شود. هنوز پذیرفته نشده است. | You are offline. Your submission is waiting on this device. Declared: if the cell's time has not run out, it will be sent when the connection returns. It has not been accepted yet. | needs human and legal review |

## 11.52 Where each notice appears, placeholders and the declared-claim register

**Usage map** [D]

| Notice group (keys) | Where it appears | Rule |
| --- | --- | --- |
| `copy.safety.iran_notice.*`, `copy.risk.account_notice.*`, `copy.privacy.pseudonymity_notice.*`, `copy.credit.not_money.*`, `copy.declared.not_guaranteed.*`, `copy.license.downstream_uncontrolled.body`, `copy.policy.no_circumvention.*` | The join page, in this order (safety first), displayed in full, not collapsed; then the consent keys | Static, readable without JavaScript and before an identity exists (S11.49) |
| `copy.consent.join.*` | Below the notices on the join page | Every box starts unticked; all are required; no box is hidden or collapsed; the continue button stays focusable and explains what is missing (S11.48) |
| `copy.identity.recovery_key_warning.*` | Immediately after the identity is created, before any other screen, and again from settings | The confirm box gates leaving the screen |
| `copy.injection.advice.*` | The cell card, one tap away, and mandatory expansion on first use (FD§5.5); the help page | `copy.injection.clean_chat_hint.default` is the target of `adapter.clean_chat_hint_key` (S0.8.3) when an entry sets no hint of its own |
| `copy.moderation.decline_explainer`, `copy.moderation.report_explainer` | Next to the decline and report buttons of the cell card; the help page | |
| `copy.moderation.rejection_explainer` | On every rejected-result screen and the appeal screen | |
| `copy.license.downstream_uncontrolled.chip` and `.body` | The cell card of every open-publication cell; the requester job form where an open license is declared; the results download page | FD§5.7 failure mode 3: the card and the job form must say so |
| `copy.declared.window_quote` | The quote screen of the requester wizard | |
| `copy.declared.reported_service` | The provenance view and the manifest page | |
| `copy.risk.service_review_line` | The cell card, next to the service | |
| `copy.consent.optin.*` | Opt-in settings | |
| `copy.offline.*` | Beside the paste-back box | |
| All of the above except the cell-level keys | The public notices page, both languages side by side, each notice with a stable anchor, reachable from every footer | Readable without login, without JavaScript, and offline once loaded |

The keys above are not API error texts. API errors use their own `copy.*` keys through `details.copy_key` (S0.11) and follow the same rules.

**Placeholder registry** [D] (every placeholder in the table of S11.51; a placeholder with no row here is a build error)

| Placeholder | Type | Source |
| --- | --- | --- |
| `{review_date}` | date | date of the latest `service.approved` event of the registry entry [A] |
| `{ip_hash_ttl_days}` | number | `retention.ip_hash_ttl_days` |
| `{job_payload_days}` | number | `retention.job_payload_days` |
| `{moderation_days}` | number | `retention.moderation_days` |
| `{report_triage_sla_days}` | number | `report.triage_sla_days` |
| `{appeal_window_days}` | number | `appeal.window_days` |
| `{credit_lifetime_days}` | number | the member's effective lifetime: `credit.lifetime_days`, or `credit.lifetime_days_accelerated` for a member assigned to the accelerated-expiry arm (S12.*, S13.*) |
| `{recovery_cooldown}` | duration | `identity.recovery_cooldown_s` |
| `{draft_ttl}` | duration | `ui.draft.ttl_s` |
| `{window}` | duration | the quoted completion window of the job (S6.*) |
| `{topic}` | topic | display name of a `TopicCategory` (stored as a `{fa, en}` pair) |
| `{min_age_years}` | number | `identity.min_age_years` (requested of S10.*, `ISS-119`); the age line is rendered only when the value is greater than 0 |

**Declared-claim register** [D]. A notice may say only what the system does. Each promise-like claim below names what makes it true; a row marked [V] is a dependency on another part that must be confirmed there before the notice is approved.

| Claim in the notices | Made true by | Status |
| --- | --- | --- |
| Identity is a device-made public key, no name | `MemberKey`, no password (S0.6); S10.* | consistent with S0 |
| Only keyed hashes of device and network identifiers, kept `retention.ip_hash_ttl_days`; never a raw network address | S0.6 hashing table; `retention.raw_ip_stored` constant false; build milestone `BM4` acceptance | consistent with S0 |
| Job and result text deleted `retention.job_payload_days` after the job ends; hashes and manifests remain | S0.7 retention class `job_bound` | consistent with S0 |
| An e-mail address is stored only if the member adds it | `identity.email_optional` constant true; the storage form is S10.* | [V] S10.* |
| No service password or session stored; chat page never read | No feature of the spec does either (ground rule 3) | consistent with the spec |
| The member presses Send every time | Ground rule 3; S9.* | consistent with the spec |
| Location is not shown | `public.location_display` = `never` | consistent with S0 |
| No third-party trackers or cookies | `analytics.third_party_trackers`, `analytics.cookies_enabled` constants false; bearer tokens, no cookies (S0.11) | consistent with S0 |
| Requesters never see who completed a cell | `vol_` handles are never shown to requesters (S0.6) | consistent with S0 |
| A service is offered only after a reviewer recorded its terms and saved a copy | Approval guard (S0.8.3, S0.9.6); S7.* | consistent with S0 |
| Declining has no penalty and does not affect the trust level | `lease.decline_cooldown_s` constant 0; trust tiers move only on reliability evidence (S0.9.4); S8.* MUST NOT count declines in reliability | [V] S8.* |
| A reviewer looks at every report; first look target; retention then counts only | `report.triage_sla_days`; S0.7 class `moderation`; S10.* | [V] S10.* |
| A different reviewer decides an appeal; the window | S0.9.7 guard; `appeal.window_days` | consistent with S0 |
| Credit moves only through completed work; is not bought, sold or sent directly | S0.8.5 entry types contain no member-to-member entry; `grant.non_transferable` | consistent with S0 |
| Credit expires and balances show expiry dates | `credit.lifetime_days`; S6.*, S11 screens | consistent with S0 |
| A price is shown before confirmation; a job is accepted only when declared capacity allows | Quote and admission flow (S6.*) | consistent with S0 |
| Recovery cooldown | `identity.recovery_cooldown_s` | consistent with S0 |
| The Hamyar team never asks for the recovery key | Operating procedure of the team | [V] operator, recorded in the launch checklist (S14.*) |
| Hamyar keeps no copy of the recovery key that it could show again | Recovery key design (S10.*) | [V] S10.* |
| Defaults of opt-ins; sensitive topics off by default | `optin.default_*`; `optin.sensitive_topics_default` constant false | consistent with S0 |
| Locked purposes open only after a terms review and a change-log entry | Rules `R5`, `R6`, `R10` (S0.8.4) | consistent with S0 |
| Inputs are reviewed and suspicious results are flagged | Screening and quarantine (S9.*) | [V] S9.* |
| Published numbers carry the measurement date; changes with advance notice | `change.notice_days_default`; public change log (S12.*) | consistent with S0 |
| The safety note is shown to every new member and Hamyar does not infer location | S11.51.C; S0.6 (no IP-derived location) | consistent with this part |
| Hamyar does not publish tips for getting around limits | Editorial rule; the copy checks of S11.50 | consistent with this part |
| Drafts stay on the device for the stated time | S11.49; `ui.draft.ttl_s` | consistent with this part |
| Opt-in changes apply to cells not yet opened | Rule `R8`; the lease-time opt-in check (S8.*) | [V] S8.* |

## 11.53 Persian quality, terminology and the review procedure

The Persian must be correct, natural written Persian, not a word-for-word rendering of the English. [D]

**Orthography and typography** [D]

- Standard written Persian in Iranian orthography, polite register (`شما`), no slang and no machine translation as a final text.
- ZWNJ (U+200C) in verb prefixes (`می‌کند`, `نمی‌کند`), before plural and comparative suffixes (`سلول‌ها`), in compounds (`اعلام‌شده`, `مشارکت‌کننده`, `جمع‌آوری`). The ezafe after a final he is written with the combining hamza above (U+0654), as in the FD Persian summary (`بازهٔ زمانی`); after a final vowel it is a yeh (`گفتگوی شما`).
- Persian yeh and kaf (`ی`, `ک`), never the Arabic forms; Persian punctuation `، ؛ ؟ « »`; no space before punctuation; no Latin letters inside Persian sentences except an allowlisted token (`IP`) in the middle of a sentence.
- Hamyar's name is `همیار`; it is not transliterated in Persian text.

**Terminology** (one term per concept in both languages; the table is the glossary source for S20.*) [D][A]

| English | Persian | Note |
| --- | --- | --- |
| cell | سلول کار | as in the FD Persian summary |
| job | کار | a large job: `کار بزرگ` |
| credit | اعتبار | never `توکن` (tokens are not the unit, FD§4.1) |
| capacity commons | مشترک ظرفیت | public descriptor (FD§0.3) |
| Commons Reserve | ذخیرهٔ مشترک | |
| volunteer, donor | مشارکت‌کننده | |
| requester | درخواست‌دهنده | |
| reviewer | بازبین | |
| operator | گردانندهٔ سامانه | [V] reviewer preference |
| service (an AI chat service) | سرویس | |
| account | حساب | |
| template | قالب | |
| prompt | متن (پرامپت) | first mention as shown, then `متن` or `متن کامل` |
| Send (the service's button) | ارسال | |
| decline | انصراف | not `رد`, which means reject |
| report | گزارش | |
| appeal | درخواست بازبینی | chosen over `اعتراض` because it sounds neutral [A] |
| rejected, accepted | رد‌شده، پذیرفته‌شده | |
| recovery key | کلید بازیابی | |
| pseudonymous, anonymous | با نام مستعار، ناشناس | the two are never mixed up |
| declared | اعلام‌شده | the required word of S11.50 |
| guarantee | تضمین | only in negated sentences |
| opt-in | انتخاب | |
| change log | سابقهٔ تغییرات | |
| provenance | شجره (provenance) | as in the FD Persian summary |
| ledger | دفتر کل | |
| lease | مهلت | |
| escrow | سپرده | [V] reviewer preference |
| quoted window | بازهٔ زمانی اعلام‌شده | |
| open license | مجوز باز | |
| downstream use | استفادهٔ بعدی | |

**Review procedure** [D]

1. The author writes the English first, as the source of meaning for counsel, and writes the Persian natively from the meaning, not from the English words.
2. A native-speaking reviewer for Persian and one for English each go through the checklist below and are recorded in `reviewed.fa_by` and `reviewed.en_by`; status becomes `human_reviewed`.
3. The notices are rendered on real phones in both locales and checked against S11.42 to S11.46 (this is also the G2 item on RTL rendering, FD§8.3).
4. A person qualified to advise on safety reads the safety and privacy-limits keys (FD§8.3 G1); counsel in the operator's jurisdiction reads all keys, the contributor waiver, and the declared-claim register [V]. Their memo reference goes into `reviewed.legal_ref`; status becomes `legal_reviewed`.
5. Two distinct admins sign off; status becomes `approved`. The launch rule that depends on this is in S11.57.
6. For the consent keys and the safety keys, a second native speaker who has not seen the English reads the Persian and says in their own words what it asks the member to accept; a mismatch returns the key to step 1 [A].
7. Any text change, in either language, resets both to `needs_human_and_legal_review` (S11.50). A change of a parameter that fills a placeholder goes through the parameter change log and the loosen-with-notice rule (`R10`, S0.8.4); it does not reset the copy, but the claim register row is re-read by the reviewer.

**Checklist** [D]

| Check | Question |
| --- | --- |
| Meaning | Does the Persian say what the English says, no more and no less? |
| Promise | Does every promise-like sentence say `اعلام‌شده`, and does no sentence promise what the claim register cannot support? |
| Register | Polite, plain, no jargon the target reader would not know (a first-use gloss where needed) |
| Terms | Every term as in the table above |
| Orthography | ZWNJ, ezafe, yeh and kaf, punctuation as above |
| Fear and blame | The safety and privacy texts neither scare nor reassure beyond the facts; no blame |
| Rendering | On a real phone: joined letters, ZWNJ pairs, digits, isolates, no boxes (S11.46) |
| Length | Fits its container at 200% zoom in both languages (S11.48) |

## 11.54 Acceptance criteria

Test cases are named here by acceptance id; S18.* assigns `T-*` ids and layers (`rtl`, `unit`, `e2e`, `load`, `inj`). Every item stays in CI once added (S0.12 ordering rule 5). [D]

| id | Given | When | Then |
| --- | --- | --- | --- |
| `AC-i18n-01` | a page in `fa` | it first paints, and then the member switches to `en` | `lang=fa dir=rtl` are set before first paint; after the switch `lang=en dir=ltr`, with no reload |
| `AC-i18n-02` | text typed in the paste-back box, an expanded prompt and a scrolled page | the language is switched | the text, the expansion, the scroll position and the focus are unchanged |
| `AC-i18n-03` | no stored locale and a browser list that starts with `en-GB` | the landing page loads | `en` is chosen and nothing about the list is sent to the server; with an empty list `fa` is chosen |
| `AC-i18n-04` | the style sources | the CI check runs | any physical-direction property or value outside the allowlist, or `row-reverse`, fails the build |
| `AC-i18n-05` | the icon sprite and a time chart in `fa` | rendered | every icon marked `mirror: true` is flipped and others are not; time runs from the inline start; the numeric axis is not mirrored |
| `AC-i18n-06` | `digits=persian` and a balance of 1234.5 credits | rendered | the display is one LTR isolate with Persian digits and Persian separators; with `digits=latin` it uses ASCII digits and `,` and `.` |
| `AC-i18n-07` | `digits=persian` and any screen that sends or exports data | a request or an export is produced | all numbers, amounts and dates in it are ASCII or ISO; no Persian digit and no Jalali string appears |
| `AC-i18n-08` | a numeric field | `۱۲۳` or `1٫5` is entered, and `1,5` is entered | the first two parse to ASCII values; `1,5` fails with the field code `number_format`; the parsed value is echoed before a credit-moving confirmation |
| `AC-i18n-09` | `digits=persian` and a prompt containing `2026`, `abc123` and `۱۲` | the card and the expanded prompt render | those characters are shown exactly as stored |
| `AC-i18n-10` | the golden table of boundary dates | the calendar library runs in CI | every row converts exactly, in both directions, for the required range |
| `AC-i18n-11` | `i18n.dual_calendar_detail` true | a detail view of an instant is opened in `fa` and in `en` | the primary calendar line, the other calendar line and the ISO line are shown, in that order |
| `AC-i18n-12` | the monthly mint cap period | it is shown in `fa` | it is labeled as a UTC month, not with a Jalali month name, with its start and end in the member's calendar and zone beside the UTC value |
| `AC-i18n-13` | a device zone and a settings override | times are shown | the override wins, and no request carries or derives a zone from an IP address |
| `AC-i18n-14` | a Persian paragraph starting with a Latin word, a code token and a dynamic service name | rendered in `fa` | the declared `lang` and `dir` apply where known, otherwise each paragraph resolves its own direction; code is an LTR isolate; the dynamic name is isolated and sentence punctuation sits correctly |
| `AC-i18n-15` | a prompt with ZWNJ, LRM, both digit sets and Persian text | it is copied, pasted back and submitted | clipboard text, submitted body and stored text are byte-equal to the stored prompt; no ZWNJ is lost; the prefill link falls back to copy-only when the encoded length exceeds `adapter.max_url_chars` |
| `AC-i18n-16` | a prompt containing U+202E | the expanded prompt and a result view render | the control is shown as a visible marker that is not in a copied range |
| `AC-i18n-17` | requester input and a submission containing U+202E, and others containing only ZWNJ and LRM | they are screened | the first two are flagged per `screen.bidi_control_action` (a submission is quarantined); the others are not flagged |
| `AC-i18n-18` | a production build | every screen is loaded with all other origins blocked | no request goes to another origin and no font comes from a third party; no screen has text inside a bitmap |
| `AC-i18n-19` | the subset font and a test page of joined words, a ZWNJ pair and Arabic-script text with a style rule | rendered | letters join correctly, the ZWNJ pair is not joined, and no `letter-spacing` or italic is applied |
| `AC-i18n-20` | a prompt with Kurdish and Urdu letters outside the subset, and the tallest Persian line | rendered | no empty boxes appear, and nothing is clipped |
| `AC-i18n-21` | every key of the copy tables and every screen | rendered in `en` | the same keys and screens exist; plurals take `one` and `other` forms |
| `AC-i18n-22` | a form with an invalid field | it is submitted | an error summary takes focus, links to the field, and shows the text of `details.copy_key`; meaning is never by color or emoji alone |
| `AC-i18n-23` | a keyboard only session in `fa` | the member tabs through a screen with a tab widget and a slider | every control is reachable and operable; ArrowLeft and ArrowRight follow the visual direction |
| `AC-i18n-24` | any screen | zoomed to 200% and at a 320 CSS pixel width, in both themes | no loss of content or function; contrast is at least 4.5:1 for text and 3:1 for controls |
| `AC-i18n-25` | a lease with `ui.lease.warn_remaining_s` configured | the countdown runs | assistive technology is told only at the warning time and at expiry, not every second |
| `AC-i18n-26` | a first-use prompt that is not expanded | the member tabs to Copy | it is focusable with `aria-disabled=true`, linked to its explanation, and expanding moves focus to the expanded text |
| `AC-i18n-27` | the build | the budget check runs | the compressed js, css and fonts, the first-load total and the card payload are at or below `ui.budget.*`; the first-interactive time on the test profile is at or below `ui.budget.first_interactive_s` |
| `AC-i18n-28` | the first-contribution flow in the harness | it runs on the test profile with other origins blocked | it completes, with no third-party request |
| `AC-i18n-29` | a draft and the network switched off | Submit is pressed, and the network returns | exactly one submission is accepted by the server; a retry of the same press replays the stored response; no submission happens before the press |
| `AC-i18n-30` | drafts in every state | the time-to-live passes, *clear local data* is pressed, or the identity is closed | the records are purged; the member key is not deleted by *clear local data* |
| `AC-i18n-31` | the copy files | the build runs | a missing key or placeholder mismatch in either language, a failed check of S11.50, or a placeholder with no registry row fails the build |
| `AC-i18n-32` | every key with `promise: true` | the declared check runs | `اعلام‌شده` is present in `fa` and `declared` in `en`; guarantee words occur only in allowlisted negated sentences |
| `AC-i18n-33` | an approved key | its Persian or English text is edited | its version increases, both languages return to `needs_human_and_legal_review`, and the hash in the manifest changes |
| `AC-i18n-34` | a request to set `launch.members_may_join` to true | any required key of S11.51 is not `approved` | the request is refused with `LAUNCH_GATE_CLOSED` |
| `AC-i18n-35` | a member accepts the consent boxes | the consent is recorded | the stored record holds `copy_key`, `copy_hash` and `accepted_at` for each box and no text; a hash that is in neither the current nor the previous manifest is refused |
| `AC-i18n-36` | the join page | it loads | all notices are shown in full in the order of S11.52, every box is unticked, and the continue button stays focusable and says what is missing |
| `AC-i18n-37` | a new member from any network | the join page is shown | the safety note appears for everyone, and no code path reads or derives a location |

## 11.55 Parameters introduced by this part

Names follow S0.10.1 (areas `i18n`, `ui`, `screen`, `identity`). Every default is an `initial configurable default` or a formula shown in the row; S16.* completes the rows without renaming (convention gap, `ISS-119` and the note after the issues table). Owner is `operator` except `screen.*`, which is `reviewer`. `Replaced by` uses the codes of S0.10.4. [D]

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `i18n.digits_default_en` | enum | `latin` | constant | `CON` |
| `i18n.calendar_default_fa` | enum | `jalali` | `jalali`, `gregorian` | `FND` |
| `i18n.calendar_default_en` | enum | `gregorian` | `jalali`, `gregorian` | `FND` |
| `i18n.week_start_fa` | enum | `saturday` [V] | `saturday`, `sunday`, `monday` | `FND` |
| `i18n.clock_24h` | bool | true | | `FND` |
| `i18n.first_visit_locale_from_browser` | bool | true | | `FND` |
| `ui.credit.display_decimals` | int | 2 | 0..6 | `P1M` interviews |
| `ui.ratio.display_decimals` | int | 3 (the FD§3.3 example shows 0.870) | 0..6 | `FND` |
| `ui.font.third_party_allowed` | bool | false | constant | `CON` |
| `ui.font.max_weights` | int | 2 | 1..4 | `TEC` |
| `ui.font.fa_stack` | string | `"Hamyar Sans", system-ui, "Segoe UI", Tahoma, sans-serif` | non-empty; ends with a generic family | `TEC` fallback check on real phones (G2) |
| `ui.budget.js_bytes` | int | 100,000 | 1..10,000,000 | `TEC` |
| `ui.budget.css_bytes` | int | 20,000 | 1..10,000,000 | `TEC` |
| `ui.budget.fonts_bytes` | int | 80,000 | 1..10,000,000 | `TEC` |
| `ui.budget.first_load_bytes` | int | 204,096 = 100,000 + 20,000 + 80,000 + 4,096 | at least js + css + fonts | `TEC` |
| `ui.budget.cell_card_bytes` | int | 16,096 = 4,000 x 3 + 4,096 | at least `cell.envelope.max_input_chars` x 3 | `CAL` envelope, then `TEC` |
| `ui.budget.repeat_view_bytes` | int | 65,248 = 16,096 + 32,768 + 16,384 | positive | `TEC` |
| `ui.budget.test_profile` | json | `{downlink_kbps: 400, rtt_ms: 400}` (a test input, not a claim about any network) | both positive | `TEC` |
| `ui.budget.first_interactive_s` | duration_s | 7 = `ceil(204,096 x 8 / 400,000 + 6 x 0.4)` | positive | `TEC` |
| `ui.draft.ttl_s` | duration_s | 3,600 | at least `lease.timeout_s + lease.max_extensions x lease.extend_s + lease.submit_grace_s` (1,200 + 600 + 120 = 1,920 with the defaults); at most 86,400 | `OPS` |
| `ui.lease.warn_remaining_s` | duration_s | 300 | 0 to `lease.timeout_s` | `CAL`, then `P1M` |
| `ui.a11y.min_target_css_px` | int | 44 | 24..64 | `TEC` |
| `ui.retry.max_attempts` | int | 5 | 1..20 | `OPS` |
| `ui.retry.base_delay_s` | duration_s | 2 | 1..30 | `OPS` |
| `ui.retry.max_delay_s` | duration_s | 60 | at least `ui.retry.base_delay_s`; at most 600 | `OPS` |
| `screen.bidi_control_action` | enum | `flag_for_review` | `reject`, `flag_for_review`, `ignore_display_only` | `P1M` incident log |
| `identity.min_age_years` | int | 0 (zero means the age line is not shown; a legal decision, `ISS-119`) | 0..99 | `CNS` |

Existing parameters used by this part: `i18n.default_locale`, `i18n.supported_locales`, `i18n.digits_default_fa`, `i18n.dual_calendar_detail`, `public.counter_refresh_s`, `lease.timeout_s`, `lease.max_extensions`, `lease.extend_s`, `lease.submit_grace_s`, `cell.envelope.*`, `retention.*`, `identity.recovery_cooldown_s`, `report.triage_sla_days`, `appeal.window_days`, `analytics.third_party_trackers`, `analytics.cookies_enabled`, `launch.min_signoffs`.

## 11.56 Assumptions and items to verify

**Assumptions [A] introduced by this part** (S3.* collects them; the right column is the owner decision that could overturn each)

| Assumption | Could be overturned by |
| --- | --- |
| Heading numbers of this file start at 11.40; issue ids `ISS-117` to `ISS-119` are used (S11.40) | the plan, at assembly |
| WCAG 2.2 level AA is the target, with the lease-timing deviation (S11.48) | the owner choosing another level, or a lower one for operator tools |
| `fa` defaults to Persian digits (S11.43) | the Phase 1 interview result |
| The clock is 24-hour in both locales (S11.44) | the owner or interview feedback |
| Public pages carry a `/fa/` or `/en/` path prefix (S11.41) | the stack decision in S4.* |
| Locale, digits, calendar and time zone live on the device, not on the server (S11.41) | a decision to sync preferences |
| The calendar range to validate is 2026-01-01 to 2040-12-31 (S11.44) | the longest horizon that S6.* decides |
| The copy review statuses and the manifest (S11.50) | `ISS-118` resolution |
| `appeal` is rendered `درخواست بازبینی` (S11.53) | the native-speaking reviewer |
| English is written first for counsel, no precedence clause is written (S11.47) | counsel |
| Hashed font files are cached as immutable; a service worker may cache the shell (S11.46, S11.49) | S10.* policy on service workers |
| Six round trips in the first-interactive formula (S11.49) | measurement on real networks (`TEC`) |
| Time axes run in reading direction (S11.42) | the interview read test, an [H] |
| The safety note is shown to every new member, not by location (S11.51.C) | the safety advisor (G1) |
| The `opt-in`, `escrow` and `operator` terms in Persian (S11.53) | the native-speaking reviewer |

**Items to verify [V]** (every inline [V] in this file maps to one row)

| What is verified | By whom | Where the answer is stored |
| --- | --- | --- |
| Persian wording, orthography and terminology of every notice, and the Persian names of months and weekdays | native-speaking reviewers | `reviewed` fields and review status of each copy key |
| Wording of the account-risk, credit, license, waiver and no-circumvention notices; declared-claim register; which language prevails | counsel in the operator's jurisdiction | counsel memo, referenced in `reviewed.legal_ref` |
| Safety and privacy-limit statements and the join-page order | a person qualified to advise on safety (FD§8.3 G1) | G1 `LaunchGateItem` evidence |
| Golden table of Jalali boundary dates and its source | a native-speaking reviewer | a CI fixture with its source reference |
| Platform support for `Intl` calendar and number formatting, data-saver signals, font metric overrides | an engineer on the target phones | G2 `LaunchGateItem` evidence |
| Font license, glyph coverage, redistribution and subsetting rights | a reviewer | license file and check date beside the font files |
| System fonts that render Persian on the target phones; Persian speech output | a tester on real devices | G2 evidence; accessibility statement |
| Whether the essential-limit exception applies to the lease timer | an accessibility auditor | accessibility statement |
| Week start and regional picker defaults | a native-speaking reviewer | `i18n.week_start_fa` and its change-log entry |
| Claims marked [V] in the declared-claim register (S8.*, S9.*, S10.*, operator procedure) | the owners of those parts and the operator | this file's register until closed, then S14.* launch items |

## 11.57 Requirements on other parts

Each row is a requirement that this part places on another part. If the owner of that part cannot meet it, they record an issue in their own block. [D]

| Part | Requirement |
| --- | --- |
| S4.* | Choose the calendar library to the requirement of S11.44; keep fonts behind the storage and host interface; decide the service-worker policy of S11.49 |
| S5.*, S7.*, S8.* | Member-visible human-authored strings are `{fa, en}` pairs or copy keys (S11.41); templates declare `lang` on slots and output fields (S11.45); comparators declare their `fold_fa` options; declines are never counted in reliability or trust (declared-claim register) |
| S9.* | Screen bidi controls per `screen.bidi_control_action` and quarantine flagged submissions; judge size and schema on the raw text, with no trimming (S11.45); lease responses carry `expires_at` and `server_time` (S11.49) |
| S10.* | Content security policy limited to the page and API origins; recovery key alphabet without ambiguous characters; *clear local data* versus key deletion (S11.49); e-mail storage form; validate consent hashes against the current and previous `copy_manifest`; no code path that derives location; add `identity.min_age_years` |
| S12.* | A public notices page (S11.52); weekly aggregates labeled as UTC weeks; share-card text follows S11.42 to S11.45; a change-log kind for notice text that changes a promise (`ISS-118`) |
| S13.* | Add to the Phase 1 interview guide: digits preference, time-axis read test, the terms `انصراف` and `درخواست بازبینی`, comprehension of the consent boxes |
| S14.* | Launch gate items: all required copy keys `approved` before `launch.members_may_join` can be true (`AC-i18n-34`); the G1 safety-note item; the G2 items for RTL rendering, accessibility pass and low-bandwidth budgets on real devices; the recovery-key procedure of the team |
| S15.* | Error bodies keep `details.copy_key` and carry no prose; no locale parameter; the consent write accepts `copy_key` and `copy_hash`; lease responses carry `server_time` |
| S16.* | Complete the parameter rows of S11.55 and the placeholder sources of S11.52 |
| S18.* | Number the acceptance ids of S11.54 as tests; state that simulation output is not evidence about human reading or reaction |
| S19.*, S20.*, S21.* | Risks: dependence on human and legal review of the notices, font license, device variation in Persian rendering; glossary from S11.53; the Persian summary uses the same terms |

## Issues raised

Problems and gaps found while writing this part. Each resolution is already applied in this file; C-001 consolidates them into S2.* and may record a different one. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-117` | minor | prompt | S0.4 gives a split part three issue sub-blocks and S0.13 gives no heading-number plan, but part 11 has at least four files, so a fourth file has no sub-block and its `S11.<m>` headings could collide with the other three | This file uses `ISS-117` to `ISS-119` and headings from `11.40`; the plan or C-001 assigns final blocks and numbers at assembly and updates references | proposed |
| `ISS-118` | major | FD§5.5, FD§9, prompt F | The FD requires explicit, informed opt-in (FD§9) and notices that change only in public, but S0 has no place to record which notice text a member accepted, no review state for legal text, and no change-log kind for notices | (a) `OptIn` rows of a new kind `consent` carry `copy_key`, `copy_hash`, `accepted_at` and no text; (b) a new enum `copy_review_status` (S11.50); (c) a `copy_manifest` shipped with each build; (d) a change-log entry kind `notice` for any approved text change that alters a promise | proposed |
| `ISS-119` | major | FD§5.3 (S3 includes minors' data), FD§8.3 | The FD keeps minors' data out of jobs but says nothing about a minimum age for members, and consent text normally needs one; setting it is a legal decision this spec cannot make | A parameter `identity.min_age_years`, default 0 (the age line `copy.consent.join.age_confirmation` is not rendered); counsel sets it [V]; also listed as an owner decision in S3.* | needs_owner |

Convention additions made by this part (not issues, listed so C-001 can fold them back): the parameters of S11.55 (names are new, no existing name is changed); the enum `copy_review_status` and the copy record of S11.50; the copy key groups of S11.51 beyond the example key of S0.5; the client-local draft states of S11.49 (explicitly not domain states); the `OptIn` kind `consent` and the change-log kind `notice` (`ISS-118`); the use of `fa` and `en` pairs for stored human-authored strings (S11.41).
