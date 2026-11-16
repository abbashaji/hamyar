# FIX-01: safety floors of parameter ranges

*Cell C-072. Applies FIX-01 of `docs/audit/FINAL.md` section 5.1 to `spec/00-conventions.md` (S0 Table A, B, C) and `spec/16-parameters.md` (S16 16.6, 16.11, 16.13). Sources: `spec/16d-parameter-consistency.md` (F-01, F-06, F-07, F-14, 16.D.8.1, CR-04, CR-06, CR-21) and `docs/audit/A03.md` finding 27. Nothing was executed; CI runs the acceptance checks. No id, parameter, endpoint or state was renamed and nothing was deleted. File:line values are the lines at which the text was found (the cited lines had not drifted).*

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E1 `price.eta_alarm_threshold` range, S0 | spec/00-conventions.md:596 | `0..1` | `(0,1]` | applied |
| E2 `change.notice_days_default` range, S0 | spec/00-conventions.md:640 | `0..90` | `1..90` | applied |
| E3 `change.notice_days_price` range, S0 | spec/00-conventions.md:641 | `0..90` | `1..90` | applied |
| E4 `retention.ip_hash_ttl_days` range, S0 | spec/00-conventions.md:717 | `0..30` | `1..30` (default applied, D-22 open) | applied |
| E5 `launch.min_signoffs` range, S0 | spec/00-conventions.md:762 | `1..5` | `2..5` (default applied, D-01 open) | applied |
| E6 `launch.min_approved_services` range, S0 | spec/00-conventions.md:763 | `0..20` | `1..20` | applied |
| E7 `price.eta_alarm_threshold` range and reason, S16 16.6 | spec/16-parameters.md:161 | `0..1` | `(0,1]` and the clause: fail-closed floor, 0 would make the alarm unreachable (FD Principle 5/8, 16d F-01) | applied |
| E8 `retention.ip_hash_ttl_days` range and reason, S16 16.11 | spec/16-parameters.md:313 | `0..30` | `1..30` and the clause: 0 would switch off the per-IP-hash join limit (FD Principle 5/8, 16d F-06) (default applied, D-22 open) | applied |
| E9 `launch.min_signoffs` range and reason, S16 16.13 | spec/16-parameters.md:389 | `1..5; C19` | `2..5; C19` and the clause: one sign-off is no two-person gate (FD Principle 5/8, 16d F-14, A03 finding 27) (default applied, D-01 open) | applied |
| E10 `launch.min_approved_services` range and reason, S16 16.13 | spec/16-parameters.md:390 | `0..20` | `1..20` and the clause: 0 would pass the G0 count with no approved service (FD Principle 5/8, 16d 16.D.8.1, A03 finding 27) | applied |
| E11 `change.notice_days_default` range and reason, S16 16.13 | spec/16-parameters.md:391 | `0..90; C20` | `1..90; C20` and the clause: 0 would remove the advance notice of a loosening (FD Principle 5/8, 16d F-07) | applied |
| E12 `change.notice_days_price` range and reason, S16 16.13 | spec/16-parameters.md:392 | `0..90` | `1..90` and the clause: 0 would remove the advance notice of a loosening (FD Principle 5/8, 16d F-07) | applied |

## Notes for the owner

- **D-01 made explicit.** A floor of 2 on `launch.min_signoffs` means that with one admin no launch gate can be signed, no switch can be opened and no kill switch released. This is intended and is not softened here. The team needs at least two independent admins before Phase 1, or the owner decides otherwise in D-01 (FINAL.md section 4). The default meanwhile is the one this edit applies.
- **D-22.** The range `1..30` on `retention.ip_hash_ttl_days` follows 16d CR-04 and the cell's authorization. Whether a value of 0 should ever be allowed is still an owner decision; this edit applies the D-22 default and marks it in the table.
- **Reasons in S16 only.** The reason clauses were added to the S16 rows and not to S0, as the cell asks. The notation `(0,1]` replaces 16d CR-21's `> 0 .. 1; S16D-C1`; the constraint id `S16D-C1` was not cited because S16 16.3 does not carry it until 16d CR-18 is applied (FIX-02).
- **Not touched (outside this cell).** The S0 row text of `change.notice_days_price` still lists `price.*`, `admission.*`, `credit.*` without `reservation.*` (16d CR-07, S0 side, assigned to FIX-03).

## Read-back

Every edited place was re-read after the edit.

| place | what is now there |
| --- | --- |
| spec/00-conventions.md:596 | row `price.eta_alarm_threshold`: validation column reads `(0,1]` |
| spec/00-conventions.md:640 | row `change.notice_days_default`: validation `1..90` |
| spec/00-conventions.md:641 | row `change.notice_days_price`: validation `1..90`, default text unchanged |
| spec/00-conventions.md:717 | row `retention.ip_hash_ttl_days`: default 1, validation `1..30` |
| spec/00-conventions.md:762 | row `launch.min_signoffs`: default text unchanged, validation `2..5` |
| spec/00-conventions.md:763 | row `launch.min_approved_services`: default 1, validation `1..20` |
| spec/16-parameters.md:161 | validation `(0,1]` followed by the floor clause citing 16d F-01; default 0.80 unchanged |
| spec/16-parameters.md:313 | validation `1..30` followed by the floor clause citing 16d F-06; default 1 unchanged |
| spec/16-parameters.md:389 | validation `2..5` with `C19` kept, then the clause citing 16d F-14 and A03 finding 27; default text unchanged |
| spec/16-parameters.md:390 | validation `1..20` then the clause citing 16d 16.D.8.1 and A03 finding 27; default 1 unchanged |
| spec/16-parameters.md:391 | validation `1..90` with `C20` kept, then the clause citing 16d F-07; default 7 unchanged |
| spec/16-parameters.md:392 | validation `1..90` then the clause citing 16d F-07; default text still names `reservation.*` |

No old range (`1..5` for sign-offs, `0..20` for services, `0..30` for the IP-hash TTL) remains on these rows in either file. Every default still lies inside its new range (2 in 2..5, 1 in 1..20, 7 and 14 in 1..90, 1 in 1..30, 0.80 in (0,1]).

Result: DONE
