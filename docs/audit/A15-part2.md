# A15 part 2: conventions 0.8-0.9 (enums, states)

Scope: sections 0.8 and 0.9 of `spec/00-conventions.md`. Line numbers in the findings are those of base 96231b6, before this cell's edits.

## Checked

- 0.8.1 against FD§5.3: codes P0-P3, L0-L3, S0-S3, M0-M2, meanings, pairings, statuses. Matches except the S1 wording (see below the table).
- 0.8.2 roles and principals against FD§3.1 and 0.11.4 (`auth_scheme` values and prefixes).
- 0.8.3 flag keys against FD§5.3 and FD§8.3 G0(a)-(k): every letter has a key; `flag_answer` values; approval rule against FD§5.3.
- 0.8.4 rules R1-R10 and slugs against FD§5.4; the `policy.<rule>.<slug>` form against 0.9.2 and 0.11.3.
- 0.8.5 account types, entry types and transaction kinds against FD§4.2 (mint, transfer, Reserve, retire, invariant) and the double-entry sum.
- 0.8.6 enums against 0.9.4, 0.10.3, `i18n.*` and 0.7 (entity names, prefixes, CHECK rule).
- 0.9.1 naming rules against 0.5 (log events) and the state and event names used in 0.9.2-0.9.8.
- 0.9.2-0.9.8: every state is reachable, every non-terminal state has an exit, terminal marks, event completeness, and the parameters each machine names (`lease.*`, `cell.max_attempts`, `template.*`, `service.*`, `appeal.*`, `trust.*`). Cell lifecycle against FD§3.4.

## Findings

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | major | spec/00-conventions.md:285 | 0.8.3 evaluated `unknown` as `no` everywhere, but `info.provider_trains_on_chats`, `info.memory_or_connectors_risk` and `info.allowance_may_change` have risk polarity (`yes` = the risk exists), so `unknown` read as `no` means no risk, the unsafe direction for volunteer advice. Rule now covers gating flags; `info.*` unknown is shown as unknown [A]. | fixed |
| 2 | minor | spec/00-conventions.md:287-301 | FD§5.3 lists automation limits among the registry flags; no `flag_key` covers it (G0(c) is split into `human_copy_paste_use` and `prefilled_link_use`, the automation and scraping half has no key). Gate or info, and its polarity, is an owner decision. | logged-needs-owner |
| 3 | minor | spec/00-conventions.md:341 | The `grant` row fixed the referral lot lifetime to `credit.lifetime_days`, contradicting 0.6.2 (members in the accelerated arm get `credit.lifetime_days_accelerated`). Now points to the 0.6.2 rule. | fixed |
| 4 | minor | spec/00-conventions.md:364-366 | `appeal_kind` (0.9.7), `closure_reason` (0.9.2) and `trust_tier` (0.9.4) are stored enums defined outside 0.8, while 0.7 says enum columns are CHECKed against 0.8. Pointer row added to 0.8.6. | fixed |
| 5 | minor | spec/00-conventions.md:374 | 0.9.1 defines (T) as terminal, but `Cell.accepted` (T) has the outgoing `cell.overturned` (line 427). Definition now allows a named correction event. | fixed |
| 6 | minor | spec/00-conventions.md:392 | The only way into `Job.admitted` is `job.escrow_confirmed` (escrow_hold posted). Commons jobs mint credit and have no requester escrow, so their path into `admitted` is unnamed. | logged-cross-part |
| 7 | minor | spec/00-conventions.md:396-398 | A primary cell that ends `exhausted` or `voided` can never be accepted, so the job cannot reach `assembling`; its only exit is `overrun_timeout` (no early closure reason), and `assembling` has no failure exit. | logged-cross-part |
| 8 | major | spec/00-conventions.md:414-415 | `lease.submit_grace_s` (late paste-back accepted if the cell is not re-leased) had no transition: Lease events start only from `active` and rejected or expired cells requeue at once. Added `Cell.queued` or `Cell.expired` to `submitted` on `cell.submitted`, and Lease `expired` to `submitted` within the grace. | fixed |
| 9 | major | spec/00-conventions.md:430 | `lease.max_extensions` and `lease.extend_s` had no Lease event. Added `lease.extended` (`active` to `active`). | fixed |
| 10 | major | spec/00-conventions.md:432 | The Submission machine gives states and events but no transitions: the targets of `submission.quarantined`, `submission.released_from_quarantine` and `submission.rejected` are unstated, `checks_failed` (T) and `rejected` (T) are not told apart, and the cell state during quarantine is undefined (no timer, so the cell can stay `submitted` indefinitely). | logged-cross-part |
| 11 | major | spec/00-conventions.md:427, 487-496 (also 386, 463, 507) | `appeal.overturned` has no named effect for four of six `appeal_kind` values: `cell_rejection` (the cell is already requeued, accepted elsewhere or `exhausted`; no rejected-to-accepted event, so credit cannot follow), `job_rejection` (`Job.rejected` is T), `template_rejection` (`Template.rejected` is T), `report_outcome` (`Report.dismissed` and `Report.actioned` are T). The remedy (reopen or new object) needs a decision. | logged-needs-owner |
| 12 | major | spec/00-conventions.md:447 | Member status `banned` is appealable (`member_ban`) but had no outgoing transition, so an overturned appeal could not restore the member. Added `banned` to `active` on `member.reinstated`. | fixed |
| 13 | minor | spec/00-conventions.md:448 | Status `closed` has no exit and no (T) mark; whether a member closed for inactivity (`retention.member_inactive_days`) can return, and how, is undecided. | logged-needs-owner |
| 14 | major | spec/00-conventions.md:460-461, 475-476, 494 | Approval-count parameters allow more approvers than the machines model: `template.min_reviewers_new` 1..5 against one `awaiting_second_review` step, `service.min_approvers` 1..5 (2 is an owner decision) against no second-approval state in 0.9.6, `appeal.ban_min_reviewers` 1..5 against one second review. Cap the ranges in 0.10.6 or add a counting rule; this file owns only the machine side. | logged-cross-part |
| 15 | major | spec/00-conventions.md:475 | A service suspended by `service.review_lapsed` had no exit: `service.resumed` applies only when the cause was a kill switch and `service.review_started` excluded `suspended`, so recovery needed a detour through `revoked`. `suspended` added as a source. | fixed |
| 16 | major | spec/00-conventions.md:476 | The `service.approved` guard said "gate flags yes", but 0.8.3 requires only `third_party_task_use` and `prohibited_content_compatible`; the other gate flags are per-purpose conditions (R5-R7). Read literally, a service with `commercial_use_of_output` = `no` could never be approved. Guard now names the two flags. | fixed |
| 17 | minor | spec/00-conventions.md:497 | An appellant could not withdraw in `awaiting_second_review`. State added to the `appeal.withdrawn` sources. | fixed |
| 18 | minor | spec/00-conventions.md:504 | `Audit` has the event `audit.third_submitted` but no state for it (states stop at `third_pending`), and `audit.resolved` has no stated source state. | logged-cross-part |
| 19 | minor | spec/00-conventions.md:504-510 | Entities with a lifecycle but no machine in 0.9: `Referral` (two-sided bonus state, held for `growth.referral.hold_s`), `Alarm` (raised, acknowledged), `Invite` (`invite.ttl_days`). Whether another part defines them was not checked. | logged-cross-part |
| 20 | minor | spec/00-conventions.md:510 | Only `launch.members_may_join_changed` is named; `launch.member_jobs_enabled` and `launch.minting_enabled` (0.10.6 table C) have no event, and `parameter.changed` already covers all three, so the dedicated name is redundant or two are missing. | logged-cross-part |

Beyond the cap of 10 fixes, 5 further minor defects are not tabled individually. Top 3: 0.8.1 S1 (line 264) drops the FD wording "no credentials, nothing under confidentiality"; the 0.9.1 state-naming rule (line 374) says adjectives or past participles, but `draft`, `screening`, `running`, `open` and `new` are neither; `Job.screening` has no cancel transition (line 402). The other two: Lease states carry no (T) marks (line 430); 0.9.8 labels a machine "Kill switch" where 0.7 names the entity `KillSwitch` (line 509).

## Not verified

- The content of `ISS-02` and `ISS-05` to `ISS-09`: they are cited in 0.8.3 and 0.8.5 but the register (`spec/02*`) is outside this cell's read list. In particular, FD§4.2 names starter grants as the only Reserve outflow, and the `grant` entry type also pays referral bonuses; whether `ISS-06` justifies that was not checked.
- `docs/source/prompt.md` was not read; the checks use the FD and the ground rules in `docs/decisions.md`.
- No part file S5.* to S14.* was read, so uses of these state and event names downstream are unchecked (findings 6, 7, 10, 11, 14, 18-20 may already be settled there).
- Sections 0.1-0.4, 0.10 and 0.11 were read only where they cross-reference 0.8-0.9; they are not audited here.
- Line numbers were counted from the start of each range returned by the read tool, which prints no per-line numbers; they were cross-checked against the heading of 0.10.5 (line 560) but may be off by a line elsewhere.
- Reachability and dead-end checks were done by reading, not by a script.
