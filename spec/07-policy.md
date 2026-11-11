# 7. Policy engine and Service Registry

*Spec part 7 · prompt scope D · vocabulary: `spec/00-conventions.md` (S0.*) · written against Founding Document draft v0.1 (FD). Nothing here is legal advice. No provider's terms, regional availability, price, limit or URL parameter is asserted anywhere in this part: each is a `FlagAnswer`, `TermsCopy` or adapter field entered by a human reviewer [V].*

## 7.1 Scope, decisions and dependencies

This part specifies rules `R1`..`R10` as data, the evaluator, policy versioning, stamping and re-check, the tighten and loosen workflow, the job metadata schema and allowlist, the volunteer opt-in model, the Service Registry workflow, the mapping of the G0 questions to stored answers, and the prompt-injection and abuse defenses. Entity, enum, state, event and parameter names are those of S0.*; additions are collected in 7.15 and reported in `## Issues raised`. [D]

**Decisions made by this part** [D]

1. Rules are rows (`Rule`), the evaluator is one pure function of `(stage, facts, PolicyVersion)`, and no code path contains a rule-specific `if`. Changing a rule is publishing a `PolicyVersion`, never a deploy (FD§5.4, prompt D).
2. Evaluation has six stages: `submit`, `screen`, `admit`, `lease`, `accept`, `publish` (7.3). `R1` is a guard at `submit`: a failure is an API error and the `Job` stays `draft` (S0.9.1: a guard failure emits no event). `R2`..`R7` failures at `screen` move the job to `rejected` (`job.policy_rejected`).
3. `unknown` is evaluated as `no` by exactly one function, `flag_value()` (7.10.6). No other code reads a `FlagAnswer`.
4. A service that is not `approved` never appears in any eligible set. `R5`, `R6`, `R7` are sequential filters on the set of eligible services; the rule that empties the set is the rule that rejects; the surviving set is stamped on the job (`eligible_service_ids`).
5. Two policy stamps: `screened_policy_version_id` at `job.policy_passed` and the binding `policy_version_id` at `job.escrow_confirmed` (admission), after a fresh evaluation under the then-current version (`ISS-74`).
6. Tightening takes effect at once, stops in-flight work and never un-accepts a cell that was legitimately accepted. Work that is not accepted under a valid policy earns no credit; the volunteer carries no penalty (7.7).
7. Loosening needs a public `ChangeLogEntry` with a stated reason, a notice period (`policy.loosen_min_notice_days`, 7 initial configurable default) and two distinct approvers. A version may not mix tightening and loosening.
8. Volunteer opt-ins are materialized as explicit `OptIn` rows at member creation, so a later change of defaults never widens an existing member's consent.
9. Registry answers are versioned by `review_round`; only answers of the round that produced the current `approved` state are effective.
10. Screening never edits stored input; it reads a normalized view and records findings. Persian text keeps its zero-width non-joiner.
11. The platform assembles the final prompt (wrapper, per-cell delimiter, closing scope clause); a template body cannot emit raw input outside the data block (7.12).
12. A fresh system has zero `approved` services: seed data contains none, and `createJob` is refused until a reviewer has approved one (7.10.7, `INV-P02`). This is the product-level expression of G0.

**Dependencies** [D]

| Needs | From | Used for |
| --- | --- | --- |
| `Job` states, `closure_reason`, `Cell`/`Lease` events | S5.* | transitions caused by policy (7.7, 7.10.5) |
| Quote, capacity, `NO_CAPACITY` | S6.* | consumes `supply_gauge()` (7.9.5) |
| Template fields `task_scope`, `policy_envelope`, `job_type`, `review_status` | S8.* | `R3`, `R4` facts (`ISS-79`) |
| Submission checks, quarantine | S9.* | consumes output rules (7.12.5) |
| Roles, `AdminAction`, two-person actions | S10.* | approvals in 7.8, 7.10 |
| Launch switches, kill switches | S14.* | `LAUNCH_GATE_CLOSED`, `kill.service.<svc_id>` |
| Operations and paths | S15.* | proposed ops in 7.15.4 |
| Screens and copy | S11.* | renders reason copy keys of 7.4.3 |

Exposed functions (internal interface): `evaluatePolicy(stage, subject)`, `eligibleServices(job)`, `visibleCellsFilter(member)`, `supplyGauge(tuple)`, `recheckAtAcceptance(cell)`, `classifyChange(oldVersion, newVersion)`, `flag_value(entry, key, region)`. [D]

## 7.2 Data model owned by this part

Field lists are normative for the registry and policy tables; S5.* reproduces them in the domain model and adds indexes. Column conventions follow S0.7 (`id`, `created_at`, `row_version`, `_at`, `_hash`, `is_`). [D]

### 7.2.1 Policy and PolicyVersion

| Entity.field | Type | Rule |
| --- | --- | --- |
| `Policy.id`, `.slug`, `.title_key` | `pol_`, text, `copy.*` key | One row per named profile; initial slug `default_phase1` (FD§5.4 default profile) |
| `Policy.current_version_id` | `plv_` | Pointer to the effective version; changed only by the flip in 7.8.5 |
| `PolicyVersion.policy_id`, `.version` | `pol_`, int | Unique `(policy_id, version)`, `version` = previous + 1 |
| `PolicyVersion.status` | enum `policy_version_status` | `draft`, `awaiting_approval`, `approved`, `effective`, `superseded`, `withdrawn` |
| `PolicyVersion.parent_version_id` | `plv_` | The version it was derived from; null only for version 1 |
| `PolicyVersion.change_class` | enum `change_class` | Computed by `classifyChange` (7.8.2), never typed by a person |
| `PolicyVersion.diff` | json | Output of the differ: added, removed and changed elements with their direction |
| `PolicyVersion.rules` | child `Rule` rows | Exactly ten, `R1`..`R10` (7.4); none can be removed or disabled (constant) |
| `PolicyVersion.allowlist` | json | Grouped rows, 7.6 |
| `PolicyVersion.pairing`, `.license_required_flags`, `.required_acks`, `.prohibited_categories` | json | 7.5, 7.6, 7.12 |
| `PolicyVersion.screening_rules`, `.output_rules`, `.wrapper_templates` | json | 7.12 |
| `PolicyVersion.content_hash` | `sha256:<hex>` | SHA-256 over RFC 8785 canonical JSON of all data columns above (S0.6.4); equal hash means equal behavior |
| `PolicyVersion.effective_from`, `.approved_at`, `.published_at` | timestamptz | 7.8 |
| `PolicyVersion.changelog_entry_id` | `chg_` | Required before `approved` for `loosen` (INV-P05) |
| `PolicyVersion.author_admin_id`, `.approver_admin_ids` | `adm_` list | Distinctness rules in 7.8.3 |

Immutability: a row leaves `draft` only by being frozen (`content_hash` computed); after that no data column changes, enforced by a database trigger that rejects `UPDATE` of data columns outside `draft` (`INV-P04`). Retention class `permanent`. [D]

### 7.2.2 Rule row

| Field | Type | Meaning |
| --- | --- | --- |
| `rule_id` | `R1`..`R10` | Natural key; equals `policy_rule_id` (S0.8.4) |
| `ordinal` | int | Evaluation order; equals the number in `rule_id` and is validated on publish |
| `slug` | text | Slug of S0.8.4; reason code is `policy.<rule_id>.<slug>` |
| `stages` | list of stage | Stages in which the rule runs (7.3.1) |
| `kind` | enum | `check` (predicate), `filter` (narrows the eligible set), `advisory` (never rejects), `procedure` (`R9`, `R10`: code-defined workflow with data parameters) |
| `applies_when` | expression | Rule is skipped (recorded as `skipped`) when false; default `true` |
| `checks` | list | `[{sub_code, fail_when, hold_when?}]`, evaluated in order; first match decides |
| `keep_where` | expression | For `filter` rules: services for which it is true stay eligible |
| `copy_key` | text | `copy.policy.<rule_id>.<slug>` (EN and FA text in 7.4.3) |
| `tighten_direction` | enum | `up` or `down` for numeric rule parameters; see 7.8.2 |

### 7.2.3 Decision record

Every evaluation at `screen`, `admit` and `accept` returns and persists a `policy_decision` (json on `Job` for job stages, on `Cell` for `accept`; also in the event payload):

```json
{ "policy_version_id": "plv_...", "stage": "admit", "result": "pass|reject|hold",
  "failed_rule": "R7", "sub_code": "license_exceeds_flags", "reason": "policy.R7.license_exceeds_service_flags",
  "details": { "underlying": null, "service_ids": ["svc_..."] },
  "eligible_service_ids": ["svc_..."], "registry_snapshot_hash": "sha256:...",
  "parameter_versions": { "screen.url_action": 3 }, "facts_hash": "sha256:...",
  "trace": [ { "rule": "R1", "outcome": "pass" }, { "rule": "R2", "outcome": "pass" } ],
  "evaluated_at": "2026-11-12T09:30:00Z" }
```

`registry_snapshot_hash` = SHA-256 over canonical JSON of the sorted list of `{svc_id, state, approved_round, effective_answer_ids, terms_copy_ids}` for every service considered. `facts_hash` hashes the canonical facts object with free text removed (hashes, ids, enums only). A decision can be replayed exactly from `(policy_version_id, facts, registry snapshot)`; the replay tool is the test oracle for `T-policy-*`. [D]

## 7.3 Facts, expression language and evaluator

### 7.3.1 Stages [D]

| Stage | Called by | Rules run | Result types | Effect of a failure |
| --- | --- | --- | --- | --- |
| `submit` | `job.submitted` guard | `R1` | `pass`, `reject` | `422 POLICY_REJECTED`, job stays `draft`, no event |
| `screen` | after input screening and reviewer decision | `R1`..`R7`, `R8` advisory | `pass`, `reject`, `hold` | `reject` -> `job.policy_rejected`; `hold` keeps `screening` with `Job.screen_status` = `awaiting_reviewer` (`ISS-75`); `pass` -> `job.policy_passed` |
| `admit` | guard of `job.escrow_confirmed` | `R1`..`R7`, `R8` advisory, `R9` | `pass`, `reject` | `422 POLICY_REJECTED`; job stays `quoted`; see 7.7.2 |
| `lease` | cell listing and `cell.leased` | `R8` | `visible`, `hidden` | cell is not shown / lease refused with `404 NOT_FOUND` (existence not leaked) |
| `accept` | before `cell.checks_passed` or `cell.audit_passed` becomes `accepted` | `R1`..`R7`, `R9` | `pass`, `reject` | cell not accepted, `reject.policy_changed` (7.7.4) |
| `publish` | publication of a `PolicyVersion` or a registry change | `R10` | `pass`, `reject` | `VALIDATION_FAILED` with `details.fields[].code` (7.8) |

### 7.3.2 Facts [D]

Facts are built by `build_facts(stage, subject)` from the database; the evaluator never reads the database itself.

| Path | Type | Source |
| --- | --- | --- |
| `job.purpose`, `.license`, `.sensitivity`, `.service_requirement` | enum | declarations (7.5) |
| `job.pinned_service_ids`, `.topic_keys`, `.acks` | lists | declarations |
| `job.prompt_source` | `template` or `freeform` | wizard; `freeform` exists only so `R4` has something to reject |
| `job.is_commons` | bool | Commons jobs are authored by an admin (S8.*) |
| `template.template_version_id`, `.review_status`, `.job_type`, `.task_scope`, `.policy_envelope` | S0.9.5 / S8.* | the chosen `TemplateVersion` |
| `screen.findings` | list of `{rule_id, group, severity, action}` | screening (7.12.3) |
| `screen.reviewer_decision` | null, `pass`, `reject` | reviewer |
| `screen.reviewer_categories` | list of category ids | reviewer, from `prohibited_categories` |
| `screen.effective_sensitivity` | `S0`..`S3` | maximum of the declared level and levels implied by findings with action `reject` or by a reviewer |
| `policy.allow_row` | `{row_id, status, owner_rule}` or null | first allowlist row matching the four declarations (7.6) |
| `policy.pairing`, `.license_required_flags`, `.prohibited_category_ids`, `.required_acks_for_job` | data | the `PolicyVersion` under evaluation |
| `registry.services[]` | `{svc_id, kind, state, flags, has_terms_copy, review_round, state_hash}` | `flags` is already passed through `flag_value()`: only `yes` or `no` |
| `registry.active_topic_keys` | list | `TopicCategory` rows with status active |
| `cell.service_id`, `cell.eligible_service_ids`, `cell.topic_keys` | | `lease` and `accept` |
| `volunteer.optins.{purposes, licenses, sensitivities, service_requirements, topics}`, `volunteer.declared_service_ids` | lists | `OptIn` rows (7.9) |
| `params.<name>` | value | parameters read at evaluation time; their versions go into the decision record |

### 7.3.3 Expression language [D]

Expressions are JSON; a string starting with `$` is a fact path; inside `keep_where` the name `$svc` is the service under test. No loops, no assignment, no user code, no regular expressions (regular expressions live only in screening rules, 7.12). Evaluation is total (an absent path is `null`), deterministic and side-effect free.

| Operator | Arguments | True when |
| --- | --- | --- |
| `all`, `any`, `not` | list / list / expr | boolean combination |
| `eq`, `ne` | a, b | equal / different (`null` equals only `null`) |
| `in`, `not_in` | value, list | membership |
| `lt`, `lte`, `gt`, `gte` | a, b | numeric comparison |
| `present`, `absent` | path | not null and not empty / null or empty |
| `empty`, `nonempty` | list | length 0 / > 0 |
| `subset` | a, b | every element of a is in b |
| `intersects` | a, b | at least one common element |
| `diff` | a, b | returns the list a minus b (used inside `nonempty`) |
| `lookup` | map, key | returns the value (used inside `in`, `eq`) |
| `flag_yes` | `$svc`, flag_key | `$svc.flags[flag_key] == "yes"` |
| `len_gt` | list, n | length greater than n |

### 7.3.4 Evaluator [D]

```
function evaluate(stage, facts, pv):
  eligible = candidate_services(facts, pv)            # state == approved, kind per service_requirement
  trace = []
  for rule in pv.rules sorted by ordinal where stage in rule.stages:
    if not eval_expr(rule.applies_when, facts):
        trace.add(rule.rule_id, "skipped"); continue
    if rule.kind == "procedure":                      # R9 (admit, accept) and R10 (publish)
        out = run_procedure(rule, stage, facts, pv)   # 7.7.3 and 7.8
        trace.add(rule.rule_id, out.outcome)
        if out.outcome == "reject": return decision("reject", rule, out.sub_code, out.details, eligible, trace)
        continue
    for chk in rule.checks:                           # first matching check decides
        if chk.hold_when and eval_expr(chk.hold_when, facts) and stage == "screen":
            return decision("hold", rule, chk.sub_code, {}, eligible, trace + [(rule.rule_id, "hold")])
        if rule.kind != "advisory" and eval_expr(chk.fail_when, facts, eligible):
            return decision("reject", rule, chk.sub_code, details_for(rule, chk, facts, eligible), eligible, trace + [(rule.rule_id, "fail")])
        if rule.kind == "advisory" and eval_expr(chk.fail_when, facts):
            facts.advisories.add(rule.rule_id, chk.sub_code)
    if rule.kind == "filter":
        eligible = [s for s in eligible if eval_expr(rule.keep_where, facts, svc=s)]
        if empty(eligible):                           # the rule that empties the set rejects
            return decision("reject", rule, rule.empty_sub_code, {"service_ids": ids_before}, eligible, trace)
    trace.add(rule.rule_id, "pass")
  return decision("pass", None, None, {}, eligible, trace)
```

Properties the implementation MUST satisfy (each is a `T-policy-*` or `T-prop-*` test): [D]

1. **Determinism.** Same `(stage, facts, pv)` gives byte-identical decisions (property test over generated facts).
2. **First failing rule.** The reported rule has the smallest ordinal among rules that would fail; there is exactly one `reason` in a gating decision (FD§5.4).
3. **Monotone filters.** The eligible set never grows during an evaluation; it is always a subset of `approved` services.
4. **Unknown is no.** Replacing any flag `unknown` by `no` in the registry changes no decision (property test).
5. **No hidden inputs.** Two fact objects equal under `facts_hash` give equal decisions; clock and randomness are absent from the evaluator (the stage's `now` is in the facts).
