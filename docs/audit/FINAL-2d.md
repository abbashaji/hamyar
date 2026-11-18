# Audit FINAL-2d: re-audit round 2, slice D (contradictions and verdict reasons)

*Cell C-136. Written by a reviewer who did not write FINAL.md or any audited part. Scope: rows 8 to 21 and row 26 of the Findings table of `docs/audit/FINAL.md`, its section 5 and its section 4. Nothing was executed.*

## Checked

- Work in progress: this file was created first and is extended as the spec files are read.

## Contradictions

| FINAL row | status | lines seen |
| --- | --- | --- |
| 8 | CHANGED | Edge clearing now exists: `05a:431` ("Edge clearing" paragraph, clears `Member.invite_id`, `Invite.issuer_member_id`, `Invite.redeemed_by_member_id`) and `10a:334` ("`invited_by_member_id` is cleared `invite.accountability_days` after"). Names still differ and are declared aliases only: `05a:358` `invite_id`, `05a:424` `issuer_member_id`, `05a:428` `redeemed_by_member_id` against `10a:31` `invited_by_member_id` and `10a:39` `inviter_member_id`, `invitee_member_id`. One name is not aliased and has another type: `05a:429` `tree_root_member_id` and Member `invite_root_member_id` (`mem_` id) against `10a:31`, `10a:39` `invite_tree_id` (an `inv_` id, `10a` registration text: a fresh opaque `inv_` ULID in open mode) |
| 9 | CLOSED | `05a:141` ("The creation-time IP hash is not a column of any table of this model"), `05a:405` (Device `Not stored` list names "any IP hash"), `05a:107` (IP held only in volatile counters); Device field table `05a:397-401` has no IP column; `10a` 10.14.2 item 2 (counters volatile, not in the database or backups) and 10.14.1 row "IP hash"; `10b:610` `AC-safety-01` ("only keyed counters exist, holding no member id"). Not searched: every other line of `05a`, `05b`, `04` for a stray `creation_ip_hash` (no search tool) |
| 10 | CLOSED for the collision, one new defect | `10a` headings seen: 10.2, 10.3, 10.4, 10.11, 10.12, 10.13, 10.14, 10.15; `10b` headings seen: 10.21, 10.21.1 to 10.21.4, 10.23.1 to 10.23.8, 10.26.5 to 10.26.8, 10.27, 10.28 (`10b:5`, `10b:603`, `10b:632`). The two files no longer share a number in what was read. Stale references to the old numbers remain: `05a:124` ("10b 10.13.1 item 11 and 10.13.3") and `05a:141` ("10b 10.13.2"), `10a` 10.14.2 items 1 and 4 ("10b S10.14.2"); `10b` has no 10.13 or 10.14 in what was read, and `10a` 10.13 is session handling |
| 11 | STILL OPEN (narrower) | Closed part: `MemberKey` is `purpose` and `status` in both (`05a:376-390`, `10a:32`); `AdminUser` matches (`05a` 5.6.8, `10a:40`); `secret.email_encryption_key` is the name in `05a:136-137` and `10b` 10.23.2. Still different: Device `10a:33` `token_hash`, `state`, `grants_issued` against `05a:397-401` `device_token_hash`, `status`, `grants_claimed`; Member `10a:31` `last_active_on`, `registration_device_id`, `email_index` against `05a:358-368` `last_active_day`, `creating_device_id`, `email_lookup_hash`; Session `10a:34` has `step_up_at`, `05a` 5.6.4 has none; AdminAction `10a:42` has `outcome` and the proposal state (`10a` two-person protocol: `state proposed`, `expires_at`), `05a` 5.6.10 has `seq`, `reason`, `payload`, `entry_hash` and no state, outcome or expiry. Not read: the S10.24.2 secrets inventory of `10b`, so `g1.secrets_inventory_complete` name equality is not confirmed |
| 12 | CLOSED | `05a:124` ("Never computed for a public page: public surfaces are aggregates and show no `vol_` handle"); `10b` 10.23.3 rows `other_member`, `requester_malicious` (handle never shown to requesters or members) and 10.23.2 row "Hashes and manifests". The citation inside `05a:124` to "10b 10.13.1 item 11" points at no section (row 10) |
| 13 | STILL OPEN (not yet re-read at this commit) | read pending: `05a` 5.8.2 Lease |
| 14 | STILL OPEN (not yet re-read at this commit) | read pending: `05a` 5.7.5, 5.8.1 |
| 15 | STILL OPEN (not yet re-read at this commit) | read pending: `05a` 5.9.2, 5.9.3 |
| 16 | CHANGED | `05a:256-258` (`state_transitions` DDL with `occurred_at`, trigger line), `05a:261-288` (`mint_headroom` table, DDL, unique indexes), `05a` 5.4 intro ("plus the two additions of S5.4.1 ... that S0.7 does not list yet"). Both entities now exist in `05a`; `S0.7` still does not list them, by `05a`'s own statement (S0 not re-read here) |
| 17 | STILL OPEN (not yet re-read at this commit) | `05a` 5.6.10 `reason` is still free text, `<= 1000 chars` in a `permanent` table (`05a` AdminAction table); `10b` 10.23.2 says "reason codes only" |
| 18 | STILL OPEN (not yet re-read at this commit) | read pending: `00-conventions` 0.9.6, `05b` |
| 19 | STILL OPEN (not yet re-read at this commit) | read pending: `05b` |
| 20 | STILL OPEN (not yet re-read at this commit) | read pending: `05b` MT-06 |
| 21 | STILL OPEN (not yet re-read at this commit) | read pending: `05b` SBT-06, `09` |
| 26 | STILL OPEN (not yet re-read at this commit) | read pending: `11a` F2/F3, `11d` S11.51, S11.52 |

## Verdict reasons

1. NOT MET: not yet assessed; see the next commit.

## Owner decisions

- Not yet listed.

## Findings

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | minor | n/a | audit of this slice not finished at this commit | continue reading |

Verdict: NOT READY
