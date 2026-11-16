# FIX-08: API reconciliation applied to part 12 (public and growth)

Cell C-079. Source of the edits: `spec/15d-api-reconcile-requester-growth.md`, section 'Edits required in citing parts', block 'Part 12', and the rows of its decision table (15.C.2) that cite part 12 (rows 4, 5, 18, 19, 20, 21, 22, 25, 26, 27). Edited file: `spec/12-public-growth.md` (811 lines before and after). Nothing was executed; CI runs the acceptance checks.

## Method

Each cited place was located by reading the surrounding lines of the part (cited lines had not drifted for 12:29, 12:35, 12:38, 12:466, 12:511). The old text was replaced in place with `apply_changes` (small old to new edits, base 5f61745, one commit). The 12.9.2 rows were matched by row text, as the source says. The full part 12 was read to find other occurrences of the replaced paths. Conflicts were checked against the ground rules in `docs/decisions.md` and the owner decisions of `docs/audit/FINAL.md` section 4; the Founding Document was not re-read in full for this cell.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| 12:29 public ledger row (rows 19, 20, 21) | spec/12-public-growth.md:29 | `listPublicLedgerCheckpoints`, `getPublicLedgerCheckpoint`, `listPublicLedgerFlows` on `/v1/public/ledger-checkpoints`, `.../{checkpoint_date}`, `/v1/public/ledger-flows`; cache cell with the immutable by-date note | `listPublicLedgerCheckpoints` (one date: `from` = `to`) and `listPublicLedgerDaily` on `/v1/public/ledger/checkpoints` and `/v1/public/ledger/daily`; cache cell `public.counter_refresh_s` only | applied |
| 12:33 public teams row (row 22) | spec/12-public-growth.md:33 | `listPublicTeams` `GET /v1/public/teams` | unchanged: source says no edit needed | already-applied |
| 12:34 experiments row (row 18) | spec/12-public-growth.md:34 | `listPublicExperiments` `GET /v1/public/experiments` | unchanged: source says no edit needed | already-applied |
| 12:35 share card row (row 25, D-15) | spec/12-public-growth.md:35 | `getShareCardPayload` `GET /v1/share-cards/preview` | `getShareCard` `GET /v1/members/me/share-card`; computed on request, no stored link, per D-15 default (stricter privacy reading), default-pending | applied |
| 12:38 flags and exposure row (rows 4, 5) | spec/12-public-growth.md:38 | `listEffectiveFlags` `GET /v1/flags` | `getFeatures` `GET /v1/members/me/features`; `recordExperimentExposure` unchanged | applied |
| 12:466 effective variants sentence (row 5) | spec/12-public-growth.md:466 | `GET /v1/flags` returns the member's effective variants | `GET /v1/members/me/features` (`getFeatures`) returns effective flags as booleans, no arm names; still the only place assignment is created | applied |
| 12:511 exposure bullet (row 4) | spec/12-public-growth.md:511 | `POST /v1/experiment-exposures` (`assignment_id`, `surface_key`, `Idempotency-Key`) | (`surface_key`, `Idempotency-Key`; the server finds the member's own assignment and answers `204` whether or not an experiment applies) | applied |
| 12.9.2 table, `leaveTeam` (row 26) | spec/12-public-growth.md:355 | `DELETE /v1/team-memberships/{membership_id}`, key required | `DELETE /v1/teams/{team_id}/memberships/me`, key optional, honored if sent | applied |
| 12.9.2 table, `reportTeam` (row 27) | spec/12-public-growth.md:356 | `POST /v1/teams/{team_id}/reports` | `POST /v1/reports` with `subject_kind` = `team`, `subject_id` = the team id; key required | applied |
| 12.11 intro, second citation of the replaced `GET /v1/flags` (not listed separately; same re-pointing as 12:466, needed so `check_stale.py` finds no replaced path) | spec/12-public-growth.md:430 | lazy assignment on the first `GET /v1/flags` | lazy assignment on the first `GET /v1/members/me/features` | applied |

## Read-back

After the commit every edited place was read again.

- 12:29 (line 29): the row names `listPublicLedgerCheckpoints` and `listPublicLedgerDaily` with the two `/v1/public/ledger/...` routes; no `ledger-flows` and no by-date route remain.
- 12:33 and 12:34 (lines 33, 34): both public rows are as before.
- 12:35 (line 35): the row reads `getShareCard` and the `members/me/share-card` route.
- 12:38 (line 38): the row reads `getFeatures` on `/v1/members/me/features`; `recordExperimentExposure` is still there.
- 12:466 (line 466): now says flags come back "as booleans, with no arm names".
- 12:511 (line 511): the bullet no longer lists `assignment_id`; it says the answer is `204` either way.
- 12.9.2 table (lines 355, 356): `leaveTeam` shows the `memberships/me` route and "optional, honored if sent"; `reportTeam` shows `POST /v1/reports` with `subject_kind` = `team`.
- 12.11 intro (line 430): lazy assignment now cites `GET /v1/members/me/features`.
- File length is still 811 lines.

## Observations not edited (outside the authorized list)

- 12.8.2 (`getShareCardPayload returns ...`) and `AC-sharecard-01` still use the operation id `getShareCardPayload`. 15d says the 12.8.2 text stays as it is (it is the design S15a follows), so the id was not renamed. A later cell (FIX-12 or the consistency cell) should align the id. Also, 12.8.2 lists payload fields (`cells_verified_total`, `badges`, `locale`, `digits`, `landing_url`, `card_version`) that 15d row 25 maps to the S15a `getShareCard` response; that mapping is not written into part 12.
- 12.11.5 still says members see their own arm on a settings screen, while `getFeatures` returns booleans only. This is open point O10 of 15d; no decision with a default exists in FINAL.md section 4, so nothing was changed. The mechanics of 12.12 have two arms each (V1, V5 named), so booleans may suffice.
- 12.9.2 and 12.16 still describe `reportTeam`, `leaveTeam` behavior that depends on S15a adding `team` to `subject_kind` (15d S1) and on the owner decision D-13 (`team.min_public_members`); neither was touched here.
- 12.1.2 row `Teams (member)` and 12.13.1 event payloads (`assignment_id` in `experiment.exposed`) are unchanged; 15d keeps the assignment id in the event payload.

Result: DONE
