# FINAL-3a: re-audit round 3, slice A (fix logs R3-01 to R3-06)

*Cell C-156. Written by a reviewer who wrote none of the six logs or the edited parts. Nothing was executed here; CI runs the acceptance commands. Line numbers are counted by me from the start of each chunk I read (at most 600 lines per read); where a log gives another number, the row says so. No file content is pasted.*

## Checked

I opened the six logs and then the cited place in the part file for more than 70 edit rows marked applied: R3-01 12 of 12, R3-06 3 of 3, R3-02 13, R3-03 11, R3-04 24, R3-05 12. For R3-01 and R3-06 I also read the surrounding text of the same file for the old fact. Owner decisions D-22, D-23, D-30, D-32, D-33 and D-34 of `docs/owner-decisions.md` are taken as accepted and are not reported as open.

**R3-01 (`spec/10a-identity.md`).** Present and correct: check 4 reads purpose `create` (:95, and :67, :79, :83 agree); purposes `rotate` (:168), `device_link` (:200), `step_up` (:206); key states `retiring` at :162, :170, :182, :234 (10.8 step 2; the log says :233) and :524; transitions of the device-link offer at :192 have `ttl` and `cancel` only, and the claim step at :201 has no counter. Edit 35 at :139 is NOT present (row 2 below).

**R3-06 (`spec/06b-admission.md`).** `AC-admission-15` at :589 reads `null` with `suppressed: true` for both counts; the Public gauge row at :175 and `AC-admission-36` at :617 agree. I read only :170-180, :580-596 and :608-618; the log's claim that the file has no other `<k` string rests on the log.

**FINAL-2 rows, status after R3.**

- Row 1 closed (10a:95). Row 3 closed (06b:589). Row 4 closed (11c:208, :233). Row 5 closed for the five rows I opened: `AC-req-14` and `AC-req-33` are gone (11b:340 is followed by the SCR-req-05 heading; 11b:471 by the SCR-req-10 heading), `AC-req-25` (11b:390), `AC-req-38` (11b:502), `AC-req-58` (11b:711) are rewritten; `AC-req-75` not opened.
- Row 2 closed: 10a:585 gives range 1..30 and a new lever, 10a:635 and 10a:701 agree, S0:753 reads 1..30; the new `kill.optional_pii` text sets `retention.request_log_days` to 0, which S0:755 allows (0..90).
- Row 7 closed for the rows it names (11c:759 uses `getMemberAdmin`; `AC-lookup-07` and `-08` are gone), open in the same table (rows 7 and 8 below). Row 8 closed for `AC-claim-04` and `-08` (11c:805-811 list 01, 02, 03, 05, 06, 07, 09; `ISS-117` at :872 reads (a) to (j)). Row 9 closed: 11c:644-665 and the catalog rows at :189-190 and :225-226 state one rule (sign-off per item, switch only by `changeLaunchSwitch`, `value: true` two-person); op ids at :653-656 follow 15b.
- Row 13 closed in text (10a:353 and 05a:1174 drop the shared-IP-hash hold); its premise is contradicted by the 05a DDL (row 5 below).
- Row 23 closed: 05a 5.9.1 (:871-884) has no `vol_` sentence; the export paragraph at :864 says the handle is removed from every cell.
- Row 34 closed at the three named lines. Row 36 closed in the transitions and the claim step, not in the entity table (row 4 below). Row 42 closed for op ids (11c:208-209, :232) and the `admin.approval_*` events (11c:119-123, :196, :234); one residue (row 10). Row 43 closed (11c:116, :234, :844 read `security.two_person_ttl_s`). Row 44 closed (11c:470).
- Row 65 closed: 05a:417-418 (`member_bound` plus residue), 10a:33, 10a:286 and 10a:551 all state one rule. Row 24: Invite names agree in 05a:438-445, 10a:39 and 10a 10.10, except one check (row 1 below).
- Rows 14, 25, 35 and 51 are NOT closed (rows 2, 3, 6, 13, 14 below).

Also confirmed present: 10a:565, 10b:167 and 05a:521, :1073, :1224, :1382 carry the D-32 sentence (free text, may contain personal data, access-controlled, `permanent`); 11b:121, :138, :563, :613, 11c:693 and 07-policy:1084 carry the R3-05 edits.

## Findings

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | major | spec/10a-identity.md:97 | Registration check 6 requires an `Invite` in state `active`; 05a:67 lists `invite_status` as `issued`, `redeemed`, `expired`, `revoked` and 05a:442 defaults to `issued`; R3-02 edit 24b changed only 10.10. Read literally every invite-only registration fails check 6 (the same class as FINAL-2 row 1) | change `active` to `issued` at :97; search 10a for any other `Invite` state named `active` |
| 2 | major | spec/10a-identity.md:139 | 10.4.4 Effect row says the old key becomes `rotated`; :162, :170, :182, :234 and :524 say `retiring`. R3-01 edit 35 and its read-back state :139 reads `retiring`; R3-02 edit 14e records writing `rotated` there. The file holds the old name, the log claim is false | set :139 to `retiring` with the grace rule unchanged; correct the R3-01 and R3-02 rows |
| 3 | major | spec/10a-identity.md:32; spec/05a-entities.md:68 | MemberKey states are named three ways: 10a:32 lists `active`, `rotated`, `revoked`; 10a:162 lists four (first state, `active`, `retiring`, `revoked`); 05a:68 `key_status` lists `active`, `rotated`, `revoked`, and 05a:393 and :395 follow it. D-30 makes the S0 names canonical; no R3 cell edited 05a or :32. I did not open S0 0.8/0.9 or 15c 15.B.3.1 for the key states | confirm the four names in S0/15c, then set 10a:32, 05a:68, 05a:393 and the `rotated_at` wording at 05a:395 to them in one cell; if S0 has no key-state list, owner decision |
| 4 | major | spec/10a-identity.md:36 | The `DeviceLinkOffer` row still lists a column `attempts` (and `claimed_key_hash`); R3-01 row 36 removed the counter at :201 and the transition at :192, so the entity keeps a field nothing writes | remove `attempts` from :36 |
| 5 | major | spec/05a-entities.md:1436-1442 and :2005 | DDL for `devices` keeps `creation_ip_hash`, `ip_hash_key_version`, `creation_ip_hash_expires_at`, a CHECK and index `devices_ip`, and 5.15.4 (`short`) nulls the column; the same file says no IP hash is persisted (:145, :418, :1174), as do 10a:353 and D-23. Row 13 was closed on a premise the DDL contradicts | delete the three columns, the CHECK, the index and the 5.15.4 clause (default under D-23); if the owner wants the hash kept, reverse D-23 and 10a:353 instead |
| 6 | major | spec/10b-safety.md:166; spec/05a-entities.md:1092, :1114, :1208 | 10b:166 says reports and appeals hold pseudonymous ids only, while `reporter_text` (1000), `statement` (2000) and `ParameterVersion.reason` (1000) are free text; D-32 forbids that claim, and only four fields received the D-32 sentence | reword 10b:166; add the D-32 sentence to 05a:1092, :1114, :1208 and to `LaunchGateItem.reopen_reason` |
| 7 | major | spec/11c-admin-tools.md:762-763 | `AC-lookup-05` expects a `member.lookup` row naming the context ids and `AC-lookup-06` starts from a farming context, while `getMemberAdmin` (:754) has no body and `AC-lookup-02` (:759) sends no context; D-20 says the read is logged, not justified. A correct implementation fails `AC-lookup-05` | rewrite both rows without a context; remove the other context requirements R3-04 listed (11.59 Context rule, 11.65.1, 11.64.1) |
| 8 | major | spec/11c-admin-tools.md:195, :198, :226, :872 | The catalog still defines action `member.resolve_handle` (CT3, own permission) and counts it among the two-person additions, although handle resolution was removed; D-34 builds the minimum set of `security.two_person_actions` from the marked actions, so a removed action enters it | delete the row at :195; remove the name at :198, :226 and `ISS-117` (f) at :872, and from the nine-name paragraph of 11.68 |
| 9 | minor | spec/11c-admin-tools.md:191 | Row `launch.reopen`, `launch.switch_off` gives `perm.launch.signoff` and events `parameter.changed`; :656 says `changeLaunchSwitch` needs `perm.launch.switch` and :190 lists the three `launch.<switch>_changed` events | split the row: reopen keeps `perm.launch.signoff` and `gate.reopened`; switch_off takes `perm.launch.switch` and the three events |
| 10 | minor | spec/10a-identity.md:728, :732 | 10a lists operation `approveApproval` only and events `admin.approval_requested`, `_granted`, `_expired`; 11c:209, :121-123 and :196 add `rejectApproval`, `withdrawApproval`, `admin.approval_rejected`, `admin.approval_withdrawn`. Row 42 asked for one set | add the two operations and two events to 10a 10.18.1 and 10.18.2 |
| 11 | minor | spec/11b-requester-ux.md:710-711 | `AC-req-57` says the screen becomes read-only after one `rateJob`; `AC-req-58` now says a second submission replaces the rating | reword :710 so the stored rating is shown and stays editable until the window ends; align `SCR-req-17` entry conditions |
| 12 | minor | spec/11c-admin-tools.md:765-767, :799 | Heading 11.66 and its Purpose still describe Release / Hand over after `AC-claim-04` was deleted; :799 says no handover | rename the heading and reword Purpose and 11.66.1 to release and takeover |
| 13 | minor | spec/05a-entities.md:438 and the `invites` DDL | Row 51 asked for a nullable `issuer_member_id` in text and DDL; the text is done (:438); R3-02 edit 51b was skipped and I did not find or open the DDL | open the `invites` DDL, drop NOT NULL on `issuer_member_id`, keep a CHECK that a `member` invite has an issuer while the edge exists |
| 14 | minor | spec/10a-identity.md:148, :33 | 10.5 Storage row still names `email_index` (05a and 10a:552 use `email_lookup_hash`); :33 keeps `registrations_count`, which 05a:408-415 does not have | rename at :148; drop `registrations_count` or add the column |
| 15 | minor | spec/10a-identity.md:181 | The case table uses `revoke_key`, one of the 13 retired purpose names, as an action; R3-01 read-back says no retired name remains | write `revokeMemberKey` (10.18.1) |
| 16 | minor | spec/10a-identity.md:197, :201-206 | Old vocabulary (`link_secret`, `offer_id`, `device_pub`) stays, and :206 says the step-up `context_hash` covers `offer_id` and `claimed_key_hash` while 15c 15.B.3.1 covers path and body (R3-01 logged it) | rewrite :197-206 to the 15c names and the 15c hash rule |
| 17 | minor | docs/fix/R3-02.md:1 | Line citations drift: Device retention is cited at 05a:404-407 (text at :417), Invite at 05a:424 (:438-445), `AC-lookup-02` in the R3-04 log at 11c:~764 (:759); the log of R3-01 says :233 and :352 where I count :234 and :353 | add an offset note to each log or re-cite |

## Not verified

- Key-state names in S0 0.8/0.9 and 15c 15.B.3.1 (needed for rows 2 and 3); 15c and 15.B.9 were not opened.
- R3-02 edits 14c, 24b, 24c, 24d, 24f (10a 10.3.1 key table, 10.10 text, `AC-invite-05`, 10.18.4), the `invites` DDL (row 13), and 05a outside the ranges named above.
- R3-04: guard 4 of 11.54.1, 11.60.3 (:~528 is not the audit events line), op ids at 11c:~697-698, the heading of 11.65.3, the paragraph of 11.68, `AC-req-75` in 11b.
- 10a lines 100-130, 300-337, 372-484, 600-625 and 745-776 and 06b outside :170-180, :580-596, :608-618: a leftover of an old purpose, key state or `<k` string there was not looked for.
- Nothing was run; `check_audit.py`, `check_params.py`, `check_issues.py`, `check_stale.py` and `check_refs.py api` are CI's.

Verdict: NOT READY
