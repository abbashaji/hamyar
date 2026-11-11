# 11. Requester experience screens (part 11b)

*Spec part 11, file 11b (requester). Binding vocabulary: `spec/00-conventions.md` (S0.*). The Founding Document draft v0.1 is cited as FD§N. Nothing here is legal advice and nothing is verified against any provider's terms or any law. Every Persian string in this file needs human and legal review before use (marker `needs_human_and_legal_review`, S0.5).*

**Placement.** S11 is split over several files (sub-block rule, S0.4). This file owns the requester screens `SCR-req-01`..`SCR-req-18`, the copy keys `copy.req.*`, the acceptance criteria `AC-req-nn` and the issues `ISS-114`..`ISS-116`. Volunteer, reviewer and operator screens live in sibling files and are not repeated here. Heading numbers start at `11.31` so they cannot collide with sibling files [A] (`ISS-114`).

## 11.31 Scope, coverage and reading guide

Coverage of the requester items of prompt scope F (every item is a decision, table, schema, pseudocode or Given/When/Then below):

| Prompt scope F requester item | Section | Screens |
| --- | --- | --- |
| Job creation wizard: template choice | 11.35, 11.36 | `SCR-req-02` |
| Data upload and screening, with the screening result display | 11.36 | `SCR-req-03`, `SCR-req-04` |
| Metadata declarations with plain-language P/L/S/M explanations | 11.36, 11.44 | `SCR-req-05` |
| Policy result with reason codes | 11.36, 11.43 | `SCR-req-06` |
| Price and window quote showing the p = 1 + v + lambda breakdown | 11.37 | `SCR-req-07` |
| Escrow confirmation and the 'downstream use uncontrolled' notice for open licenses | 11.36, 11.45 | `SCR-req-08` |
| Job progress with a per-cell status map (panel status-graph and bottleneck ideas, [V]) | 11.39, 11.48 | `SCR-req-12`, `SCR-req-13` |
| Cancellation and refund display | 11.40 | `SCR-req-14`, `SCR-req-15` |
| Waitlist and reservation screens | 11.38 | `SCR-req-09`..`SCR-req-11` |
| Results download with provenance manifest, including the manifest JSON schema | 11.41, 11.42 | `SCR-req-16` |
| Rating of the outcome | 11.41 | `SCR-req-17` |
| Requester-visible rejection reasons in EN and FA | 11.43 | `SCR-req-06`, `SCR-req-18` |
| Copy for policy, privacy and risk notices in FA and EN | 11.45 | all |
| Persian first: RTL, numerals, Jalali and Gregorian, mixed direction, accessibility, low bandwidth | 11.33, 11.46 | all |
| Home of the requester area (entry to all of the above) | 11.36 | `SCR-req-01` |

**Owned elsewhere (this file only states which fields it needs from them).**

| Topic | Owner | What 11b consumes |
| --- | --- | --- |
| Price formula, escrow postings, refund and settlement rules, admission algorithm, reservations rules | S6.* | `quote`, `escrow`, `window`, `receipt`, `reservation.terms` fields (11.34) |
| Policy evaluator, allowlist, license options, reason-code semantics | S7.* | `getPolicyProfile`, `rejection.reasons` |
| Template format, data slots, splitter, output formats | S8.* | `template.input_slots`, `cell_count`, `deliverable.files` |
| Input screening rules, quarantine, output flagging | S9.* | `upload.screen_status`, `findings`, `withheld_for_review` |
| Identity, session, recovery, rate limits | S10.* | auth failures, `identity.recovery_cooldown_s` |
| API paths and schemas | S15.* | operation ids in 11.34 are the contract; paths there are proposals [A] |

## 11.32 Requester decisions

Each row is a decision [D] that every requester screen obeys.

| ID | Decision | Reason |
| --- | --- | --- |
| `RD-01` | The client displays server values and never computes a price, a window, a refund, a policy outcome or a deadline. The only client arithmetic is display conversion of integers (11.33.3), done with arbitrary-precision integers, never floating point. [D] | Ledger amounts are exact integers (S0.6.1); two implementations of the price would drift. |
| `RD-02` | User-facing promises say "declared", never "guaranteed"; a quoted window is never presented as instant completion. [D] | FD Principle 11 and Principle 10. |
| `RD-03` | The wizard may use the active allowlist (`getPolicyProfile`) to grey out and explain combinations, but the server decision is final and a hint is never a promise. [D] | Policy is data and can change at any time (`R9`, `R10`). |
| `RD-04` | The wizard is a server-side draft (`Job.draft`). The browser keeps only in-memory state and the current step name; no uploaded text, glossary or result is written to browser storage. [D] | Shared devices and member safety (FD Principle 8); S0.7 retention classes. |
| `RD-05` | Declaring `S2` or `S3` honestly is not punished: the job is not accepted, the reason is shown, nothing is charged. Only false declarations found later fall under abuse handling (S10.*). [D] | An honest answer must be the easy path (FD§5.7 failure mode 1). |
| `RD-06` | The price breakdown (`v`, `lambda`, `p`, `eta`) is always shown and always says whether `v` is measured or the prior. [D] | Verification cost is shown, not hidden (FD§4.3). |
| `RD-07` | Escrow confirmation is the only requester action that spends credit; it is an explicit button bound to the hash of the quote the person saw; initial focus is on the summary, not on the button. [D] | Prevents accidental spend and price drift. |
| `RD-08` | A requester never sees a volunteer identity, a `vol_` handle, a gold cell, or any timing finer than the granularity in 11.42. [D] | FD§5.6, S0.6.4, member safety. |
| `RD-09` | For licenses `L1` and `L2` the notice "downstream use uncontrolled" is shown on the declarations step, requires acknowledgement on escrow confirmation, and is repeated on the results screen and in the manifest. [D] | FD§5.7 failure mode 3: "the card and the job form must say so". |
| `RD-10` | No result is shown before assembly or partial settlement. [D] | A cell can be overturned (`cell.overturned`); showing then retracting output would mislead. |
| `RD-11` | A `rejected`, `quote_expired` or `cancelled` job is terminal. "Fix and resubmit" creates a new job that copies declarations and uploads (`createJob` with `copy_from_job_id`). [D] | Keeps the Job machine of S0.9.2 unchanged. |
| `RD-12` | No requester screen mentions, suggests or enables bypassing a regional or technical restriction or a service's terms. [D] | FD Principle 9, prompt ground rule 3. |
| `RD-13` | Every state a requester must act on is reachable by polling the app; notification channels are optional extras (in-app, plus e-mail only if the member gave one, `identity.email_optional`). No push service is required. [D][A] | No mandatory third-party dependency; low bandwidth; S10.* decides channels. |
| `RD-14` | Everything that originates from volunteers or uploads (outputs, file names, glossary terms, reported model names) is untrusted text: rendered with text-only APIs, never as HTML or Markdown, never auto-linked, never executed; mixed-direction text is isolated (11.46). [D] | FD§10 item 4, prompt scope E. |
| `RD-15` | Numbers in copy are placeholders (`{n}`) bound to parameter values or server fields, never literals. [D] | S0.2 writing rule 2. |

## 11.33 Shared contracts

### 11.33.1 Per-screen format [D]

Every screen below uses these rows: **Purpose**, **Entry conditions**, **Blocks** (top to bottom), **States**, **Actions** (with the API operation id from 11.34), **Copy intent** (copy keys, 11.43-11.45), **Accessibility**, and **Given/When/Then** (`AC-req-nn`). The states `loading`, `error_retry`, `offline`, `auth_required`, `gate_closed`, `kill_switch`, `rate_limited` and `member_blocked` are global (11.33.2) and are not repeated; a screen lists only its own states.

### 11.33.2 Global states [D]

| State | Trigger | Behaviour |
| --- | --- | --- |
| `loading` | request in flight | Text placeholder with the screen title already visible; announced politely to assistive technology; no spinner-only content |
| `error_retry` | network failure, `INTERNAL`, `UNAVAILABLE` | Entered data is kept in memory; a Retry button re-sends with the same `Idempotency-Key` (11.33.4); `Retry-After` honored |
| `offline` | no connectivity | Banner; read-only view of the last loaded data of this visit; no write is attempted |
| `auth_required` | `AUTH_REQUIRED`, `AUTH_INVALID`, `AUTH_EXPIRED` | Hand off to member session restore (S10.*); return to the same screen and step afterwards |
| `gate_closed` | `403 LAUNCH_GATE_CLOSED` (`launch.member_jobs_enabled` is false) | Whole requester area shows `copy.req.err_gate_closed`; no form is rendered; nothing is charged |
| `kill_switch` | `503 KILL_SWITCH_ENGAGED` (`kill.all_new_jobs`, `kill.template.<tpl_id>`, `kill.service.<svc_id>`) | Creation actions disabled with `copy.req.err_kill_switch`; existing jobs stay readable |
| `rate_limited` | `429 RATE_LIMITED` | Disabled action with a countdown from `Retry-After`; never auto-repeats faster than allowed |
| `member_blocked` | `403 FORBIDDEN`, `member_status` `suspended` or `banned`, or `identity.recovery_cooldown_s` not elapsed | Read-only; shows the reason class and, for a cooldown, the end time in local time |

### 11.33.3 Display rules [D]

| Item | Rule |
| --- | --- |
| Amounts | Wire format is an integer string of `ucr`. Display `whole = ucr div 1,000,000` and `frac = ucr mod 1,000,000`. Summary lines show `ui.credit_display_decimals` decimals; balances round down, prices and escrow round up (S0.6.1); detail views show the exact value with up to 6 decimals, trailing zeros trimmed |
| Ratios | Wire format is integer `*_ppm`. Display three decimals (`ui.ratio_display_decimals`), half-up; the detail view shows the exact ppm. Example: `eta_ppm` 869,565 shows 0.870 |
| Dates and times | RFC 3339 UTC on the wire; shown in the device time zone or the zone chosen in settings (S0.6.2); every deadline shows the local time next to any UTC day boundary; detail views show Jalali and Gregorian together (`i18n.dual_calendar_detail`) |
| Digits | `fa` locale uses Persian numerals by default `i18n.digits_default_fa`, switchable to Latin; stored copy contains Latin placeholders only |
| Identifiers | `job_` ids are shown shortened (last 8 characters) with a copy button; the full id is in the detail view; never parsed for meaning (S0.6.3) |
| Hashes | Shown as the first 12 hex characters with a copy button for the full value |

### 11.33.4 Idempotency and retry rule [D]

```
for every write action (S0.11.5 requires a key on job, escrow, report, appeal writes):
  action_key = new_ulid()                      # matches ^[A-Za-z0-9_-]{16,64}$
  loop:
    resp = send(method, path, body, header Idempotency-Key = action_key)
    if network_error or status >= 500: retry with the SAME key and the SAME body (jittered exponential backoff,
                                       honors Retry-After and RateLimit-Remaining; schedule is client-side, not specified)
    if 409 IDEMPOTENCY_IN_PROGRESS:    wait Retry-After, retry with the SAME key
    if 422 IDEMPOTENCY_KEY_MISMATCH:   client bug; stop; show copy.req.err_internal; never retry
    else:                              stop (2xx and deterministic 4xx are stored and replayed by the server)
  if the person changes any field after a failed attempt: action_key = new_ulid()
```

The key lives in memory for the duration of one user action. A double tap on Confirm therefore sends the same key twice and the server replays the stored response (`Idempotent-Replayed: true`), so credit cannot be spent twice (S0.11.5, natural idempotency of `escrow_hold`).
