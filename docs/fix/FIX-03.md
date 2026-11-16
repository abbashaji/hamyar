# FIX-03: parameter corrections in S0 tables

*Cell C-074. Source: `spec/16d-parameter-consistency.md` `## Corrections required` (CR-02, CR-06, CR-07, CR-08, CR-09, CR-11, S0 side) and `docs/audit/FINAL.md` sections 4 and 5.1. File edited: `spec/00-conventions.md` only. Line numbers are those found at the time of editing (the audit lines had drifted by a few lines). Nothing was executed; CI runs the acceptance scripts.*

Scope notes. FIX-01 already set the safety ranges, so the `1..90` range of the two `change.notice_days_*` rows was not touched; only the relation text that CR-06 adds for the price row was appended. D-07 and D-13 have no owner decision yet, so CR-02 and CR-08 are not applied. The 0.10.3 `notice_days` field text still names only `price`, `admission` and `credit`; CR-07 names the Table A row only, so that sentence was left as it is (logged here for the owner of the assembly).

## Edits

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| CR-06 `change.notice_days_default` range | spec/00-conventions.md:640 | `1..90` | `1..90` (unchanged) | already-applied (FIX-01) |
| CR-06 `change.notice_days_price` relation | spec/00-conventions.md:641 | `1..90` | `1..90; >= change.notice_days_default; S16D-C9` | applied |
| CR-07 `change.notice_days_price` scope text | spec/00-conventions.md:641 | `(for price.*, admission.*, credit.*)` | `(for price.*, credit.*, admission.*, reservation.*)` | applied |
| CR-09 `inflation.mint_cap_cut_ratio` default text | spec/00-conventions.md:630 | `0.25 (cut applied when the threshold is passed)` | same, with `; the cap after the cut = floor(cap x (1 - ratio))` appended inside the brackets | applied |
| CR-11a `tighten_direction` enum | spec/00-conventions.md:538 | `up`, `down`, `none` | `up`, `down`, `toward:<value>`, `none` | applied |
| CR-11b `public` default text | spec/00-conventions.md:542 | `(default true except security.*)` | `(default true except security.* and the rows listed in S16 16.17.5)`; `security.*` kept because S16 16.17.5 was not read and the 16d wording says it hides "more" rows | applied (wording keeps the old exception; see Read-back) |
| CR-11c 0.10.5 operator exceptions and the area `abuse` | spec/00-conventions.md 0.10.5 (about lines 548-560) | area table without `abuse` and without the S16 16.12 exceptions | unchanged | skipped-needs-owner: the 12 exception rows are in `spec/16-parameters.md` 16.12, which this cell does not read, and no defining part for `abuse` is stated in the 16d text or FINAL.md section 4 (16d 16.D.6 says 0.10.5 is regenerated at assembly; ISS-16014, ISS-16015) |
| CR-08 `team.min_public_members` 5 to 10 | spec/00-conventions.md:776 | `5` | unchanged (5) | skipped-needs-owner: D-13 default is team 5 with a warning (`S16D-C21`), not team 10; the owner decides between 10 and an exemption for team totals |
| CR-02 `mint.monthly_cap_credits` formula (S0 Table A row; `C13` is not in S0) | spec/00-conventions.md:625 | `x (1 - 0.5)` | unchanged | skipped-needs-owner: D-07 (min(phi, 1 - phi) or the redeemable share alone); default 4,800 stands meanwhile |

## Read-back

All rows were re-read after the edits (branch base c5da329).

- Line 538: the `tighten_direction` row now shows the four values up, down, toward:<value>, none, with the original two examples intact.
- Line 542: the `public` row now says the default is true except `security.*` and the rows listed in S16 16.17.5. The `security.*` exception is still there, so nothing was deleted; if S16 16.17.5 already lists `security.*` the owner may shorten it at assembly.
- Line 630: the `inflation.mint_cap_cut_ratio` row shows the cut text and, after it, the new cap formula with `(1 - ratio)`; range `0 < x <= 1` unchanged.
- Line 640: `change.notice_days_default` still reads 7 with range `1..90` (FIX-01 result, not touched).
- Line 641: `change.notice_days_price` now lists four areas, price, credit, admission and reservation, and its validation reads `1..90` followed by the relation to the default and `S16D-C9`.
- Line 776: `team.min_public_members` still reads default 5, range `1..1000`; not edited.
- Line 625 (`mint.monthly_cap_credits`) was not edited and still carries the `(1 - 0.5)` derivation.

Result: DONE WITH SKIPS
