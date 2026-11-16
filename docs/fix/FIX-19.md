# FIX-19: S0 state machines, missing transitions

Cell C-090. Sources: `docs/audit/A15.md` findings 21, 22, 25, 33, 34, 35 and `docs/audit/A06.md` findings 27, 32. Only `spec/00-conventions.md` was edited. File:line values are those of the file after the edits and are approximate (+-3). Nothing was run; CI runs the acceptance checks. `docs/audit/FINAL.md` section 4 has no default for any edit below, so no edit is marked default-pending. The Founding Document was not re-read for these edits: they rest on the text of A15, A06, FINAL, `spec/05b-state-machines.md` (5.22.1, 5.22.3, 5.23.4, 5.26) and S0 itself.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| A15 #21 Commons path into `admitted` | spec/00-conventions.md:393 | `job.escrow_confirmed` described only as escrow_hold posted | Same event now reads member job: escrow_hold posted; Commons job: confirmed by an admin, no hold and no Escrow (05b 5.22.3). No new event or state | applied |
| A15 #22 early exit, closure reason | spec/00-conventions.md:399 | `job.stop_requested` closure reasons ended at `overrun_timeout` | `cells_exhausted` added with its condition (no primary cell non-terminal, at least one exhausted), promoted from 05b convention addition 4 | applied |
| A15 #22 early exit, cell side | spec/00-conventions.md:424 | `cell.attempts_exhausted` row had no consequence for the job | Row now says a primary cell that ends there can never be accepted and the job leaves by `job.stop_requested` with `cells_exhausted` | applied |
| A15 #22 `assembling` has no failure exit | spec/00-conventions.md:398 | `assembling --job.assembled--> settling` only | not changed; `assembling` is not a source of `job.stop_requested` in S0 or in 05b JT-15, and adding one is a design choice with no default in FINAL section 4 | skipped-needs-owner |
| A15 #25 Submission transitions, `checks_failed` against `rejected`, cell during quarantine | spec/00-conventions.md:436-448 | States and events listed, no transitions | Nine transitions added with targets for `submission.quarantined`, `submission.released_from_quarantine` and `submission.rejected`; text separates `checks_failed` (failed before acceptance) from `rejected` (checks passed, cell then rejected or voided); the cell stays `submitted` during quarantine, bounded by `screen.quarantine_max_age_days` | applied |
| A06 #32 release returns to verification | spec/00-conventions.md:444 | no S0 transition; 05b SBT-06 says `quarantined` to `checks_passed` | `quarantined --submission.released_from_quarantine--> received`, described as return to verification (gold, audit, automatic checks), not to `checks_passed`. 05b SBT-06 and S9 9.9 are outside the allowed paths and must be aligned by their own cells | applied |
| A15 #33 Audit third state | spec/00-conventions.md:521 | states stopped at `third_pending`; `audit.resolved` had no source | State `third_executed` added; `audit.third_submitted` leads to it and `audit.resolved` leaves it; `audit.cancelled` sources named. Name `third_executed` is parallel to `second_executed` [A] | applied |
| A15 #34 Referral machine | spec/00-conventions.md:525, 535-537 | no machine | States `held`, `released` (T), `revoked` (T), events `referral.created`, `referral.released`, `referral.revoked`; hold is `growth.referral.hold_s` [A] | applied |
| A15 #34 Alarm machine | spec/00-conventions.md:526, 538 | no machine | States `raised`, `acknowledged` (T), events `alarm.raised`, `alarm.acknowledged` [A] | applied |
| A15 #34 Invite machine | spec/00-conventions.md:527, 539-540 | no machine | States `issued`, `redeemed` (T), `expired` (T), `revoked` (T), events `invite.issued`, `invite.redeemed`, `invite.expired`, `invite.revoked`; lifetime `invite.ttl_days` [A] | applied |
| A06 #27 Service `suspended` to `in_review` | spec/00-conventions.md:490 | n/a | `suspended` was already a source of `service.review_started` (A15 finding 30), with the lapse-only rule, matching 05b SVT-02 | already-applied |
| A06 #27 Service `in_review` to `revoked`, with `inflight_policy` | spec/00-conventions.md:499 | `service.revoked` sources were `approved`, `review_due`, `suspended` | `in_review` added; the line states `inflight_policy` (`drain` or `void`) and `job.stop_requested` with `service_revoked`. 05b SVT-09 still lists no `in_review` source and must follow | applied |
| A15 #35 events for `launch.member_jobs_enabled`, `launch.minting_enabled` | spec/00-conventions.md:531 | only `launch.members_may_join_changed` named | not changed; whether the dedicated name is redundant (`parameter.changed` covers all three) or two events are missing is undecided and FINAL section 4 has no default | skipped-needs-owner |

## Read-back

All places were re-read after the edits.

- Line 393 (Job `escrow_confirmed`): shows both a member-job and a Commons-job reading; the event name is unchanged.
- Line 399 (`job.stop_requested`): the closure list now ends with `cells_exhausted` and says non-primary cells are cancelled.
- Line 424 (`cell.attempts_exhausted`): the row names the early exit through `cells_exhausted`.
- Lines 436-448 (Submission): a paragraph and a code block; the quarantine paragraph says the cell "stays `submitted`"; nine rows cover `received`, `schema_failed`, `checks_passed`, `checks_failed`, `quarantined`, release, age-out, `accepted` and `rejected`; the release row goes to `received`.
- Line 499 (`service.revoked`): five source states including `in_review`, and the `inflight_policy` effect is stated.
- Line 490 (`service.review_started`): `suspended` is among the sources, unchanged.
- Line 521 (Audit row): eight states with `third_executed` between `third_pending` and `resolved`.
- Lines 525-527 (table): three new rows for `Referral`, `Alarm`, `Invite`, each tagged [A]; the stray space in the `Referral` row was corrected.
- Lines 531-543 (transitions block): Audit, Referral, Alarm and Invite transitions, each non-terminal state has an exit; every terminal state is marked (T).
- Not changed, as logged above: line 398 (`assembling`) and the launch event names in line 531.

Residual items for other cells: 05b SBT-06 and SVT-09, S9 9.9.2 and S8 audit text must be aligned with the S0 rows above; the state and event names of `Referral`, `Alarm` and `Invite` and `third_executed` must be confirmed by 05a, S8, S10 and S12 at assembly (no rename was made).

Result: DONE WITH SKIPS
