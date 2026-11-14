# 2.E Register summary and owner decisions

*Spec part 2.E · owner cell C-033 · reads `spec/02-issues.md`, `spec/02b-issues-parts-a.md`, `spec/02c-issues-parts-b.md`, `spec/02d-issues-parts-c.md` and `spec/03-assumptions.md` · no other file was edited · ids are kept exactly and none is minted here · nothing here is legal advice, and nothing here has been verified against any provider's terms or any law.*

## 2.E.1 Counts by severity and status

How counted. [D] One row is one row of a register table. The counts were redone from the rows, not copied from the files' own count lines; all four of those lines agree with the recount. The ids `ISS-117`, `ISS-118` and `ISS-119` are each used twice (`11c` and `11d` in `02d`), so unique ids are rows minus 3. Four ids cited only in `spec/14-launch-gates.md` (`ISS-141`, `ISS-143`, `ISS-144`, `ISS-147`) have no row and no severity; they are outside every count below.

| File | Rows | blocking | major | minor | proposed | applied | needs_owner | unstated |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `02-issues.md` (part 0, S1, S2, S3) | 35 | 2 | 22 | 11 | 25 | 8 | 2 | 0 |
| `02b` (S4 to S7) | 30 | 0 | 15 | 15 | 18 | 1 | 11 | 0 |
| `02c` (S8 to S11a) | 23 | 0 | 14 | 9 | 15 | 2 | 6 | 0 |
| `02d` (S11b to S19) | 68 | 0 | 32 | 36 | 41 | 11 | 13 | 3 |
| **Rows** | **156** | **2** | **83** | **71** | **99** | **22** | **32** | **3** |
| **Unique ids** | **153** | **2** | **81** | **70** | **97** | **22** | **31** | **3** |

| Severity (rows) | proposed | applied | needs_owner | unstated | Total |
| --- | --- | --- | --- | --- | --- |
| `blocking` | 2 | 0 | 0 | 0 | 2 |
| `major` | 49 | 5 | 28 | 1 | 83 |
| `minor` | 48 | 17 | 4 | 2 | 71 |
| **Total** | **99** | **22** | **32** | **3** | **156** |

Reading the counts. [D]

- Both `blocking` issues (`ISS-11`, `ISS-12`) are `proposed`, not `needs_owner`: the build goes on under the spec's resolution, but `ISS-12` turns on `OD-08` and `ISS-11` on `OD-04` (S3.2).
- No row is `accepted` or `rejected`: the owner has reviewed none (2.1 of the register).
- `unstated` is not a status of S0.4. It is `ISS-151`, `ISS-152` and `ISS-153` (`15a`), each of which names a decider instead of a status. Each has a resolution applied in its part, so this summary reads them as `proposed` [A] wherever a status is needed.
- The four cited-only ids of 2.D.5 have no status. `ISS-141` is called an owner decision in the line that cites it.
- `02b` maps S7's `Needs owner: yes` to `needs_owner` [A] (2.B.1).
- `spec/02-issues.md` lists 35 of the 153 ids. 2.9 says assembly lists the rest, so the four files above are the register until then. Rule 4 of 2.9 asks that every `needs_owner` issue is also in S3.2; 2.E.3 checks that rule: S3.2 names 2 of the 31 by id.

## 2.E.2 Issues that contradict each other or resolve the same FD point differently

Rule used. [D] Per `spec/02-issues.md` 2.9 rule 3, a part applies its own resolution until the central register records a different one, and where the two differ the register wins. Where the register is silent, the table says so and gives the resolution the spec applies with the reason. Nothing is renamed or renumbered here (cell rule). Table A holds conflicts of substance; table B holds clashes of names, numbers and ids.

### Table A: conflicts of substance

| No. | Ids | The conflict | Resolution applied | Why |
| --- | --- | --- | --- | --- |
| A1 | `ISS-12`, `ISS-41`, `ISS-81`, `ISS-91` | One finding, four rows (`02c` Observations). `ISS-12` (`blocking`): the platform never executes submitted content in Phases 1 and 2, no sandbox, and `code_change_tests` still qualifies through non-executing checks plus sampled verification. The other three allow an isolated runner behind a flag. The flag has two names, `ff.verify.sandboxed_tests` (S4) and `ff.template.code_change_sandbox` (S8a); S9 names none. `ISS-91` says that while the runner is off `code_change_tests` cannot be approved or leased (9.8.2; S4 4.4.4 says the same), against `ISS-12` item 3. S8a 8.15 still lists `test_run` as the strongest check | `ISS-12` | 2.9 rule 3, and prompt E states the no-execution rule itself. The `_rs` variant of `ISS-81` (the requester runs the tests, the platform runs nothing) agrees with `ISS-12` and is kept. S4, S8a and S9 must drop the runner and `test_run`, and must not block approval of `code_change_tests`. If the owner ever allows a sandbox (`OD-08`), one flag name and one threat-model entry (`ISS-12` item 5) are needed |
| A2 | `ISS-16`, `ISS-61`, `ISS-85` (c) | Who pays when verification costs more than the pool. `ISS-16` item 3: the pool is a hard budget, the job stops with `verification_budget_exhausted`, the Reserve never subsidizes verification (FD§4.2 gives it one outflow, starter grants). `ISS-61`: draw on the pool, then on the job's levy budget, so Reserve inflow absorbs the overrun. `ISS-85` (c): floor-band and mandatory events are funded from the pool remainder, then the levy share. `AC-ledger-03` and `T-unit-01` (S6a) test the levy draw. The numerator of v also differs: `ISS-16` counts audit, third, rework, review, gold and blanket replicas beyond the first; `ISS-61` names `third` and `review` only | `ISS-16` | Register wins. The levy is Reserve inflow, so paying verification from it is a Reserve outflow that FD§4.2 does not allow. S6a text, `AC-ledger-03`, `T-unit-01` and S8b 8.32 must change |
| A3 | `ISS-16` item 2, `ISS-85` (a) | Quote basis of the pool. `ISS-16`: `v_quote` = max(measured v, v_floor) with v_floor = 0.02 + 0.01 = 0.03, and "the floors then fit in the pool in expectation". `ISS-85` (a): the default `g` and `s` imply v of about 0.15 to 0.17 (8.31), above `price.v_prior` 0.10, so pools start underfunded; S6 should quote with max(`price.v_prior`, v_exp). `ISS-85` (e): budget truncation censors measured v | `ISS-16` as written, flagged | Register wins, but its claim is doubtful: a pool sized on the floors cannot pay sampling above the floor, and `ISS-16` item 3 turns every shortfall into a stopped job. Before any measurement exists no file gives a measured v. The S6 owner must state the launch quote; max(measured v, `price.v_prior`, v_floor) [A] is `ISS-85`'s proposal with the floor added. Found by this cell; no id yet |
| A4 | `ISS-17`, `ISS-56`, `ISS-62`, `ISS-85` (d), `ISS-118` (11c) (b), `ISS-119` (11c) (c), `ISS-125` | Credit after an overturn. (i) `ISS-56` pays an overturned `cell_rejection`, and lots lost in an overturned ban, by a Reserve `grant` with reason `appeal_restitution`; `ISS-17` item 4 says lots expired during a ban stay expired, and `ISS-16` item 3 and `ISS-27` item 3 bar a Reserve outflow beyond starter grants. (ii) `ISS-85` (d) pays an overturned rejection by a `transfer` or a capped `mint`; `ISS-14` item 2 allows a `mint` only against one accepted Commons cell, so a mint for a member-job cell breaks mint provenance, and `ISS-56` names a third path. (iii) `ISS-62` lets a reversal after escrow close land on the requester as restitution; `ISS-17` records `unrecovered_ucr` and nobody bears it. (iv) `ISS-125` asks S6 for a partial-amount reversal rule that `ISS-17` item 1 already gives. (v) `ISS-118` (11c) (b) restores a rejected cell to `accepted` and names no payment | `ISS-17` for reversals; no rule for an overturned rejection after escrow close | Register wins where it speaks: reversals touch unspent lots only, the requester gets no restitution, the Reserve pays nothing beyond grants. `ISS-85` (d) is out, because it breaks `ISS-14` item 2. `ISS-56` is `needs_owner`; until the owner decides, its `appeal_restitution` entry type stays off and a rejection overturned after escrow close pays nothing [A]. That is a gap, not a rule, and the donor bears it. Not in S3 (2.E.3) |
| A5 | `ISS-14`, `ISS-62` | Traceability. `ISS-14` item 3: credit is not traced unit by unit and public text must not say it is. `ISS-62` keeps lineage along transfers, stopping at the Reserve, with `INV-L19` for unrecovered mint | `ISS-14` | Register wins. Keep the two integer checks of `ISS-14` items 1 and 2; drop lineage tracking; keep `INV-L19` only as the alarm on the published `unrecovered_ucr` of `ISS-17` item 2 |
| A6 | `ISS-27`, `ISS-76`, `ISS-74` | Work in flight when a policy tightens. `ISS-27`: a cell `submitted` and passed before `effective_at` is paid at `cell.voided` (reason `reject.policy_changed`) from the escrow, left out of the deliverable. `ISS-76` (S7), `AC-policy-19`, `AC-race-28` and `RC-28`: no credit, requeue, `Cell.attempt` unchanged, same reason code. Different end state and different payment. `ISS-74` adds two stamps (`screened_policy_version_id`, then a binding `policy_version_id` at `escrow_confirmed`) | `ISS-27`, with `ASM-23` and the default of `OD-09` | Register wins. `ISS-27` pays a donor who followed the rules in force at lease time and charges the job's escrow, not the Reserve. `ISS-76` stays `needs_owner`; the three tests must be rewritten to the `ISS-27` behavior. `ISS-74` is compatible with `ISS-27` item 1 but moves the binding stamp from admission to escrow confirmation, where R9 says admission (`ISS-74`'s own note) |
