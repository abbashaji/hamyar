# Specification status and hand-over to the build phase

*Written by cell C-192 (R5-final) from the files named in the cell: `docs/decisions.md`, `docs/owner-decisions.md`, `docs/audit/FINAL-4.md`, the fix logs `docs/fix/R5-01a.md` to `docs/fix/R5-09.md` and `scripts/check_opids.py`. Anything this cell did not open is marked [UNVERIFIED]. No file under `spec/` was edited by this cell.*

## Status

The specification is the Hamyar product specification: one markdown part per file under `spec/`, written one part per cell and assembled into one document by `scripts/assemble.py` (`docs/decisions.md`). Five rounds of fixes and independent audits were applied to it: the audit round, the fix round with its re-audit, rounds 3 and 4 with a re-audit each (`docs/audit/FINAL-2.md`, `FINAL-3.md`, `FINAL-4.md`), and round 5 (`docs/decisions.md`; counting of rounds as there). The last audit, `docs/audit/FINAL-4.md`, found 66 merged rows (2 blocking, 25 major, 39 minor) and gave the verdict NOT READY; round 5 (cells C-179 to C-191) applied an edit for every one of those rows, and the fix logs `docs/fix/R5-*.md` mark each edit applied, already-applied or skipped. Round 5 had no re-audit, by decision of the owner (`docs/decisions.md`, Round 5), so no independent reader has checked the round 5 edits. The pattern of FINAL-3 and FINAL-4 is that an edit that conforms one part to a decision can leave a sibling part on the old text; expect further disagreements of that kind. The honest limit: the CI scripts (`check_params.py`, `check_issues.py`, `check_stale.py`, `check_refs.py api`, `check_opids.py`, `check_text.py`, `check_fixlog.py`, `check_audit.py`) check names, paths, parameter definitions, issue registers and operation ids, not meaning; FINAL-4 says the scripts do not show consistency. A green CI run is therefore necessary and not sufficient. [UNVERIFIED: `docs/audit/FINAL.md`, `FINAL-2.md` and `FINAL-3.md` were not read in full by this cell; their content is taken from `docs/decisions.md` and from the summary in FINAL-4.]

## Rules for build cells

1. **Two parts disagree.** Use the authority order of `docs/decisions.md` and D-30 of `docs/owner-decisions.md`: owner decisions (`docs/owner-decisions.md`), then the Founding Document (`docs/source/Hamyar - Founding Document.md`), then S0 (`spec/00-conventions.md`), then the part that owns the fact, then the other parts. D-30 sets the owner of a fact: entities and columns S5a; enums and state names S0 0.8 and 0.9; operation names and paths S15 (FINAL-4 cites 10a 10.18.1 for this); Device retention the S10a 10.14.1 and S10b 10.23.2 rule. [UNVERIFIED: the order as written in `docs/decisions.md` is not stated there as a numbered list; this is the order in the cell text of C-192, which D-30 supports for entities, enums and state names.]
2. **Apply the winner and record it.** Build to the winning text, and add one row to `docs/spec-issues-found.md` (date, parts, disagreement, winner, rule used, build cell). Never pick silently: a disagreement with no row is a defect of the build cell.
3. **Default-pending.** Where `docs/owner-decisions.md` marks a value default-pending (sections A and B, and rule C), build the default. Do not invent another choice. If a needed decision is in neither section, log `skipped-needs-owner` with the question and do not edit (rule C of that file).
4. **Protected files.** `docs/decisions.md` and `docs/owner-decisions.md` are not edited by cells; the owner records decisions there.
5. **Known issues.** Read the list below before building a part. An item listed there is a known disagreement or gap: build to the rule above, and add the row of rule 2 when the build meets it.

## Known issues

Source: every row of `docs/audit/FINAL-4.md` and every Noticed, not fixed item of `docs/fix/R5-01a.md` to `R5-09.md`. A row or item is called closed only where an R5 log says applied or already-applied for it. Closed means the edit was made; nothing was re-audited.

### FINAL-4 rows

Rows 1 to 66 each have an edit that the R5 log of its cell marks applied or already-applied (cells in brackets): rows 1, 12, 13, 41 to 45, 48 [R5-01a]; 10, 11 [R5-01b]; 14, 15, 16, 39, 40 [R5-02]; 3, 4, 7, 8, 28 to 32, 38 [R5-03a]; 5, 6, 9, 33 to 36 [R5-03b]; 37, 57, 58 and the S0 side of 6 [R5-04]; 2, 17, 18, 49 to 52 [R5-05a]; 19, 53 to 55, 59, 60 [R5-05b]; 20, 21, 56 [R5-06]; 22 [R5-07a]; 23 to 26, 61 to 64 [R5-07b]; 27 [R5-08]; 46, 47, 65, 66 [R5-09]. These rows have a remainder that is still open:

- Row 3 (device token typing): `spec/15a-api-core.md` is fixed; `spec/15b` to `spec/15g` were not searched for another 16-byte typing (R5-03a). Open.
- Row 12 (two-person claims): `spec/12-public-growth.md` and `spec/13-measurement.md` were checked only in the ranges read; other mentions of `experiment.start` or `flag.enable_credit_moving` were not searched (R5-01a). Open.
- Row 27 (reconciliation coverage): R5-08 fixed ids in 04, 06b, 07, 09, 12, 13 and 11c; `spec/15f-api-reconcile-measurement.md`, `spec/15g` and the second half of 15c to 15e were not opened, and no R5 log reports that `scripts/check_refs.py api` now covers operation ids (`check_opids.py` is the new check, per `docs/decisions.md`). Open; [UNVERIFIED] whether `check_opids.py` covers every id of 11d.
- Row 45 (names with no operation): closed by D-39. Credential add and unlock got operations (R5-01b); `invite.seed_issue`, `disclosure.release` and `secret.emergency_access` are marked reserved, no operation in Phase 1 (R5-01a, R5-01b). Closed by decision, still untestable.
- Row 61 (operation id collisions): applied; the check that the BM0 suite in `spec/18-testing.md` is keyed by the OpenAPI operationId was skipped (R5-07b 61-c). Open.
- Row 66 (log citations): only the citations FINAL-4 names were re-cited; other citations in `docs/fix/R4-03.md`, `docs/fix/R4-01.md` and logs R4-02, R4-05 to R4-07, R4-09 to R4-13 drift (R5-09). Open, low impact.

### Operation ids with no S15 operation (logged in docs/opid-aliases.txt)

- `spec/11c-admin-tools.md` 11.55: internal template review comment has no operation (action code `template.comment` remains) (R5-08).
- `spec/12-public-growth.md` 12.1.2, 12.6.1, SCR-pub-06: no read of one public milestone (R5-08).
- `spec/12-public-growth.md` 12.1.2, 12.10.5: no read of one referral by id (R5-08).
- `spec/07-policy.md` 7.15.4, 7.8.4: no stored draft policy version and no separate proposal step; S15b 15.25 creates, classifies and publishes in one call, so the draft and awaiting_approval states of 7.2.1 and 7.8.4 are unreachable through S15 (R5-08).
- `spec/11a-volunteer-ux.md` 11.6, 11.7: no public operation for the launch state or the approved-service count, which the landing needs before sign-in (R5-07a).

### Noticed, not fixed, by log (all open unless marked closed)

**R5-01a**

- `spec/15b-api-admin.md` 15.22.4: the enrollment code is shown in the final approval response and the proposer hands it over; delivery to the proposer is not specified.
- `spec/11c-admin-tools.md` 11.54.2 against `spec/15b`: fields `approval_request_id` and `state` against `approval_id` and `status`; S5a owns columns (D-30).
- `spec/15d`, `spec/15e` (15.D.4.3), `spec/15f`, `spec/15g`: may still say a cell overturn returns an approval (two-person), against D-39 (also R5-08).
- `spec/11c-admin-tools.md` 11.60: says the only admin write path to the ledger is the two-person reversal, while the single-admin cell overturn also posts a reversal; needs an owner or S6 decision.
- `spec/12-public-growth.md` 12.6.2, 12.17: `milestone.publish` is still called a two-person action to be appended to the list; it is not one of the 14 names and D-39 adds none.
- `spec/13-measurement.md` ISS-132, ISS-138: the name `prereg.lock` differs from `preregistration.lock` of 10a 10.12 and S0.
- Closed by later cells: `createCredentialChallenge` adding a credential with single-admin step-up (R5-01b 10-d); the `spec/11c` line 439 alarm kinds (R5-02 15a).

**R5-01b**

- `spec/14-launch-gates.md` 14.8.4, :60: `perm.killswitch.release_propose` and `perm.killswitch.release_approve` against `perm.killswitch.release` of the matrix, 11c and S15b.
- `spec/14-launch-gates.md` :56 against `spec/10a-identity.md` :420 and `spec/11c-admin-tools.md` :190: who may sign off an item of scope service (reviewer or operator only).
- `spec/14-launch-gates.md` :55 `perm.launch.attach_evidence` against `spec/15b-api-admin.md` :71 `perm.launch.evidence`; `perm.launch.read` against `perm.launch.read_restricted`; neither has a matrix row.
- `spec/15b-api-admin.md` :69 `perm.policy.tighten` against `spec/10a-identity.md` :399 `perm.policy.edit`: one action, two names.
- `spec/15b-api-admin.md` :61 `perm.admin.manage_users` has no matrix row; `perm.admin.role_grant` is used by S15b only as an action name.
- `spec/11c-admin-tools.md` 11.54.3 catalog: no row for `policy.loosen`, `admin.role_grant`, `admin.credential_add`, `admin.credential_unlock`, `preregistration.lock`, `secret.emergency_access`.
- `spec/14-launch-gates.md` :508, :509, :514 and 11.14 events: action names `launch.switch_propose`, `launch.switch_approve`, `launch.switch_close` against `launch.switch_on`, `launch.switch_off` of 11c and `changeLaunchSwitch` of 15b.
- `spec/15b-api-admin.md` 15.37: no acceptance criterion for the three credential operations or for refusing a credential added without approval.
- `spec/10a-identity.md` :421: the cell `2P on, Y off` holds two values; AC-access-01 must read the per-direction cell.
- `spec/15b-api-admin.md` :82 lists founders as holders of `perm.prereg.lock`; the matrix has roles only; reading stays [A].
- `spec/15c` to `spec/15g`, S10b, S5a, S16: not searched for `createCredentialChallenge` as admin with step-up or for `perm.launch.signoff` used for reopen.

**R5-02**

- `spec/11c-admin-tools.md` :732, :361, :380: alarm kinds `abuse.admin_lookup_rate` and `abuse.reviewer_disagreement` are not in the table of S15b 15.29.4, and the abuse queue now takes only category `abuse`.
- `spec/11c-admin-tools.md` :552: `ops.changelog_overdue` against kind `changelog.explanation_overdue` of 15.29.4.
- `spec/11c-admin-tools.md` :744, :761 against `spec/15b-api-admin.md` :603: the device-sharing count is in 11c only; `getMemberAdmin` returns no field for it.
- `spec/11c-admin-tools.md` :479 against `spec/15b-api-admin.md` :80: 11c lets a reviewer read ledger entries through an open appeal, report or alarm; 15b gives the ledger read permissions to the operator only.
- `spec/11c-admin-tools.md` :696: member rows of SCR-ops-13 are said to show context ids, which R4-05 removed.
- `spec/11c-admin-tools.md` :155-197 against the 10.11 matrix and 15b 15.21.4: catalog permission names differ by part (FINAL-4 row 11 residue).
- `spec/15b-api-admin.md` 15.29.3 `getReport`: returns the reporter as a pseudonymous `mem_id`, against AD7 and AC-abuse-04 of 11c (no admin API exposes a reporter id).
- `spec/14-launch-gates.md` :374: `g4.keep_wrap_replace` still lists Hand over.

**R5-03a**

- `spec/10a-identity.md` :233 (:238 per R5-04), 10.8 step 2: a recovery key is looked up with status active or retiring only, while both recovery keys work during the grace and the new one holds the first K4 value; the lookup does not name that value.
- `spec/15c-api-reconcile-core.md` :62: wording that the byte layout "may" bind origin and body hash is stale since 10a 10.3.2 (not a contradiction).
- Closed by later cells: the `DeviceLinkOffer` model (R5-03b 5-a to 5-j); Idem flags and the export id in 15c (R5-03b 33-a, 34-a).

**R5-03b**

- `spec/15c-api-reconcile-core.md` :~372 Observations: says `redeemDeviceLink` carries no challenge; 15a now carries one.
- `spec/15a-api-core.md` :173-176 against `spec/10a-identity.md` :771: 15a gives the device link operations no event; 10.18.2 lists `device_link.*` events; 15b 15.34 not opened.
- `spec/15a-api-core.md` :215, :236, `spec/15c` :299: `createMember` and `recoverMember` carry no `platform_class` in 15a while 15c and 10a 10.8 send it; type and out-of-range handling not stated.
- `spec/15a-api-core.md` :222: the key-state reason of `createSession` is now reachable only for a key with the first K4 value, which only a recovery key holds and a recovery key is not a session key.
- `spec/10a-identity.md` 10.18.1: no row for `revokeDevice`, `denyDeviceLink`, `listDevices`, `listSessions`; the step-up decisions for the first two are not in D-01 to D-44.
- `spec/15a-api-core.md` :208: `listDevices` shows expired and denied offers until the sweep; whether it should hide them is not stated.
- Closed by R5-04 (applied): the four identity entities in S0 0.7. The enums are still open (see R5-04).

**R5-04**

- `spec/10a-identity.md` :166 (10.6 pseudocode): a client label spelled like the first K4 value reads as a stored state; S0 0.8.6 says it is not.
- `spec/05a-entities.md` :7, :157, :225: still say S0.7 does not list the four identity entities, `StateTransition` and `mint_headroom`; the count "62 entities" at :225 is stale.
- `spec/00-conventions.md` :487 (0.9.4): lacks `member.key_revoked`, which 10a 10.6 uses [A].
- `spec/00-conventions.md` 0.8 and 0.9.8: offer states of `DeviceLinkOffer` and the enums `challenge_purpose`, `recovery_outcome`, `security_notice_kind` are in no S0 list, against D-30.
- `spec/00-conventions.md` :623: the owner cell names only `anomaly.*` as founders thresholds; 16c gives founders also three more names.

**R5-05a**

- `spec/00-conventions.md` 0.9.2 and 0.9.3: do not say that a deferral exists only in a job that is not settling or cancelling (optional pointer).
- `spec/11c-admin-tools.md` and `spec/08b-verification.md`: the operation that records a human decision on an escalated audit (CT-19, CT-09, CT-10) was not confirmed.
- `spec/16-parameters.md`: may repeat the old wording for `commons.job_overrun_days` (value at confirmation instead of at quote) [UNVERIFIED, not read].
- Closed by R5-05b (applied): the 5.29.8 overturn bullet and the headroom wording (rows 19, 53, 54, 55).

**R5-05b**

- `spec/05b-state-machines.md` :383-394: the lock-order table of 5.29.2 has no row for `mint_headroom`; the order of its two rows is stated nowhere.
- `spec/06a-ledger.md`: other text may still say a Commons lease locks the `issuance` account (not searched).
- `spec/06a-ledger.md` :381: the owner of S6 must confirm that `can_lease` needs no account lock.
- `spec/06a-ledger.md` 6.8.1: the exclusion of a flagged cell applies to `active_commons_leases` only, an interpretation [A].
- `spec/06a-ledger.md` :381: the cite `05a 5.4` for the `mint_headroom` section was not confirmed.

**R5-06**

- `spec/08b-verification.md` :687 (a): says S6 quotes with `max(price.v_prior, v_exp)`; D-04 and 06a 6.11.2 do not use `v_exp`.
- `spec/08b-verification.md` :558 against `spec/05b-state-machines.md` :326: a queued rejected cell is accepted on the original submission against not reopened.
- `spec/08b-verification.md` :525 (8.32) against `spec/06a-ledger.md` :317: a rework cell is created against none when the escrow is closed.
- `spec/08b-verification.md` :~100 (8.22.2 `choose_plan`): the random audit draw has no skip branch for a floor-band draw the pool cannot pay.
- `spec/08b-verification.md` :302, `spec/06a-ledger.md` :508: v exactly n minus 1 leaves no room for gold cells; a margin is an owner question.
- `spec/06a-ledger.md` :526 (6.11.4): at p = 3.05 eta is about 0.33, below the alarm threshold 0.80, so the alarm fires at once for the code-change type; same tension in `S16D-C1`.
- `spec/16-parameters.md` :84 (C8), :181: C8 does not cover a high-risk template (915 credits against K = 350); `price.v_cap` row does not say the cap does not apply to it.
- `spec/11b-requester-ux.md`, `spec/06b-admission.md`: no criterion that the price of a high-risk template is stated before the hold; no refusal at quote with the largest holdable job.
- `spec/06a-ledger.md` 6.16.2, `spec/08b` 8.38, `spec/08a`: no acceptance criterion for the first quote of a high-risk template.

**R5-07a**

- `spec/11a-volunteer-ux.md` :177, :478, :1149: 11a says `getMe` carries the restriction end, the key-saved flag and the first accepted cell; the 15a `Member` object does not.
- `spec/11a-volunteer-ux.md` :430-437, :451, :459, :490 against 15a 15.6.2: eight `expand_required` reasons and an acknowledge semantic against `requires_expansion`, a two-value reason and a call that returns the prompt.
- `spec/11a-volunteer-ux.md` :509-516, :640: service and paste-back field names differ from `ServiceView` and `submitResult`.
- `spec/11a-volunteer-ux.md` :1087, :1094: with `ff.growth.v5_referral` on, 15a 15.8 issues the bonus invite through `createReferral`; 11a uses `createInvite` only.
- `spec/11a-volunteer-ux.md` :1150, :1317, :1318, :1157: no `Step-Up` header mentioned; :1150 says rotating the recovery key invalidates the old key, while 15a keeps both during `identity.key_rotation_grace_s`.
- `spec/11a-volunteer-ux.md` :876: the History filter declined is served by `listLeases`; a card declined before any lease leaves no row.

**R5-07b**

- `spec/11b-requester-ux.md` :694, AC-req-57, 11.49: tags, a comment and flagged cell indices are collected, while `rateJob` takes only a score (D-24); 11.49 still lists a rating entity with comment and an event.
- `spec/11b-requester-ux.md` :~1066: parameter `ui.requester.appeal_note_max_chars` is unused now.
- `spec/11a-volunteer-ux.md` :~202: defines `appeal.reason_max_chars` in a convention table; its S16 entry and the field name in 11a were not checked.
- `spec/11b-requester-ux.md` :155-169 and :~176, :~192: other Job, Quote and progress fields differ from 15a.
- `spec/11b-requester-ux.md` 11.42.1, 11.45 against 15a 15.7.3: the no-training flag and the notice differ for P1.
- `spec/11b-requester-ux.md` :~404: the acknowledgement ticks are said to be client-side only, while 15a stores acknowledgements in the declarations.
- `spec/15b-api-admin.md` :~24 (15.21.1): the colliding-id list omits `listAppeals` and `getAppeal`.
- `spec/18-testing.md`: not checked whether BM0 is keyed by the OpenAPI operationId.

**R5-08**

- `spec/06b-admission.md` 6.28.3: the confirm body is `{quote_seq}` against `{quote_hash, reservation_id?}` in 15a 15.7.2 and 6.35.
- `spec/04-architecture.md` 4.4.2: the interface block names internal service methods (old operation names) without backticks.
- `spec/04-architecture.md` 4.9.4: `launch.members_may_join` is said to be checked at lease time; the gate matrix of 15a 15.4 checks it only in `createMember`.
- `spec/07-policy.md` 7.15.4: other rows keep paths that differ from S15b.
- `spec/09-result-return.md` 9.4.1, 9.5.2: request and response field names differ from 15a 15.6.2 and 15.6.4.
- `spec/12-public-growth.md` 12.8.2: share card payload fields differ from `ShareCard` (mapping in 15d row 25).
- `spec/13-measurement.md` 13.10.2: permission `perm.calibration.record` against `perm.calibration.write`.
- `spec/11c-admin-tools.md` 11.56 and AC-svc-04 against 15b 15.23.2: one-request terms copy upload against chunked upload and seal.
- `spec/15e-api-reconcile-admin.md` 15.D.2 rule 3, 15.D.4.3: still makes cell overturn two-person against D-39.
- `spec/15f`, `spec/15g`, second half of 15c to 15e: not opened by R5-08; ids there taken as defined.

**R5-09**

- `spec/13-measurement.md` :869, :891: the salt change-log entry names no `subject_kind`; the list of 12.5.1 has none for it.
- `spec/12-public-growth.md` :441: `min_trust_tier` and `locales` of `eligibility` have no meaning or default.
- `spec/14-launch-gates.md` :551 against `spec/15a-api-core.md` :354: which service a lease tests (the cell's or the one the member sends) is stated twice differently.
- `spec/12-public-growth.md` 12.12.2 (V2): says population `all_members` without saying `include_existing` must be true; 12.12.3 to 12.12.6 not read.
- `docs/fix/R4-03.md` rows 11-c to 11-g, 13-g and `docs/fix/R4-01.md` row 1: citations drift; only those named by FINAL-4 row 66 were corrected.
- `docs/fix/R4-04.md` and other offset notes: state that no other citation was re-checked.
