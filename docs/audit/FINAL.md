# Final readiness report (FINAL)

*Cell C-057. Critical read of the 15 audit logs `docs/audit/A01.md` .. `A15.md` (read completely), `spec/02e-issues-summary.md`, `spec/16d-parameter-consistency.md` and `spec/15g-api-consistency.md` (read completely). Base commit 8074eac. No spec part was edited by this cell. Counts below are recounted from the finding tables of each log, not copied from the logs' own summary lines; where a log's summary line disagrees with its table, the table is used and the disagreement is reported. Nothing here is legal advice and nothing was checked against any provider's terms or any law.*

## Checked

- All 15 logs were read to the last line, every Findings table row was classed as fixed, logged-cross-part or logged-needs-owner from its `action` cell, and the three consolidation files (02e, 16d, 15g) were read completely, including every table and the whole `## Corrections required` list of 16d and 15g.
- Cell ids: A01 = C-042 and A03 to A14 = C-044 to C-055 are stated in the logs. A02 (C-043) and A15 (C-056) state no cell id; they are assigned by elimination from the dependency list of this cell (C-042 to C-056). [A]
- Recount of the 15 finding tables: 397 tabled findings; 273 fixed, 86 logged-cross-part, 38 logged-needs-owner (273 + 86 + 38 = 397). Beside them, about 25 minor items are named in prose and are neither fixed nor tabled (A06: 8, A12: 6, A15: 11). All 15 logs end with the verdict READY WITH LOGGED ITEMS (none READY, none NOT READY); see the per-log table.
- Blocking findings in the 15 tables: 5 (A03 findings 1 to 3 and 4; A05 finding 1), all marked fixed. No blocking finding is open in any audit table. Open blocking items exist only in the register: `ISS-11` and `ISS-12` (02e 2.E.1), both `proposed`, neither accepted by the owner.
- Unfixed major findings in the audit tables: 44 (43 labelled `major` plus A04 finding 3, whose severity cell reads `needs-owner`). They are listed one by one in section 2.
- Every log lists, under `Not verified`, the other parts it did not read. No log read the whole spec. The only whole-spec cross-checks are 02e, 15g and 16d, and each of those states what it did not read. A statement in this file that two parts agree rests on those three files or on one log that read both parts; it is not an independent check of the part files, except where section 3 says a part file was read.

## 1. One row per audit log

`Fixed` = the log says the defect was edited in the audited file; this cell did not re-read the part files to confirm each edit landed (see Not verified). `Cross` = logged-cross-part. `Owner` = logged-needs-owner. `Untabled` = minor items named in prose only.

| Log | Cell | Files | Verdict | Findings | Fixed | Cross | Owner | Untabled |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | C-042 | `spec/06a-ledger.md` | READY WITH LOGGED ITEMS | 23 | 16 | 3 | 4 | 0 |
| A02 | C-043 [A] | `spec/06b-admission.md` | READY WITH LOGGED ITEMS | 28 | 22 | 4 | 2 | 0 |
| A03 | C-044 | `spec/14-launch-gates.md`, `spec/07-policy.md` | READY WITH LOGGED ITEMS | 32 | 25 | 6 | 1 | 0 |
| A04 | C-045 | `spec/10a-identity.md`, `spec/10b-safety.md` | READY WITH LOGGED ITEMS | 21 | 13 | 6 | 2 | 0 |
| A05 | C-046 | `spec/05a-entities.md` | READY WITH LOGGED ITEMS | 29 | 14 | 12 | 3 | 0 |
| A06 | C-047 | `spec/05b-state-machines.md`, `spec/09-result-return.md` | READY WITH LOGGED ITEMS | 32 | 25 | 4 | 3 | 8 |
| A07 | C-048 | `spec/04-architecture.md`, `spec/17-build-plan.md` | READY WITH LOGGED ITEMS | 23 | 21 | 0 | 2 | 0 |
| A08 | C-049 | `spec/08a-templates.md`, `spec/08b-verification.md` | READY WITH LOGGED ITEMS | 16 | 12 | 3 | 1 | 0 |
| A09 | C-050 | `spec/11a-volunteer-ux.md`, `spec/11d-i18n-copy.md` | READY WITH LOGGED ITEMS | 38 | 25 | 7 | 6 | 0 |
| A10 | C-051 | `spec/11b-requester-ux.md`, `spec/11c-admin-tools.md` | READY WITH LOGGED ITEMS | 17 | 9 | 6 | 2 | 0 |
| A11 | C-052 | `spec/12-public-growth.md`, `spec/13-measurement.md` | READY WITH LOGGED ITEMS | 16 | 7 | 4 | 5 | 0 |
| A12 | C-053 | `spec/15a-api-core.md`, `spec/15b-api-admin.md` | READY WITH LOGGED ITEMS | 29 | 24 | 3 | 2 | 6 |
| A13 | C-054 | `spec/16-parameters.md`, `19-risks`, `01-purpose`, `03-assumptions`, `20-glossary`, `21-persian-summary` | READY WITH LOGGED ITEMS | 23 | 13 | 8 | 2 | 0 |
| A14 | C-055 | `spec/18-testing.md`, `spec/02-issues.md` | READY WITH LOGGED ITEMS | 20 | 17 | 3 | 0 | 0 |
| A15 | C-056 [A] | `spec/00-conventions.md`, `spec/00-decisions.md` | READY WITH LOGGED ITEMS | 50 | 30 | 17 | 3 | 11 |
| **Total** | | | | **397** | **273** | **86** | **38** | **25** |

Disagreements between a log's own summary and its table (the table is used above):

- A13 says `Fixed 15 of 23. Logged 8`. Its table has 13 fixed (1, 3, 4, 5, 7 to 15) and 10 logged (8 cross-part: 2, 6, 16 to 20, 23; 2 needs-owner: 21, 22).
- A03 says `7 logged (5 cross-part, 1 needs-owner, plus finding 26)`. Its table has 6 cross-part (26 to 31) and 1 needs-owner (32).
- A12 grants 24 fixes and logs 5 tabled items (25 to 29) plus 6 grouped minor items that are not fixed; those 6 are counted under `Untabled`, not under `Cross`.
- A06 and A15 also name minor defects in prose that no table row covers (A06: 8; A15 part 2: 5, part 3: 6). They are counted under `Untabled` and appear in the fix round (section 5, task FX-17).
- A11 finding 1 is marked `fixed`, but A11 finding 2 states that after that fix the text of S12.11.3 and `AC-exp-01..08` still describe the other form. Counted as fixed in the table, treated as only partly fixed in section 2.
- A03 findings 8 and 9 and A06 finding 6 are marked `fixed` in the audited file while the S0 side (`launch.min_signoffs` range, `launch.min_approved_services` range, S0.9.6 `suspended` exit) stays wrong and is logged as A03 finding 27 and A06 finding 27. Counted as fixed; the S0 half is in section 2.

## 2. Blocking and major findings that are not fixed

Source: the `action` cell of each log table (`logged-cross-part`, `logged-needs-owner`) for every row with severity `blocking` or `major`. `file:line` is copied from the log; the logs say their line numbers are approximate and often pre-edit (A02, A03, A04, A05, A06, A07, A09, A10, A11, A12, A13, A14), so a line is a pointer to the section, not an exact position. A05 and A14 cite sections instead of lines. No log row was softened.

**Blocking, audit tables: none open** (A03 findings 1 to 4 and A05 finding 1 are marked fixed). **Blocking, register: `ISS-11` and `ISS-12` are open** (02e 2.E.1): both `proposed`, the owner has accepted none of the 193 register rows. `ISS-12` (the platform never executes submitted content) is contradicted by A07 finding 3, which added a check-runner milestone and work package to `spec/17-build-plan.md` (row `X-01` below).

| # | Log | Cell | Sev | file:line | Defect (short) | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | A01 #6 | C-042 | major | spec/06a-ledger.md:316 | Reversal of `levy`, `refund`, `escrow_hold` mirrors into a possibly closed escrow; breaks INV-L04, INV-L07 and `escrows never reopen` | needs-owner |
| 2 | A02 #9 | C-043 [A] | major | spec/06b-admission.md:162 | S0 0.10.6 default formula of `mint.monthly_cap_credits` uses (1 - 0.5); S6 must read the redeemable key, not the Commons key | cross-part |
| 3 | A02 #24 | C-043 [A] | major | spec/06b-admission.md:338 | A waiting entry blocked by the global scope does not block other categories; a large early job can starve | needs-owner |
| 4 | A03 #26 | C-044 | major | spec/14-launch-gates.md:610 (end) | Cites `ISS-141/143/144/147` but has no `## Issues raised` table; `ISS-144` has no content | cross-part |
| 5 | A03 #27 | C-044 | major | spec/00-conventions.md:703 (table C) | `launch.min_signoffs` allows 1..5 (needs 2..5), `launch.min_approved_services` allows 0..20 (needs 1..20), `security.two_person_actions` can drop `launch.signoff` and `killswitch.release` | cross-part |
| 6 | A03 #32 | C-044 | major | spec/14-launch-gates.md:330 | Who the two admins are, how the first is bootstrapped: until decided no gate can be signed | needs-owner |
| 7 | A04 #3 | C-045 | needs-owner (no severity given) | spec/10a-identity.md:424 | With one admin `launch.signoff`, `ledger.reversal`, `member.ban` cannot run at all | needs-owner |
| 8 | A04 #6 | C-045 | major | spec/05a-entities.md:270-340 vs spec/10a-identity.md:337 | 05a holds the invite edge permanently with no clearing rule; column and enum names differ from 10a | cross-part |
| 9 | A04 #15 | C-045 | major | spec/05a-entities.md:330-345 | 05a `Device` stores `creation_ip_hash` in the relational table; 10a 10.14.2 and AC-safety-01 say IP hashes live only in a volatile store, never in the database or backups. The log calls it a direct contradiction on the most safety-critical datum | cross-part |
| 10 | A04 #18 | C-045 | major | spec/10a-identity.md:1-776 vs spec/10b-safety.md:1-701 | Heading numbers 10.11..10.19 exist in both files; `S10.13` is ambiguous | cross-part |
| 11 | A04 #19 | C-045 | major | 10a vs 10b vs 05a | Name mismatches: `secret.email_enc_key` / `email_encryption_key`, `email_index_key` / `email_lookup_key`, `MemberKey`, `AdminUser`, `AdminCredential` states and columns; `g1.secrets_inventory_complete` cannot pass | cross-part |
| 12 | A04 #20 | C-045 | major | spec/05a-entities.md (5.3.2) vs spec/10b-safety.md:205 | 05a computes `vol_` handles on read for public pages; 10b says handles are never shown on public surfaces | cross-part |
| 13 | A05 #15 | C-046 | major | spec/05a-entities.md S5.8.2 vs 05b S5.23.3 | `Lease` has no `hard_expires_at`, `extensions`, `release_reason`; the reaper index is on the wrong column | cross-part |
| 14 | A05 #16 | C-046 | major | spec/05a-entities.md S5.7.5, S5.8.1 vs 05b S5.22, S5.23.2, S5.29.8 | 05b uses Job and Cell columns 05a lacks (`pause_causes`, `state_before_pause`, `held_ucr`, `acceptance_deferred_until`, ...) and the `closure_reason` `cells_exhausted` | cross-part |
| 15 | A05 #17 | C-046 | major | spec/05a-entities.md S5.9.2, S5.9.3 vs 05b S5.29.5 | `idempotency_key` / `entry_key` (05b) vs `natural_key` (05a) | cross-part |
| 16 | A05 #18 | C-046 | major | spec/05a-entities.md S5.4 vs 05b S5.21.3, S5.29.6 | `StateTransition` (`stt_`) and `mint_headroom` exist in 05b but in no entity catalogue; monthly mint-cap accounting has no table | cross-part |
| 17 | A05 #19 | C-046 | major | spec/05a-entities.md S5.6.10, S5.12.3, S5.10.6, S5.13.6 | Append-only `permanent` tables hold free text that can name a person, while S0.7 defines `permanent` as no personal data by construction | needs-owner |
| 18 | A06 #27 | C-047 | major | spec/05b-state-machines.md:279 | S0.9.6 has no `suspended` to `in_review` and no `in_review` to `revoked`; a re-review that ends `rejected` pauses no pinned job and applies no `inflight_policy` | cross-part |
| 19 | A06 #28 | C-047 | major | spec/05b-state-machines.md:97 | A Commons job has no overrun deadline and a `flagged_for_audit` cell has no age-out: cell, mint-headroom reservation and job stay open forever | needs-owner |
| 20 | A06 #31 | C-047 | major | spec/05b-state-machines.md:233 | MT-06 restricts a member on an anomaly with no count or window; one hard duplicate could restrict an honest donor; untestable | needs-owner |
| 21 | A06 #32 | C-047 | major | 05b SBT-06 and spec/09-result-return.md:392 | 09 returns a released submission to verification; S0.9.3 and SBT-06 move `quarantined` to `checks_passed` | cross-part |
| 22 | A07 #5 | C-048 | major | spec/04-architecture.md:566 | The invariant brake stops only minting and new jobs; payout, settle, expire, grant, retire postings continue on a ledger that just failed its integrity check | needs-owner |
| 23 | A08 #13 | C-049 | major | spec/08b-verification.md:462 | 8.31 excludes Commons cells from member-job v; 06a 6.11.2 counts them together and publishes `v_commons` and `v_member` | cross-part |
| 24 | A08 #14 | C-049 | major | spec/08b-verification.md:511 | 8.32 says mandatory verification is never skipped for budget; 06a LD-05 lets the scheduler skip what the budget cannot pay | cross-part |
| 25 | A09 #26 | C-050 | major | spec/11a-volunteer-ux.md:1380 | `ISS-113` (when the recovery key is shown) is undecided; 11a and 11d now agree only on the default | needs-owner |
| 26 | A09 #27 | C-050 | major | spec/11d-i18n-copy.md:565 | Join consent (all notices plus eight unticked boxes) vs 11a F2/F3 (one three-fact notice, no checkbox wall, 10 s); the sub-60-second path and informed consent (FD 9) cannot both hold | cross-part |
| 27 | A10 #10 | C-051 | major | spec/11b-requester-ux.md:~15 and spec/11c-admin-tools.md:~7 | 11.41..11.49 exist twice with different content (02e B4: three files) | cross-part |
| 28 | A10 #11 | C-051 | major | spec/11b-requester-ux.md:~860 | Requester rejection copy has two owners (`copy.policy.*` in 07, `copy.req.reason_r1..r7` in 11b) with different wording | cross-part |
| 29 | A10 #13 | C-051 | major | spec/11b-requester-ux.md:~213, ~560 vs spec/11c-admin-tools.md:~520 | 11b shows a kill-switch job pause that 11c's effects table does not produce for `kill.all_new_jobs` or `kill.member`; leak risk for a member switch | cross-part |
| 30 | A11 #2 | C-052 | major | spec/12-public-growth.md:484-520, 12.16 AC-exp-01..08 | After the precedence-rule fix the S12.11.3 text and the AC-exp tests still describe the S12 form; S0 and S5 need one Experiment state list | cross-part |
| 31 | A11 #4 | C-052 | major | spec/12-public-growth.md:618 | `day7_return` and the other `hamyar_growth_*` metrics of V1 to V6 are defined in no S13 row; FD 9 Phase 2 measures unspecified | cross-part |
| 32 | A11 #5 | C-052 | major | spec/12-public-growth.md:86 | Headline counter excludes verification cells, so a donor can see her own hidden gold or audit cell (02e A11 agrees it leaks) | needs-owner |
| 33 | A11 #6 | C-052 | major | spec/12-public-growth.md:140 | Daily cumulative `cumulative_mint_ucr` and `reserve_ucr` can be differenced to recover a small group's daily flow | needs-owner |
| 34 | A11 #7 | C-052 | major | spec/12-public-growth.md:343 | `team.min_public_members` 5 is below `analytics.min_cohort_k` 10: a listed team publishes totals the cohort rule suppresses (16d F-10 agrees) | needs-owner |
| 35 | A12 #25 | C-053 | major | spec/15a-api-core.md:600 vs spec/15b-api-admin.md:1030 | Share-card design contradicts (computed, no stored link vs stored, revocable, token-addressed card with a view counter) | needs-owner |
| 36 | A12 #26 | C-053 | major | spec/15a-api-core.md:518 | A `cancelled` job has paid for its accepted cells but the requester cannot retrieve them | needs-owner |
| 37 | A12 #27 | C-053 | major | spec/15b-api-admin.md:773, 1090 | No member inbox or notice read operation exists in any S15 file read; suspension, ban, policy-rejection and appeal outcomes depend on one | cross-part |
| 38 | A12 #28 | C-053 | major | spec/15a-api-core.md:20 | Member-facing appeal operations (file, list, withdraw) are said to live in the sibling file; 15b has none | cross-part (15d defines `createAppeal`, see 15g G-19) |
| 39 | A12 #29 | C-053 | major | spec/15a-api-core.md:900 and 15b | 13 parameters used by 15a and 15b are in no S0 or S16 table (`identity.challenge_ttl_s`, `session.max_active_per_member`, `ratelimit.write_weight`, ... `growth.share_card_max_active`) | cross-part |
| 40 | A13 #2 | C-054 | major | spec/19-risks.md:301-304 and spec/03-assumptions.md:16-28 | `OD-01..OD-12` (S19) and `OD-01..OD-13` (S3) collide with different meanings (OD-05, OD-03, ...) | cross-part |
| 41 | A13 #6 | C-054 | major | spec/16-parameters.md:437-447 and spec/19-risks.md:110-111 | TRIP-10, TRIP-11, TRIP-15 name thresholds `locked in the PreRegistration` but 16.15 has no seed or `thr.*` key for them | cross-part |
| 42 | A15 #25 | C-056 [A] | major | spec/00-conventions.md:432 | The Submission machine has states and events but no transitions; targets of `quarantined`, `released_from_quarantine`, `rejected` unstated | cross-part |
| 43 | A15 #26 | C-056 [A] | major | spec/00-conventions.md:427, 487-496 | `appeal.overturned` has no named effect for 4 of 6 `appeal_kind` values (`cell_rejection`, `job_rejection`, `template_rejection`, `report_outcome`) | needs-owner |
| 44 | A15 #29 | C-056 [A] | major | spec/00-conventions.md:460-461, 475-476, 494 | Approval-count parameters allow 1..5 approvers, the machines model one second step | cross-part |

A14 has no unfixed major finding.

**Contradictions between the audit logs and the register that no log notices.** These are not rows of any log table; they come from reading 02e Table A against the logs. [D]

| # | Where | Contradiction | Severity (this cell) |
| --- | --- | --- | --- |
| X-01 | A07 #3 (fixed: `AC-bm6-26`, WP-BM6-04, BM6 scope) vs 02e A1, `ISS-12` | A07 added a build work package for the isolated check runner and `ff.verify.sandboxed_tests`. `ISS-12` (blocking, prompt scope E: never executing submitted content) and 02e A1 resolve the other way: S4, S8a and S9 must drop the runner and `test_run`. The audit fix wrote the rejected design into the build plan. | blocking until the owner decides `OD-08`; the plan must follow the register meanwhile |
| X-02 | A01 (verifies the levy draw in `AC-ledger-03`, `T-unit-01`) vs 02e A2, `ISS-16` item 3 | The register says verification never draws on the levy (that would be a Reserve outflow FD 4.2 forbids); A01 recomputed and accepted the levy-draw behaviour. 02e A2 says S6a text, `AC-ledger-03`, `T-unit-01` and S8b 8.32 must change. No log applies it. | major |
| X-03 | A01 findings 6, 18 and 02e A4 | Credit after an overturn has four incompatible rules (`ISS-56`, `ISS-85` d, `ISS-62`, `ISS-17`, `ISS-118`); 02e keeps `appeal_restitution` off, so an overturned rejection after escrow close pays nothing. A15 #26 (no effect named) is the same hole in S0. | major (owner) |
| X-04 | A06 #10 fixes 05b to 09 for nonce replay; 02e A14 and `ISS-151` | `ISS-151` (store the secret encrypted) and `ISS-98` (return null, rotate) disagree; 02e picks `ISS-98`. 15g `IG-07` finds the same fault in 15b `createAdminUser`. | major |
| X-05 | A09 #38 and A10 | `ISS-117`, `ISS-118`, `ISS-119` are used by both 11c and 11d (02e B4); 2.9 rule 2 forbids reuse. A10 states 11c owns 117..119; A09 states 11d uses 117..119 too. Unresolved; `scripts/check_issues.py` is an acceptance check of this cell. | major |
| X-06 | A06 reads `spec/05a-domain-model.md`; the file is `spec/05a-entities.md` | A06 did not check 05b and 09 field names against the real 05a. A05 read 05b only at lines 1-220 and 520-640. The 05a to 05b column conflicts (rows 13 to 16 above) are therefore known only from A05's partial read; the full extent is unknown. | major (unknown extent) |
