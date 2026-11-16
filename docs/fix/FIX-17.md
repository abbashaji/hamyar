# FIX-17: 05a entities: device, member, invite minimization

Cell C-088. Edited file: `spec/05a-entities.md` only. Sources: `docs/audit/FINAL.md` sections 4 and 5.1 (FIX-17), `docs/audit/A04.md` findings 6, 15, 20, 21, `spec/10a-identity.md` 10.10 and 10.14.2, `spec/10b-safety.md` 10.13.1 and 10.13.2. Stricter reading applied: an IP hash exists only in the volatile counter store (10a 10.14.2 item 2). Line numbers are the pre-edit lines found by reading around the cited place; the audit cited about 107, 136 and 324, and the Device and Invite rows were found about 80 to 110 lines further down. D-12 is the owner decision whose default (edges treated like retention) is used for the invite edge; rows that rely on it say default D-12, owner decision open.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 minimization table, raw IP row | spec/05a-entities.md:107 | nearest permitted thing was a keyed hash named as the column `devices.creation_ip_hash` plus the rate-limit counters | a keyed hash with a TTL held only in the volatile rate-limit counters, never in a table or a backup (S5.3.3, 10a 10.14.2) | applied |
| E2 keyed-hash table, `devices.creation_ip_hash` row | spec/05a-entities.md:136 | row with HMAC of the client IP at identity creation, key `secret.ip_hash_key[v]`, kept `retention.ip_hash_ttl_days` then NULL | row removed; the hash is not a column of any table | applied |
| E3 paragraph after the keyed-hash table | spec/05a-entities.md:142 | counters live in the cache or in a `rate_counters` table | counters live only in the volatile `CounterStore`, not in a table, not in backups, no member id; consequence stated: per-day limits keyed by IP hash or invite tree use the volatile counter only, so they cannot be audited from the database and a restart resets them; limits on stored columns unaffected | applied |
| E4 Device columns | spec/05a-entities.md:403 | `creation_ip_hash`, `ip_hash_key_version`, `creation_ip_hash_expires_at` | row removed (all three columns) | applied |
| E5 Device indexes | spec/05a-entities.md:406 | index on `(creation_ip_hash, created_at)` where not null, and `(last_seen_day)` | only `(last_seen_day)` | applied |
| E6 Device Not stored | spec/05a-entities.md:408 | Not stored: raw IP, user-agent and the rest | adds any IP hash, whose creation-time form lives only in the volatile counter | applied |
| E7 `vol_` handle on public reads (A04 finding 20) | spec/05a-entities.md:124 | computed on read for `vol_` shown on public pages | never computed for a public page; public surfaces are aggregates (10b 10.13.1 item 11, 10.13.3); handle read only from `submissions.volunteer_handle` and the internal manifest by verifier and admin paths | applied |
| E8 Member `invite_id` (A04 finding 6, names) | spec/05a-entities.md:360 | the invite redeemed, if any | adds: with `Invite.issuer_member_id` it is the edge 10a calls `Member.invited_by_member_id` (alias, 10a canonical); NULL after edge clearing (default D-12, owner decision open) | applied |
| E9 Invite `issuer_member_id` (A04 finding 6, names and clearing) | spec/05a-entities.md:436 | NN, FK | NN, FK, NULL once the edge is cleared; alias of 10a `inviter_member_id`, 10a canonical (default D-12, owner decision open) | applied |
| E10 Invite `redeemed_by_member_id`, `redeemed_at` (A04 finding 6) | spec/05a-entities.md:439 | null, both set or both null; empty note | after clearing `redeemed_by_member_id` NULL and `redeemed_at` holds its UTC date; alias of 10a `invitee_member_id`, 10a canonical (default D-12, owner decision open) | applied |
| E11 Invite edge clearing rule (A04 finding 6) | spec/05a-entities.md:443 | no clearing rule; the edge was permanent | new paragraph: after `invite.accountability_days` from the invitee `created_at` the sweep nulls the three edge columns and truncates `redeemed_at` to its date; tree columns stay; kept until `retention.moderation_days` after resolution if a party is banned; operators alone see edges (default D-12, owner decision open) | applied |
| S1 Device token hash and retention (A04 finding 15, second half) | spec/05a-entities.md:399, 400, 393 | HMAC-SHA-256 of a 256-bit token, `hash_key_version`, retention `short`; 10a (ISS-103) uses plain SHA-256 of a 128-bit token and `member_bound` with grant-memory residue | unchanged | skipped-needs-owner |
| S2 Self-invite same-IP-hash hold (10a 10.10 anti-farming) | spec/10a-identity.md:352 (read only) | 10a holds the invitee starter grant when the inviter and invitee share an IP hash on the same day; with no persisted IP hash and no member id in the counter, nothing can answer that later | unchanged; a persisted yes-or-no value derived from an IP hash would need an owner decision, so no column was kept or added | skipped-needs-owner |
| S3 Tree identifier (A04 finding 6) | spec/05a-entities.md:361, 440 | 05a stores `invite_root_member_id` and `tree_root_member_id` (a `mem_` id); 10a keeps an opaque `invite_tree_id` equal to the seed invite id | unchanged; a different type of id is a rename, not an authorized edit | skipped-needs-owner |
| S4 Precise timestamps on Member (A04 finding 21) | spec/05a-entities.md:352-368 | 10b says the row holds a creation day; 05a stores `created_at`, `status_changed_at`, `first_accepted_at`, `starter_granted_at`, `restricted_until` as precise timestamps; no default in D-01 to D-22 covers it | unchanged | skipped-needs-owner |

## Read-back

Every edited place was re-read on the cell branch after the edits.

- E1 (line 107): the row now says the permitted thing is a hash held only in the volatile counters, and names no column `devices.creation_ip_hash`.
- E2 (former 136): the keyed-hash table now lists `devices.device_token_hash`, then `members.email_lookup_hash`; no IP row remains in it.
- E3 (line 142 and after): the paragraph opens with "not a column of any table", names the volatile `CounterStore`, and states the minimization consequence.
- E4 and E5 (Device table, about 396 to 404): the rows are `device_token_hash`, `hash_key_version`, `status`, the day columns and `grants_claimed`; the line below the table gives `(last_seen_day)` as the only index.
- E6 (Device Not stored): it now lists "any IP hash" with a pointer to S5.3.3.
- E7 (line 124): the Stored in row says the handle is never computed for a public page and is read only from the submission row and the internal manifest.
- E8 (line 359): the `invite_id` note names the 10a alias and says NULL after clearing.
- E9 and E10 (Invite table, lines 424 and 428): `issuer_member_id` reads NN, FK, NULL once cleared with the 10a alias; the redeemed row says `redeemed_at` holds its UTC date after clearing, with the 10a alias.
- E11 (line 432): the Edge clearing paragraph stands above the Unique line and names `invite.accountability_days` and `retention.moderation_days`.
- Against 10a 10.14.2 item 2 and 10b 10.13.1 item 6 and 10.13.2: 05a no longer stores any IP hash in a table at the places read. Not read: `AC-safety-01` itself (its line was not in the ranges read, so its wording is taken from the cell text), the rest of `spec/05a-entities.md` beyond the ranges 1 to 520, which includes the DDL of S5.14 and the retention rules of S5.15.4; any further mention of `creation_ip_hash` there would not have been seen, and no search tool was available. The Founding Document and `docs/source/prompt.md` were not opened; FD references come from the text of 05a, 10a and 10b.
- Names: 05a column names were not renamed; 10a names are recorded as aliases.

Result: DONE WITH SKIPS
