# FIX-27: remove the isolated test runner everywhere (ISS-12)

*Fix log of cell C-098 (task FIX-27 of `docs/audit/FINAL.md` section 5.1 as restated in the cell). Files edited: `spec/04-architecture.md`, `spec/08a-templates.md`, `spec/09-result-return.md`. Sources read: `docs/audit/FINAL.md`, `spec/02e-issues-summary.md` (2.E.1, 2.E.2 A1), `docs/decisions.md`, and the three edited files in full. Nothing was executed. Line numbers are the lines after the edits, counted from the read-back, and may be off by a line or two.*

Rule applied [D]: `ISS-12` (blocking) rules over `ISS-41`, `ISS-81` and `ISS-91` (02e A1). The platform never executes submitted content: no isolated runner, no sandbox, no `test_run` check. Decision `OD-08` is **default-applied** (default: the platform never runs submitted code); the owner may still change it, and then one flag name and one threat-model entry are needed (`ISS-12` item 5). The flag had two names, `ff.verify.sandboxed_tests` (S4) and `ff.template.code_change_sandbox` (S8a); both are removed from the three files. Every other flag is kept. The code-change template now verifies by static checks (parse, diff applies cleanly to the supplied snapshot, file-path allowlist, size, forbidden patterns) plus a sampled audit against a second donor's output; the requester runs the supplied tests on their own machine after delivery and may report a result, which is a rating input and never mints or moves credit; the volunteer is never asked to run anything.

## Edits

Flag removals are logged in rows E-06, E-11, E-16, E-21, E-22 (`ff.verify.sandboxed_tests`) and E-35, E-48, E-50, E-54 (`ff.template.code_change_sandbox`).

| edit | file:line | before | after | status |
| --- | --- | --- | --- | --- |
| E-01 | spec/04-architecture.md:17 | decision 1 said the monolith has one optional isolated check runner | decision 1 says submitted content is never executed (`ISS-12`); `OD-08` default-applied | applied |
| E-02 | spec/04-architecture.md:46 | fail closed: an unreachable check runner means no code-running template | fail closed: no check ever runs submitted content | applied |
| E-03 | spec/04-architecture.md:60 | exclusion row: only exception is the isolated check runner | exclusion row: no runner, no sandbox, no `test_run`, no exception | applied |
| E-04 | spec/04-architecture.md:89-91 | context diagram box: check runner, flag-gated, no network | diagram box now says no runner exists, content is never executed | applied |
| E-05 | spec/04-architecture.md:116 | port list ended with `CheckRunner` | `CheckRunner` removed from the port list | applied |
| E-06 | spec/04-architecture.md:125-126 | deployable unit row `check-runner`, absent unless `ff.verify.sandboxed_tests` is on | row removed; flag removed here | applied |
| E-07 | spec/04-architecture.md:161 | trust boundary B4: application to check runner | B4 kept as an id: no boundary exists, the platform executes nothing | applied |
| E-08 | spec/04-architecture.md:178 | verification pipeline row: optional check runner, check runner port | both mentions removed | applied |
| E-09 | spec/04-architecture.md:187 | component row `Check runner` | row removed | applied |
| E-10 | spec/04-architecture.md:234 | interface line `CheckRunner.run(...) -> CheckResult or Unavailable` | line removed | applied |
| E-11 | spec/04-architecture.md:259-266 | 4.4.4 `Check runner`: run_tests via CheckRunner, isolation limits, off by default under `ff.verify.sandboxed_tests`, G1 decision | 4.4.4 retitled `Checks never execute submitted content` (number kept); four bullets: no execution, static checks plus sampled audit, requester runs tests and reports as rating input, no runner design or G1 item; flag removed here | applied |
| E-12 | spec/04-architecture.md:298 | port table row `CheckRunner`, `Mailer` | row is `Mailer` only | applied |
| E-13 | spec/04-architecture.md:766 | F2: checks that need the check runner or a second donor make the cell `flagged_for_audit` | checks that need a second donor's output | applied |
| E-14 | spec/04-architecture.md:817 | Phase 1 topology: no check runner; full topology has a separate check runner | no check runner in any phase; full topology without one | applied |
| E-15 | spec/04-architecture.md:852 | panel merge-gate pattern kept as the model for the check runner | kept for Hamyar's own pipeline only; not a model for executing submitted content | applied |
| E-16 | spec/04-architecture.md:889 | 4.19.1 `Also added: flag ff.verify.sandboxed_tests (default off); ...` | flag removed from the list | applied |
| E-17 | spec/04-architecture.md:895 | assumption: modular monolith with an optional check runner | assumption: modular monolith | applied |
| E-18 | spec/04-architecture.md:909-918 | verification row: check runner design is safe enough to enable (G1) | row removed | applied |
| E-19 | spec/04-architecture.md:941 | `AC-arch-16`: flag off, a template needing `run_tests` is refused | `AC-arch-16`: a code-change template is not refused for lack of a runner, static checks, nothing executed | applied |
| E-20 | spec/04-architecture.md:956 | `ISS-41` resolution: runner behind `ff.verify.sandboxed_tests` | `ISS-41` resolution: never executed, `ISS-12` rules, `OD-08` default applied; id and status kept | applied |
| E-21 | spec/04-architecture.md:960 | `ISS-45` row listed flag `ff.verify.sandboxed_tests` among convention gaps | flag removed from that list | applied |
| E-22 | spec/04-architecture.md:966 | convention-additions paragraph listed `ff.verify.sandboxed_tests` | flag removed from that list | applied |
