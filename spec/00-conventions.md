# 0. Conventions and Shared Vocabulary

*Spec part 0 · owner cell C-000 · binding on every other spec file. Written against Founding Document draft v0.1 (FD). Nothing here is legal advice and nothing here has been verified against any provider's terms or any law.*

## 0.1 How to use this file

- Every other spec file MUST use the names, IDs, enum values, state names, event names and parameter names in this file exactly (case-sensitive). [D]
- A name missing here MAY be added by the owning part, but it MUST be reported in that part's `## Issues raised` list as a convention gap (see 0.4) so C-001 can fold it back. [D]
- MUST, MUST NOT, SHOULD and MAY carry their usual RFC 2119 meaning. [P]
- Identifiers in `code font` are normative; prose labels are not.
- Facts about provider terms, regional availability, pricing, limits, URL parameters or law are configuration data entered by a human reviewer. This file hardcodes none of them; every dependence is tagged [V]. [D]
- Scope boundary: this file fixes vocabulary. Guards, side effects, algorithms, screens and copy live in the parts listed in 0.13. [D]

## 0.2 Evidence-tag legend

| Tag | Meaning | Required companion | Example |
| --- | --- | --- | --- |
| `[D]` | A decision this spec makes; binding on implementers | A one-line reason, or an FD§ reference | "Ledger amounts are integer micro-credits [D]" |
| `[H]` | A hypothesis; may be false | The measurement that tests it and the success or kill criterion | "A contribution takes under 60 s [H]" |
| `[V]` | Must be verified by a human before anyone relies on it | What is verified, by whom, and where the answer is stored (parameter, `ServiceRegistryEntry`, `LaunchGateItem`, counsel memo) | "Iran reachability of the host [V]" |
| `[P]` | A premise taken from the brief or the FD, not independently checked | The FD§ it comes from | "Free allowances cannot be transferred [P]" |
| `[A]` | An assumption introduced by this spec, not present in the FD | The owner decision that could overturn it (collected in S3.*) | "Admin host is a separate origin [A]" |

Writing rules for all parts: [D]

1. One tag per bracket. Combine by adjacency: `[H][V]`. Place the tag directly after the claim it qualifies.
2. Every number is either derived by a formula shown next to it or labeled exactly `initial configurable default` (and then it must exist in the parameter table, 0.10).
3. No statistic is invented. Simulation output is never evidence about human behavior (prompt K).
4. User-facing promises say "declared", never "guaranteed" (FD Principle 11). Legal conclusions are never drawn; they are `[V]` for counsel.
5. An unverified claim is never written as a fact; it is tagged or removed.

## 0.3 Cross-reference style

| Form | Meaning | Example | Rule |
| --- | --- | --- | --- |
| `FD§N` / `FD§N.M` | Section of the Founding Document | `FD§4.3` = price and exchange rate | Never "section 4.3" without the prefix |
| `S<n>.<m>` | Heading `## <n>.<m>` of spec part `<n>` (part number = section number of the required deliverable structure, prompt) | `S6.3` | Always contains a dot. A whole part is written `S<n>.*` |
| `S0.<m>` | This file | `S0.9` = state machines | |
| `ISS-nn` | An Issue (0.4) | `ISS-03` | |
| `R1`..`R10` | Policy rules (FD§5.4) | `R9` | Bare `R<n>`, never "rule 9" |
| `G0`..`G5` | Launch gates (FD§8.3) | `G1` | Not to be confused with parameter `grant.starter_credits` (FD symbol G) |
| `BM0`..`BM9` | Build milestones (0.12) | `BM2` | See `ISS-01` for why not `M0..Mn` |
| `P0`..`P3`, `L0`..`L3`, `S0`..`S3`, `M0`..`M2` | Purpose, license, sensitivity, service requirement (0.8) | `S1` (sensitivity) | Sensitivity has no dot; a spec reference always has one, so `S1` and `S1.2` never collide |
| `C-nnn` | Build cell id | `C-022` | Allowed only in this file, in `## Issues raised` and in provenance notes; never in normative text |

A reference to a section that does not exist yet MUST still be written in this form; C-001 checks every reference resolves at assembly. [D]

## 0.4 Issue ID scheme and how parts report issues

An Issue is a problem, gap or unimplementable rule found in the FD (or in an instruction) together with a proposed resolution. [D]

**ID format.** `ISS-nn`, `nn` at least two digits, never reused, never renumbered. Collisions between parts written in parallel are prevented by fixed blocks: part `p` (first number of the file's top heading) owns `ISS-(10p+1)` .. `ISS-(10p+9)`; part 0 owns `ISS-01`..`ISS-09`, part 1 `ISS-11`..`ISS-19`, part 2 `ISS-21`..`ISS-29`, and so on up to part 21 (`ISS-211`..`ISS-219`). If the plan splits one part over several files, the file that sorts first uses digits 1-3, the second 4-6, the third 7-9. [D]

**Reporting.** Every spec file ends with `## Issues raised`, a table with these columns (an empty table states "none"): [D]

| Column | Values |
| --- | --- |
| `id` | `ISS-nn` from the file's block |
| `severity` | `blocking` (cannot be implemented as written), `major` (changes a design), `minor` (naming, wording) |
| `fd_ref` | `FD§N` or `prompt` or `none` |
| `issue` | One line |
| `resolution` | Proposed resolution, already applied consistently inside the file |
| `status` | `proposed`, `accepted`, `applied`, `rejected`, `needs_owner` (only the owner can decide; also listed in S3.*) |

C-001 consolidates all tables into S2.* (grouped by severity, each with the parts that apply the resolution) and may add its own issues in `ISS-21`..`ISS-29`. A part applies its own proposed resolution until C-001 records a different one. [D]

## 0.5 Other document ID schemes

| Scheme | Format | Owner part | Example |
| --- | --- | --- | --- |
| Ledger invariants | `INV-L<nn>` | S6.* | `INV-L01` |
| Threats | `THR-<nn>` | S10.* | `THR-07` |
| Risks | `RISK-<nn>` (FD§8.2 rows keep their numbers 1-15 as `RISK-01`..`RISK-15`) | S19.* | `RISK-08` |
| Screens | `SCR-<role>-<nn>`, role in `vol`, `req`, `rev`, `ops`, `pub` | S11.*, S12.* | `SCR-vol-03` |
| Acceptance criteria | `AC-<area>-<nn>` (Given / When / Then) | the part that specifies the feature | `AC-ledger-12` |
| Tests | `T-<layer>-<nn>`, layer in `unit`, `prop`, `fsm`, `policy`, `adv`, `inj`, `rtl`, `load`, `e2e`, `sim` | S18.* | `T-prop-04` |
| API operations | `op` ids in lowerCamelCase | S15.* | `createJob` |
| User-facing copy keys | `copy.<area>.<key>`, each with `fa` and `en` text and the marker `needs_human_and_legal_review` | S11.*, S12.* | `copy.privacy.pseudonymity_notice` |
| Metrics | `hamyar_<area>_<name>_<unit>` | S4.*, S13.* | `hamyar_ledger_invariant_violations_total` |
| Log events | `<area>.<event>` lowercase dotted, same names as domain events (0.9) | S4.* | `cell.leased` |
| Experiments | `EXP-<nn>`; growth mechanics keep `V1`..`V6` (FD§6.2) | S12.*, S13.* | `EXP-02` |
| Measurements that replace defaults | codes in 0.10 (`CAL`, `P1M`, `DEM`, `FND`, `CNS`, `SEC`, `TEC`, `OPS`, `CON`) | S16.* | `CAL` |
