# FIX-25: verification cost, v_commons and v_member, and the shortfall path

Cell C-096. Sources: docs/audit/A08.md findings 13 and 14; spec/02e-issues-summary.md A2 and A3. Decision: D-04 of docs/audit/FINAL.md section 4, applied as its default (ISS-16: hard pool, the job stops when verification cannot be paid, no levy draw; quote at max(measured v, `price.v_prior`, floor)). Every edit is default-pending D-04. Line numbers are those after the edits.

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| 1. 8.31 Commons row: both published separately, say so | spec/08b-verification.md:497 | Commons cells not in member-job v; published as `commons_verification_share` | not in `v_member`, in `v_commons`; quoted v follows 06a 6.11.2 (both counted together, both published separately); default-pending D-04 | applied |
| 2. 8.31 strata: quote basis | spec/08b-verification.md:499 | below the minimum sample the quote falls back to `price.v_prior` | quoted v is max(measured v, `price.v_prior`, floor); default-pending D-04 | applied |
| 3. 8.31 floor funding check | spec/08b-verification.md:507 | must not exceed `price.v_prior + price.levy_lambda`, 0.0321 within 0.15 | must not exceed `price.v_prior`, 0.0321 within 0.10, the levy is not a source; default-pending D-04 | applied |
| 4. 8.32 verification budget: mandatory events and shortfall | spec/08b-verification.md:529 | mandatory events never skipped, overrun absorbed by pool then levy share, S6 behavior open | scheduler may not create a cell the pool cannot pay; shortfall stops the job (JT-15 then JT-17), event `ledger.verification_budget_exhausted`, never paid by levy, Reserve or mint; default-pending D-04 | applied |
| 5. LD-05 | spec/06a-ledger.md:27 | paid from pool, then levy budget; scheduler may not create a cell the budgets cannot pay | pool only; scheduler may not create a cell the pool cannot pay; the job stops; default-pending D-04 | applied |
| 6. 6.11.2 quote basis (Rounding row) | spec/06a-ledger.md:505 | pool never smaller than measured cost | adds quoted v = max(measured v, `price.v_prior`, floors of ISS-16); default-pending D-04 | applied |
| 7. 6.11.2 which jobs count | spec/06a-ledger.md:500 | Commons and member cells together, `v_commons` and `v_member` published separately | unchanged, this is the version kept by the register note; 8.31 now agrees | already-applied |
| 8. 6.11.2 cap row, excess absorbed by the levy | spec/06a-ledger.md:503 | cap applies, excess cost absorbed by the levy through 6.7.2 | not changed: with a hard pool the levy cannot absorb it, but section 4 gives no default for the v cap (price.v_cap) against a hard pool; searched 6.11.2 and 6.7.2 | skipped-needs-owner |
| 9. 6.6.2 post_payout verification branch | spec/06a-ledger.md:297 | pool first, then levy budget (from_pool, from_levy, paid_levy_budget) | pool only, assert pool covers the payout, no levy draw; default-pending D-04 | applied |
| 10. 6.7.2 payment source, free(J), shortfall | spec/06a-ledger.md:334 | pool then levy budget; free(J) adds levy budget; optional verification stops, mandatory third execution requeues the cell | pool only; free(J) = pool budget minus paid pool; no cell is created and the job stop is requested; default-pending D-04 | applied |
| 11. 6.14.1 small job row | spec/06a-ledger.md:757 | next cell takes the pool and the rest from the levy budget | no cell from a pool below one cell, levy does not pay, job stops if one is required; default-pending D-04 | applied |
| 12. 6.15 fixture free(J) | spec/06a-ledger.md:786 | free(J) = 24,000,000 + 12,000,000 | free(J) = 24,000,000, pool only; default-pending D-04 | applied |
| 13. T-unit-01 | spec/06a-ledger.md:807 | Step 4 asserts `paid_levy_budget_ucr` = 0 and `paid_pool_ucr` = 24,000,000 | no text change needed: the test already asserts no levy draw, and its fixture (edit 12) now agrees | already-applied |
| 14. AC-ledger-03 | spec/06a-ledger.md:820 | case (b) one cell takes 700,000 from the pool and 300,000 from the levy budget | case (b) no cell is created, event logged, job stops, nothing from the levy budget; default-pending D-04 | applied |
| 15. state and event for the stop in spec/05b | spec/05b-state-machines.md:~102 | JT-15 closure_reason list has no value for a verification shortfall | not edited: file is outside allowed_paths; 06a and 08b point to JT-15 and JT-17 and say that 05b owns the closure_reason value; searched JT-01 to JT-20 and 5.22.1 | skipped-needs-owner |
| 16. 02e A2 and A3 status lines | spec/02e-issues-summary.md:~85 | rows say S6a text, AC-ledger-03, T-unit-01 and 8.32 must change | not edited: file is outside allowed_paths; left for the register owner | skipped-needs-owner |

## Read-back

Each edited place was read again after the edits.

- 08b:497 reads that Commons cells are in `v_commons` and not in `v_member`, with 06a 6.11.2 counting both together.
- 08b:499 reads that the quoted v is a maximum of three terms, with the prior as one of them.
- 08b:507 reads the floor funding check against `price.v_prior` alone, ending at 0.10.
- 08b:529 reads that the scheduler may not create a cell the pool cannot pay and that the job stops, with the phrase "never paid by a levy draw" in substance.
- 06a:27 (LD-05) reads "verification pool only" and ends with the shortfall path pointer.
- 06a:297 to 301 read pool only, one assert on the pool, two comment lines on the absent levy draw, and one add to `paid_pool_ucr`.
- 06a:334 to 341 read pool only, `free(J)` equal to the pool remainder, no cell created, stop requested through JT-15 and JT-17; the closure_reason note is present.
- 06a:505 reads the quoted v as a maximum including the floors of ISS-16.
- 06a:757 reads that a pool below one cell cannot create a verification cell and the levy does not pay.
- 06a:786 reads "the pool only" in the free(J) cell of the fixture row.
- 06a:807 (T-unit-01 Step 4) still reads `paid_levy_budget_ucr` = 0, which agrees.
- 06a:820 (AC-ledger-03) reads case (b) as no cell created and the job stopped, with case (a) unchanged.
- 06a:500 and 503 were read and not changed; 503 still mentions the levy absorbing the cap excess (edit 8).

Open points for the owner: the v cap against a hard pool (edit 8); the closure_reason value in 05b JT-15 (edit 15); the 02e register rows (edit 16). Remaining text of 6.7.3 still reads the levy budget in settlement; it is unchanged because `paid_levy_budget_ucr` stays 0 and the formulas remain correct.

Result: DONE WITH SKIPS
