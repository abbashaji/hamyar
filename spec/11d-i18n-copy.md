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
