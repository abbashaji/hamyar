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

| # | Log | Cell | severity | file:line | Defect (short) | action |
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

## 4. Owner-only decisions, one list

Consolidated from every `logged-needs-owner` row of A01 to A15 (38 rows), the 39 `needs_owner` register rows and 17 `Rows to add to S3.2` of 02e 2.E.3, and the founders' and owner decisions named in 16d and 15g. Ids are the sources' own; one line may merge several. `Meanwhile` is the default the source says applies; where a source gives none, the cell says so. 02e 2.E.3 counts 7 `yes`, 9 `partly` and 23 `no` for presence in S3.2: S3.2 does not yet carry most of these decisions, and S3 and S19 use the same `OD-nn` ids for different questions (section 2 row 40), so an owner cannot yet answer them from S3 alone. [D]

| # | Decision the owner must make | Sources | Meanwhile (source default) | Needed before |
| --- | --- | --- | --- | --- |
| O-01 | Who the two admins are, how the first admin is bootstrapped and vetted, how many independent reviewers exist in Phase 1 | A03 #32, A04 #3, `ISS-102`, `ISS-168`, `ISS-119` (11c) (a)(b)(d)(e), `ISS-82`, `ISS-196`, `ISS-16110`, 16d F-14 | Two-person actions unavailable below two admins; reviewer numbers not lowered; `C19` warns | first sign-off |
| O-02 | Whether a platform-side sandbox ever executes submitted code (blocking `ISS-12`) | `ISS-12`, `ISS-41`, `ISS-81`, `ISS-91`, `OD-08`, X-01 | No; the requester runs tests (`_rs`) | build of BM6 |
| O-03 | Accept or change blocking `ISS-11` (only `commons_capable` services count for minting and for `launch.min_approved_services`) | `ISS-11`, `OD-04` | `ISS-11` stands as proposed | G0 sign-off |
| O-04 | Exit rule of FD 8.3 governs launch, not building | `ISS-31`, `ISS-171`, `ISS-192` | Build proceeds; all `launch.*` switches `false` | launch sign-off |
| O-05 | Whether the Reserve may pay anything beyond starter grants (restitution for an overturned rejection or ban, goodwill after a policy change) and who bears an overturned rejection after escrow close; effect of `appeal.overturned` for the four unnamed `appeal_kind` values | `ISS-56`, `ISS-76`, `ISS-85` (d), `ISS-119` (11c) (c), A15 #26, X-03 | Nothing paid; donor bears it; `appeal_restitution` entry type off | BM7 acceptance |
| O-06 | Reversal of `levy`, `refund`, `escrow_hold` after the escrow is closed: restitution to the requester, or refuse with `STATE_CONFLICT` | A01 #6, `ISS-62`, `ISS-17` | none stated by A01 | BM1 |
| O-07 | Expired credit slice in escrow: pay donors as fresh credit, or send to the Reserve | A01 #18 | current behaviour: paid to donors | BM1 |
| O-08 | Transferred lot: fresh E-day clock at acceptance, or E days from minting (FD 4.5) | A01 #20 | fresh clock, tagged [H] | BM1 |
| O-09 | Levy on an overturned primary cell: charged or refunded | A01 #23 | charged; rework paid from the pool | BM1 |
| O-10 | Whether escrowed credit counts toward cap K and whether it keeps ageing in the accelerated arm | A06 #26, 16d F-03, `ISS-18` | register `ISS-18`: escrow counts; ageing undecided; `S16D-C3` warns | before the PreRegistration lock |
| O-11 | Quote basis of the verification pool before any measurement; whether any template is `high` in Phase 1; who pays when verification exceeds the pool | `ISS-16` item 2, `ISS-85` (a)(b)(c)(e), 16d F-20, X-02 | max(measured v, `price.v_prior`, v_floor) [A]; job stops, Reserve pays nothing | BM7 acceptance |
| O-12 | Ledger store under one serialization point; scope of the integrity brake (halt all postings or only minting and new jobs) | `ISS-43`, A07 #5 | one ledger, one chain; brake stops minting and new jobs only | before the store is fixed (S4 4.6.2) |
| O-13 | Waitlist rule when a global-scope entry blocks others; whether a reserved job at the concurrent-job cap loses its reservation | A02 #24, A02 #25 | none stated | BM6 |
| O-14 | Reservation penalty or fee for late cancel and no-show | `ISS-66` | no money; cooldown | before `ff.job.reservations` |
| O-15 | Reserve seeding, Commons backlog author, license, publication target, sponsor label | `ISS-19`, `ISS-22`, `OD-05`, `OD-06`, 16d F-13 | Reserve starts empty, grants pause; precondition [V]: Reserve at least 150 credits before join opens | before join opens |
| O-16 | Human review of the panel repository for G4; backups (places, retention, key holder) and whether `invite.accountability_days` counts as retention | `ISS-49`, `ISS-47`, `ISS-16021`, `OD-12` | G4 stays open; encrypted, two locations | G1 / G4 sign-off |
| O-17 | What e-mail is for; whether `actor_day_hash` should exist at all | `ISS-44`, `ISS-102`, A04 #9 | in-app notices; e-mail opt-in only, never recovery or login | first member invitation |
| O-18 | Free text in `permanent` append-only tables; `members.time_zone` stored server-side; fate of a `Team` whose owner closes; whether a `closed` member can return | A05 #19, #22, #28, A15 #28 | none stated | BM0 data model |
| O-19 | When the recovery key is shown; minimum member age; join consent versus the sub-60-second path | `ISS-113`, `ISS-119` (11d), A09 #26, #27 | key after first accepted cell [H]; age 0; none for the consent conflict | BM8 acceptance, launch |
| O-20 | Notice wording versus immediate tightening; the headline `One minute a day`; per-sentence `declared` rule; glossary spelling; byte-exact copy fallback | A09 #30, #31, #32, #33, #37 | none stated | copy review (OD-13) |
| O-21 | Approval guard for copy-paste and pooling flags; regional `no`; P2/P3 license pairing; key and polarity of `info.automation_limits` | `ISS-71`, `ISS-72`, `ISS-73`, `ISS-77`, A15 #17 | stricter S7 guard; region never blocks; no P2/P3 rows | G0 sign-off |
| O-22 | `lease.max_job_share_ratio` value, rounding and visibility | `ISS-105`, `ISS-16107` | 0.34; max(1, floor(x x N)); hidden | first `S1` job |
| O-23 | What a requester gets when a job is cancelled or fails, including retrieval of accepted cells of a `cancelled` job | `ISS-115`, A12 #26 | in-flight cells finish, accepted ones paid, partial `Deliverable` | BM7 acceptance |
| O-24 | Share-card design (computed vs stored token); a member token for V3; money-moving rewards | A12 #25, `ISS-124`, `ISS-127`, 15g G-02 | 15g picks the computed card; V3 descriptive; no rewards | G1 sign-off |
| O-25 | Headline counter and gold leakage; differencing of daily aggregates; `team.min_public_members` below the cohort k; TH-01 early-fail rule; envelope proposal margin | A11 #5, #6, #7, #14, #15, 16d F-10 | disclosure added; 16d proposes team minimum 10 | before public pages |
| O-26 | Pilot size cap; minimum number of G5 interviews; who acts on each alarm; reachability test method; thresholds locked before day 1 | `ISS-179`, `ISS-141`, `ISS-194`, `ISS-197`, `ISS-198`, `OD-11` | invite supply; no minimum; thresholds in a PreRegistration | pilot invitations, G2, G5 |
| O-27 | Commons job and `flagged_for_audit` age-out; criterion of MT-06 restriction; delimiter-collision rule for code slots | A06 #28, #31, A08 #16 | none stated | BM6 / BM7 |
| O-28 | Split of `invite.strike_window_days`; floor on `report.decision_sample_rate`; values of `abuse.admin_lookup_rate`; name of the pending-approval lifetime | `ISS-16009`, `ISS-16020`, `ISS-16015`, `ISS-16017` | one parameter; no floor; no value invented | before the S16 seed runs |
| O-29 | Accelerated-expiry arm: whether large-job trial jobs come from the standard arm; K = 500 or `admission.max_job_cells` 200; platform-wide join limit; exempt team totals from the cohort rule | 16d F-17, F-04, F-12, F-10 | defaults unchanged | PreRegistration lock |
| O-30 | S5 file names and heading numbers; one numbering plan for S10 and S11; unique `ISS-117..119`; `OD` id series of S3 and S19 | `ISS-52`, 02e B4, B5, A13 #2 | cell path authoritative | assembly |
| O-31 | S0 owner confirms the `Admin` suffix rename of 11 colliding operation ids (the only rename 15g asks for) and the `legal_hold` kill-switch reason | 15g CR-01, CR-26 | none | before the OpenAPI document is generated |

Not an owner decision, though the logs file it as one: A07 #23 (`hamyar_config_epoch_count` naming) is a naming fix for the S4 owner; A09 #28 to #29 are S16 naming.

## 3. Corrections and edits required in citing parts that are not applied

Sources: `## Corrections required` of 16d (CR-01 to CR-25, 25 rows) and of 15g (CR-01 to CR-44 without CR-10, 43 numbers); the edit lists at the end of 15c to 15f are cited by 15g as already specified there and were not re-audited by 15g. Status is decided by reading the cited place in the part file at base 8074eac. `not applied` = the old text is still there; `applied` = the new text is there; `not yet checked` = the place has not been read by this cell. Line numbers are those of the file as read. [D]

### 3.1 16d corrections (16d CR-nn)

| CR | Place | Required change | Status | Evidence |
| --- | --- | --- | --- | --- |
| 01 | P 16.15 row 1 | relabel eta as 1/(1+v+lambda) | **not applied** | P 16.15 row 1 (line 438) still reads `Minimum eta (Reserve inflow versus spend)` |
| 02 | P 16.3 `C13`; P 16.5 row `mint.monthly_cap_credits`; S Table A | use min(phi, 1 - phi) | **not applied** | P `C13` (line 92) still multiplies `admission.phi_ppm`; P line 140 still reads `x phi 0.5`; the divisor fix of A13 #1 is in, CR-02 is not |
| 03 | P 16.7 `admission.min_window_s`, `admission.window_step_s`; S Table A | positive window floor and step range | **not applied** | P lines 180 and 182: `> 0; C7, C9` and `divides 86,400; C9` |
| 04 | P 16.11 `retention.ip_hash_ttl_days`; S Table B | range `1..30` | **not applied** (P and S) | P line 313: `0..30`; S Table B row `retention.ip_hash_ttl_days` (S0 lines 640 to 735 read): `0..30` |
| 05 | P 16.3 `C2`; S 0.10.3 `C2` | add `verify.gold_rate_floor > 0` | **not applied** (P) | P line 78 adds `> 0` for the audit floor only; S not yet checked |
| 06 | P 16.13; S Table A | notice ranges `1..90` | **not applied** (P and S) | P lines 391 and 392: `0..90`; S Table A rows `change.notice_days_default` (line 640) and `change.notice_days_price` (line 641): `0..90` |
| 07 | P 16.13; S Table A | `reservation.*` in `change.notice_days_price` | applied in P (by A13 #12); **not applied** in S | P line 392 lists `reservation.*`; S Table A line 641 still reads `(for price.*, admission.*, credit.*)` |
| 08 | P 16.14; S Table C | `team.min_public_members` 5 to 10 | **not applied** (P) | P 16.14 row `team.min_public_members` still has default 5 (validation `1..1000`); S Table C not read |
| 09 | P 16.5; S Table A | state cut as floor(cap x (1 - ratio)) | **not applied** | P line 145 reads `0.25 (cut applied when the threshold is passed)` |
| 10 | P 16.18 | basis of size defaults, rows not in FD 4.9 | **not applied** | P 16.18 basis of the envelope row still reads `FD§3.2 estimate [H]; replaced by CAL` (no `[A] initial safe default, no derivation`); the Reserve ceiling and mint cap rows are not marked as non-FD§4.9 rows; the closing paragraph says the FD§4.9 table was not re-read |
| 11 | S 0.10.3, 0.10.5 | `tighten_direction` enum, `public` default, operator exceptions, `abuse` area | not yet checked | A13 #16 (logged) says the two vocabularies still differ |
| 12 | P 16.16, 16.17.5 | public and hidden lists | **not applied** | P 16.16 header and 16.17.5 make only `ops.rpo_s`, `ops.rto_s`, `ops.backup_retention_days` public among `ops.*` (no `ops.purge_interval_s`); the 16.17.5 hidden list names only `growth.referral.max_per_referrer_per_30d` (no `growth.referral.max_per_day`, no per-invite-tree row); `lease.max_job_share_ratio` is not a row of 16.9 (other groups not searched) |
| 13 | `spec/16b-parameters-a.md` | new rows for generic two-person lifetime, four S10a names, `abuse.admin_lookup_rate` | not yet checked | A12 #29 and 02e B3 say the names are undefined |
| 14 | C 16.C.3, 16.C.2 | appeal note range, warning range | not yet checked | |
| 15 | P 16.12 `template.autopause_report_count` | distinct reporting members | **not applied** | P 16.12 row default reads `5 reports inside template.autopause_window_s`, no `distinct reporting members` |
| 16 | P 16.16 `ops.rpo_s` | `[V]` on the archive interval | **not applied** | P 16.16 row `ops.rpo_s` has default 300 and calibration `OPS: restore drill`, no `[V]` |
| 17 | P 16.8 `verify.duplicate_min_chars` | `>= verify.duplicate_shingle_chars` | **not applied** | P 16.8 row validation is `1..10000` |
| 18 | P 16.3 | add `S16D-C1..C24` | **not applied** | P 16.3 read completely (lines 70 to 102): the table ends at `C20`, the worked check lists only `C1`..`C20`, no id `S16D-C*` exists |
| 19 | P 16.3, 16.17.2 | evaluate lifetime relations for both lifetimes | **not applied** | neither the 16.3 intro nor 16.17.2 states the twice-evaluated rule; 16.17.2 only uses the two lifetimes as an example of a batch |
| 20 | S14 at 14:603 and 14:600 | 20 to 30; secret-rotation alias | not yet checked | A03 #20 says `calibration.min_samples_per_service` was aligned to 30; the rotation name is A03 #29, logged |
| 21 | P 16.6 `price.eta_alarm_threshold` | range `> 0 .. 1` | **not applied** | P 16.6 row validation is `0..1` |
| 22 | C 16.C.2 `ui.draft.ttl_s` | state baseline | not yet checked | |
| 23 | P 16.16 `security.two_person_actions` | always contains `parameter.loosen` | **not applied** | P 16.16 validation is `subset of the action names in S10.*`; only the default contains `parameter.loosen`; A03 #27 logs the related S0 gap |
| 24 | P 16.3 | record `S16D-C3` as warning | **not applied** | no `S16D-C3` in 16.3 (see CR-18) |
| 25 | C 16.C.8 | add `admission.redeemable_capacity_cells_per_day` | not yet checked | |

Result of the checks: 19 of the 25 corrections were checked (CR-01 to 10, 12, 15 to 19, 21, 23, 24) in `spec/16-parameters.md`, and CR-04, 06, 07 also in S0 Tables A and B (S0 lines 640 to 735). 18 are not applied. One is applied: CR-07, in S16 only (by an audit fix of A13, not by the 16d correction); in S0 Table A it is not applied. 6 are not yet checked: CR-11 (S0 0.10.3 and 0.10.5), CR-13 (`spec/16b-parameters-a.md`), CR-14, CR-22, CR-25 (`spec/16c-parameters-b.md`) and CR-20 (S14); the S side of CR-02, 03, 05, 08, 09 (S0 Table A and C, 0.10.3) was also not read. In addition `spec/16-parameters.md` 16.7 closing note still says the default of `mint.monthly_cap_credits` derives from phi, which is the 16d CR-02 conflict.

### 3.2 15g corrections (15g CR-nn) and the 15c to 15f edit lists

Checked by this cell: 15g `CR-01` and `CR-02` only (15b, below). The other 41 correction numbers of 15g and the edit lists of 15c to 15f were not compared with the part files by this cell; they remain unchecked and must be re-checked before the verdict can change. Two audit logs say something about the same places and are the only evidence so far:

- A12 #15 made the 11 colliding operation ids unique without renaming, by prefixing the admin ids with `admin` in the OpenAPI key. 15g `CR-01` asks for the suffix `Admin` on the admin operation id itself. If A12's rule is in the files, `CR-01` and `CR-02` are not applied and the two rules conflict (15g `P6`: no rename except `CR-01`). Checked: `spec/15b-api-admin.md` (line 24, `Operation ids`) holds A12's rule, the prefix `admin` on the generated `operationId` with the ids in the tables unchanged; it is not 15g `CR-01` and `CR-02` (suffix `Admin`, rename of the admin duplicates in 15.23.1, 15.24, 15.29.2, 15.29.3, 15.30.1). `CR-01` and `CR-02` are **not applied** in 15b and the two rules conflict until the S0 owner chooses (O-31). S0 0.5 was not read.
- A12 #6 aligned `kill.member` to 403 `account_frozen` in 15a and 15b, which is 15g `G-11` for those two files; 15g `CR-25` (S14 and `AC-launch-52`) and the step-7 limit in 15a 15.4 are separate edits and are not evidenced.

The 15g corrections to check, grouped by file (numbers are 15g's): S0 (`CR-01`, `CR-05`, `CR-09`, `CR-26`, `CR-44`); S14 (`CR-23`, `CR-25`, `CR-26`, `CR-28`, `CR-40`, `CR-41`); 15a (`CR-04`, `CR-08`, `CR-28`, `CR-29`, `CR-30`, `CR-31`, `CR-33`, `CR-03` (keep), `CR-15`, `CR-16`, `CR-19`, `CR-36`, `CR-37`, `CR-02`); 15b (`CR-01`, `CR-02`, `CR-03`, `CR-04`, `CR-05`, `CR-06`, `CR-07`, `CR-11`, `CR-12`, `CR-20`, `CR-21`, `CR-22`, `CR-24`, `CR-27`, `CR-35`, `CR-32`, `CR-36`, `CR-09`, `CR-34`, `CR-18`, `CR-17`, `CR-42`, `CR-43`); 15c to 15f and parts 11 and 13 (`CR-13`, `CR-12`, `CR-14`, `CR-38`, `CR-39`).

## 5. Overall verdict and the next fix round

**Verdict: NOT READY** as one consistent spec that a build can follow without further reconciliation. The 15 logs each say READY WITH LOGGED ITEMS; read together with 02e, 16d and 15g that verdict does not hold for the whole. [D]

Reasons:

1. **Open contradictions between parts: 29 of the 44 unfixed major findings are logged cross-part and 15 need an owner** (section 2). They are not wording. Examples: the same safety-critical datum, the IP hash, is stored in a relational table in 05a and said never to be in the database in 10a and 10b (row 9); 05b and 09 use Job, Cell and Lease columns and key names that 05a does not define (rows 13 to 16); the join flow of 11d and of 11a cannot both be built (row 26); S0, the file every other part defers to, has no Submission transitions and allows one admin to be the whole two-person rule (rows 5 and 42 to 44).
2. **The register is not applied.** 02e Table A lists 18 conflicts of substance with the register's resolution; 2.E.5 says the edits belong to later cells, and no log applies them. Two are against the prompt's own constraints: the build plan now contains a sandbox runner that `ISS-12` (blocking) rules out (X-01), and S6a, `AC-ledger-03` and `T-unit-01` still let verification draw on the levy that FD 4.2 reserves for the Reserve (X-02). Both blocking register issues, `ISS-11` and `ISS-12`, are `proposed`, not accepted.
3. **The two consolidation files are mostly unapplied.** 16d: of the 19 corrections checked, 18 are not applied and 1 (CR-07) is applied in S16 only (section 3.1); 6 are unchecked. 15g: of 43 numbered corrections only `CR-01` and `CR-02` were checked (not applied; A12's prefix rule conflicts with them); 41 and the edit lists of 15c to 15f are unchecked; 15g reports 24 duplicate or conflicting definitions, 11 operation-id collisions that make the OpenAPI document ungenerable as written, a missing wrong-scheme rule for the admin routes, 10 idempotency gaps, 11 groups of undeclared error reasons, 12 missing events, and enforcement points of S14 for which no endpoint exists (Commons job creation) or no endpoint names its check (`createJob`, `submitJobForScreening`, `decideScreening`, `createReservation`, `createLease`, `submitResult`). The ground rule `build everything, launch nothing` rests on those checks.
4. **Owner decisions are not collected where the owner will look.** 31 groups (section 4); 02e counts 23 of 39 `needs_owner` rows absent from S3.2, and S3 and S19 reuse the same `OD-nn` ids for different questions.
5. **No log ran any script, test or query.** Every arithmetic result was recomputed by hand; every acceptance script (`check_spec.py`, `check_audit.py`, `check_params.py`, `check_refs.py`, `check_issues.py`) is stated as not run by the auditors. This cell did not run them either.

What is sound: every log recomputed the FD 3.3 example (price 1,150,000 ucr; escrow 276,000,000; pool 24 cells; levy 12,000,000; refund 0; eta 869,565 ppm; capacity 320 against 264) and found it correct; 16d re-derived the 46 existing parameter relations (all pass at the defaults in the standard arm; one fails in the accelerated arm) and 24 added ones (22 pass); the logs report no provider fact, no volunteer-account automation and no `guaranteed` promise in the parts they read. 273 of 397 tabled defects are marked fixed.

**It becomes READY WITH LOGGED ITEMS when** FX-01 to FX-16 below are applied, the unchecked rows of section 3 are re-checked, `ISS-11`, `ISS-12`, O-01 and O-02 each have an owner answer or an explicit recorded default, and the acceptance scripts pass in CI. **It becomes READY only when** the logged-needs-owner items of section 4 have answers.

### Fix tasks (each small enough for one cell)

Files are the only files the cell may edit. Rule for every task: no id, parameter name, endpoint or state is renamed except FX-07a (15g `CR-01`, S0 owner to confirm); minimal in-place edits; do not shorten sections. `After` lists tasks whose result a task reads.

| Task | Files | Edit | Acceptance | After |
| --- | --- | --- | --- | --- |
| FX-01 | `spec/16-parameters.md` rows 16.3 to 16.7 | 16d CR-02, 03, 05, 18, 19, 24: `C13` min(phi, 1 - phi); window and step ranges; gold floor `> 0` in `C2`; add `S16D-C1..C24`; both-lifetime rule; `S16D-C3` as warning | `python scripts/check_params.py`; `AC-paramd-01` to `AC-paramd-05` hold on the seed | |
| FX-02 | `spec/16-parameters.md` rows 16.8 to 16.18 | 16d CR-01, 04, 06, 09, 10, 12, 15, 16, 17, 21, 23 (CR-07 already applied): eta label and range, IP-hash range `1..30`, notice `1..90`, cut-ratio text, distinct reporters, RPO `[V]`, shingle relation, two-person list, basis of size defaults, public lists | `check_params.py`; `AC-paramd-02`, `-03`, `-04`, `-10` | FX-01 |
| FX-03 | `spec/00-conventions.md` Tables A to C, 0.10.3, 0.10.5 | S side of 16d CR-02 to 09 and CR-11; A03 #27: `launch.min_signoffs` `2..5`, `launch.min_approved_services` `1..20`, `security.two_person_actions` must contain `launch.signoff`, `killswitch.release`, `parameter.loosen`; A15 #29: cap approver ranges at what the machines model | `check_params.py`; names unchanged | FX-01, FX-02 |
| FX-04 | `spec/00-conventions.md` 0.9.2 to 0.9.8 | Submission transitions (05b SBT-01..07), service `suspended` to `in_review` and `in_review` to `revoked`, `quarantined` target (A06 #32), the convention additions 3 to 9 and 13 of 05b, A15 #21, #22, #33 to #35 | every state and event of 05b exists in 0.9; `check_spec.py` | |
| FX-05 | `spec/16b-parameters-a.md`, `spec/16c-parameters-b.md` | 16d CR-13, 14, 22, 25: rows for the two-person lifetime, four S10a names, `abuse.admin_lookup_rate` unseeded; appeal and warning ranges; draft baseline; the redeemable key as a non-parameter | `check_params.py`; `AC-param-02` | FX-01 |
| FX-06 | `spec/14-launch-gates.md` | 15g CR-23, 25, 26, 28, 40, 41 and 16d CR-20; add the `## Issues raised` table for `ISS-141`, `ISS-143`, `ISS-144`, `ISS-147` with content for `ISS-144`; name the Commons authoring path | `check_issues.py`; every `ISS` cited has a row | FX-16 |
| FX-07a | `spec/15b-api-admin.md` 15.21 to 15.28 | 15g CR-01, 02 (decide the `Admin` suffix against A12 #15's prefix rule, S0 owner confirms), 04, 05, 06, 07, 12, 20, 21, 22, 24, 27 | `check_refs.py api`; `AC-auth-01`, `-02`, `-03` | FX-03 |
| FX-07b | `spec/15b-api-admin.md` 15.29 to 15.37 | 15g CR-03, 11, 27 (15.28.1 line), 32, 35, 36, 09, 34, 17, 18, 42, 43; remove 15.33.5 only if O-24 is answered as 15g G-02 | `check_refs.py api` | FX-07a |
| FX-08 | `spec/15a-api-core.md` | 15g CR-04, 08, 28 to 31, 33, 15, 16, 19, 36, 37; decide A12 #27 (member inbox) and #28 (appeal operations, point to 15d) | `check_refs.py api`; `AC-gate-01` to `AC-gate-03` | FX-06, FX-07a |
| FX-09 | `spec/15c`..`15f` edit lists, `spec/11b`, `spec/13` citing lines | 15g CR-12, 13, 14, 38, 39; delete `ui.variant_exposed`, `perm.metrics.view_small_cells`; one `listMetricSnapshots` | `check_refs.py api` with the decision tables excluded | FX-07b |
| FX-10 | `spec/05a-entities.md` | A04 #6, #15, #20; A05 #15 to #18: `Lease.hard_expires_at`, `extensions_used`, `release_reason`; Job and Cell columns of 05b; `idempotency_key` / `entry_key`; `StateTransition`, `mint_headroom`; `Device` without `creation_ip_hash`; edge clearing | every column cited in 05b S5.22, 5.23, 5.29 exists; `check_spec.py` | FX-04 |
| FX-11 | `spec/10a-identity.md`, `spec/10b-safety.md` | A04 #18, #19: one heading scheme, one set of secret names and enum states | `g1.secrets_inventory_complete` names equal in both; no heading number defined twice | FX-10 |
| FX-12 | `spec/06a-ledger.md`, `spec/06b-admission.md`, `spec/08b-verification.md` | 02e A2, A3, A5, A17, A18; A02 #9; A08 #13, #14: verification never draws on the levy; redeemable key; one v definition; `AC-ledger-03`, `T-unit-01` rewritten; open owner items stay marked | `check_spec.py`; FD 3.3 numbers unchanged | O-05, O-06, O-11 |
| FX-13 | `spec/17-build-plan.md`, `spec/04-architecture.md`, `spec/08a-templates.md`, `spec/09-result-return.md` | 02e A1, X-01: remove the check-runner work package, `AC-bm6-26`, `ff.verify.sandboxed_tests` and `test_run` as a milestone item unless `OD-08` is answered yes | `check_spec.py`; no part defines a sandbox flag | O-02 |
| FX-14 | `spec/11a`..`11d` | unique `ISS` ids (117 to 119), one heading numbering plan, one owner of rejection copy (A10 #10, #11, #13), join consent as O-19 decides | `check_issues.py`; no duplicate heading number | O-19 |
| FX-15 | `spec/12-public-growth.md`, `spec/13-measurement.md` | A11 #2, #4; 15g G-04, G-06, G-07, G-24: one Experiment machine and name set; define the V1 to V6 metrics | `check_spec.py`; every `hamyar_growth_*` key has a definition | FX-09 |
| FX-16 | `spec/02*-issues*.md`, `spec/03-assumptions.md`, `spec/19-risks.md`, `spec/16-parameters.md` 16.15 | mint ids for 02e A3, A11, A17; collect the owner decisions of section 4 as rows of S3.2 with unique `OD` ids; seeds for TRIP-10, 11, 15 (A13 #6); recount 02e | `check_issues.py` | |
| FX-17 | the parts named in `Untabled` | log the 25 untabled minor items (A06 8, A12 6, A15 11) as register rows or fix them | each item has a row or an edit | |
| FX-18 | `spec/18-testing.md` | add `AC-auth-01..03`, `AC-gate-01..03` (15g), `AC-paramd-01..10` (16d) to the criteria and the BM table; A14 #18 to #20 | every new test id cited by one criterion | FX-06, FX-08 |


Verdict: NOT READY
