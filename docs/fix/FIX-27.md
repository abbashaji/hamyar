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
| E-23 | spec/08a-templates.md:36 | decision 8: checks that execute code run only in an isolated runner | decision 8: no check ever executes submitted content; static checks, sampled audit, requester runs tests | applied |
| E-24 | spec/08a-templates.md:124-125 | schema `execution.mode` enum none, server_sandbox, requester_side; property `runner_profile` | enum none, requester_side; `runner_profile` removed (ids kept otherwise) | applied |
| E-25 | spec/08a-templates.md:278 | 8.5.4: the only exception is the isolated runner of 8.13 | no exception and no runner exists | applied |
| E-26 | spec/08a-templates.md:284 | 8.6.1: inconclusive example, the runner is unavailable | example: a check cannot be evaluated | applied |
| E-27 | spec/08a-templates.md:303-305 | check type `test_run` (isolated runner, `execution.mode` = `server_sandbox`) | `test_run` removed; three static check types added by this fix: `diff_applies_cleanly`, `path_allowlist`, `forbidden_patterns` (reasons existing; assumption [A]) | applied |
| E-28 | spec/08a-templates.md:311-314 | evaluation order ended `8 static_parse  9 test_run`, test_run last so nothing flagged is executed | step 8 is the four static checks; nothing is ever executed | applied |
| E-29 | spec/08a-templates.md:327 | comparator `test_outcome_equal` (needs `test_run`) and `patch_normalized_equal` used by requester_side only | `test_outcome_equal` removed; `patch_normalized_equal` used by both code-change slugs | applied |
| E-30 | spec/08a-templates.md:839 | tests run by exactly one of two parties fixed by `execution.mode` | tests never run by the platform; run by the requester after delivery | applied |
| E-31 | spec/08a-templates.md:843 | slug `code_change_tests`: `server_sandbox`, platform runner, `standard`, then `test_run` | slug `code_change_tests`: `requester_side`, requester runs tests, `high` (LR-08 requires it for this mode), static checks, gold, sampled audit | applied |
| E-32 | spec/08a-templates.md:846 | second slug exists because risk class and checks differ per version | both slugs kept (no id deleted); with the runner removed they are equivalent; merge is an owner matter | applied |
| E-33 | spec/08a-templates.md:848-850 | 8.13.3 `Runner contract (interface TestRunner)` | 8.13.3 `Static verification contract; no runner` (number kept) | applied |
| E-34 | spec/08a-templates.md:854-859 | contract rows Isolation, Limits (`template.exec.*`), Inputs (hold-out tests, runner command), Profiles, Order, Outage | rows now: Checks, Limits, Inputs, Languages, Order, Outage, all static; no process is started | applied |
| E-35 | spec/08a-templates.md:860 | Gate row: flag `ff.template.code_change_sandbox` off, so only the `_rs` slug can be approved | row replaced by an Audit row (sampled, blanket where `high`); flag removed; nothing blocks approval | applied |
| E-36 | spec/08a-templates.md:861 | RC-13: sandbox design reviewed in the G1 threat model | RC-13 id kept: reviewer confirms that nothing executes submitted content | applied |
| E-37 | spec/08a-templates.md:863 | this is the one place where the platform executes submitted text; owner may decline | no place executes submitted text; `ISS-81` resolved by `ISS-12`; sandbox would need a new flag and threat-model entry | applied |
| E-38 | spec/08a-templates.md:869 | slot `language` values are the runner profiles | values are the languages reviewers allow | applied |
| E-39 | spec/08a-templates.md:873 | slot `tests_holdout` used only by `test_run` | slot kept (id not deleted), read by no check, removal for the owner | applied |
| E-40 | spec/08a-templates.md:875 | upload validation runs a red baseline twice in the sandbox, field code `flaky_tests` | platform runs nothing at upload; no baseline; `flaky_tests` unused | applied |
| E-41 | spec/08a-templates.md:929 | text never interpreted outside the runner | never interpreted or executed | applied |
| E-42 | spec/08a-templates.md:934-945 | yaml for server_sandbox: c06 `test_run`, comparator `test_outcome_equal`; `_rs` identical minus c06 | requester_side: c06 `diff_applies_cleanly`, c07 `path_allowlist`, c08 `forbidden_patterns`, comparator `patch_normalized_equal`; `_rs` identical | applied |
| E-43 | spec/08a-templates.md:948 | sentence on `test_outcome_equal` | sentence on `patch_normalized_equal`, rare agreement, why `high` | applied |
| E-44 | spec/08a-templates.md:954-957 | gold steps use runner baseline, reference, wrong variant, hold-out, `property` kind | gold steps by reading and static checks, kind `reference_tolerant`, second reviewer re-reads | applied |
| E-45 | spec/08a-templates.md:963-968 | KR-CC-1, 2, 4, 6 about sandbox escape, hold-out tests, repeated baseline, runner languages | rewritten for static checks, no tests run, requester sees flaky tests, parser languages; ids kept | applied |
| E-46 | spec/08a-templates.md:975-977 | H-CC-1 measures `test_run` passes; H-CC-3 hold-out tests reduce test-gaming | H-CC-1 measures static-check passes; H-CC-3 removed (depends on running hold-out tests) | applied |
| E-47 | spec/08a-templates.md:1097-1098 | summary row: strongest check `test_run` in the isolated runner, comparator `test_outcome_equal`, `standard`; `_rs` row `static_parse` only | `code_change_tests`: static checks, `patch_normalized_equal`, `high`; `_rs`: static checks as above | applied |
| E-48 | spec/08a-templates.md:1121-1123 | AC-template-15 invokes `test_run`; AC-template-16 `ff.template.code_change_sandbox` off blocks approval; AC-template-17 runner outage | AC-15 later checks not invoked; AC-16 no runner, no flag gates approval; AC-17 nothing executed; ids kept; flag removed | applied |
| E-49 | spec/08a-templates.md:1143 | note: `template.exec.*` parameters are operational, owned by operator | note: they belonged to the removed runner, no component reads them, rows stay because S0 and S16 may define them | applied |
| E-50 | spec/08a-templates.md:1149 | 8.17 table row: feature flag `ff.template.code_change_sandbox` (default off) | row removed | applied |
| E-51 | spec/08a-templates.md:1150-1151 | check types listed `test_run`; comparator types listed `test_outcome_equal` | `test_run` and `test_outcome_equal` removed; three static check types added | applied |
| E-52 | spec/08a-templates.md:1160 | open decision: platform may execute submitted code in an isolated runner; which runner languages | may ever execute (`OD-08` default-applied: never); which languages have a safe parser | applied |
| E-53 | spec/08a-templates.md:844,1098 | `_rs` row said non-executing checks only (`static_parse`) | `_rs` row says the same static checks as `code_change_tests` | applied |
| E-54 | spec/08a-templates.md:1171 | `ISS-81` resolution: scoped exception behind `ff.template.code_change_sandbox` | superseded by `ISS-12`; no flag; id and status `needs_owner` kept; `OD-08` default applied | applied |
| E-55 | spec/09-result-return.md:304 | 9.8.2: code runs in an isolated runner; until built and signed off the check is inconclusive and `code_change_tests` cannot be approved | no runner; static checks plus sampled audit; requester runs tests; template approvable like any other | applied |
| E-56 | spec/09-result-return.md:812 | `ISS-91` resolution: runner, inconclusive, template cannot be approved | superseded by `ISS-12`; id and status `proposed` kept | applied |
| E-57 | spec/03-assumptions.md (`OD-08` row) | `OD-08` row of S3 not read and not editable here | `OD-08` is marked default-applied in this log and in the text of the three files; the S3 row is outside `allowed_paths` | skipped-needs-owner |
| E-58 | spec/08a-templates.md:1143-1148 | rows `template.exec.timeout_s`, `template.exec.memory_bytes`, `template.exec.max_output_bytes` | rows kept and annotated (E-49); defined or used in S0 and S16, which are outside `allowed_paths` and would fail `check_params.py` if only one side changed | skipped-needs-owner |
| E-59 | spec/08a-templates.md:843-844 | two slugs `code_change_tests` and `code_change_tests_rs` | kept as two ids; now equivalent (E-31, E-32); merging or retiring one is a rename or deletion this cell may not do | skipped-needs-owner |
| E-60 | S0, S16, 06, 07, 08b, 14, 15a to 15g, 17, 18 and every file other than the three edited | any mention of `ff.verify.sandboxed_tests`, `ff.template.code_change_sandbox`, `test_run`, `test_outcome_equal` or a runner | not searched: only the three files named by the cell were read; searched nothing else | skipped-not-found |

## Read-back

Every edited place was re-read after the last edit. What is there now:

| rows | place | what is now there |
| --- | --- | --- |
| E-01, E-02, E-03 | spec/04:17, 46, 60 | decision 1 reads `submitted content is never executed`; the fail-closed row ends `no check ever runs submitted content`; the exclusion row says there is `no exception` |
| E-04, E-05 | spec/04:89-91, 116 | the fourth diagram box reads `No runner: submitted content is never executed anywhere`; the port list ends at `StaticHost` and `Mailer` follows on the next line |
| E-06, E-09, E-10 | spec/04:125-126, 187, 236 | the deployable table goes from `server` to `static bundles`; the component table ends with the `Scheduler and outbox relay` row; the verification block ends with `createAudit / compare(audit) / estimateReliability(member)` and has no runner call |
| E-07, E-08 | spec/04:161, 178 | B4 reads `no such boundary exists` and B5 follows; the verification pipeline row ends `human-review cells` and depends on the job service and the ledger only |
| E-11, E-12 | spec/04:259-266, 298 | 4.4.4 is titled `Checks never execute submitted content` with four bullets, none naming a flag, a port or a runner design; the port row is `Mailer` alone |
| E-13, E-14, E-15 | spec/04:766, 817, 852 | F2 reads `a second donor's output`; the Phase 1 topology says `no check runner in any phase`; the merge-gate row says it is `not a model for executing submitted content` |
| E-16, E-17, E-18 | spec/04:889, 895, 906-909 | `Also added:` starts with `registry field`; the assumption reads `Modular monolith (4.3.2)`; the verification table goes from the reachability row on, with no check-runner row seen in the window read |
| E-19, E-20, E-21, E-22 | spec/04:941, 956, 960, 966 | `AC-arch-16` is about a code-change template that is not refused; the `ISS-41` row says `ISS-12` rules and keeps status `proposed`; the `ISS-45` list and the closing paragraph name `adapter.open_url` and no flag |
| E-23, E-24, E-25, E-26 | spec/08a:36, 124-125, 278, 284 | decision 8 says `No check ever executes submitted content`; the enum is `none` and `requester_side` only; 8.5.4 says `no runner exists`; the inconclusive example reads `a check cannot be evaluated` |
| E-27, E-28, E-29 | spec/08a:303-305, 311-314, 327 | the registry has `diff_applies_cleanly`, `path_allowlist` and `forbidden_patterns` after `static_parse` and no `test_run` row; step 8 of the order lists the four static checks; the comparator table has no `test_outcome_equal` row and `patch_normalized_equal` is used by both slugs |
| E-30, E-31, E-32, E-53 | spec/08a:839-846 | the tests are run `by the requester, on their own machine`; both slug rows say `requester_side` and `high` with static checks; the paragraph says `renames and deletes no id` |
| E-33, E-34, E-35, E-36, E-37 | spec/08a:848-863 | 8.13.3 is `Static verification contract; no runner`; the table has Checks, Limits, Inputs, Languages, Order, Outage, Audit and the `RC-13` row; no flag name remains; the closing paragraph says there is `no place` that executes submitted text |
| E-38, E-39, E-40 | spec/08a:869-875 | `language` lists the languages reviewers allow; `tests_holdout` is read by no check; upload validation says the platform `runs nothing at upload` |
| E-41, E-42, E-43 | spec/08a:929, 934-948 | 8.13.7 ends `never interpreted or executed`; the yaml has c01 to c08 with c06 `diff_applies_cleanly`, c07 `path_allowlist`, c08 `forbidden_patterns` and comparator `patch_normalized_equal`; the sentence below names only `patch_normalized_equal` |
| E-44, E-45, E-46 | spec/08a:954-976 | gold steps use reading and static checks only; KR-CC-1 to KR-CC-7 keep their ids and no row names a runner; the H-CC table has H-CC-1 and H-CC-2 and no H-CC-3 |
| E-47, E-48 | spec/08a:1097-1098, 1121-1123 | the summary row reads `Static checks` with `high`; AC-template-15 says `no later check`; AC-template-16 says `no flag gates it`; AC-template-17 says `no process is started` |
| E-49, E-50, E-51, E-52 | spec/08a:1143-1160 | the note says the `template.exec.*` parameters `belonged to the removed runner`; the other-additions table has no feature-flag row and lists the three static checks and no `test_outcome_equal`; the open decision reads `default applied: it never does` |
| E-54 | spec/08a:1171 | the `ISS-81` row says `Superseded by ISS-12` and keeps status `needs_owner` |
| E-55, E-56 | spec/09:304, 812 | 9.8.2 says there is no runner, sandbox or `test_run` check and the template is approved `like any other template`; the `ISS-91` row says `Superseded by ISS-12` and keeps status `proposed` |

Checked and left unchanged: spec/04 `4.2.2` first two exclusion rows, `4.18` rows other than the merge-gate row, and the `execute` and `exec` words in spec/09 9.8.2 (forbidden-API table) and 9.16; spec/08a 8.7 lint words `run` and `execute` (they block volunteer prompts, not runners) and 8.8.5 `execution.mode` to `requester_side` as a loosening. The file names `spec/08b-verification.md`, `spec/03-assumptions.md`, S0 and S16 were not opened (rows E-57, E-58, E-60).

Assumptions made [A]: the three static check types of E-27 are named by this fix; `code_change_tests` is `requester_side` and `high` because LR-08 requires `high` for that mode, which makes the two slugs equivalent (E-59); `reject.schema_invalid` is the reason of the two new reject checks.

Result: DONE WITH SKIPS
