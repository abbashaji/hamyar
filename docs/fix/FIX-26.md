# FIX-26: ledger: reversal into closed escrow and expired slice (default of D-03)

*Cell C-097. Source: `docs/audit/A01.md` findings 6, 18, 20, 23 and `spec/02e-issues-summary.md` A4, A6, applied as the DEFAULT of D-03 (`docs/audit/FINAL.md` section 4): the Reserve pays nothing beyond grants, `appeal_restitution` stays off, the donor bears the gap. Every applied edit carries the tag D-03 default in the part file. File:line values are the lines after the edits (a few lines later than the audit's numbers; the audit's finding numbers 20 and 23 are in the cell text in the opposite order: finding 20 is the lot clock, finding 23 is the levy on an overturn, both done). Only `spec/06a-ledger.md` and this log were edited. Nothing was run.*

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| F6-1 split the reversal row for `levy`, `refund`, `escrow_hold` (6.6.3 table) | spec/06a-ledger.md:~318 | one row `grant`, `expire`, `levy`, `retire`, `refund`, `escrow_hold`: mirror along the original accounts | `grant`, `expire`, `retire` keep the mirror; `levy`, `refund`, `escrow_hold` mirror only while the escrow is `open` or `settling`; if `closed`: `STATE_CONFLICT`, no entry, no transaction, logged `ledger.reversal_refused` (D-03 default) | applied |
| F6-2 escrows never reopen, levy and restitution defaults (6.6.3 paragraph) | spec/06a-ledger.md:~322 | no statement that a closed escrow is untouched by reversals; levy behavior on overturn implicit | `reversed_in_ucr` frozen at close; levy does not follow an overturn; Reserve pays nothing beyond grants, an overturned rejection after close pays the donor nothing (D-03 default) | applied |
| F6-3 INV-L04 reasoning | spec/06a-ledger.md:619 | closed escrow = 0 | closed escrow = 0 and stays 0 because a reversal into or out of it is refused (D-03 default) | applied |
| F6-4 INV-L07 reasoning | spec/06a-ledger.md:622 | closing identity and `levy_posted <= accepted_primary x quote_lambda` | adds: `reversed_in` frozen at close; an overturn does not lower `accepted_primary` (D-03 default) | applied |
| F6-5 INV-L07 check | spec/06a-ledger.md:685-686 | SQL only | adds a recompute line: no reversal leg on a closed escrow above the seq of its settle or cancel entries | applied |
| F6-6 test AC-ledger-15 | spec/06a-ledger.md:~838 | one approver refused, two approvers reverse, second reversal refused | adds (a) closed-escrow refusal with `STATE_CONFLICT`, no entry, logged; (b) N = 1 hand-computed case (levy 50,000, refund 1,100,000, identity 2,150,000) | applied |
| F6-7 test T-prop-06 | spec/06a-ledger.md:848 | identity, refund >= 0, balance 0 at close | adds: reversal leaves `accepted_primary_cells` and `levy_due` unchanged; reversal after close refused | applied |
| F6-8 convention gap list | spec/06a-ledger.md:~878 | events up to `ledger.checks_stale` | adds `ledger.reversal_refused`, `ledger.payout_slice_expired` (convention gaps for C-001, as the file's own rule) | applied |
| F6-9 reversal of a `transfer` into a closed escrow (restitution to the requester, ISS-62) | spec/06a-ledger.md:~317 | `M -> requester's member account`, a restitution | unchanged | skipped-needs-owner: not one of the authorized edits; 02e A4 (iii) says the register gives the requester no restitution while ISS-62 gives it, and D-03 covers restitution; the default text of this cell names only `levy`, `refund`, `escrow_hold` |
| F18-1 `pick_slices` | spec/06a-ledger.md:149-153 | `pick_slices(escrow_account, amount_ucr)`, no expiry filter | `pick_slices(escrow_account, amount_ucr, now, for_payout)`: a payout skips expired slices and refuses with `STATE_CONFLICT` if the rest cannot cover it (D-03 default) | applied |
| F18-2 slices after expiry (6.4.3 prose) | spec/06a-ledger.md:156 | restored expired lot swept to the Reserve | adds: a payout never draws an expired slice; the levy (earliest expiry first) or the refund plus the next `expire` sends it to the Reserve | applied |
| F18-3 payout guard (6.6.1) | spec/06a-ledger.md:~299 | escrow state, budget, headroom, donor not banned | adds: unexpired slices cover 1,000,000 ucr; otherwise `STATE_CONFLICT`, `ledger.payout_slice_expired`, acceptance rolls back (LD-09), the donor bears the gap | applied |
| F18-4 payout pseudocode call (6.6.2) | spec/06a-ledger.md:~322-330 | `pick_slices(e.account, 1_000_000)` | `pick_slices(e.account, 1_000_000, now, for_payout = true)` | applied |
| F18-5 expiry rule (6.9.1) | spec/06a-ledger.md:407 | expired credit moves to the Reserve | adds that this holds for credit in escrow | applied |
| F18-6 INV-L13 reasoning | spec/06a-ledger.md:628 | no `escrow_hold` or `reserve_donation` movement from an expired lot | adds payout `transfer`; the levy may draw an expired slice | applied |
| F18-7 INV-L13 check | spec/06a-ledger.md:713 | `IN ('escrow_hold','reserve_donation')` | `IN ('escrow_hold','reserve_donation','transfer')` | applied |
| F18-8 test AC-ledger-06 | spec/06a-ledger.md:~832 | refund restores an expired lot, second `expire` | adds the N = 2 example (levy 100,000, refund 200,000, Reserve +300,000) and the variant refused with `STATE_CONFLICT` | applied |
| F18-9 test T-prop-02 | spec/06a-ledger.md:~844 | `pick_lots` properties | adds `pick_slices` with `for_payout` property | applied |
| F20-1 lifetime list (6.4.2) | spec/06a-ledger.md:118 | `mint` and `transfer` lots use `credit.lifetime_days` | `mint` lots only | applied |
| F20-2 transferred lot clock (6.4.2) | spec/06a-ledger.md:118 | a transferred lot starts its own clock at acceptance, [H] weakens expiry | keeps `earned_at`, `expires_at`, lifetime parameter and version of its source lot, one donor lot per slice (D-03 default); [H] reworded | applied |
| F20-3 decision LD-07 | spec/06a-ledger.md:34 | every earning event creates its own lot | mint and grant create a lot; a transfer lot keeps the source expiry | applied |
| F20-4 payout row (6.6 table) | spec/06a-ledger.md:~262 | drains escrow slices, creates donor lot | drains unexpired slices, one donor lot per slice with the source expiry | applied |
| F20-5 lineage (6.4.3) | spec/06a-ledger.md:160 | the lot created for the donor | the lot or lots, one per slice with that slice's expiry | applied |
| F20-6 payout pseudocode lot (6.6.2) | spec/06a-ledger.md:~331 | `new_lot(donor, 1_000_000, now, now + lifetime_days(donor) * 86400, 'transfer')` | `new_lot_from_slice(...)` with the source `earned_at` and `expires_at` | applied |
| F20-7 worked example 6.15 donors row | spec/06a-ledger.md:791 | balances only | adds donor lot expiry: cells 1 to 10 day 60, cells 261 to 264 day 86 | applied |
| F20-8 test T-unit-01 step 4 | spec/06a-ledger.md:~810 | counts and counters | adds the expiry assertion (cell 1 day 60, cell 264 day 86) | applied |
| F20-9 test AC-ledger-05 | spec/06a-ledger.md:~829 | spending order | adds: donor lot from a day-0 lot expires on day 60 | applied |
| F23-1 levy on overturn, 6.7.3 properties | spec/06a-ledger.md:360 | levy charged on accepted primary cells | adds: an overturn does not lower `accepted_primary_cells`, the levy does not follow it (D-03 default) | applied |

## Read-back

After all edits the edited places were read again in `spec/06a-ledger.md` (884 lines, 4 more than before; nothing deleted). What is now there:

- 6.6.3 table: two rows; the first (`grant`, `expire`, `retire`) is a plain mirror; the second says "nothing is posted" for a closed escrow and names `ledger.reversal_refused`. The `transfer`, escrow `closed` row still reads as a restitution to the requester (F6-9, skipped). The paragraph below the table now says escrows never reopen, the levy does not follow an overturn, and an overturned rejection after close pays the donor nothing.
- INV-L04 and INV-L07 rows carry the D-03 default text; the INV-L07 query block ends with the recompute line about reversal legs on closed escrows.
- 6.4.3: `pick_slices(escrow_account, amount_ucr, now, for_payout)` with three comment lines; the disbursement paragraph says an expired slice pays no donor. 6.6.1 payout guard and 6.6.2 pseudocode use `for_payout = true`. INV-L13 text and its second query include `transfer`.
- 6.4.2: `mint` lots alone use the lifetime parameter; a `transfer` lot keeps the source lot's dates. LD-07, the payout row of 6.6, the lineage sentence and the `new_lot_from_slice` line agree.
- Tests: AC-ledger-05, -06, -15, T-prop-02, T-prop-06 and T-unit-01 step 4 carry the new assertions; no test id was added or renamed.

Arithmetic recomputed by hand:

- 6.15 (FD 3.3) is unchanged in amounts. Slices are 270 lots of d0..d26 plus 6 of d27 = 276 of 1,000,000 ucr. Payout k takes slice k, so cells 1..264 use d0..d25 (260 slices, 10 per day) and 4 of d26: cell 1 expires day 0 + 60 = 60, cell 264 expires day 26 + 60 = 86. The levy then takes the 12 remaining slices (6 of d26, 6 of d27) = 12,000,000, refund 0. Closing identity 240 + 24 + 0 + 12 + 0 = 276 holds; 566 entries, donor balances 24 x 7 + 16 x 6 = 264 unchanged. No slice expires during the job (earliest expiry day 60, job on day 30), so the expired-slice rule does not change this example.
- AC-ledger-15(b): N = 1, escrow 1,150,000 = 1,000,000 + 100,000 + 50,000. Payout reversed: reversed_in 1,000,000; balance = 1,150,000 + 1,000,000 - 1,000,000 = 1,150,000; levy_due = 1 x 50,000; refund = 1,150,000 - 50,000 = 1,100,000; identity 1,150,000 + 1,000,000 = 1,000,000 + 50,000 + 1,100,000 = 2,150,000. Holds.
- AC-ledger-06 example: N = 2, escrow 2,300,000 = 2,000,000 + 200,000 + 100,000; S1 300,000 + S2 1,000,000 + S3 1,000,000 = 2,300,000. Payouts 2 x 1,000,000 from S2 and S3; balance 300,000; levy 2 x 50,000 = 100,000 from S1; refund 300,000 - 100,000 = 200,000; Reserve gains 100,000 + 200,000 = 300,000; identity 2,300,000 = 2,000,000 + 100,000 + 200,000. Variant S1 600,000 + S2 1,000,000 + S3 700,000 = 2,300,000: after the first payout 700,000 unexpired is below 1,000,000, so the second is refused.

Points the owner should see (not decided here):

- The expired-slice default has a side effect: a payout that the unexpired slices cannot cover is refused and the cell's acceptance rolls back (LD-09), so a donor can go unpaid for an accepted-looking cell. The cell text says the donor bears the gap; no other part (05b) defines what happens to such a cell. Needs D-03 and 05b.
- 6.6.3 `transfer` reversal after close still pays the requester (F6-9). 02e A4 says the register gives no restitution; this stays open.
- The Founding Document was not re-read in this cell; the claim that FD 4.5 expires credit E days after minting is taken from A01 finding 20.
- The two new events are convention gaps for C-001; no new ISS id was minted.

Result: DONE WITH SKIPS
