# FIX-04: parameter rows missing from S0 and S16

Cell C-075. Files edited: `spec/16b-parameters-a.md`, `spec/16c-parameters-b.md`. Sources: `docs/audit/A12.md` finding 29, `docs/audit/A03.md` finding 29, `docs/audit/A11.md` finding 16, `spec/16d-parameter-consistency.md` CR-13, CR-14, CR-22, CR-25, and the parameter lists of S10a (10.18.3), S10b (10.18), S12 (12.13.3), S13 (13.13), S14 (14.13, `ISS-147`), S15a (convention list, 15.12, 15.13) and S15b (15.21.2, `ISS-154`). Owner decisions D-01..D-22 are in `docs/audit/FINAL.md` section 4; where a default applies the row says `default-pending`. Nothing was run: `check_params.py`, `check_spec.py` and `check_fixlog.py` run in CI.

## Edits

Line numbers are those of the branch after the edits. A new row is one edit; no name, id, endpoint or state was renamed and no content was deleted (the only text changes to existing rows are appends and the two range corrections CR-14).

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E01 rule RB-7 (records the additions) | spec/16b-parameters-a.md:17 | no rule row for the additions | row RB-7 added; the counts of 16.B.1 are stated as unchanged | applied |
| E02 alias `invite.required_to_join` (A12 f29, 15a:882) | spec/16b-parameters-a.md:113 | name defined nowhere | alias of `identity.registration_mode` (`true` = `invite_only`), not seeded | applied |
| E03 alias `security.approval_ttl_s` (A12 f29, 15b ISS-154) | spec/16b-parameters-a.md:114 | name defined nowhere | alias of `security.two_person_ttl_s`, 86,400 s (default-pending D-22) | applied |
| E04 alias `security.secret_rotation_max_age_days` (A03 f29, 14.13) | spec/16b-parameters-a.md:115 | name defined nowhere | alias of `security.secret_rotation_days`, 90 days | applied |
| E05 `abuse.admin_lookup_rate` not seeded (CR-13) | spec/16b-parameters-a.md:86 | default cell: no value invented | appended: not seeded and refused as unknown until type, unit and default are supplied (default-pending D-22) | applied |
| E06 `identity.registration_mode` (CR-13) | spec/16b-parameters-a.md:178 | absent | enum `invite_only`/`open`, default `invite_only`, `T→invite_only` | applied |
| E07 `identity.code_max_attempts` (CR-13) | spec/16b-parameters-a.md:179 | absent | int 1..20, default 5, `T↓` | applied |
| E08 `invite.strikes_to_revoke_issuing` (CR-13) | spec/16b-parameters-a.md:180 | absent | int 1..20, default 2, `T↓` | applied |
| E09 `invite.tree_freeze_ban_threshold` (CR-13) | spec/16b-parameters-a.md:181 | absent | int 1..100, default 3, `T↓` | applied |
| E10 `ratelimit.write_weight` (A12 f29) | spec/16b-parameters-a.md:189 | absent | int 1..100 [A], default 4, `T↑`, `S16B-C11` | applied |
| E11 `ratelimit.member_uploads_per_hour` (A12 f29) | spec/16b-parameters-a.md:190 | absent | int 1..1000 [A], default 10, `T↓` | applied |
| E12 `ratelimit.admin_write_cost` (A12 f29) | spec/16b-parameters-a.md:191 | absent | int 1..100 [A], default 2, `T↑`, `S16B-C11` | applied |
| E13 `ratelimit.admin_auth_attempts_per_hour` (A12 f29) | spec/16b-parameters-a.md:192 | absent | int 1..1000 [A], default 10, `T↓` | applied |
| E14 `ratelimit.public_verify_cost` (A12 f29) | spec/16b-parameters-a.md:193 | absent | int 1..100 [A], default 5, `T↑`, `S16B-C11` | applied |
| E15 `ratelimit.device_link_offers_per_day` (10a:747) | spec/16b-parameters-a.md:194 | absent | int 1..100, default 5, `T↓` | applied |
| E16 `ratelimit.auth_failures_per_hour` (10a:748) | spec/16b-parameters-a.md:195 | absent | int 1..1000, default 20 per IP hash, `T↓` | applied |
| E17 `api.deprecation_window_days` (A12 f29) | spec/16b-parameters-a.md:196 | absent | days 30..3650 [A], default 180, `T↑` | applied |
| E18 `security.two_person_ttl_s` (CR-13, 10a:755) | spec/16b-parameters-a.md:206 | absent | duration_s 600..604,800, default 86,400, `T↓`, `S16B-C12` (default-pending D-22) | applied |
| E19 `security.admin_min_credentials` (10a:756) | spec/16b-parameters-a.md:207 | absent | int 1..5, default 2, `T↑` [A] | applied |
| E20 `security.emergency_access_ttl_s` (10b:639) | spec/16b-parameters-a.md:208 | absent | duration_s 60..86400, default 3,600, `T↓` | applied |
| E21 `security.reachability_check_interval_days` (10b:640) | spec/16b-parameters-a.md:209 | absent | days 1..365, default 30, `T↓` | applied |
| E22 `launch.require_locked_preregistration` (A12 f29, 15b ISS-154) | spec/16b-parameters-a.md:210 | absent | bool, default true, recorded as a constant `C` because S14 14.7.1 and FD§9 require the lock (default-pending D-17) | applied |
| E23 `growth.share_card_max_active` (A12 f29) | spec/16b-parameters-a.md:220 | absent | int 0..100 [A], default 3, `T↓`; unused if the stored cards are deleted (default-pending D-15) | applied |
| E24 `growth.badge.thresholds` (A11 f16, 12:666) | spec/16b-parameters-a.md:221 | absent | json of three ascending lists, default as S12, owner founders, `N` | applied |
| E25 `public.change_log_service_labels` (A11 f16, 12:668) | spec/16b-parameters-a.md:222 | absent | bool, default false, `T→false` [A] | applied |
| E26 `report.external_contact` (10b:646) | spec/16b-parameters-a.md:223 | absent | string, default empty, non-empty before launch, `N`, calibration `CON` as S10b states [V] | applied |
| E27 `report.reporter_identity_hidden` (10b:647) | spec/16b-parameters-a.md:224 | absent | bool constant, default true, `C` | applied |
| E28 `template.autopause_min_distinct_reporters` (10b:648) | spec/16b-parameters-a.md:225 | absent | int 1..1000, default 3, `T↓`, `S16B-C10` | applied |
| E29 `template.autopause_min_reporter_tier` (10b:649) | spec/16b-parameters-a.md:226 | absent | enum `new`/`established`/`trusted`, default `established`, `T→new` [A] | applied |
| E30 constraints `S16B-C10`, `S16B-C11`, `S16B-C12` | spec/16b-parameters-a.md:236 | absent | three constraints with a worked check at the defaults (all pass) | applied |
| E31 `metrics.concentration_top_fraction` (A11 f16, 13:1007) | spec/16c-parameters-b.md:156 | absent | ratio 0 < x <= 0.5, default 0.10, founders, `N` | applied |
| E32 `analytics.client_events_enabled` (13:1008) | spec/16c-parameters-b.md:157 | absent | bool, default true, `T→false` [A] | applied |
| E33 `calibration.lease_timeout_multiplier` (13:1009) | spec/16c-parameters-b.md:158 | absent | int 1..100, default 10, `N` | applied |
| E34 `calibration.timing_min_percentile` (13:1010) | spec/16c-parameters-b.md:159 | absent | int 1..25, default 1, founders, `N` | applied |
| E35 `calibration.envelope_min_success` (13:1011) | spec/16c-parameters-b.md:160 | absent | ratio 0.5..1, default 0.95, founders, `N` | applied |
| E36 `admission.allowed_job_types` (A03 f29, 14:500) | spec/16c-parameters-b.md:161 | absent | json list of `job_type` values, default all values (no restriction) [A], `T↓` | applied |
| E37 CR-14 `ui.requester.appeal_note_max_chars` range | spec/16c-parameters-b.md:51 | validation `0..5,000` | `100 .. appeal.reason_max_chars` | applied |
| E38 CR-14 `ui.lease.warn_remaining_s` range | spec/16c-parameters-b.md:37 | `0 to lease.timeout_s`, 0 switches the warning off | `1 to lease.timeout_s`, 0 refused | applied |
| E39 CR-22 `ui.draft.ttl_s` baseline | spec/16c-parameters-b.md:36 | validation ends at `S16C-C4` | sentence appended: the draft lives from its last write; 3,600 s satisfies `S16C-C4` on either reading | applied |
| E40 CR-25 `admission.redeemable_capacity_cells_per_day` | spec/16c-parameters-b.md:102 | two entries under 16.C.8 | third entry added (a `MetricSnapshot` key, not a parameter), intro sentence added at line 96 | applied |
| E41 already defined: `identity.challenge_ttl_s`, `session.max_active_per_member`, `session.admin_stepup_ttl_s` (A12 f29) | spec/16b-parameters-a.md:39, 55, 56 | n/a | rows present with the values and units of S15 | already-applied |
| E42 already defined: `launch.approval_window_s`, `launch.generic_validity_days`, `launch.counsel_validity_days`, `launch.measurement_validity_days`, `launch.evidence_max_bytes` (A03 f29) | spec/16b-parameters-a.md:96-100 | n/a | rows present | already-applied |
| E43 already defined: five `growth.referral.*` rows and `team.label_max_chars` (A11 f16, 12.13.3) | spec/16b-parameters-a.md:66-71 | n/a | rows present | already-applied |
| E44 already defined: `metrics.daily_rollup_offset_s`, `metrics.large_job_min_cells` (A11 f16, 13.13) | spec/16c-parameters-b.md:71-72 | n/a | rows present | already-applied |
| E45 sweep of all seven spec files for further undefined names | spec/14, 15a, 15b, 12, 13, 10a, 10b | no search over the repository exists in this cell and reads were limited to the cited passages | not enumerated; only the ten passages named in the Notes were read | skipped-not-found (searched: 10a 735-770, 10b 628-655, 12 650-690, 13 985-1020, 14 440-545 and 585-674, 15a 670-730 and 880-887, 15b 20-112 and 1085-1142) |

## Read-back

After the last commit the edited places were read again.

- 16b rule rows (lines 11-17): RB-7 is present after RB-6 and says the counts of 16.B.1 stay as written.
- 16b alias table (lines 108-115): three new rows follow the `session.admin_stepup_s` row; each says "no" under seeded and names its canonical row; `invite.required_to_join` maps `true` to `invite_only`.
- 16b line 86: `abuse.admin_lookup_rate` still has no value and now ends with "default-pending D-22".
- 16b 16.B.11.1 to 16.B.11.4 (lines 178-226): 24 rows with ten columns each; every default carries its source part in brackets; rows with a chosen range or direction carry [A]. `launch.require_locked_preregistration` reads as a constant (`C`, default true).
- 16b 16.B.11.5 (lines 236-238): `S16B-C10`, `S16B-C11`, `S16B-C12` and the worked check "All pass"; `S16B-C12` passes with zero margin (86,400 <= 86,400).
- 16c lines 36-38: `ui.draft.ttl_s` carries the appended CR-22 sentence; `ui.lease.warn_remaining_s` reads "1 to `lease.timeout_s`" and "0 is refused". Residual: the unit cell of `ui.draft.ttl_s` still reads "counted from the lease end", which CR-22 asked only to append to; the appended sentence states the other baseline. Left for the owner (D-19 area), not changed here.
- 16c line 51: `ui.requester.appeal_note_max_chars` reads "100 .. `appeal.reason_max_chars`"; its default 1,000 lies inside the range.
- 16c lines 96-102: 16.C.8 has three entries; the intro names the third as added by CR-25. `AC-paramc-08` (line 138) still names only the first two entries; not changed.
- 16c lines 156-161: six new rows; the note below them says no new constraint was added.
- Not read back because not edited: `spec/16-parameters.md`, `spec/00-conventions.md` (outside `allowed_paths`). Names the 16d CRs ask to correct there (CR-01 to CR-12, CR-15 to CR-21, CR-23, CR-24) belong to FIX-02 and FIX-03.

## Notes

- Coverage: the new rows come from the audit lists and from the parameter lists and tables of the passages named in E45. A name used elsewhere in the seven files that is in none of those passages is not covered; `AC-param-01` and the CI check will show it.
- Decisions applied as defaults: D-15 (share card cap), D-17 (lock constant), D-22 (approval lifetime name, `abuse.admin_lookup_rate` without a value). None was decided by this cell.
- Chosen values are labeled [A] in the rows: ranges of the rate-limit weights and costs, of `api.deprecation_window_days` and of `growth.share_card_max_active`; directions of `security.admin_min_credentials`, `public.change_log_service_labels`, `analytics.client_events_enabled` and `template.autopause_min_reporter_tier`; the default "all job types" of `admission.allowed_job_types`.
- Constraint ids `S16B-C10` to `S16B-C12` are new; no `ISS-` id was added, so the register of `spec/02*` is unchanged.

Result: DONE WITH SKIPS
