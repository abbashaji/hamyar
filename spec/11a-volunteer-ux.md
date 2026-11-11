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
