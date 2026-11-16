# FIX-13: API consistency corrections to 15b, part 1 (15.21 to 15.28)

*Cell C-084. Applies the corrections of `spec/15g-api-consistency.md` `## Corrections required` that target `spec/15b-api-admin.md`: CR-04, CR-05, CR-06, CR-07, CR-11, CR-20, CR-21, CR-22, CR-24, CR-27, CR-32. Edits are small old-to-new replacements inside `spec/15b-api-admin.md`; no id, parameter, endpoint or state was renamed except as the CRs authorize. Lines are the lines after the edits. Nothing was run; CI runs acceptance. Where an edit follows a default of `docs/audit/FINAL.md` section 4 it is marked default-pending [D].*

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| CR-04a wrong-scheme rule on admin routes | spec/15b-api-admin.md:26 | no statement what a member token does on an admin route | member token is `401 AUTH_INVALID` `wrong_scheme`, never 403/404, not stored under a key | applied |
| CR-04b ignored header on `none` routes | spec/15b-api-admin.md:26 | not stated | `Authorization` on a `none` operation is ignored and never logged | applied |
| CR-04c wrong-scheme in 15.22.1 | spec/15b-api-admin.md:87 | only the `assertion_invalid` bullet | new bullet repeats `wrong_scheme` for admin routes | applied |
| CR-05a four bootstrap operations are `none` | spec/15b-api-admin.md:26 | exception undocumented | four ops listed, deliberate exception to S0 0.11.2 stated | applied |
| CR-05b precedence on the two dual rows (V-03) | spec/15b-api-admin.md:87 | not stated | `enrollment_code` request is `none`; otherwise admin `SU`; any other token `wrong_scheme` | applied |
| CR-05c one sentence in S0 0.11.2 | spec/00-conventions.md | n/a | not editable in this cell (path not allowed); referenced from :26 | skipped-not-found |
| CR-06a `X` marker in the Idem legend | spec/15b-api-admin.md:15 | `req`, `opt`, `n/a` | adds `X` = key ignored and never stored | applied |
| CR-06b rule 4 exception list | spec/15b-api-admin.md:49 | three unauthenticated endpoints, key optional | four ops marked `X` | applied |
| CR-06c `startAdminLogin` | spec/15b-api-admin.md:94 | `opt` | `X` | applied |
| CR-06d `createAdminSession` | spec/15b-api-admin.md:95 | `opt` | `X` | applied |
| CR-06e `createCredentialChallenge` | spec/15b-api-admin.md:171 | `opt` | `X` | applied |
| CR-06f `createStepUpChallenge` | spec/15b-api-admin.md:108 | `req` (set by audit A12 finding 21) | `X`, as IG-03 lists all four | applied |
| CR-06g name `registerAdminCredential` in rule 4 | spec/15b-api-admin.md:49 | not named | named, stays `req`, stored body holds no secret, IP-hash scope | applied |
| CR-06h admin idempotency scope | spec/15b-api-admin.md:49 | defined for members only | (`adm_` id, method, path template, key) for 24 hours | applied |
| CR-06i POST that changes nothing takes `opt` (IG-08) | spec/15b-api-admin.md:49 | not stated | stated with four example ops | applied |
| CR-06j consistency note in ISS-155 (supplementary, same file) | spec/15b-api-admin.md:1139 | says three endpoints take the key as optional | appended sentence: superseded by CR-06 | applied |
| CR-07a no secret in `AdminApproval.result` | spec/15b-api-admin.md:127 | code "never stored in clear" | `result` carries only a `secret_ref`; code only in the final `200`, encrypted in the idempotency record, purged | applied |
| CR-07b replay semantics of `2P` (IG-06) | spec/15b-api-admin.md:152 | undefined | initiation replay returns stored `202`; row status makes execution once-only; final replay returns stored `200` | applied |
| CR-07c `createAdminUser` response row | spec/15b-api-admin.md:170 | code shown once to the approving admin | unchanged, already consistent with CR-07a | already-applied |
| CR-11a `content_hash` on the lock request | spec/15b-api-admin.md:679 | `{reason}` | `{content_hash, reason}` with `hash_mismatch` | applied |
| CR-11b hash bound to approvers and re-checked | spec/15b-api-admin.md:681 | hash defined only | step-up bound to it, re-checked at execution | applied |
| CR-11c `lock_pending` | spec/15b-api-admin.md:678 | `locked` only | `lock_pending` while a lock approval is pending | applied |
| CR-11d status `registered` | spec/15b-api-admin.md:685 | `draft, running, stopped` | `draft, registered, running, stopped` | applied |
| CR-11e `startExperiment` guard | spec/15b-api-admin.md:693 | re-read `fraction_source` at start | starts from `registered` only; no re-read; `not_registered` | applied |
| CR-11f `AC-admin-25` | spec/15b-api-admin.md:1117 | prereg locked then start | `registerExperiment` needed; `not_registered`; `lock_pending` | applied |
| CR-11g carry part 13 `content` as one field, hashed once | spec/15b-api-admin.md:681 | `content_hash` over scope, title, thresholds, decision_rules, linked ids | not changed: needs part 13 shape (13.7) and an owner decision not in FINAL section 4 | skipped-needs-owner |
| CR-20a evidence entry fields | spec/15b-api-admin.md:408 | `kind, ref, sha256?, note, ...` | adds `visibility` (incl. `restricted`), `media_type`, `size_bytes`; bytes stored up to `launch.evidence_max_bytes` | applied |
| CR-20b sign-off fields | spec/15b-api-admin.md:409 | `admin_id, signed_at, comment` | adds `outcome`, `conditions_text`, `generation`, `valid_until`, `watch_digest`, digest challenge | applied |
| CR-20c sign-off and attach requests | spec/15b-api-admin.md:419 and :420 | `{kind, ref, sha256?, note}` and `{comment}` | adds `visibility?`; `{comment, outcome, conditions_text?}` | applied |
| CR-20d step-up bound to digest | spec/15b-api-admin.md:423 | bound to evidence hash | also WebAuthn challenge equals the sign-off digest | applied |
| CR-20e evidence `kind` enum replaced by S14 list | spec/15b-api-admin.md:408 | `service_review, terms_copy, counsel_ref, threat_model_ref, calibration_ref, measurement_ref, fallback_decision, other` | not changed: `service_review`, `threat_model_ref`, `fallback_decision` (used at :419 and :452) have no S14 equivalent and no default in FINAL section 4 | skipped-needs-owner |
| CR-21 chunked evidence upload | spec/15b-api-admin.md:425 | no path above 1,048,576 bytes | three ops, 785,408-byte chunks, 14 chunks for 10,485,760 bytes; ids `evu_` marked [A] | applied |
| CR-22a approval-time guard | spec/15b-api-admin.md:455 | S15b clauses only | `evaluate_switch` plus the three S15b-only clauses; `LaunchAuthorization` with `authorized_until` | applied |
| CR-22b `getLaunchStatus` | spec/15b-api-admin.md:461 | no authorization state | adds `authorization {authorized_until, revoked_at}` and live `reasons` | applied |
| CR-22c `changeLaunchSwitch` execution | spec/15b-api-admin.md:462 | blockers recomputed | also writes `LaunchAuthorization` with the `ParameterVersion` in one transaction | applied |
| CR-22d cascade | spec/15b-api-admin.md:455 | none | closing `launch.member_jobs_enabled` closes `launch.minting_enabled` | applied |
| CR-22e event mapping (EV-09) | spec/15b-api-admin.md:455 | S14.11 names unmapped | proposal, approval, close and release proposal mapped | applied |
| CR-22f case 2 names `launch_integrity_check` | spec/15b-api-admin.md:517 | not named | named | applied |
| CR-22g rule-stops-holding paragraph | spec/15b-api-admin.md:464 | switch never flips by itself | S14.8.3 closes it as `system` (P3); old reasoning kept as overridden | applied |
| CR-24a `approvalGuard` flags (default-pending D-16) | spec/15b-api-admin.md:260 | two flags | four flags | applied |
| CR-24b `approvalGuard` `g0.svc.*` items | spec/15b-api-admin.md:263 | no item check | every `g0.svc.*` item signed and valid (default-pending D-16) | applied |
| CR-24c `details.missing` | spec/15b-api-admin.md:273 | `gate_flag_not_yes` for two flags | also two added flags and `g0_item_not_valid:<catalog_key>` | applied |
| CR-24d `reopenGateItem` | spec/15b-api-admin.md:421 | no effect on the service | service to `review_due`, `service.review_due` with `cause` `item_reopened` | applied |
| CR-27 "grants that mint" | spec/15b-api-admin.md:486 | grants that mint answer 503 | removed; `grant` and referral postings are not mint | applied |
| CR-32a rule 9 health | spec/15b-api-admin.md:740 | endpoint named in S0 0.12, none specified | `GET /v1/public/health`, `getPublicHealth`, S15c 15.B.8.3 | applied |
| CR-32b rule 6 always-on list | spec/15b-api-admin.md:737 | parameters, change log, metrics, pre-registrations, verification | adds policy, capacity, health, experiments, teams | applied |

## Read-back

After all edits every edited place was read again on the branch; what is there now:

- :26 states the `wrong_scheme` rule, the ignored header on `none` routes and the four bootstrap operations, ending with "separation of the two surfaces is not broken". (CR-04a, CR-04b, CR-05a)
- :87 holds the new bullet with `wrong_scheme` and the `enrollment_code` precedence. (CR-04c, CR-05b)
- :15 legend lists `X`; :49 rule 4 lists the four `X` operations, `registerAdminCredential` as `req`, the `opt` rule for no-state POSTs and the 24-hour admin scope. (CR-06a, b, g, h, i)
- :94, :95, :171 and :108 show `X` in the Idem column; :172 `registerAdminCredential` still shows `req`. (CR-06c to f)
- :1139 ISS-155 now ends its point (2) with the note that CR-06 supersedes it. (CR-06j)
- :127 `result` mentions only a `secret_ref`; :152 gives the replay rules; :170 is unchanged. (CR-07a, b, c)
- :678 shows `lock_pending`; :679 shows `{content_hash, reason}` and `hash_mismatch`; :681 says the lock request names the hash and is re-checked. (CR-11a, b, c)
- :685 status list includes `registered`; :693 says "from `registered` only" and `not_registered`; :1117 lists `registerExperiment` and `lock_pending`. (CR-11d, e, f)
- :408 and :409 carry the added evidence and sign-off fields; :419 and :420 show the new request fields; :423 names the digest; :408 still lists the old `kind` enum. (CR-20a to d; CR-20e not applied)
- :425 to :433 define the three upload operations and "14 for a maximal upload". (CR-21)
- :455 holds the approval-time guard paragraph with the event mapping; :461 shows `authorization` and `reasons`; :462 shows the `LaunchAuthorization` write; :464 says S14.8.3 closes the switch; :517 names `launch_integrity_check`. (CR-22a to g)
- :260 lists four flags; :263 has the `g0.svc.*` line marked default-pending D-16; :273 lists `g0_item_not_valid:<catalog_key>`; :421 moves the service to `review_due`. (CR-24a to d)
- :486 now reads "cell acceptance; `grant` and referral postings are not mint". (CR-27)
- :737 rule 6 has the extended always-on list; :740 rule 9 names `GET /v1/public/health`. (CR-32a, b)

## Skips and notes

- CR-05c: S0 0.11.2 is outside the allowed paths; the sentence is still to be added by the S0 fix cell.
- CR-11g: the part 13 `content` field needs 13.7 and an owner decision with no default in FINAL section 4.
- CR-20e: replacing the evidence `kind` enum would orphan `service_review` (:419) and `fallback_decision` (:452); the mapping needs an owner decision.
- CR-22g overrides an earlier sentence of this file by P3 of 15g; the old reasoning is kept in the text.
- CR-11 targets 15.32 and CR-32 targets 15.33.1; both were applied because the cell lists them.
- CR-06f replaces the `req` that audit A12 finding 21 set on `createStepUpChallenge`.
- New ids and names (`evu_`, the three upload operations, `LaunchAuthorization`) are convention additions [A] for the next S0 edit.

Result: DONE WITH SKIPS
