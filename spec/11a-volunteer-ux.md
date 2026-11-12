# 11. Volunteer, Requester, Reviewer and Operator experiences, Persian first

*Spec part 11a (file `spec/11a-volunteer-ux.md`) · owner cell C-013 · covers prompt scope F, volunteer experience. Requester, Reviewer and Operator screens are specified in the other S11 files. Written against `spec/00-conventions.md` (S0) and Founding Document draft v0.1 (FD). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law. All Persian text is a draft marked `needs_human_and_legal_review`.*

## 11.1 Scope, reading guide and hard exclusions

This file specifies every screen a volunteer (a member acting as `donor`) uses, mobile-first, with no install, Persian first (right-to-left) plus English. It covers: landing, the first-contribution flow, the cell card, copy and open-in-service, paste-back, result feedback, balance and expiry, history, opt-in settings, teams, share card, invite flow, recovery key handling, appeal, help, plus two supporting screens (report sheet; identity and display settings). [D]

- Screen ids are `SCR-vol-01`..`SCR-vol-17`; acceptance criteria are `AC-vol-nn` in Given / When / Then form; copy keys are `copy.<area>.<key>` with `fa` and `en` text (S0.5). API calls are written as operation names only; their paths, schemas and the final operation ids belong to S15.* (see 11.5). [D]
- Every wireframe is a text wireframe drawn in logical (reading) order. In `fa` the whole layout is mirrored by `dir="rtl"`; wireframes are not drawn twice. [D]
- Each screen section has the same blocks: purpose, entry conditions, wireframe, states (empty, loading, error, offline or low-bandwidth, blocked), actions, API calls, copy intent, accessibility notes, acceptance criteria. [D]
- Evidence tags follow S0.2. A number that is not derived is an `initial configurable default` and exists in the parameter table or is listed in 11.5.2 as a convention addition. [D]

**Hard exclusions: what no volunteer screen does** (ground rule 3; FD Principles 3, 8, 9). If a future feature would need any of these, it is excluded, not built. [D]

| # | The platform never... | How the design enforces it |
| --- | --- | --- |
| X1 | presses Send, submits, or types into a provider's page on the volunteer's behalf | The only hand-off artifacts are a clipboard copy and, where the registry says it is supported, a link the volunteer taps; the volunteer presses Send in the provider's own page |
| X2 | reads, scrapes, embeds (iframe), screenshots or observes the provider's chat page or tab | No iframe, no extension, no `window.open` handle that is read, no page-visibility inference of what happened in the other tab; the answer reaches Hamyar only by the volunteer pasting it |
| X3 | stores a provider credential, cookie, session, API key or chat link | No screen has a field for any of these; paste-back rejects nothing but also never asks for them; chat links are not requested |
| X4 | helps anyone bypass a regional or technical restriction | No screen mentions proxies, VPNs, alternative regions or accounts; a service unavailable to the volunteer is simply not chosen |
| X5 | reads the clipboard in the background | The clipboard is read only inside a tap handler on the optional `Paste` button (11.10); never on focus, load, visibility change or timer [V: browser support and permission prompts on the target phones] |
| X6 | asks the volunteer to do more than copy, press Send and return text | Card copy and help say exactly this; any prompt that asks otherwise is rejected upstream by `R3` and can be reported by the volunteer |
| X7 | shows a member id, an e-mail, a location, or another member's handle | Only the volunteer's own aggregates are shown; teams show aggregates and the volunteer's own row (11.15) |

## 11.2 Decisions in this part

| # | Decision | Reason | Tag |
| --- | --- | --- | --- |
| V-01 | One single-page web app, one front-end origin, works in a mobile browser with no install; "add to home screen" is allowed but never promoted | FD§3.2 step 1, FD§10 item 8 | [D] |
| V-02 | Default locale is `fa` (`i18n.default_locale`), full RTL; `en` is one tap away from every screen; locale is stored on the device only | FD§10; minimal collection (FD Principle 8) | [D] |
| V-03 | Display digits (`latin` or `persian`) and calendar (`jalali` or `gregorian`) are device-local display options; detail views show both calendars (`i18n.dual_calendar_detail`) | FD§10; S0.6.2 | [D] |
| V-04 | The card shows eight fixed fields and one provenance sentence on every cell, in both locales, before any other control | FD§5.5 | [D] |
| V-05 | The full prompt is always one tap away; expansion is a UI gate (copy and open are disabled until expanded) when the server returns at least one `expand.*` reason; "can see" is enforced, "has read" is not claimed | FD§0.1 item 7, FD§5.5 | [D] |
| V-06 | A decline is one tap, has no penalty, no cooldown (`lease.decline_cooldown_s` = 0) and no confirmation dialog | FD§5.5 | [D] |
| V-07 | The platform cannot observe the Send press or the provider's answer, so the "under 60 seconds" figure is measured on the server as `submission.received` minus `lease.issued`, and is a hypothesis, not a promise | FD§3.2, FD§6.2 V1, X2 | [D][H] |
| V-08 | Prefill ("Open in service") is offered only when the registry entry says it is supported, the URL fits, and `prefilled_link_use` is `yes`; otherwise the screen is copy-only | S0.8.3, FD§10 caution | [D][V] |
| V-09 | The recovery key is shown once, after the first accepted cell, not before it, so the 60-second path is not blocked; a visible "key not saved" marker stays until the member confirms the key | Stake before first accepted cell is at most 0 credit; FD§3.2 step 1 | [D][H] |
| V-10 | Feedback after paste-back is asynchronous by design: the answer can be `accepted`, `rejected` with a reason code, or waiting for a second check; the volunteer is never told a cell was a hidden check before it is decided | FD§4.4 | [D] |
| V-11 | No streaks, no streak loss, no daily-goal nag, no countdown to "lose" anything except a visible credit expiry date | FD§6.1 rank 4, FD§8.2 RISK-15 | [D] |
| V-12 | No push notifications and no e-mail by default; status is pulled in the app | Data minimization; `identity.email_optional` | [D] |
| V-13 | Sharing and team features are off unless their flags are on (`ff.growth.v3_share_card`, `ff.growth.v4_teams`, `ff.growth.v5_referral`) and are never shown in the first-contribution flow | FD§6.2, FD Principle 8 | [D] |
| V-14 | All help, notices and error copy is bundled with the app and works offline; no copy is fetched from a third party | FD§8.2 RISK-14; prompt I | [D] |
| V-15 | Prompts and outputs are rendered as inert text only; nothing the volunteer sees from a job is parsed as HTML, Markdown or a link | Prompt E result return; FD§5.5 | [D] |

## 11.3 Screen inventory and navigation

| Id | Screen | Reached from | Section |
| --- | --- | --- | --- |
| `SCR-vol-01` | Landing | Public URL; invite link | 11.6 |
| `SCR-vol-02` | First-contribution flow (orchestrates 03, 04, 05, 06 and the notices) | Landing primary action | 11.7 |
| `SCR-vol-03` | Cell card (offer list and card detail) | Home after sign-in; flow step 3 | 11.8 |
| `SCR-vol-04` | Hand-off: copy and open in service | Card | 11.9 |
| `SCR-vol-05` | Paste-back | Hand-off | 11.10 |
| `SCR-vol-06` | Result feedback | Paste-back; History | 11.11 |
| `SCR-vol-07` | Balance and expiry | Header credit chip | 11.12 |
| `SCR-vol-08` | History | Menu | 11.13 |
| `SCR-vol-09` | Opt-in settings | Menu; card ("why am I seeing this") | 11.14 |
| `SCR-vol-10` | Teams | Menu when `ff.growth.v4_teams` is on | 11.15 |
| `SCR-vol-11` | Share card | Result feedback; menu, when `ff.growth.v3_share_card` is on | 11.16 |
| `SCR-vol-12` | Invite flow | Menu | 11.17 |
| `SCR-vol-13` | Recovery key handling (save, restore) | Result feedback; marker; landing "I already have an identity" | 11.18 |
| `SCR-vol-14` | Appeal | History; suspension or ban banner | 11.19 |
| `SCR-vol-15` | Help | Menu; every error state | 11.20 |
| `SCR-vol-16` | Report sheet | Card; Result feedback; History | 11.21 |
| `SCR-vol-17` | Identity and display settings (language, digits, calendar, device link, key rotation, close account) | Menu | 11.21 |

```
Landing 01 --(Start)--> Flow 02 --> [notice, once] --> Offer list 03
Offer list 03 --(Take)--> Card detail 03 --(expand if required)--> Hand-off 04 --> Paste-back 05 --> Feedback 06
Card detail 03 --(Decline)--> Offer list 03            Card detail 03 --(Report)--> Report 16
Feedback 06 --(first accepted cell)--> Recovery key 13 --> (optional) Share 11 / Invite 12
Header: credit chip -> Balance 07 | menu -> History 08, Opt-ins 09, Teams 10, Invite 12, Help 15, Settings 17
History 08 --(rejected cell)--> Appeal 14      Any error state --> Help 15 (anchored topic)
```

## 11.4 Global UI rules

### 11.4.1 Shell [D]

- Mobile-first single column. Header: wordmark, language switch (`فا | EN`), credit chip (balance, tap opens `SCR-vol-07`), key marker (only while the key is unsaved, opens `SCR-vol-13`), menu. Footer: Help.
- One primary action per screen, placed at the thumb end. Destructive or irreversible actions (close account, create a new recovery key) are never the primary action and always need a confirmation that states the consequence.
- Touch targets at least 44 x 44 CSS px [A: design assumption verified on real phones in G2, measurement `TEC`]. Desktop uses the same layout, centred, with a maximum reading width.
- No modal dialogs for reading content; sheets are used for short confirmations only. Back navigation always works and never loses a lease or a pasted draft.

### 11.4.2 Locale, numerals and calendars [D]

| Setting | Values | Default | Where stored | Applies to |
| --- | --- | --- | --- | --- |
| `locale` | `fa`, `en` | `i18n.default_locale` (`fa`) | device | all UI chrome and copy; `dir` = `rtl` for `fa`, `ltr` for `en` |
| `digits` | `latin`, `persian` | `i18n.digits_default_fa` (`persian`) for `fa` [A][H], `latin` for `en` | device | numbers in UI chrome only (balances, counts, dates, countdowns) |
| `calendar` | `jalali`, `gregorian` | `jalali` for `fa`, `gregorian` for `en` | device | every date in the UI; detail views show both |

- Digit conversion never touches prompt text, pasted output text, recovery keys, ids, hashes or codes (they are content or secrets, not chrome). [D]
- Dates come from the server as RFC 3339 UTC; conversion to Jalali uses platform calendar support where present, otherwise a bundled arithmetic fallback (S0.6.2) [V: platform support on target phones]. The server never receives a Jalali string. [D]
- Every countdown shows the server-provided end time converted for display and a relative duration; the relative duration is computed from the server `expires_at` minus the server time given in the same response, never from the device clock alone (S0.6.2). [D]

### 11.4.3 Mixed-direction content (prompts, outputs, keys) [D]

- Prompt and output blocks are rendered as text nodes inside a container with `dir="auto"` evaluated per paragraph; the container itself takes the page direction only for its chrome (border, copy button). Code fences and recovery keys are forced `dir="ltr"` with `unicode-bidi: isolate`.
- Copy buttons copy the exact byte sequence of the prompt string as issued by the server. The client inserts no left-to-right or right-to-left marks, no zero-width characters, no digit conversion, no trimming, no normalization. Test: the copied string hashes to the `prompt_hash` of the lease (`T-rtl-nn`, S18.*).
- Inline fragments of the other direction inside chrome copy (a template name in Latin inside a Persian sentence, an id) are wrapped in an isolating element so punctuation does not flip.
- Pasted-back text is shown back to the volunteer exactly as typed, with the same per-paragraph direction rule, before submit.

### 11.4.4 Fonts and third-party resources [D]

- No mandatory third-party CDN, font host, analytics, tracker or social SDK (`analytics.third_party_trackers` = false, `analytics.cookies_enabled` = false). Fonts are bundled: a Persian-capable open-licensed text face plus a system fallback stack [V: font choice and its license, checked by a human]. If a resource fails to load, text renders in the fallback and the screen stays usable.
- Reachability of the host from Iran is [V] (G2, RISK-14); the app is built so the API host and static host can differ and move (S4.*).

### 11.4.5 Accessibility [D][V]

Target: WCAG 2.2 level AA [V: a human conformance audit before launch]. Every screen section below adds screen-specific notes; these rules are global:

- Text contrast and focus indicators meet AA in light and dark system themes; no information by color alone (every status has an icon shape and a word).
- Full keyboard operation; logical focus order follows reading order in both directions; focus moves to the heading of a new screen and to the first error of a failed form.
- Live regions (`aria-live="polite"`) announce lease time warnings, submission outcome and errors; `assertive` is never used for countdowns.
- Countdowns are not an exam: the screen reader reads the remaining time on request and at thresholds, not every second. Extending the lease (11.10) is always one action.
- Respect reduced-motion and larger-text settings; layout survives text scaled to twice the default.
- Persian screen-reader behavior of Latin fragments is tested (`T-rtl-nn`).

### 11.4.6 Low bandwidth and offline [D]

| Condition | Behavior |
| --- | --- |
| Slow link | The shell, all copy and help are static assets; screens render before data arrives; lists load one page (`api.page_size_default`); no image is required for any step; the share card image is generated on the device |
| First-load weight | Budget is `ui.first_load_budget_bytes` (11.5.2), replaced by measurement `TEC` |
| Offline at load | Shell and help render from the local copy; screens that need data show the offline state with a retry; no data is invented |
| Offline during a lease | The prompt already on the device stays usable (copy still works); paste-back keeps the draft; Submit retries with the same `Idempotency-Key` when the link returns; the server decides whether the lease is still valid (`lease.timeout_s`, `lease.submit_grace_s`) |
| Flaky link on submit | The client retries with the same `Idempotency-Key`; a replay returns the stored outcome and creates nothing new (S0.11.5) |
| Data saver | No automatic polling; the status screens show a "Check again" button, and polling uses backoff only while the screen is open |

### 11.4.7 Global states and error mapping [D]

Every API failure maps to a screen state and a `details.copy_key`-style copy key (S0.11.3). The client never shows `message` text.

| Error code | HTTP | Screen state | Copy key | Next action offered |
| --- | --- | --- | --- | --- |
| `AUTH_EXPIRED`, `AUTH_REQUIRED` | 401 | Silent re-sign-in with the device key; if no key on this device, restore screen | `copy.error.session_restore` | Restore (`SCR-vol-13`) |
| `LAUNCH_GATE_CLOSED` | 403 | Blocked: not open yet | `copy.error.not_open_yet` | See public status; no sign-up form |
| `KILL_SWITCH_ENGAGED` | 503 | Blocked: paused | `copy.error.paused` | Wait; see public status |
| `FORBIDDEN` (member `suspended` or `banned`) | 403 | Blocked: account notice | `copy.error.account_blocked` | Appeal (`SCR-vol-14`) |
| `RATE_LIMITED` | 429 | Blocked: slow down, with the `Retry-After` time | `copy.error.rate_limited` | Wait; nothing is lost |
| `UNAVAILABLE`, `INTERNAL`, no network | 503, 500 | Offline or error with retry | `copy.error.try_again` | Retry; drafts kept |
| `LEASE_EXPIRED` | 410 | Lease lost | `copy.error.lease_expired` | Back to offers |
| `LEASE_CONFLICT` | 409 | Cell taken by someone else | `copy.error.cell_taken` | Back to offers |
| `STATE_CONFLICT` | 409 | Stale view | `copy.error.refresh` | Refresh the screen |
| `IDEMPOTENCY_IN_PROGRESS` | 409 | Still working (no visible error) | none | Automatic retry after `Retry-After` |
| `PAYLOAD_TOO_LARGE` | 413 | Field error on paste-back | `copy.paste.too_large` | Shorten or split; see help |
| `VALIDATION_FAILED` | 400 | Field errors from `details.fields` | per field | Fix and resubmit |
| `CAP_EXCEEDED` | 422 | At cap | `copy.balance.at_cap` | See balance |
| `NOT_FOUND` | 404 | Item gone | `copy.error.not_found` | Back |

### 11.4.8 What the device holds [D][A]

| Item | Where | Lifetime | Note |
| --- | --- | --- | --- |
| Member private key (signing) | Device storage, non-extractable where the platform allows [V] | Until the member closes the identity or rotates the key | Clearing site data loses it; the recovery key (11.18) is the only remedy |
| Session token | Device storage | `session.member_idle_ttl_s` idle, `session.member_abs_ttl_s` absolute | No cookies (S0.11.4) |
| Display options | Device storage | Until changed | locale, digits, calendar |
| Active lease data (prompt, nonce, `expires_at`) | Memory, with a best-effort copy in session storage | Until submit, decline or expiry | Session storage access is always wrapped in try and catch |
| Paste-back draft | Memory and session storage | Until submit or tab close | Never uploaded before Submit |
| Never held | Provider credentials, chat links, clipboard history, the provider's page content | n/a | X1..X7 |

## 11.5 API operation names and parameters this part uses

### 11.5.1 Operation names [A]

Names only. Paths, bodies and final ids are owned by S15.*; where S15.* renames one, this part follows the rename and nothing else changes. Resource shapes follow S0.11.1 (for example the lease is created by a `POST` on a cell's leases sub-resource).

| Operation | Used by | Purpose |
| --- | --- | --- |
| `getPublicStatus` | 01 | Launch state, public counter (when `ff.growth.v2_live_counter` is on), approved-service count |
| `createMember` | 02 | Create the identity; carries the public key and, if present, an invite token |
| `createSession` | all | Sign a challenge with the device key |
| `getMember` | all | Status, `trust_tier`, restriction end, key-saved flag |
| `listOffers` | 03 | Card summaries the member may lease, already filtered by `R8` opt-ins |
| `createLease`, `getLease`, `extendLease`, `releaseLease` | 03, 04, 05 | Lease, read, extend once, decline or release |
| `acknowledgePrompt` | 03 | Record that the full prompt was expanded (11.8.4) |
| `submitResult`, `getSubmission` | 05, 06 | Paste-back and outcome |
| `listCellHistory` | 08 | Member's cells and outcomes |
| `getBalance`, `listCreditLots`, `listMemberLedgerEntries` | 07 | Balance, lots with expiry, own entries |
| `getOptIns`, `updateOptIns`, `listTopicCategories`, `listApprovedServices` | 09, 04 | Opt-in model and service list |
| `createReport` | 16 | Report a cell |
| `createAppeal`, `getAppeal`, `listAppeals`, `withdrawAppeal` | 14 | Appeals |
| `createInvite`, `listInvites`, `revokeInvite`, `getReferralStatus` | 12 | Invites and referral state |
| `createTeam`, `getTeam`, `joinTeam`, `leaveTeam` | 10 | Teams |
| `getShareCard` | 11 | Aggregate data for the card |
| `startRecovery`, `completeRecovery`, `rotateRecoveryKey`, `confirmRecoveryKey` | 13 | Recovery |
| `createDeviceLinkCode`, `redeemDeviceLinkCode`, `rotateMemberKey`, `closeMember` | 17 | Device linking, rotation, closure |

### 11.5.2 Parameters this part reads, and additions [A]

Read (all exist in S0.10.6): `lease.timeout_s`, `lease.max_active_per_member`, `lease.max_extensions`, `lease.extend_s`, `lease.submit_grace_s`, `lease.decline_cooldown_s`, `cell.envelope.expected_time_s`, `cell.envelope.max_input_chars`, `cell.envelope.max_output_chars`, `cell.envelope.max_submission_bytes`, `ui.card.expand_required_first_use`, `ui.comprehension_check_rate`, `ui.fast_contribution_threshold_s`, `i18n.*`, `optin.*`, `credit.lifetime_days`, `credit.expiry_notice_days`, `credit.member_cap_credits`, `grant.*`, `trust.*`, `identity.*`, `invite.*`, `growth.referral.*`, `team.*`, `appeal.window_days`, `appeal.max_per_decision`, `appeal.reviewer_sla_days`, `report.max_per_member_per_day`, `report.triage_sla_days`, `retention.job_payload_days`, `public.location_display`, `api.page_size_default`.

Convention additions requested by this part (C-022 completes the table; names are binding once added):

| Name | Type | Initial configurable default | Validation | Replaced by |
| --- | --- | --- | --- | --- |
| `ui.first_load_budget_bytes` | int | 204,800 | 20,000..5,000,000 | `TEC` measurement on real phones and links |
| `ui.offer_list_size` | int | 3 (equals the default of `lease.max_active_per_member`) | 1..`api.page_size_max` | `P1M` |
| `ui.recovery_confirm_groups` | int | 2 | 1..8 | `SEC` |
| `ui.status_poll_max_s` | duration_s | 60 (upper bound of the polling backoff) | 5..600 | `OPS` |
| `appeal.reason_max_chars` | int | 1000 | 100..10000 | `OPS` |
| `invite.required_to_join` | bool | true (closed Phase 1 pilot, FD§9) | | `FND` |

## 11.6 SCR-vol-01 Landing

**Purpose.** Explain in one screen what Hamyar is, what the volunteer does and the risks they take, and get them to the first contribution without sign-up. [D]

**Entry conditions.** Public URL, an invite link (`#invite=<token>` in the URL fragment, never sent to analytics), or a returning visitor with no valid session. A visitor with a valid session goes straight to the offer list (`SCR-vol-03`).

**Wireframe**

```
+--------------------------------------------------+
| Hamyar (fa wordmark)               [FA | EN] [=] |
+--------------------------------------------------+
| H1  One minute a day. Reviewed tasks. Your own    |
|     account. You press Send.                      |
| P   What you do: copy a task, press Send in the   |
|     chat service you already use, paste the answer|
|     back. Verified answers earn expiring credit.  |
| [ Start: about 2 minutes the first time ] (primary)|
| ( I already have an identity )  (secondary link)  |
+--------------------------------------------------+
| What Hamyar never does   (4 icon+word rows)       |
|  - never presses Send for you                     |
|  - never reads your chat or asks for passwords    |
|  - never asks you to bypass any limit or rule     |
|  - never shows your identity to anyone            |
+--------------------------------------------------+
| Risks to you, in plain words (collapsed, 1 line)  |
|  > Your provider's terms and your country's rules |
|    may limit this. Read before you start.         |
+--------------------------------------------------+
| Live counter (only if ff.growth.v2_live_counter): |
|  N verified cells   (verified only; hidden if off)|
| Footer: Help | Privacy | Public ledger (if on)     |
+--------------------------------------------------+
```

**States**

| State | Condition | Behavior |
| --- | --- | --- |
| Empty | Not applicable (static content) | The page never depends on data to be useful |
| Loading | `getPublicStatus` in flight | Static content and primary action render at once; the counter area shows a placeholder, never a spinner over the whole page |
| Error | `getPublicStatus` fails | Counter area omitted silently; the rest is unchanged |
| Offline or low bandwidth | No network | Static shell from the local copy if previously loaded; a first-ever visit shows the browser's own offline page (unavoidable); the primary action is disabled with `copy.landing.offline` |
| Blocked: not open | `launch.members_may_join` = false (`LAUNCH_GATE_CLOSED`) | Primary action replaced by a notice `copy.landing.not_open`; no member is created; an existing member can still sign in to see balance and history [D] |
| Blocked: join by invite only | `invite.required_to_join` = true and no invite token | Primary action opens the invite-code field (`copy.landing.invite_needed`); no identity is created without a valid token |
| Blocked: paused | `kill.all_new_jobs` or `kill.all_minting` engaged | Landing is unchanged; the offer list shows the paused state (11.8) |

**Actions**

| Action | Result |
| --- | --- |
| Start | Enters `SCR-vol-02`; the identity is created at flow step F2, not here |
| I already have an identity | Opens `SCR-vol-13` restore mode, or signs in silently if this device holds a key |
| Language switch | Changes `locale` on this device only |
| Expand risks | Shows the full risk notice (`copy.risk.provider_and_law`) |

**API calls.** `getPublicStatus`.

**Copy intent.** Plain, calm, short. State the human-presses-Send model and the "never" list before any benefit claim. No claim of anonymity (promise minimization, never anonymity, FD Principle 8), no claim about speed of completion, no political framing (FD§6.1 rank 2). The counter line says "verified cells" and nothing else.

| Copy key | `fa` (draft) | `en` |
| --- | --- | --- |
| `copy.landing.headline` | یک دقیقه در روز، کارهای بازبینی‌شده، حساب خودِ شما. دکمهٔ ارسال را شما می‌زنید. | One minute a day. Reviewed tasks. Your own account. You press Send. |
| `copy.landing.never_list` | همیار هرگز به جای شما ارسال نمی‌کند، صفحهٔ گفت‌وگوی شما را نمی‌خواند، رمز نمی‌خواهد، و هیچ‌وقت شما را به دور زدن محدودیت‌ها تشویق نمی‌کند. | Hamyar never presses Send for you, never reads your chat, never asks for passwords, and never encourages you to bypass any limit. |
| `copy.landing.not_open` | همیار هنوز برای عضویت باز نیست. | Hamyar is not open for new members yet. |

All keys carry `needs_human_and_legal_review`.

**Accessibility.** One `h1`; the primary action is the first focusable element after the language switch; the "never" list is a real list; the risk disclosure is a `details` element that works without scripts.

**Acceptance criteria**

- `AC-vol-01` Given `launch.members_may_join` is false, When a visitor opens the landing, Then the primary action is replaced by `copy.landing.not_open` and no `createMember` call is possible from the UI.
- `AC-vol-02` Given the visitor's locale is unset, When the landing loads, Then it renders `fa` with `dir="rtl"` and Persian numerals, and the language switch shows `EN` as one tap.
- `AC-vol-03` Given `ff.growth.v2_live_counter` is off, When the landing loads, Then no counter, number of members or number of active members is rendered or requested.
- `AC-vol-04` Given the network is unavailable after a previous visit, When the landing loads, Then the shell, headline, never-list and risk notice render from the local copy and the primary action is disabled with `copy.landing.offline`.
- `AC-vol-05` Given the landing is loaded, When network requests are inspected, Then no request goes to a third-party host and no cookie is set.

## 11.7 SCR-vol-02 First-contribution flow (the sub-60-second path)

**Purpose.** Take a newcomer from landing to a pasted-back first result with the fewest screens, in about 2 minutes the first time and under 60 seconds once practiced (FD§3.2 step 2). Both figures are hypotheses [H]. [D]

**Entry conditions.** `launch.members_may_join` true; invite token present when `invite.required_to_join` is true; at least one approved service and at least one offerable Commons cell exist, otherwise the flow stops at the empty state (below).

**Step list and time budget.** Budgets are hypothesis targets [H] to be replaced by server-measured timings (measurement `CAL` in Phase 0, `P1M` in Phase 1). The flow's success metric is `submission.received` minus `flow_started` and the share at or under `ui.fast_contribution_threshold_s` (`initial configurable default` 60, FD§6.2 V1). `flow_started` is the event `member.created` for a first-time member and the `lease.issued` of the first lease for a returning member.

| Step | Screen | Volunteer action | First-time budget [H] | Practiced budget [H] | Stakes before the step |
| --- | --- | --- | --- | --- | --- |
| F1 | Landing | Tap Start | 3 s | 0 s (returning members skip it) | none |
| F2 | Identity created | None (automatic): device key generated, `createMember`, `createSession` | 2 s | 0 s | no personal data; no key shown yet (V-09) |
| F3 | One-time notice | Read three short facts, tap "I understand" (shown once; version-stamped) | 10 s | 0 s | none |
| F4 | Offer list | Tap the first card (`ui.offer_list_size` offers) | 5 s | 3 s | none |
| F5 | Card | Read the 8-field card; expand the full prompt (required on first use) | 20 s | 5 s | decline is free |
| F6 | Hand-off | Tap Copy (or Open in service) | 3 s | 3 s | none |
| F7 | Provider page | Paste, press Send, wait for the answer, copy it (outside Hamyar; time depends on the provider) | 60 s [H] | 25 s [H] | volunteer's own account |
| F8 | Paste-back | Return, tap Paste (or long-press paste), tap Submit | 10 s | 8 s | none |
| F9 | Feedback | See "received, being checked" and later the outcome | 2 s | 2 s | none |
| | | **Sum** | **115 s** (about 2 minutes) | **46 s** | |

The sums are plain arithmetic of the columns (3 + 2 + 10 + 5 + 20 + 3 + 60 + 10 + 2 = 115; 0 + 0 + 0 + 3 + 5 + 3 + 25 + 8 + 2 = 46). They are targets that make the claim testable, not measurements. Step F7 dominates and is outside the platform's control and observation (X2). [H]

**Wireframe (progress strip shown on F3..F9)**

```
+--------------------------------------------------+
| (*)--(*)--( )--( )--( )   Step 2 of 5: The card   |
+--------------------------------------------------+
|  (content of the current screen: 03, 04, 05, 06)  |
+--------------------------------------------------+
| [ primary action ]            ( Decline this one )|
+--------------------------------------------------+
```

Five visible steps: Notice, Card, Hand-off, Paste-back, Done. Identity creation is not a visible step.

**One-time notice (F3), copy intent.** Exactly three facts and one button: (1) you use your own account and press Send yourself; (2) the text you copy comes from a stranger, was reviewed, can be read in full, and any task may be declined; (3) your provider's terms and your country's rules may limit this, which is your decision [V]. No checkbox wall. The notice version is stored with the member; a changed version is shown again once.

| Copy key | `fa` (draft) | `en` |
| --- | --- | --- |
| `copy.notice.first_use` | ۱) از حساب خودتان استفاده می‌کنید و خودتان دکمهٔ ارسال را می‌زنید. ۲) متنی که کپی می‌کنید از طرف یک ناشناس است؛ بازبینی شده و همهٔ آن را می‌توانید بخوانید و هر کاری را رد کنید. ۳) شرایط سرویس شما و قوانین کشورتان ممکن است این کار را محدود کند؛ تصمیم با شماست. | 1) You use your own account and press Send yourself. 2) The text you copy comes from a stranger; it was reviewed, you can read all of it, and you may decline any task. 3) Your provider's terms and your country's rules may limit this; the decision is yours. |

**States**

| State | Condition | Behavior |
| --- | --- | --- |
| Empty | `listOffers` returns no offers | `copy.flow.no_offers`: no work fits your opt-ins or nothing is queued right now; actions: "Review opt-ins" (`SCR-vol-09`), "Check again"; nothing is lost |
| Loading | Identity creation or `listOffers` in flight | Progress strip with a text label; never a blocking spinner longer than `ui.status_poll_max_s` without a retry button |
| Error | `createMember` fails | Retry with the same `Idempotency-Key`; the device key is kept so a retry never creates two members; after a failed retry, show Help |
| Offline or low bandwidth | No network at F2 | Flow pauses with `copy.error.try_again`; nothing is created locally except the key pair |
| Blocked: rate limited | `ratelimit.device_new_members_per_day` or tree limit (`RATE_LIMITED`) | `copy.error.rate_limited` with the time; no reason is given about which limit applied (abuse-safe) |
| Blocked: no approved service | `listApprovedServices` empty | `copy.flow.no_service`: contributions are not available yet; no cell is offered (launch-gate machinery, S14.*) |

**Actions.** Start, I understand, Take this card, Decline, Back (never destroys a lease), Cancel flow (releases the lease with no penalty).

**API calls.** `createMember`, `createSession`, `getMember`, `listApprovedServices`, `listOffers`, then those of 11.8 to 11.11.

**Accessibility.** The progress strip is a labeled ordered list with `aria-current="step"`; each step change moves focus to the new heading and announces it; the whole flow works with one hand and with the keyboard.

**Acceptance criteria**

- `AC-vol-06` Given a visitor with a valid invite and the gate open, When they tap Start, Then a `Member` is created with `status` = `active` and `trust_tier` = `new`, no e-mail is asked, and no recovery key screen blocks the next step.
- `AC-vol-07` Given a first-time member at F3, When they tap "I understand", Then the notice version is stored and the notice is not shown again until its version changes.
- `AC-vol-08` Given the flow is complete, When `submission.received` is stored, Then the elapsed time between `member.created` and `submission.received` is recorded server-side and the share of durations at or under `ui.fast_contribution_threshold_s` is available to metrics (S13.*); the UI states no such figure to the volunteer.
- `AC-vol-09` Given no offers match the member's opt-ins, When F4 loads, Then `copy.flow.no_offers` is shown with a link to `SCR-vol-09` and no card is fabricated.
- `AC-vol-10` Given `createMember` times out and is retried with the same `Idempotency-Key`, When the first request had succeeded, Then exactly one `Member` exists and the UI continues as if once.

## 11.8 SCR-vol-03 Cell card (offer list and card detail)

### 11.8.1 Purpose and entry [D]

Show, before any prompt is copied, who asked for what under which declarations, so that the volunteer can decide to take, decline or report. The offer list shows up to `ui.offer_list_size` card summaries; the card detail is the full card of one leased cell. Entry: signed-in member with `status` = `active`.

### 11.8.2 Offer list wireframe

```
+--------------------------------------------------+
| Tasks for you (3)                                |
+--------------------------------------------------+
| +----------------------------------------------+ |
| | Template: Translation with glossary    ~2 min | |
| | P1 | L2 | S0 | service: any approved (M0)     | |
| | [ Take ]                                     | |
| +----------------------------------------------+ |
| (two more summaries)                             |
| Why am I seeing these?  -> Opt-ins (SCR-vol-09)  |
+--------------------------------------------------+
```

The list is filtered server-side by `R8` (opt-ins cover purpose, sensitivity, license, service, topic); the client never filters on its own to hide a mismatch and never shows a cell the server did not offer. A summary shows the card fields in abbreviated form; `Take` calls `createLease` and opens the card detail. [D]

### 11.8.3 Card detail wireframe and fields

```
+--------------------------------------------------+
| < Back                      lease time left 18:40|
+--------------------------------------------------+
| 1 Purpose      P1  Open publication               |
| 2 License      L2  Open license with attribution  |
|                    (anyone may reuse the result)  |
| 3 Sensitivity  S0  Public material                |
| 4 Service      M0  Any approved service you choose|
| 5 Template     Translation with glossary  v3      |
| 6 Expected     about 2 min                        |
| 7 Category     default | topic: general           |
| 8 Credit       +1 credit when accepted            |
+--------------------------------------------------+
| A stranger asked for this; the text below was     |
| reviewed by a reviewer on {date, both calendars}  |
+--------------------------------------------------+
| v Read the full prompt (required)                 |
|   [expanded: full prompt text, dir=auto, scroll]  |
|   length: 1,842 characters                        |
+--------------------------------------------------+
| [ Copy prompt ]  [ Open in service ]  (SCR-vol-04)|
| ( Decline )                      ( Report )       |
+--------------------------------------------------+
```

Field definitions [D]:

| # | Field | Source | Display rule |
| --- | --- | --- | --- |
| 1 | Purpose | `purpose` of the job | Code plus plain name from `copy.taxonomy.purpose.<code>` |
| 2 | License | `license` | Code plus name; for `L1` and `L2` adds "anyone may reuse the result" (FD§5.7 failure mode 3; "downstream use uncontrolled") |
| 3 | Sensitivity | `sensitivity` | Code plus name; only `S0` or `S1` can appear in Phases 1-2 (S0.8.1) |
| 4 | Service | `service_requirement`, plus for `M1` the pinned service names from the registry | `M0` says the volunteer chooses and that the choice is recorded |
| 5 | Template | `TemplateVersion` name and version | Always with the version |
| 6 | Expected time | `cell.envelope.expected_time_s` | Rounded up to whole minutes; labeled "expected", never "takes" [H] |
| 7 | Category | Opt-in category of the cell (default, or a non-default purpose, license, service or topic category) | Drives the expansion rule (11.8.4) |
| 8 | Credit | 1 credit when accepted | Says "when accepted"; never "you will earn" |
| 9 | Lease time left | `expires_at` of the lease | Visible countdown with an extend action (11.10) |

**Provenance line (fixed sentence) [D].** `copy.card.provenance`: `fa` «یک ناشناس این را خواسته است؛ متن زیر در تاریخ {date} توسط یک بازبین بررسی شده است.» and `en` "A stranger asked for this; the text below was reviewed by a reviewer on {date}." `{date}` is the template version's approval date in the member's calendar, the other calendar in the detail view. The sentence is exactly one sentence, is never shortened away, and is not a promise about quality or safety. Wording `needs_human_and_legal_review`.

### 11.8.4 Mandatory expansion rules [D]

The server decides; the client enforces display. `createLease` returns `expand_required` as a list of reasons (empty means not required):

| Reason code | Condition | Source |
| --- | --- | --- |
| `expand.first_use_of_template` | This member has never acknowledged this `Template` (any version) | FD§5.5; `ui.card.expand_required_first_use` = true (constant) |
| `expand.new_template_version` | The `TemplateVersion` differs from the one last acknowledged | [A]: a new version is new text |
| `expand.non_default_purpose` | `purpose` not in `optin.default_purposes` | FD§5.5 |
| `expand.non_default_sensitivity` | `sensitivity` not in `optin.default_sensitivities` | FD§5.5 |
| `expand.non_default_license` | `license` not in `optin.default_licenses` [A] | FD§5.5 |
| `expand.non_default_service` | `service_requirement` not in `optin.default_service_requirements` [A] | FD§5.5 |
| `expand.sensitive_topic` | Topic category with `optin.sensitive_topics_default` = false (opt-in only) | FD§5.4 R8 |
| `expand.comprehension_check` | Selected at random with probability `ui.comprehension_check_rate` (default 0.00) [H] | FD§5.7 failure mode 6 |

Pseudocode:

```
function cardGate(card, expand_required, ui_state):
    # expanded = the prompt text was rendered and its container scrolled to the end
    if expand_required is empty:
        copy_enabled = true
        open_enabled = card.adapter.prefill_allowed
    else:
        copy_enabled = ui_state.expanded
        open_enabled = ui_state.expanded and card.adapter.prefill_allowed
    if ui_state.expanded and not ui_state.ack_sent:
        call acknowledgePrompt(lease_id, reasons_covered = expand_required)   # idempotent
        ui_state.ack_sent = true
    decline_enabled = true      # always
    report_enabled  = true      # always
```

Rules:

- Expanded means the full prompt text was rendered and the scroll container reached its end (or the prompt fits without scrolling). `acknowledgePrompt` records that the prompt was displayed, not that it was read; copy never says "you confirmed you read it" (FD§0.1 item 7: "can see" is enforced, "has read" is not). [D]
- When the rule applies and the prompt is collapsed, Copy and Open are disabled with the visible reason `copy.card.expand_first`, so a keyboard or screen-reader user finds the reason next to the disabled control. Decline and Report are never disabled. [D]
- For `expand.comprehension_check`, the card asks one multiple-choice question about the card's own fields (for example "What is the purpose of this task?"); a wrong answer re-shows the card and never penalizes the member, never reduces credit and is not stored as a per-member score; the aggregate wrong-answer rate measures banner blindness [H] (S13.*). Off by default. [D]
- Even when no expansion is required, the expander is visible and works. [D]

### 11.8.5 Decline and report [D]

- **Decline** is one tap with no dialog. It calls `releaseLease`, emits `cell.declined`, returns the cell to `queued` with no penalty, no cooldown (`lease.decline_cooldown_s` = 0) and no change to trust tier or sampling (FD§5.5). The next offer list excludes that cell for this member for the rest of its current attempt [A]. An optional reason is chosen from a short fixed list (too long, not my topic, I do not want to, other) and used only as an aggregate demand-quality signal, never per member; skipping it is one tap.
- **Report** opens `SCR-vol-16` and does not release the lease unless the member also chooses Decline. Reporting is never penalized.

### 11.8.6 States

| State | Condition | Behavior |
| --- | --- | --- |
| Empty | `listOffers` returns none | As `AC-vol-09`; copy `copy.offers.empty` |
| Loading | `createLease` in flight after Take | The tapped summary shows "Reserving..."; double taps are ignored (one `Idempotency-Key` per tap) |
| Error: taken | `LEASE_CONFLICT` | `copy.error.cell_taken`; the list refreshes |
| Error: lease cap | `lease.max_active_per_member` reached | `copy.offers.lease_cap`: finish or decline an active task; the active leases are listed |
| Offline | No network after the lease was issued | Card, countdown label and prompt stay usable; Decline is queued locally and sent when online; the countdown shows "time left (last known)" |
| Blocked: restricted | `trust_tier` = `restricted` | Offers continue; banner `copy.account.restricted` states a temporary review with its end date (`trust.restriction_days`); no reason about gold failures is shown [D] |
| Blocked: suspended or banned | `member_status` not `active` | No offers; banner and Appeal action (`SCR-vol-14`) |
| Blocked: paused | `kill.template.<tpl_id>`, `kill.service.<svc_id>` or `kill.all_new_jobs` engaged | Affected cells are absent from the list; if all are, `copy.offers.paused`; a lease open at the moment of the pause is revoked server-side and the card shows `copy.card.revoked` with a one-tap return, telling the volunteer a pasted result for it can no longer be accepted (`reject.policy_changed` or `reject.lease_expired`) |

**API calls.** `listOffers`, `createLease`, `getLease`, `acknowledgePrompt`, `releaseLease`, `getMember`.

**Copy intent.** Neutral and factual; no urgency language, no "hurry", no social proof. The credit line never promises credit. The license line always states reuse plainly. Category names come from data (`TopicCategory`), not from code.

**Accessibility.** The card is one `article` with a labeled heading; the eight fields are a description list so a screen reader reads label and value pairs; the expander is a `button` with `aria-expanded` and `aria-controls`; the prompt container is focusable with an accessible name and its text is not hidden from assistive technology by truncation; disabled Copy uses `aria-disabled` with a described-by reason and stays in the tab order.

**Acceptance criteria**

- `AC-vol-11` Given a member who has never acknowledged template `tpl_x`, When the card opens, Then `expand_required` contains `expand.first_use_of_template`, Copy and Open are disabled with `copy.card.expand_first`, Decline and Report are enabled, and after the prompt is expanded and scrolled to its end Copy is enabled and `acknowledgePrompt` is called once.
- `AC-vol-12` Given a cell whose `license` is outside `optin.default_licenses` but inside the member's opt-ins, When the card opens, Then `expand.non_default_license` is present and the expansion gate applies.
- `AC-vol-13` Given the member taps Decline, When the call completes, Then the cell is `queued`, no cooldown applies, the member's `trust_tier` and sampling are unchanged, and the next `listOffers` excludes that cell for that member for the current attempt.
- `AC-vol-14` Given a card is rendered, When its fields are inspected, Then purpose, license, sensitivity, service, template with version, expected time, category and credit all appear before the full prompt, and the provenance sentence appears exactly once with the approval date.
- `AC-vol-15` Given the template is paused by `kill.template.<tpl_id>` while the member holds a lease, When the member returns to the card, Then the lease is shown revoked with `copy.card.revoked`, Copy is disabled, and no submission can be created for it.
- `AC-vol-16` Given a prompt containing Persian text, Latin words and digits, When Copy is tapped, Then the clipboard holds the exact prompt string whose hash equals the lease's `prompt_hash`, with no added marks and no digit conversion.

## 11.9 SCR-vol-04 Hand-off: copy and open in service (service-adapter layer)

### 11.9.1 Purpose and entry [D]

Get the exact prompt text into the volunteer's chosen chat service with the fewest taps, where the volunteer then presses Send themselves. Shown inside the card (11.8) once the expansion gate (11.8.4) allows it. No provider is hardcoded: every capability comes from the `ServiceRegistryEntry` through the service-adapter layer (S4.*, S7.*).

### 11.9.2 Adapter contract used by the client [D]

For each service offered to this member, `listApprovedServices` returns only services in state `approved` (S0.9.6) with these fields (names from S0.8.3; every value is entered by a reviewer [V]):

| Field | Type | Meaning for the screen |
| --- | --- | --- |
| `service_id` | `svc_` id | Identity of the service, recorded on the submission when the volunteer picks it |
| `display_name` | string | Name shown to the volunteer (registry data, not code) |
| `adapter.supports_prefill` | bool | A prefilled link may exist |
| `adapter.prefill_url_template` | string with `{prompt}` | The link pattern; the client fills `{prompt}` with the URL-encoded prompt |
| `adapter.max_url_chars` | int | Longest allowed link |
| `adapter.copy_only` | bool | True when prefill is unsupported or `prefilled_link_use` is not `yes` |
| `adapter.clean_chat_hint_key` | copy key | Service-specific advice for a clean chat (memory off, new conversation) |
| `prefill_allowed` | derived bool (server-computed) | See the rule below |

`prefill_allowed` = `adapter.supports_prefill` AND NOT `adapter.copy_only` AND `prefilled_link_use` = `yes` for the service (a flag answer, S0.8.3) AND `length(url) <= adapter.max_url_chars`, where `url` is the template filled with the prompt. A `FlagAnswer` of `unknown` counts as `no`. [D] The server computes the flag part; the client computes the length part against the actual encoded prompt, because encoding length depends on the text. The client never invents a link pattern, never guesses a service's URL, and never opens a link not produced from a registry template. [D]

```
function handoffModes(card, service):
    url = null
    if service.prefill_allowed_flags:                      # server: supports_prefill, not copy_only, flag yes
        url = fill(service.adapter.prefill_url_template, encodeURIComponent(card.prompt))
        if length(url) > service.adapter.max_url_chars: url = null   # too long: copy-only for this card
    return { copy: true, open: (url != null), url: url }   # copy is always available
```

### 11.9.3 Wireframe

```
+--------------------------------------------------+
| Step 3 of 5: Send it in your chat service        |
+--------------------------------------------------+
| Your service:  ( ) ServiceA  (o) ServiceB  ( ) ... |
|   (only approved services allowed by this task;   |
|    your choice is recorded with your result)      |
+--------------------------------------------------+
| Prefill mode:                                    |
|  [ Open in ServiceB ]   <- shown only if allowed |
|  [ Copy prompt ]        <- always shown           |
|  Open in a NEW clean chat. Turn memory off if the |
|  service lets you. (service hint)                 |
+--------------------------------------------------+
| Copy-only mode:                                  |
|  1. Tap Copy prompt.   2. Open your chat service  |
|  yourself.  3. Paste and press Send.              |
|  4. Copy the whole answer, come back, paste it.   |
+--------------------------------------------------+
| Timer: lease time left 17:55    [ Need more time ]|
| [ I have the answer -> paste-back ]               |
+--------------------------------------------------+
```

### 11.9.4 Behavior rules [D]

- **Service choice.** For `M0` the volunteer picks any listed approved service; for `M1` only the pinned ones are listed; for `M2` only `M2` entries. The choice is sent with the submission as the volunteer-reported service and model (attested, never proven; FD§5.6, FD§5.7 failure mode 7). The screen says "you report which service you used". An optional free-text model name field is allowed, length limited, never required.
- **Copy** copies the prompt exactly (11.4.3). After copying, the button changes to "Copied" for the next 3 seconds and announces it in a live region; if the clipboard API is unavailable or denied [V: browser support and permission prompts on target phones], the screen selects the prompt text and shows `copy.handoff.copy_manual` (long-press, select all, copy). Copy never fails silently.
- **Open in service** is a plain link the volunteer taps, opened with `rel="noopener noreferrer"` in a new tab. The client does not hold a reference to the opened window, does not poll it, does not message it and does not infer anything about it (X1, X2). The platform never attempts to read the destination page. When the volunteer comes back, the tab becomes visible and nothing else happens.
- **Copy-only** is the default whenever `prefill_allowed` is false; the screen then shows only the numbered instructions and the Copy button. No broken or truncated links are ever offered. A copy-only card is not an error and is not marked as inferior. [D]
- **Reachability and region.** The screen never says a service is available in the volunteer's region and never suggests a way around a restriction (X4). If the volunteer cannot use any listed service, the escape is Decline.
- **Clean chat hint.** The hint from `adapter.clean_chat_hint_key` is shown for every service (memory or connectors may leak content; FD§5.5 prompt-injection note); its wording comes from the registry-linked copy key and is `needs_human_and_legal_review`.
- **Never ask for more than copy, Send, return text.** The hand-off screen contains no instruction to open anything other than the prefilled link, install anything, download anything, sign in anywhere or share anything (`R3`; X6).
- **Prompt injection reminder.** A static line below the instructions: "If the answer contains links, code to run or requests for you to do something, do not follow them; paste it anyway and it will be set aside" (`copy.handoff.output_warning`) (FD§5.5; S9.* quarantine).

**States**

| State | Condition | Behavior |
| --- | --- | --- |
| Empty | No approved service offered for this task | Not reachable: such a cell is not offered (`R8`, `R7`); if it happens, `copy.handoff.no_service` with Decline |
| Loading | `listApprovedServices` pending | Copy works at once if the prompt is on the device; service list shows a placeholder |
| Error | `getLease` fails | Retry; the on-device prompt is still usable until the lease expires |
| Offline or low bandwidth | No network | Copy and the instructions work; the link mode works because it needs no Hamyar call; Submit is deferred to paste-back |
| Blocked: service paused | `kill.service.<svc_id>` engaged or service enters `review_due`, `suspended`, `revoked` | The service disappears from the list; a lease bound to `M1` for it is revoked; `copy.handoff.service_paused` |
| Blocked: lease expired | Lease timer passes `expires_at` | See 11.10; Copy disabled; "Back to tasks" |

**API calls.** `listApprovedServices`, `getLease`, `extendLease`.

**Copy intent.** Imperative, numbered, four steps; says "you press Send" in words. No logo, brand claim or provider endorsement; service names come from registry data. No statement that a service is safe, free or allowed (those are [V] and live in the registry).

**Accessibility.** The service choice is a radio group with a legend; the Open link has a name that includes the service and states that it opens in a new tab; the four copy-only steps are an ordered list; the timer follows 11.4.5.

**Acceptance criteria**

- `AC-vol-17` Given a registry entry with `adapter.supports_prefill` true, `adapter.copy_only` false and `prefilled_link_use` = `yes`, When the encoded URL length is at most `adapter.max_url_chars`, Then both Copy and Open in service are shown; and When the length exceeds the maximum, Then only Copy and the numbered instructions are shown for that card.
- `AC-vol-18` Given a registry entry whose `prefilled_link_use` is `unknown`, When the hand-off renders, Then Open in service is not shown and the screen is copy-only.
- `AC-vol-19` Given the clipboard API is denied, When Copy is tapped, Then the prompt text is selected and `copy.handoff.copy_manual` is announced in a live region.
- `AC-vol-20` Given the volunteer taps Open in service, When network and script activity is inspected, Then no code in the page reads, messages or polls the opened window and no request carries any content of the provider's page.
- `AC-vol-21` Given any service entry, When the hand-off renders, Then no credential field, chat-link field or token field is present and no instruction mentions bypassing a restriction.

## 11.10 SCR-vol-05 Paste-back

### 11.10.1 Purpose and entry [D]

Return the provider's answer to Hamyar by a human paste, bound to the lease and its nonce, with local checks that catch obvious mistakes before the server does. Entry: an `active` lease (`Lease.active`) on this device.

### 11.10.2 Wireframe

```
+--------------------------------------------------+
| Step 4 of 5: Paste the answer here               |
| lease time left 09:12   [ Need more time ] (1 use)|
+--------------------------------------------------+
| Which service did you use?  [ ServiceB v ]       |
| (optional) model name: [______________]          |
+--------------------------------------------------+
| +----------------------------------------------+ |
| | (large text field, dir=auto, empty)          | |
| |                                              | |
| +----------------------------------------------+ |
| [ Paste from clipboard ]     characters: 0/6,000 |
| Checks on this device (advisory only):           |
|  - not empty                                     |
|  - within the size limit                         |
+--------------------------------------------------+
| [ Submit ]  (disabled until a check-able answer) |
| ( Release this task )                            |
+--------------------------------------------------+
```

### 11.10.3 Fields, local checks and limits [D]

| Item | Rule |
| --- | --- |
| Answer field | Plain text only; multi-line; the pasted text is never interpreted as HTML or Markdown and is rendered back only as text (V-15) |
| Paste from clipboard | A button that reads the clipboard inside its own tap handler and fills the field; if unsupported or denied, the volunteer pastes manually [V]; the clipboard is never read otherwise (X5) |
| Size checks | Count characters against `cell.envelope.max_output_chars` and UTF-8 bytes against `cell.envelope.max_submission_bytes`; over the limit shows `copy.paste.too_large` and keeps Submit disabled; the server repeats the check and answers `PAYLOAD_TOO_LARGE` (reject reason `reject.size_exceeded`) |
| Empty check | Submit disabled for an empty or whitespace-only field |
| Advisory checks | Only checks that need no server secret: non-empty, size, and (when the template declares it) a language hint. The UI never runs the template's real automatic checks and never reveals gold or audit status, so the checks on the device cannot be used to probe the verifier (S9.*) |
| Own-output reminder | If the pasted text equals the prompt text exactly, the screen shows `copy.paste.looks_like_prompt` (probably the wrong thing was copied) and still lets the volunteer submit |
| Service and model | Service from the hand-off choice, changeable here; model name free text up to 80 characters [A], never required |
| Draft | Held in memory and session storage, never uploaded before Submit; survives going back and a page reload within the lease |
| No attachments | No file or image upload; text only (X6, `R3`) |

### 11.10.4 Submit protocol (client side) [D]

```
function submit(lease, answer, service_id, model_name):
    key = lease.idempotency_key                      # generated once per lease, kept on device
    body = { nonce: lease.nonce, text: answer, service_id, model_name }
    loop with backoff up to ui.status_poll_max_s:
        r = submitResult(lease_id, body, Idempotency-Key: key)
        if r is 2xx: show outcome per 11.11; stop
        if r is 409 IDEMPOTENCY_IN_PROGRESS: wait Retry-After; continue
        if r is 410 LEASE_EXPIRED: show lease-lost state; keep the draft visible, never discard it
        if r is 413 or 400: show field error; stop
        if network error or 5xx: show 'saved on this device, trying again'; continue
```

The client sends the nonce it received with the lease; it never generates, guesses or alters it. One submission is accepted per lease and nonce; a replay returns the stored outcome (S0.9.3). A submission within `lease.submit_grace_s` after expiry is accepted only if the cell has not been re-leased (server decision); the screen says nothing about the grace period beforehand, so it is not a target. [D]

### 11.10.5 Lease timer and extension [D]

- The timer is the server `expires_at` minus server time at last response (11.4.2). Warning states by remaining share of `lease.timeout_s`: normal above 25 percent, `copy.lease.warning` below 25 percent, with the extension offer. [A: the 25 percent threshold is an `initial configurable default` and is added as `ui.lease_warning_ratio` = 0.25 (range 0..1), replaced by measurement `CAL`.]
- "Need more time" calls `extendLease` and adds `lease.extend_s`; the number of extensions is limited by `lease.max_extensions`; after the last one the button is replaced by `copy.lease.no_more_extensions`. Extending is never penalized.
- At expiry the lease becomes `expired`; the cell requeues (`cell.lease_expired`, `cell.requeued`) and the screen shows `copy.error.lease_expired` with the draft preserved on screen so the volunteer can copy it; submitting it is refused unless the grace rule applies.
- **Release this task** is the same as Decline (11.8.5).

**States**

| State | Condition | Behavior |
| --- | --- | --- |
| Empty | Field empty | Submit disabled; helper text under the field |
| Loading | `submitResult` in flight | Submit shows "Sending..."; the field is read-only; a visible text status, no spinner-only state |
| Error: field | `VALIDATION_FAILED`, `PAYLOAD_TOO_LARGE` | Error next to the field with its copy key; draft kept |
| Error: lease lost | `LEASE_EXPIRED` (410), `LEASE_CONFLICT` (409) | `copy.error.lease_expired` or `copy.error.cell_taken`; draft kept on screen; one action: Back to tasks |
| Offline or low bandwidth | No network on Submit | `copy.paste.saved_locally`; automatic retry with the same `Idempotency-Key`; on return of the network the screen continues; the lease timer shows last known time |
| Blocked: paused or revoked | Lease revoked (`lease.revoked`) | `copy.card.revoked`; Submit disabled; draft kept; the volunteer is told the result will not be credited |
| Blocked: rate limited | `ratelimit.member_submissions_per_hour` (`RATE_LIMITED`) | `copy.error.rate_limited` with time; draft kept |

**API calls.** `getLease`, `extendLease`, `releaseLease`, `submitResult`.

**Copy intent.** Short, procedural, forgiving. Never accuse of forgery or copying; never reveal which checks exist. The size message gives the number from the parameter. Text for "looks like prompt" is a question, not a warning.

**Accessibility.** The field has a visible label and a described-by with the limit and the live character count (updated politely, not per keystroke); errors are linked with `aria-describedby` and announced; Submit disabled state is `aria-disabled` with a reason; the extension button is reachable before the timer text in the focus order.

**Acceptance criteria**

- `AC-vol-22` Given an active lease and a non-empty answer within limits, When Submit is tapped, Then `submitResult` is called once with the lease nonce, the volunteer-reported service and the `Idempotency-Key` fixed for that lease, and the screen moves to result feedback.
- `AC-vol-23` Given the network drops during Submit, When it returns within the lease, Then the retry uses the same `Idempotency-Key` and exactly one `Submission` exists.
- `AC-vol-24` Given an answer over `cell.envelope.max_output_chars` or `cell.envelope.max_submission_bytes`, When the field changes, Then Submit is disabled with `copy.paste.too_large`, and if the request is forced the server returns `PAYLOAD_TOO_LARGE` and the draft is kept.
- `AC-vol-25` Given the lease expires while the volunteer is pasting, When Submit is tapped after `lease.submit_grace_s` or after the cell was re-leased, Then the server returns `LEASE_EXPIRED`, the screen shows `copy.error.lease_expired`, and the pasted text remains visible and copyable.
- `AC-vol-26` Given `lease.max_extensions` = 1, When the volunteer taps "Need more time" twice, Then the first extends `expires_at` by `lease.extend_s` and the second is unavailable with `copy.lease.no_more_extensions`.
- `AC-vol-27` Given the screen is open, When the clipboard is inspected by instrumentation, Then it is read only inside the tap handler of "Paste from clipboard" and never on focus, load, visibility change or timer.
- `AC-vol-28` Given a pasted answer containing HTML tags, script text and a URL, When it is displayed back or in History, Then it is shown as inert text with no markup interpreted and no link made clickable.

## 11.11 SCR-vol-06 Result feedback

### 11.11.1 Purpose and entry [D]

Tell the volunteer, honestly and without revealing the verifier, what happened to the submitted result and what it means for credit. Entry: after `submitResult`, and from History (11.13). The outcome is read with `getSubmission` (S0.9.3 states).

### 11.11.2 Outcome model shown to the volunteer [D]

The server states map to four volunteer-facing outcomes. The UI never exposes the words gold, audit sampling, or reliability estimate for an individual result (V-10; FD§4.4 keeps checks hidden to be useful).

| Volunteer-facing outcome | Server state | Icon and word | Credit line | Next action |
| --- | --- | --- | --- | --- |
| `received` (checking) | `Submission.received`, `checks_passed` pending, `Cell.submitted`, `Cell.flagged_for_audit` | Hourglass: "Received, being checked" | "Credit is added when it is accepted" | Take another task; Check again |
| `accepted` | `Submission.accepted`, `Cell.accepted` | Check mark: "Accepted" | "+1 credit" with its expiry date (`credit.lifetime_days`) | Another task; Save recovery key if unsaved (first accepted) |
| `rejected` | `Submission.schema_failed`, `checks_failed`, `rejected`, `Cell.rejected` | Cross: "Not accepted" plus the reason | "No credit for this one" | See reason; Try again if the cell requeued to you; Appeal (`SCR-vol-14`) |
| `set_aside` | `Submission.quarantined` | Flag: "Set aside for review" | "Credit is decided after review" | Nothing required; History shows the final outcome |

The volunteer also has "flagged" in the sense of their own report on a card (`SCR-vol-16`); that is a separate outcome of reporting, not a verdict on the submission.

**Rejection reason display.** The reason comes from the seed list of S0.8.4 and is shown as the code's plain-language copy key `copy.reject.<code>` plus one line of what to do. Reasons are shown only as far as they do not teach evasion: `reject.gold_mismatch`, `reject.audit_mismatch` and `reject.timing_anomaly` are shown with the generic text `copy.reject.generic_check` ("did not pass our checks") and never as "gold", "audit" or "too fast"; the exact code stays in the member's own History detail only if S9.* allows it [A: issue ISS-111]. A `reject.duplicate_of_other_output` is shown neutrally, never as an accusation. [D]

| Reason code | Copy intent (plain, no blame) | Suggested volunteer action |
| --- | --- | --- |
| `reject.schema_invalid` | The answer was not in the expected form | Paste only the answer text; try the next task |
| `reject.refusal_pattern` | The service declined or did not do the task | Try again with another service if allowed, or decline |
| `reject.length_out_of_bounds` | The answer was much shorter or longer than expected | Check you copied the whole answer |
| `reject.language_mismatch` | The answer was not in the expected language | Check the answer, try again |
| `reject.test_failed` | The answer did not pass the task's own tests | Try again or decline |
| `reject.forbidden_content` | The answer contained content we cannot accept | Nothing to do; see Help; you may appeal |
| `reject.nonce_invalid`, `reject.lease_expired`, `reject.size_exceeded` | The submission could not be linked to your task, or arrived too late or too large | Take the task again if offered |
| `reject.policy_changed` | The rules changed while you were working on it (`R9`) | No fault of yours; take another task |
| `reject.gold_mismatch`, `reject.audit_mismatch`, `reject.duplicate_of_other_output`, `reject.timing_anomaly` | Generic: did not pass our checks | You may appeal |

### 11.11.3 Wireframe

```
+--------------------------------------------------+
| Step 5 of 5: Result                              |
+--------------------------------------------------+
| [hourglass] Received, being checked              |
|   Credit is added when it is accepted. You can    |
|   leave this page; we keep the status in History. |
|   [ Check again ]                                |
+--------------------------------------------------+
|  -- after acceptance --                          |
| [check] Accepted      +1 credit  expires {date}  |
|   Balance: 4 credits                             |
|   [ Take another task ]                          |
|   (first time) Save your recovery key  [ Save ]   |
|   (if flag on) [ Share a card ]  [ Invite ]       |
+--------------------------------------------------+
|  -- after rejection --                           |
| [x] Not accepted: {reason copy}                  |
|   No credit for this one.                         |
|   [ Take another task ]  ( Appeal )  ( Report )   |
+--------------------------------------------------+
```

### 11.11.4 Rules [D]

- Feedback is asynchronous when checks are not immediate: the screen shows `received`, and the final outcome appears on the next `getSubmission` read. Polling runs only while the screen is open, with backoff up to `ui.status_poll_max_s`, and stops on any final outcome; there is no push notification (V-12).
- The credit amount shown is from the ledger (`getBalance`), never computed on the device. "+1 credit" appears only after `Submission.accepted`; no optimistic credit is ever displayed. [D]
- Accepted credit shows its expiry date, converted per 11.4.2, and a second line with the other calendar in the detail view.
- The first accepted cell triggers one prompt to save the recovery key (V-09); it can be dismissed; the marker remains (11.18). If the member's `trust_tier` or the grant state changes (starter grant needs `grant.required_verified_cells` verified cells), a plain one-line note says what happened (`copy.feedback.starter_grant`); starter grant wording says "declared" rules, not guarantees. [D]
- An outcome of `accepted` can later become `Cell.overturned` (appeal or fraud finding; ledger reversal). History shows it with its reason and `copy.feedback.overturned`; nothing is hidden. [D]
- A rejected result is not punished by the UI; any penalty or restriction is a trust-tier matter handled in S8.* and S10.*, and the UI never says "strike" or "warning".

**States**

| State | Condition | Behavior |
| --- | --- | --- |
| Empty | No submission id (deep link to nothing) | `copy.error.not_found` and a link to History |
| Loading | `getSubmission` in flight | Last known status shown with "checking" label |
| Error | `getSubmission` fails | `copy.error.try_again`; the submission is safe; History is the fallback |
| Offline or low bandwidth | No network | Last known outcome shown with "last checked" time; Check again enabled when online; no polling |
| Blocked: suspended | Member suspended after submit | Outcome still readable; new tasks blocked; Appeal offered |
| Blocked: paused | Job or template paused or voided (`cell.voided`) | `copy.feedback.voided`: the task was withdrawn; no fault of yours; credit rules shown (S6.*) |

**API calls.** `getSubmission`, `getBalance`, `getMember`.

**Copy intent.** Say what is known, say what is not yet known, never congratulate beyond the fact. Never promise credit before acceptance. Never describe verification internals. Use "declared" for any statement about rules or expiry: "credit expires on the declared date".

**Accessibility.** The outcome is announced once in a polite live region with the word and icon meaning; color is never the only signal; the Check again button keeps focus after use; the reason text is plain and short.

**Acceptance criteria**

- `AC-vol-29` Given a submission in `Submission.received`, When the feedback screen renders, Then it shows `received` with "credit is added when it is accepted" and no credit amount.
- `AC-vol-30` Given `Submission.accepted`, When the screen refreshes, Then it shows +1 credit with an expiry date equal to `earned_at` plus `credit.lifetime_days` days (per the parameter version in force at `earned_at`) in the member's calendar, and the balance comes from `getBalance`.
- `AC-vol-31` Given `reject.gold_mismatch`, When the rejection is shown, Then the screen uses `copy.reject.generic_check` and does not contain the words gold, audit, sampling or timing.
- `AC-vol-32` Given `Submission.quarantined`, When the screen renders, Then it shows `set_aside`, no credit and no link to the submitted text as clickable content.
- `AC-vol-33` Given the first accepted cell and an unsaved recovery key, When the outcome is `accepted`, Then the screen offers `SCR-vol-13` once and keeps the key marker visible until `confirmRecoveryKey`.
- `AC-vol-34` Given the network is lost while the screen is open, When status polling fails, Then polling backs off up to `ui.status_poll_max_s`, the last known outcome stays visible, and no error blocks the page.

## 11.12 SCR-vol-07 Balance and expiry view

**Purpose.** Show the volunteer what credit they hold, when each part expires, what is near the cap, and why, with every number taken from the ledger. [D]

**Entry conditions.** Signed-in member; opened from the header credit chip.

**Wireframe**

```
+--------------------------------------------------+
| Credit                                           |
+--------------------------------------------------+
| Balance            12 credits                    |
| Expires soonest    3 credits on {date J / G}     |
| Cap                12 of 350 (credit.member_cap)  |
+--------------------------------------------------+
| Lots, oldest first (spent in this order)         |
|  # | Credits | Earned    | Expires    | Source   |
|  1 |    3    | {date}    | {date}  !  | task     |
|  2 |    5    | {date}    | {date}     | task     |
|  3 |    3    | {date}    | {date}     | starter  |
|  4 |    1    | {date}    | {date}     | referral |
|  ! = expires within credit.expiry_notice_days     |
+--------------------------------------------------+
| What expiry means (declared rules):              |
|  Credit expires {E} days after it is earned and   |
|  is spent oldest first. Expired credit moves to   |
|  the public Commons Reserve.        [ Read more ] |
| [ Take a task ]          ( View my ledger entries)|
+--------------------------------------------------+
```

**Content rules [D]**

- Balance is the sum of unexpired `CreditLot` amounts of the member's `member` ledger account, from `getBalance`; lots from `listCreditLots`; entries from `listMemberLedgerEntries`. Display rounds balances down (S0.6.1) and shows whole credits plus a fraction only when non-zero. The client never sums, rounds, or computes expiry itself.
- Each lot row shows credits, earned date, expiry date (`expires_at = earned_at + credit.lifetime_days x 86,400 s` with the parameter version in force at `earned_at`, S0.6.2), source (`mint`, `transfer`, `grant` starter, `grant` referral, `refund` restored), and an expiry warning when within `credit.expiry_notice_days`. Both calendars appear in the detail tooltip.
- The starter-grant lot shows its own shorter expiry (`grant.starter_lifetime_days`) and is labeled non-transferable (`grant.non_transferable`).
- When a member is in the accelerated-expiry arm (`ff.experiment.expiry_arm` on and an `ExperimentAssignment` exists), the screen shows only the member's own declared lifetime in days and never the word "experiment" or the other arm's value; the assignment itself is logged server-side (S12.*, S13.*) and its disclosure is part of the pilot opt-in notice (FD§9 Phase 1 setup, participants informed). [D][A]
- Cap: shows balance against the member's effective cap (`credit.member_cap_credits` times the tier multiplier `trust.cap_multiplier.<tier>`). At the cap, `copy.balance.at_cap` states that new credit cannot be added until some is spent or expires (`CAP_EXCEEDED`), and that nothing is lost. [D]
- A note states that credit is not money, property or an entitlement, that it cannot be cashed out, and that its legal character is not decided (FD§4.1; `needs_human_and_legal_review` [V: counsel]).
- Nothing promises a future job will be completed; the line about spending says "you can use credit to request work when requests are open; completion is within a quoted window, declared at the time of the request" (FD Principle 10). When `launch.member_jobs_enabled` is false, the line is replaced by `copy.balance.requests_not_open`. [D]

**States**

| State | Condition | Behavior |
| --- | --- | --- |
| Empty | No lots | `copy.balance.empty`: "No credit yet. Your first accepted task adds 1 credit." with Take a task |
| Loading | Fetching | Balance and lots show placeholders; static explanation text renders at once |
| Error | `getBalance` fails | Last cached balance shown only if marked "last known" with its time, otherwise `copy.error.try_again` |
| Offline or low bandwidth | No network | Cached values labeled last known; no calculation on the device |
| Blocked: suspended or banned | `member_status` not `active` | Balance readable; spending actions blocked; Appeal link |
| Blocked: minting off | `launch.minting_enabled` false or `kill.all_minting` engaged | A line: "Tasks may be unavailable or may not add credit right now" (`copy.balance.minting_off`); no promise on when it returns |

**Actions.** Take a task, View ledger entries (list only, own entries), Read more (expiry explainer), Back.

**API calls.** `getBalance`, `listCreditLots`, `listMemberLedgerEntries`, `getMember`.

**Copy intent.** Dates before percentages; no loss framing ("you will lose") beyond the plain expiry date; no countdown animation; the expiry notice is shown on this screen and as a header dot, never as a push message (V-11, V-12).

**Accessibility.** The lots list is a real table with captions and column headers; the near-expiry mark has a word, not only an icon; the dual-calendar dates are available as text, not only on hover.

**Acceptance criteria**

- `AC-vol-35` Given lots with expiry dates, When the screen renders, Then lots are listed oldest first and each shows an expiry date from the server; none is computed on the device.
- `AC-vol-36` Given a lot expiring within `credit.expiry_notice_days`, When the screen renders, Then the lot shows the word "expires soon" and the header chip shows a dot, and no notification is sent outside the app.
- `AC-vol-37` Given a member at the cap, When the screen renders, Then `copy.balance.at_cap` is shown and the member can still open History and Help.
- `AC-vol-38` Given `launch.member_jobs_enabled` is false, When the screen renders, Then no text states that credit can be spent on requests, and `copy.balance.requests_not_open` is shown.
- `AC-vol-39` Given the member is in the accelerated-expiry arm, When the screen renders, Then the lifetime shown is the member's own `credit.lifetime_days_accelerated` and the other arm's value and the word "experiment" are absent.

## 11.13 SCR-vol-08 History

**Purpose.** A member's own record of cells and outcomes, a place to find a rejection to appeal and a report to follow up. [D]

**Entry conditions.** Signed-in member; menu entry.

**Wireframe**

```
+--------------------------------------------------+
| History                       [Filter: all v]    |
+--------------------------------------------------+
| {date}  Translation w/ glossary v3   Accepted +1 |
| {date}  Classification v2   Not accepted   [ > ] |
| {date}  Summarize v1        Set aside              |
| {date}  Translation v3      Received (checking)    |
| {date}  Classification v2   Declined               |
|                           [ Load more ]          |
+--------------------------------------------------+
| Detail (tap a row): template and version, service |
| you reported, outcome, reason copy, credit and     |
| expiry, both calendars, [Appeal] [Report]         |
+--------------------------------------------------+
```

**Rules [D]**

- Newest first with cursor pagination (`api.page_size_default`); no total count (S0.11.6). Filters: all, accepted, not accepted, set aside, declined, appeals.
- Row detail shows what the volunteer submitted only as inert text and only while the payload is retained (`retention.job_payload_days`); after purge it shows hashes and the outcome (`copy.history.payload_purged`). The prompt text of a past cell is not re-shown after purge. [D]
- The Appeal action appears only for a rejected or overturned cell within `appeal.window_days` of the decision and only if `appeal.max_per_decision` is not reached; otherwise the action is replaced by a reason (window closed or already appealed). [D]
- Overturned items show the reversal in plain words (`copy.feedback.overturned`); no entry is ever hidden or deleted (corrections are new rows, S0.7).
- A volunteer's own history never reveals another member, a requester, a job's subject, or the content of other submissions. [D]
- Export: a plain `.csv` of the member's own rows is allowed [A] (dates in Gregorian ISO, S0.6.2), generated on request; it excludes submitted text.

**States.** Empty: `copy.history.empty` with Take a task. Loading: skeleton rows. Error: `copy.error.try_again`. Offline: the last loaded page, labeled "last known"; Load more disabled. Blocked: suspended or banned members can read history and use Appeal; closed members see nothing.

**Actions.** Filter, Load more, Open detail, Appeal, Report, Export.

**API calls.** `listCellHistory`, `getSubmission`, `listAppeals`.

**Copy intent.** Neutral list language; outcome words match 11.11.2; no ranking against others.

**Accessibility.** Rows are a list of buttons with full text names ("Accepted, translation, {date}"); detail opens inline, not as a modal; focus returns to the row.

**Acceptance criteria**

- `AC-vol-40` Given a rejected cell decided 3 days ago and `appeal.window_days` = 14, When its detail opens, Then Appeal is offered; and Given the decision is 15 days old, Then Appeal is replaced by `copy.appeal.window_closed`.
- `AC-vol-41` Given a cell whose payload was purged after `retention.job_payload_days`, When its detail opens, Then no prompt or submitted text is shown and `copy.history.payload_purged` is shown.
- `AC-vol-42` Given more rows than `api.page_size_default`, When Load more is tapped, Then the next page is fetched by cursor and no total count is shown.

## 11.14 SCR-vol-09 Opt-in settings

**Purpose.** Let the volunteer choose which cells they may be offered, per axis and per topic category, with the safe defaults on and everything else off (`R8`; FD§5.4 R8). Backed by the `OptIn` entity. [D]

**Entry conditions.** Signed-in member; menu entry; "Why am I seeing these?" from the offer list.

**Wireframe**

```
+--------------------------------------------------+
| What tasks may I be offered?                     |
+--------------------------------------------------+
| Purpose          [x] P0 personal/study (default) |
|                  [x] P1 open publication (default)|
|                  [ ] P2 commercial  (locked*)     |
|                  [ ] P3 training    (locked*)     |
| Sensitivity      [x] S0 public (default)          |
|                  [x] S1 private, non-sensitive    |
|                  (S2, S3 are never offered)       |
| License          [x] L0 [x] L1 [x] L2 [ ] L3      |
| Service          [x] M0 [x] M1 [x] M2             |
| Topic categories (each is opt-in):                |
|    [ ] {category from data} ...                   |
| Services I can use:  [x] ServiceA [ ] ServiceB    |
| * locked until the platform declares it open      |
| [ Save ]                           ( Reset to defaults )|
+--------------------------------------------------+
```

**Rules [D]**

- Initial values: `optin.default_purposes` (`P0`, `P1`), `optin.default_sensitivities` (`S0`, `S1`), `optin.default_licenses` (`L0`, `L1`, `L2`), `optin.default_service_requirements` (`M0`, `M1`, `M2`); `optin.sensitive_topics_default` = false, so every sensitive topic category starts off (S0.10.6).
- `P2` and `P3` appear greyed with the reason "not open yet" while locked per S0.8.1 (`P2` unlocks per service after its terms are verified [V]; `P3` needs `M2` or a service whose `training_use_of_output` is `yes`, `S0` only). Enabling a locked axis is impossible in the UI; the server also refuses it.
- `S2` and `S3` are shown as "never offered", not as options.
- Topic categories come from `listTopicCategories` (`TopicCategory`, data-defined); each has a plain description and a sensitivity note, and enabling a sensitive category shows a confirmation (`copy.optin.sensitive_confirm`) that lists what such tasks can contain in plain words.
- Changes apply to future offers only; held leases are not changed; the server emits `member.optin_changed`. Opting out never penalizes, never lowers trust tier, and the opt-out rates are tracked per category only in aggregate (FD§9 measures; S13.*). [D]
- Fewer opt-ins mean fewer or slower offers; the screen says so once in neutral words (`copy.optin.fewer_tasks`), and does not nudge toward opting in (FD§5.7 failure mode 8 is handled by the supply gauge in the quote, not by pressure).
- Service choices list only `approved` registry entries and let the volunteer say which they can use; this is a preference, not an attestation, and no credential is requested (X3).

**States.** Empty: topic list empty shows `copy.optin.no_topics`. Loading: current values placeholders. Error: `VALIDATION_FAILED` with `details.fields`. Offline: edits kept locally as unsaved and Save disabled until online. Blocked: a locked axis is shown disabled; a paused category shows "paused"; suspended members can view but not change.

**Actions.** Toggle, Save, Reset to defaults, Back (asks before discarding unsaved changes).

**API calls.** `getOptIns`, `updateOptIns`, `listTopicCategories`, `listApprovedServices`.

**Copy intent.** Respectful and neutral; each item says what the volunteer will see, not what they should choose.

**Accessibility.** Fieldsets with legends per axis; locked items are `aria-disabled` with the reason read out; the confirmation for sensitive topics is a sheet with focus trapped and Escape to cancel.

**Acceptance criteria**

- `AC-vol-43` Given a new member, When the screen opens, Then exactly the values in `optin.default_*` are selected, `P2` and `P3` are disabled, `S2` and `S3` are not selectable, and no topic category is selected.
- `AC-vol-44` Given the volunteer enables a sensitive topic category, When they tap Save, Then a confirmation listing what such tasks can contain is shown first, `updateOptIns` is called only after confirmation, and `member.optin_changed` is emitted.
- `AC-vol-45` Given the volunteer disables `P1`, When they next open the offer list, Then no `P1` cell is offered and their trust tier and credit are unchanged.
- `AC-vol-46` Given a request that enables a locked axis is forced, When the server evaluates it, Then it returns `UNPROCESSABLE` and the stored `OptIn` is unchanged.

## 11.15 SCR-vol-10 Teams

**Purpose.** Opt-in, self-created groups scored only on verified cells (FD§6.1 rank 5; V4). Entirely behind `ff.growth.v4_teams` and the randomized offer logic of S12.*. Never shown in the first-contribution flow. [D]

**Entry conditions.** Flag on; the member is offered teams by the experiment assignment (`ExperimentAssignment`, S12.*, S13.*); creating a team needs `team.create_min_tier` (`established`); joining needs no tier.

**Wireframe**

```
+--------------------------------------------------+
| Teams (optional)                                 |
+--------------------------------------------------+
| Your team: {name chosen by its creator}           |
|  Members: 7   Verified cells this week: 142       |
|  Your own verified cells: 11                      |
|  [ Leave team ]                                  |
+--------------------------------------------------+
| No team yet:  [ Create a team ]  [ Join with code ]|
|  Teams are optional. Joining shows only your       |
|  verified-cell count to your team, as a number.    |
+--------------------------------------------------+
```

**Rules [D]**

- A team has a name, a join code and aggregate counts of verified cells; it shows no member list, handles, ids, avatars, places or affiliations to anyone, including other members (X7). Only the member's own count is shown to the member. A team smaller than `team.min_public_members` is never shown on any public surface (S12.*).
- A team name is free text chosen by the creator, checked by the server for length and prohibited content; it is never a location or institution field, and the screen has no field for city, country or university (`public.location_display` = `never`; FD§6.1 row 5).
- `team.max_members` bounds a team; joining by code is rate-limited; leaving is one tap and removes the member's future contribution from that team's count only.
- Scoring counts verified cells only (accepted, not overturned), so a team cannot be raised by volume of unverified work; the screen says "verified cells".
- Teams are never required for anything, never gate credit, and never create a leaderboard of individuals. [D]

**States.** Empty: no team (as drawn). Loading: placeholders. Error: `ALREADY_EXISTS` for a duplicate name, `NOT_FOUND` for a bad code (same message for wrong and expired, no probing). Offline: read-only cached values labeled last known. Blocked: flag off, tier too low (`copy.teams.needs_tier`, no number given beyond the declared rule), member suspended.

**Actions.** Create, Join with code, Leave, Copy invite code (the code, never a link containing identity).

**API calls.** `createTeam`, `getTeam`, `joinTeam`, `leaveTeam`.

**Copy intent.** Light and optional; no pressure, no "your team is losing".

**Accessibility.** Counts are text; join code field has a visible label and paste support; no color-coded ranking.

**Acceptance criteria**

- `AC-vol-47` Given `ff.growth.v4_teams` is off, When the member opens the menu, Then no Teams entry is present and `createTeam` is not callable from the UI.
- `AC-vol-48` Given a member in a team, When any screen is inspected, Then no other member's id, handle, name or contribution count is shown, only team aggregates and the member's own count.
- `AC-vol-49` Given a team with fewer than `team.min_public_members` members, When public surfaces render, Then the team does not appear.
- `AC-vol-50` Given a member whose cell is later `Cell.overturned`, When the team count refreshes, Then that cell no longer counts.

## 11.16 SCR-vol-11 Share card

**Purpose.** Let a volunteer share a small image or text card that contains only aggregate, non-identifying facts (FD§6.2 V3). Behind `ff.growth.v3_share_card` and never shown in the first-contribution flow. [D]

**Entry conditions.** Flag on; the member has at least one verified cell; entry from the accepted-result screen or the menu.

**Wireframe**

```
+--------------------------------------------------+
| Share a card                                     |
+--------------------------------------------------+
|  +--------------------------------------------+  |
|  |  Hamyar                                    |  |
|  |  12 verified cells so far                  |  |
|  |  Badge: First 10                           |  |
|  |  (no name, no place, no id, no date of join)|  |
|  +--------------------------------------------+  |
|  What is on this card:  count, badge, project name |
|  [ Share ]   [ Copy text ]   [ Save image ]       |
+--------------------------------------------------+
```

**Rules [D]**

- Allowed content: a count of the member's verified cells (rounded down to a bucket, for example the nearest 10, to resist fingerprinting [A]), a badge name from `Badge` (criteria in verified cells only), the project name and an optional public milestone. Never: handle, member id, e-mail, location, institution, team name, dates of activity, service names, template names or the volunteer's time zone.
- The image is drawn on the device from `getShareCard` data; the server never receives the image; the card links to the public landing and carries the member's invite token only if the member explicitly adds it (that link is covered by 11.17 and is the only identifying-by-tree element, and is shown as such).
- The Share button uses the platform share sheet if present and otherwise copies text; no social SDK is loaded, no tracking pixel, no short-link service (`analytics.third_party_trackers` = false).
- A one-line notice says that sharing tells others the member uses Hamyar, which may matter for personal safety, and that not sharing is always fine (`copy.share.safety_notice`, member safety outranks growth, FD Principle 8). `needs_human_and_legal_review`.
- Share events are instrumented in aggregate only (S12.*, S13.*).

**States.** Empty: no verified cell yet (`copy.share.not_yet`, no card). Loading: card skeleton. Error: `copy.error.try_again`. Offline: card can still be drawn from last known data and saved. Blocked: flag off; member suspended.

**Actions.** Share, Copy text, Save image, Toggle "add my invite link" (default off).

**API calls.** `getShareCard`, `createInvite` (only if the toggle is on).

**Copy intent.** Matter-of-fact, no boasting language; the safety notice precedes the Share button.

**Accessibility.** The card image has a text alternative with the same content; the toggle is a labeled switch; the share sheet is the platform's own.

**Acceptance criteria**

- `AC-vol-51` Given the share card is generated, When its data and image are inspected, Then it contains no member id, handle, e-mail, location, team, date or service name.
- `AC-vol-52` Given the member has 0 verified cells, When they open the screen, Then no card is shown and `copy.share.not_yet` is displayed.
- `AC-vol-53` Given the share card is saved, When network requests are inspected, Then no image or card data was sent to the server and no third-party host was contacted.
- `AC-vol-54` Given the invite-link toggle is off by default, When the card is shared, Then no invite token appears in the shared text or image.

## 11.17 SCR-vol-12 Invite flow

**Purpose.** Let an eligible member vouch for a newcomer through a single-use invitation, forming an edge in the invite tree (`Invite`, FD§6.2 V5 and the anti-farming rules of S10.*). Referral bonus UI appears only when `ff.growth.v5_referral` is on. [D]

**Entry conditions.** Signed-in `active` member with at least `invite.min_accepted_cells_to_issue` accepted cells; fewer than `invite.max_active_per_member` active invites; the invite tree is below `invite.tree_max_members` and `invite.tree_max_depth`.

**Wireframe**

```
+--------------------------------------------------+
| Invite someone you trust                         |
+--------------------------------------------------+
| Invites left: 2 of 3 active                       |
| [ Create an invitation ]                         |
|  -> one-time code + link, valid {ttl} days        |
|  [ Copy link ]  [ Copy code ]                     |
| Before you invite: Hamyar is for people who can    |
| decide for themselves to take part. You vouch for  |
| the person; you do not see what they do.           |
+--------------------------------------------------+
| Your invitations:                                |
|  code ...a7f2  Created {date}  Pending  [Revoke]  |
|  code ...91cc  Used {date}     Joined             |
+--------------------------------------------------+
| (flag v5) Referral: you and the newcomer each get |
| a small declared bonus after their first verified |
| cell. Rules: {copy.referral.rules}                |
+--------------------------------------------------+
```

**Rules [D]**

- An invitation is a single-use token delivered as a URL fragment (`#invite=<token>`), so it is not sent to the server in a request line or to analytics. It shows only the last four characters of its code in the list. It carries no member id, handle or other identity of the issuer to the invitee. The invitee never learns who invited them unless the issuer tells them outside the app. [D][A]
- The issuer sees only the state of each invitation (`pending`, `used`, `expired`, `revoked`) and the date. They are never told who joined or what the invitee does. [D]
- Limits come from the parameters: active invites per member, time to live (`invite.ttl_days`), tree size and depth. Reaching a limit shows its plain reason once (`copy.invite.limit_reached`) and not the numeric thresholds of fraud rules (abuse-safe).
- Referral (flag on): the declared bonus amounts are `growth.referral.bonus_referrer_credits` and `growth.referral.bonus_newcomer_credits`, paid after the newcomer has `growth.referral.min_newcomer_verified_cells` verified cells and the hold `growth.referral.hold_s`, limited to `growth.referral.max_per_referrer_per_30d`; they come from the Reserve and pause when the Reserve is empty (`ISS-06`). The copy states these as declared rules and says the bonus may be paused. It never uses "guaranteed" or "free money". [D]
- Pressure is forbidden: no counters of friends, no "invite to unlock", no bonus shown before the first accepted cell, no prompt in the first-contribution flow. [D]
- Member safety notice (`copy.invite.safety_notice`): inviting someone tells them you use Hamyar; invite only people who can decide for themselves and whom you trust; do not invite anyone for whom taking part could be unsafe. `needs_human_and_legal_review`.

**States.** Empty: no invitations yet. Loading: list placeholders. Error: `ALREADY_EXISTS`, `CAP_EXCEEDED` (limit), `copy.error.try_again`. Offline: list last known; creating disabled. Blocked: gate closed (`LAUNCH_GATE_CLOSED`), member below the accepted-cell requirement (`copy.invite.not_yet`), member restricted or suspended, flag `ff.growth.v5_referral` off (referral block hidden).

**Actions.** Create, Copy link, Copy code, Revoke, toggle "add to share card" (11.16).

**API calls.** `createInvite`, `listInvites`, `revokeInvite`, `getReferralStatus`.

**Copy intent.** Quiet, safety-first; a trust relationship, not a promotion.

**Accessibility.** Code and link are selectable, labeled, `dir="ltr"`; Revoke confirms with a sheet that names the code suffix.

**Acceptance criteria**

- `AC-vol-55` Given a member with fewer than `invite.min_accepted_cells_to_issue` accepted cells, When they open the screen, Then Create is disabled with `copy.invite.not_yet`.
- `AC-vol-56` Given an invite token in a URL, When the landing loads, Then the token is read from the fragment, sent only in the `createMember` body, and absent from every request URL and analytics event.
- `AC-vol-57` Given the issuer views the list, When any entry is inspected, Then no invitee id, handle or activity is shown, only state and dates.
- `AC-vol-58` Given `ff.growth.v5_referral` is off, When the screen renders, Then no bonus text, amount or counter appears.

## 11.18 SCR-vol-13 Recovery key handling

**Purpose.** Let a member save, confirm and, if needed, use a recovery key to restore a pseudonymous identity without e-mail (FD§3.2 step 1, FD§10 item 2). The cryptography, key format, recovery abuse limits and rotation rules are owned by S10.*; this screen specifies only what the volunteer sees and does. [D]

**Design position [D][A].** The identity key pair is created on the device at F2 (11.7). The recovery key is a separate secret of `identity.recovery_key_bits` bits (default 128) generated on the device. It is first shown after the first accepted cell (V-09), not before, because before that moment the identity holds no credit and nothing to lose, and the 60-second path stays unblocked [H]. This is a UX position, and it differs from the reading of FD§3.2 step 1 that the key is created at join; the generation is at join (so a lost device before the first cell loses nothing) and the display is deferred. Challenged in `ISS-113`.

**Wireframe: save**

```
+--------------------------------------------------+
| Save your recovery key                           |
+--------------------------------------------------+
| If you lose this device you cannot get your credit |
| back without this key. Hamyar cannot recover it    |
| for you and does not know who you are.             |
|                                                  |
|  K7Q2-M9XD-4TPB-...-W8ZA  (dir=ltr, groups of 4)  |
|  [ Copy ]  [ Show as words? ] [ Download .txt ]    |
|                                                  |
|  Keep it somewhere only you can read: not in this  |
|  chat, not in a shared note.                      |
+--------------------------------------------------+
| Confirm: type groups 3 and 7 of the key  [____][__]|
| [ I saved it ]                    ( Later )       |
+--------------------------------------------------+
```

**Wireframe: restore**

```
+--------------------------------------------------+
| Restore your identity                            |
+--------------------------------------------------+
| Enter your recovery key:  [____-____-____-...]    |
| [ Restore ]                                      |
| After a restore, spending and starting requests   |
| wait {recovery_cooldown} (declared safety rule).  |
+--------------------------------------------------+
```

**Rules [D]**

- The key is shown only after `getMember` reports the first accepted cell, only on the device, with Copy and Download as plain text. It is never sent to the server in clear; the server stores only a verifier (S10.*). Display is not logged. The screen is excluded from screenshots where the platform lets a page ask for that [V].
- Confirmation asks the member to re-enter `ui.recovery_confirm_groups` groups chosen at random from the key (default 2), proving the member saved it; success calls `confirmRecoveryKey` and removes the header marker. The member may choose Later; the marker stays, and the key can be shown again only by `rotateRecoveryKey`, which creates a new key and invalidates the old one after a confirmation that states the consequence. [D]
- The key is excluded from digit conversion (11.4.2) and rendered `dir="ltr"`; alternate "words" display is an option only if S10.* defines a word list for it [A].
- Restore: signed with a new device key; success emits `member.recovered`; the member then faces `identity.recovery_cooldown_s` (default 86,400 s) during which they cannot start jobs or spend (S10.*), shown as a declared safety rule with the end time. Attempts are limited by `ratelimit.recovery_attempts_per_day` and `identity.recovery_max_per_90d`; the screen never says which limit triggered or whether the key was close. A wrong key and an unknown key give the same answer (no account enumeration). [D]
- Honest limit statement (FD Principle 11): the screen says plainly that a recovery key is the only way back, that anyone who has it can restore the identity, and that Hamyar cannot protect a key the member shares. [D]

**States.** Empty: no key yet generated (not reachable after F2). Loading: restore in progress. Error: `RATE_LIMITED`; wrong key (`copy.recovery.not_recognized`); `copy.error.try_again`. Offline: save and confirm work offline except `confirmRecoveryKey`, which is queued; restore requires network. Blocked: member `closed` (`copy.recovery.closed`); too many attempts (`RATE_LIMITED` with time).

**API calls.** `confirmRecoveryKey`, `rotateRecoveryKey`, `startRecovery`, `completeRecovery`, `createSession`.

| Copy key | `fa` (draft) | `en` |
| --- | --- | --- |
| `copy.recovery.warning` | اگر این دستگاه را از دست بدهید، بدون این کلید نمی‌توانید اعتبارتان را پس بگیرید. همیار نمی‌تواند آن را برایتان بازیابی کند و نمی‌داند شما کی هستید. | If you lose this device you cannot get your credit back without this key. Hamyar cannot recover it for you and does not know who you are. |
| `copy.recovery.cooldown` | پس از بازیابی، خرج کردن و شروع درخواست تا {time} متوقف می‌ماند؛ این یک قاعدهٔ ایمنی اعلام‌شده است. | After a restore, spending and starting requests wait until {time}; this is a declared safety rule. |

**Accessibility.** The key is real text in groups separated by non-selectable hyphens; Copy announces success; confirmation inputs have labels with the group numbers in the member's digit style; no CAPTCHA and no time pressure.

**Acceptance criteria**

- `AC-vol-59` Given a member with no accepted cell, When they use the app, Then no recovery key is displayed and the header marker is absent; and Given the first accepted cell, Then the key is offered once and the marker appears until confirmed.
- `AC-vol-60` Given the key screen, When network requests are inspected, Then the key never appears in any request, URL, log event or analytics event.
- `AC-vol-61` Given the member enters the wrong groups at confirmation, When they tap "I saved it", Then the key remains unconfirmed, the marker stays and the member can retry or choose Later.
- `AC-vol-62` Given a wrong recovery key and an unknown one, When Restore is tapped, Then the visible result and timing class are the same, and the attempts counters are incremented.
- `AC-vol-63` Given a successful restore, When the member opens the balance screen, Then the cooldown end time is shown and spend or job start actions are blocked until it passes.

## 11.19 SCR-vol-14 Appeal

**Purpose.** Let a volunteer challenge a cell rejection, a suspension or a ban (`appeal_kind` `cell_rejection`, `member_suspension`, `member_ban`, S0.9.7). Reviewer-side handling is specified in the reviewer screens. [D]

**Entry conditions.** The decision exists, is inside `appeal.window_days`, and `appeal.max_per_decision` is not reached. Suspended or banned members can reach this screen and no other action.

**Wireframe**

```
+--------------------------------------------------+
| Appeal a decision                                |
+--------------------------------------------------+
| Decision: Not accepted ({reason copy}) {date}    |
| Appeals can be filed until {date J / G}           |
| Why do you think it was wrong?                   |
| [ text field, max appeal.reason_max_chars ]       |
|  Do not include personal data or secrets.         |
| [ Send appeal ]                                  |
| What happens next: a reviewer who did not make    |
| the decision looks at it; target {appeal.reviewer_ |
| sla_days} days (a target, not a promise).         |
+--------------------------------------------------+
| Status: filed > assigned > in review > decision   |
| [ Withdraw appeal ]                              |
+--------------------------------------------------+
```

**Rules [D]**

- The status line follows the appeal machine (`filed`, `assigned`, `in_review`, `awaiting_second_review`, `upheld`, `overturned`, `withdrawn`), shown with plain words. The reviewer is never named; the original decider is never the reviewer (S0.9.7), stated as a declared rule.
- The SLA is displayed as a target (`appeal.reviewer_sla_days`), never as a promise. Outcome copy for `overturned` states what is restored (credit via ledger reversal, `Cell.overturned` reversed, tier) in plain words and links to Balance; for `upheld` it gives the reason class and nothing that teaches evasion.
- A late filing shows `copy.appeal.window_closed`; the API error is not shown. One appeal per decision unless the parameter allows more.
- The reason text is plain text, length-limited, and visible only to reviewers; the screen warns not to include personal data.

**States.** Empty: nothing to appeal (`copy.appeal.none`). Loading. Error: `STATE_CONFLICT` (already appealed), `VALIDATION_FAILED`, `CAP_EXCEEDED`. Offline: the text is kept locally; Send disabled until online. Blocked: window closed; member `closed`.

**API calls.** `createAppeal`, `getAppeal`, `listAppeals`, `withdrawAppeal`.

**Copy intent.** Fair and calm; no suggestion that appeals are unlikely to succeed and no suggestion that they are certain to.

**Accessibility.** Status steps are an ordered list with the current step marked in text; the field has a live character count.

**Acceptance criteria**

- `AC-vol-64` Given a rejected cell inside the window, When the member sends an appeal, Then `appeal.filed` is emitted, the status shows `filed`, and a second appeal on the same decision is refused with `STATE_CONFLICT` when `appeal.max_per_decision` = 1.
- `AC-vol-65` Given an appeal is `overturned`, When the member opens it, Then the screen states what was restored and the balance reflects the ledger reversal from `getBalance`.
- `AC-vol-66` Given a banned member, When they sign in, Then only the account notice, Appeal, Help and Settings (close account) are reachable, and no offers are shown.

## 11.20 SCR-vol-15 Help

**Purpose.** Static, bundled help that answers the volunteer's likely questions in both locales, works offline and is the destination of every error state. [D]

**Wireframe**

```
+--------------------------------------------------+
| Help                                    [search] |
+--------------------------------------------------+
| Start here: what do I do?                        |
| Topics:                                          |
|  > How a task works (copy, Send, paste back)      |
|  > What is credit and when does it expire?        |
|  > Why was my answer not accepted?                |
|  > My lease ran out                               |
|  > Clean chat and memory off (service hints)      |
|  > What Hamyar never does                         |
|  > Safety and privacy: what we can and cannot say |
|  > Lost my device / recovery key                  |
|  > Report a task / appeal a decision              |
|  > Terms and rules may limit this: read this      |
+--------------------------------------------------+
```

**Rules [D]**

- All text is bundled (V-14), searchable on the device, linked by anchor from error states (`copy.error.*` has a `help_topic`). Service-specific hints come from registry-linked copy keys, never hardcoded in help text.
- Help contains no instruction on bypassing any restriction, no legal conclusion, and the topic "Safety and privacy" states what Hamyar cannot promise (pseudonymity is minimization, not anonymity; a network observer or the host may see that the app is used; a recovery key is not recoverable; sharing a card or an invite can expose the member) [V: G1 threat model, S10.*].
- A contact route is the report sheet (11.21); no support e-mail is displayed unless the operator configures one [A].
- Help states the rule "Hamyar never asks you to do more than copy, press Send and return text" and tells the volunteer to report any task that does.

**States.** Empty search: `copy.help.no_results` with the topic list. Loading: none (static). Error: none. Offline: fully available. Blocked: never blocked, available to every principal including suspended members.

**API calls.** None.

**Copy intent.** Plain language, short answers, no jargon (cell, lease and nonce words are replaced by "task", "time" and "code").

**Accessibility.** Headings in order; search is a labeled field; each topic is a link with a visible focus ring; the page is usable at 200 percent text.

**Acceptance criteria**

- `AC-vol-67` Given the device is offline, When Help opens, Then all topics render and search works.
- `AC-vol-68` Given any error state of 11.4.7, When the member taps "Help", Then the matching topic opens at its anchor.
- `AC-vol-69` Given Help topics are scanned, When their text is inspected, Then none contains an instruction to bypass a regional or technical restriction, a legal conclusion, or the word "guaranteed" in a promise.

## 11.21 SCR-vol-16 Report sheet and SCR-vol-17 Identity and display settings

### 11.21.1 SCR-vol-16 Report sheet

**Purpose.** Report a task, an output or an account problem in two taps. Opened from the card, from feedback and from History. [D]

```
+--------------------------------------------------+
| Report this task                                 |
+--------------------------------------------------+
| What is wrong?   ( ) asks me to open a link / install / log in
|                  ( ) looks like personal or private data
|                  ( ) harmful, illegal or abusive content
|                  ( ) asks for something beyond copy, Send, paste
|                  ( ) other: [________]            |
| [ Send report ]     ( Also decline this task )     |
+--------------------------------------------------+
```

- Creates a `Report` (state `open`, S0.9.8) tied to the cell and the lease, with a reason code from a fixed list [A] and optional text (length-limited, plain text). Limited by `report.max_per_member_per_day`. No penalty for reporting, and a volunteer is never told who the requester is. Triage target is `report.triage_sla_days`, shown as a target. An autopause of the template can follow when several reports arrive (`template.autopause_report_count` in `template.autopause_window_s`); the screen does not say whether a report triggered a pause (abuse-safe).
- States: Empty (not reachable); Loading (sending); Error: `RATE_LIMITED`, `copy.error.try_again`; Offline: the report is kept locally and sent when online; Blocked: suspended members can still report (it is a safety channel).
- API: `createReport`. Copy intent: calm, thanks without praise. Accessibility: radio group with legend; the optional text has a live count.
- `AC-vol-70` Given the volunteer reports a card, When they tap Send report, Then a `Report` in state `open` is created, no decline occurs unless chosen, and no trust-tier or credit change results.
- `AC-vol-71` Given more reports than `report.max_per_member_per_day`, When the next is sent, Then `RATE_LIMITED` is shown with the time and the draft is kept.

### 11.21.2 SCR-vol-17 Identity and display settings

**Purpose.** Language, digits, calendar, time zone, device linking, key rotation, and closing the account. [D]

```
+--------------------------------------------------+
| Settings                                         |
+--------------------------------------------------+
| Language        (o) Persian  ( ) English          |
| Digits          (o) Persian  ( ) Latin            |
| Calendar        (o) Jalali   ( ) Gregorian        |
| Time zone       Device  [choose a zone v]         |
+--------------------------------------------------+
| Devices         [ Link another device ] (code)    |
| Key             [ Rotate my device key ]          |
| E-mail (optional): none  [ Add ]  (used only for  |
|                  recovery help? S10.* decides)     |
+--------------------------------------------------+
| Close my account  (confirmation, states what is   |
|                    deleted and what is kept)      |
+--------------------------------------------------+
```

- Display options are device-local (11.4.2); time zone is the device zone by default and an IANA zone if chosen, never inferred from an IP address (S0.6.2).
- **Link another device:** `createDeviceLinkCode` shows a one-time code valid `identity.device_link_code_ttl_s` (default 300 s); the new device enters it with `redeemDeviceLinkCode`; success emits `member.device_linked`; the old device is told. The screen explains that a linked device holds full access to the identity. [D]
- **Rotate key:** `rotateMemberKey` replaces the device key with a grace period `identity.key_rotation_grace_s`; emits `member.key_rotated`; a confirmation states the consequence.
- **E-mail:** optional (`identity.email_optional`); if S10.* allows it, the screen says in plain words what the address is used for and that adding it can link the identity to a person; it is never requested elsewhere. [A]
- **Close account:** `closeMember` after a confirmation that states what is deleted or reduced to an opaque id (`member_bound` retention, S0.7) and that ledger records without personal data remain (`permanent` retention); irreversible; shows the credit that will be forfeited. Emits `member.closed`.
- States: Loading; Error with retry; Offline: display options still change (device-local), server actions disabled; Blocked: suspended or banned members can change display options and close the account, nothing else.
- `AC-vol-72` Given the member changes language, digits and calendar, When any screen renders, Then the choices apply immediately, are stored only on the device and no server call carries them.
- `AC-vol-73` Given a link code older than `identity.device_link_code_ttl_s`, When it is redeemed, Then it is refused with `NOT_FOUND` and the same message as an unknown code.
- `AC-vol-74` Given the member confirms Close account, When `closeMember` completes, Then the identity status is `closed`, the device key and session are removed and the confirmation shows what was kept.
