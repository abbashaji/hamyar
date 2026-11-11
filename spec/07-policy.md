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
7. Loosening needs a public `ChangeLogEntry` with a stated reason, a notice period (`policy.loosen_min_notice_days`, 7 initial configurable default) and two distinct admins (the author counts as one). A version may not mix tightening and loosening.
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
| `kind` | enum | `check` (predicate), `filter` (narrows the eligible set), `procedure` (`R9`, `R10`: code-defined workflow whose parameters are data) |
| `applies_when` | expression | Rule is skipped (recorded as `skipped`) when false; default `true` |
| `checks` | list | `[{sub_code, fail_when, hold_when?}]`, evaluated in order; first match decides |
| `keep_where` | expression | For `filter` rules: services for which it is true stay eligible |
| `empty_sub_code` | text | `sub_code` used when a `filter` empties the eligible set |
| `post_checks` | list | Same shape as `checks`, evaluated after the filter step (used by `R7`) |
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
| `screen` | after input screening and reviewer decision | `R1`..`R7` (coverage by `supplyGauge`, 7.9.5) | `pass`, `reject`, `hold` | `reject` -> `job.policy_rejected`; `hold` keeps `screening` with `Job.screen_status` = `awaiting_reviewer` (`ISS-75`); `pass` -> `job.policy_passed` |
| `admit` | guard of `job.escrow_confirmed` | `R1`..`R7`, `R9` (coverage by `supplyGauge`, 7.9.5) | `pass`, `reject` | `422 POLICY_REJECTED`; job stays `quoted`; see 7.7.2 |
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
| `screen.flagged`, `screen.sampled` | bool | any finding with action `flag_for_review`; selected by `screen.review_rate_new_requester` / `screen.review_rate_established_requester` |
| `screen.reject_groups` | list | groups (7.12.3) of findings whose action is `reject` |
| `$eligible` | list of `svc_` ids | the evaluator's working set, readable by expressions (`diff`, `empty`, `nonempty`) |
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
| `flags_yes` | `$svc`, list of flag_key | every listed flag is `yes` (an empty list is true) |

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
        if eval_expr(chk.fail_when, facts, eligible):
            return decision("reject", rule, chk.sub_code, details_for(rule, chk, facts, eligible), eligible, trace + [(rule.rule_id, "fail")])
    if rule.kind == "filter":
        eligible = [s for s in eligible if eval_expr(rule.keep_where, facts, svc=s)]
        if empty(eligible):                           # the rule that empties the set rejects
            return decision("reject", rule, rule.empty_sub_code, {"service_ids": ids_before}, eligible, trace)
    for chk in rule.post_checks:                      # R7: pinned services must all survive the filter
        if eval_expr(chk.fail_when, facts, eligible):
            return decision("reject", rule, chk.sub_code, details_for(rule, chk, facts, eligible), eligible, trace + [(rule.rule_id, "fail")])
    trace.add(rule.rule_id, "pass")
  return decision("pass", None, None, {}, eligible, trace)
```

Properties the implementation MUST satisfy (each is a `T-policy-*` or `T-prop-*` test): [D]

1. **Determinism.** Same `(stage, facts, pv)` gives byte-identical decisions (property test over generated facts).
2. **First failing rule.** The reported rule has the smallest ordinal among rules that would fail; there is exactly one `reason` in a gating decision (FD§5.4).
3. **Monotone filters.** The eligible set never grows during an evaluation; it is always a subset of `approved` services.
4. **Unknown is no.** Replacing any flag `unknown` by `no` in the registry changes no decision (property test).
5. **No hidden inputs.** Two fact objects equal under `facts_hash` give equal decisions; clock and randomness are absent from the evaluator (the stage's `now` is in the facts).

## 7.4 Rules R1..R10 as data

### 7.4.1 Order, stages and what each rule decides [D]

| Rule | Slug (S0.8.4) | Kind | Stages | Decides |
| --- | --- | --- | --- | --- |
| `R1` | `metadata_missing_or_inconsistent` | check | `submit`, `screen`, `admit`, `accept` | structure, enums, pairing, acknowledgements, pinned services, topics, allowlist membership |
| `R2` | `sensitivity_not_accepted` | check | `screen`, `admit`, `accept` | declared or detected `S2`/`S3` |
| `R3` | `prohibited_content` | check | `screen`, `admit`, `accept` | prohibited categories, screening rejects, reviewer rejects, and any task beyond copy, Send, return text |
| `R4` | `template_required` | check | `screen`, `admit`, `accept` | approved template version and its policy envelope |
| `R5` | `commercial_needs_flag` | check + filter | `screen`, `admit`, `accept` | `P2` unlocked and service flag `commercial_use_of_output` |
| `R6` | `training_needs_m2_or_flag` | check + filter | `screen`, `admit`, `accept` | `P3` unlocked, `S0` only, service flag `training_use_of_output` |
| `R7` | `license_exceeds_service_flags` | check + filter + post-check | `screen`, `admit`, `accept` | a non-empty eligible set whose flags cover the license |
| `R8` | `volunteer_optin_mismatch` | check | `lease` | visibility of a cell to one volunteer |
| `R9` | `policy_version_stale` | procedure | `admit`, `accept` | fresh evaluation when the stamp is stale (7.7.3) |
| `R10` | `loosen_without_changelog` | procedure | `publish` | publication guard (7.8) |

An `accept` evaluation reuses the persisted screening outcome of the job (`screen.*` facts) and does not re-run input screening, unless the version diff touched `screening_rules` or `prohibited_categories`, in which case the sweep of 7.7.5 re-screens stored inputs first. [D]

### 7.4.2 Rule rows (the seed `PolicyVersion` 1 of policy `default_phase1`) [D]

```json
[
 {"rule_id":"R1","ordinal":1,"kind":"check","stages":["submit","screen","admit","accept"],"checks":[
  {"sub_code":"missing_field","fail_when":{"any":[{"absent":"$job.purpose"},{"absent":"$job.license"},{"absent":"$job.sensitivity"},{"absent":"$job.service_requirement"},{"absent":"$job.topic_keys"}]}},
  {"sub_code":"invalid_enum","fail_when":{"any":[{"not_in":["$job.purpose",["P0","P1","P2","P3"]]},{"not_in":["$job.license",["L0","L1","L2","L3"]]},{"not_in":["$job.sensitivity",["S0","S1","S2","S3"]]},{"not_in":["$job.service_requirement",["M0","M1","M2"]]}]}},
  {"sub_code":"pairing_inconsistent","fail_when":{"not_in":["$job.license",{"lookup":["$policy.pairing","$job.purpose"]}]}},
  {"sub_code":"pinned_required","fail_when":{"all":[{"eq":["$job.service_requirement","M1"]},{"empty":"$job.pinned_service_ids"}]}},
  {"sub_code":"pinned_forbidden","fail_when":{"all":[{"ne":["$job.service_requirement","M1"]},{"nonempty":"$job.pinned_service_ids"}]}},
  {"sub_code":"pinned_too_many","fail_when":{"len_gt":["$job.pinned_service_ids","$params.policy.max_pinned_services"]}},
  {"sub_code":"ack_missing","fail_when":{"nonempty":{"diff":["$policy.required_acks_for_job","$job.acks"]}}},
  {"sub_code":"topic_unknown","fail_when":{"nonempty":{"diff":["$job.topic_keys","$registry.active_topic_keys"]}}},
  {"sub_code":"not_allowlisted","fail_when":{"absent":"$policy.allow_row"}}]},
 {"rule_id":"R2","ordinal":2,"kind":"check","stages":["screen","admit","accept"],"checks":[
  {"sub_code":"declared_s2_s3","fail_when":{"in":["$job.sensitivity",["S2","S3"]]}},
  {"sub_code":"detected_s2_s3","fail_when":{"in":["$screen.effective_sensitivity",["S2","S3"]]}}]},
 {"rule_id":"R3","ordinal":3,"kind":"check","stages":["screen","admit","accept"],"checks":[
  {"sub_code":"task_exceeds_copy_send_return","fail_when":{"ne":["$template.task_scope","copy_send_return"]}},
  {"sub_code":"prohibited_category","fail_when":{"intersects":["$screen.reviewer_categories","$policy.prohibited_category_ids"]}},
  {"sub_code":"reviewer_rejected","fail_when":{"eq":["$screen.reviewer_decision","reject"]}},
  {"sub_code":"screen_reject","fail_when":{"intersects":["$screen.reject_groups",["link","instruction","delimiter","control","action_request"]]}},
  {"sub_code":"awaiting_review","hold_when":{"any":[{"all":[{"eq":["$screen.flagged",true]},{"absent":"$screen.reviewer_decision"}]},{"all":[{"eq":["$screen.sampled",true]},{"absent":"$screen.reviewer_decision"}]}]},"fail_when":{"eq":[1,0]}}]},
 {"rule_id":"R4","ordinal":4,"kind":"check","stages":["screen","admit","accept"],"checks":[
  {"sub_code":"template_required","fail_when":{"any":[{"ne":["$job.prompt_source","template"]},{"absent":"$template.template_version_id"}]}},
  {"sub_code":"template_not_approved","fail_when":{"ne":["$template.review_status","approved"]}},
  {"sub_code":"outside_template_envelope","fail_when":{"any":[{"not_in":["$job.purpose","$template.policy_envelope.purposes"]},{"not_in":["$job.license","$template.policy_envelope.licenses"]},{"not_in":["$job.sensitivity","$template.policy_envelope.sensitivities"]},{"not_in":["$job.service_requirement","$template.policy_envelope.service_requirements"]}]}}]},
 {"rule_id":"R5","ordinal":5,"kind":"filter","stages":["screen","admit","accept"],"applies_when":{"eq":["$job.purpose","P2"]},
  "checks":[{"sub_code":"purpose_locked","fail_when":{"ne":["$policy.allow_row.status","active"]}}],
  "keep_where":{"flags_yes":["$svc",["commercial_use_of_output"]]},"empty_sub_code":"no_service_with_flag"},
 {"rule_id":"R6","ordinal":6,"kind":"filter","stages":["screen","admit","accept"],"applies_when":{"eq":["$job.purpose","P3"]},
  "checks":[{"sub_code":"purpose_locked","fail_when":{"ne":["$policy.allow_row.status","active"]}},{"sub_code":"p3_requires_s0","fail_when":{"ne":["$screen.effective_sensitivity","S0"]}}],
  "keep_where":{"flags_yes":["$svc",["training_use_of_output"]]},"empty_sub_code":"no_service_with_flag"},
 {"rule_id":"R7","ordinal":7,"kind":"filter","stages":["screen","admit","accept"],
  "checks":[{"sub_code":"pinned_service_not_approved","fail_when":{"all":[{"eq":["$job.service_requirement","M1"]},{"nonempty":{"diff":["$job.pinned_service_ids","$eligible"]}}]}},
            {"sub_code":"no_approved_service","fail_when":{"empty":"$eligible"}}],
  "keep_where":{"flags_yes":["$svc",{"lookup":["$policy.license_required_flags","$job.license"]}]},"empty_sub_code":"license_exceeds_flags",
  "post_checks":[{"sub_code":"pinned_service_ineligible","fail_when":{"all":[{"eq":["$job.service_requirement","M1"]},{"nonempty":{"diff":["$job.pinned_service_ids","$eligible"]}}]}}]},
 {"rule_id":"R8","ordinal":8,"kind":"check","stages":["lease"],"checks":[
  {"sub_code":"purpose_not_opted","fail_when":{"not_in":["$job.purpose","$volunteer.optins.purposes"]}},
  {"sub_code":"license_not_opted","fail_when":{"not_in":["$job.license","$volunteer.optins.licenses"]}},
  {"sub_code":"sensitivity_not_opted","fail_when":{"not_in":["$job.sensitivity","$volunteer.optins.sensitivities"]}},
  {"sub_code":"service_requirement_not_opted","fail_when":{"not_in":["$job.service_requirement","$volunteer.optins.service_requirements"]}},
  {"sub_code":"service_not_declared","fail_when":{"not":{"intersects":["$cell.eligible_service_ids","$volunteer.declared_service_ids"]}}},
  {"sub_code":"topic_not_opted","fail_when":{"nonempty":{"diff":["$cell.topic_keys","$volunteer.optins.topics"]}}}]},
 {"rule_id":"R9","ordinal":9,"kind":"procedure","stages":["admit","accept"],"procedure":"stale_recheck"},
 {"rule_id":"R10","ordinal":10,"kind":"procedure","stages":["publish"],"procedure":"publish_guard"}
]
```

Notes on the rows. [D]

- `R3.awaiting_review` is a hold, never a rejection (its `fail_when` is constant false). At stage `screen` the evaluator returns `hold`; the job stays `screening` with `Job.screen_status` = `awaiting_reviewer` until the reviewer decision exists (7.12.4).
- `R4` containment: the template declares the combinations it was reviewed for (`policy_envelope`, `ISS-79`); a job outside it is rejected even if the allowlist would permit it. This is how the two Phase 1 profiles are narrowed per template.
- `R5` and `R6` order matters: `purpose_locked` is checked before the service filter so a locked purpose never leaks which services would have qualified.
- `R7` runs for every purpose. For `P0` with license `L0` the required-flag list is empty, so the filter keeps every candidate; the rule still rejects an empty candidate set (`no_approved_service`, the fresh-install case).
- `R8` is the only rule evaluated per volunteer; the same rows power the supply gauge (7.9.5).

### 7.4.3 Requester-facing reasons: codes and copy keys (EN and FA) [D]

Reason code `policy.<rule_id>.<slug>`; the optional `sub_code` travels in `details.sub_code` and selects an optional hint key `copy.policy.<rule_id>.<sub_code>.hint`. Every text below carries the marker `needs_human_and_legal_review`; Persian text is a draft for a native reviewer. Texts say "declared" where they describe the requester's input, never "guaranteed" (FD Principle 11). [D]

| Copy key | `en` | `fa` |
| --- | --- | --- |
| `copy.policy.R1.metadata_missing_or_inconsistent` | The declarations for this job are missing or inconsistent. Check purpose, license, sensitivity and service. | اظهارات این کار ناقص یا ناسازگار است. هدف، مجوز، حساسیت و سرویس را بررسی کنید. |
| `copy.policy.R2.sensitivity_not_accepted` | Data declared or detected as S2 or S3 is not accepted in this phase. Only public (S0) or private non-sensitive (S1) data is accepted. | دادهٔ اعلام‌شده یا شناسایی‌شده با حساسیت S2 یا S3 در این مرحله پذیرفته نمی‌شود. فقط دادهٔ عمومی (S0) یا خصوصیِ غیرحساس (S1) پذیرفته می‌شود. |
| `copy.policy.R3.prohibited_content` | The content or task is not compatible with the prohibited-content rules, or it asks a volunteer to do more than copy, press Send and return text. | محتوا یا وظیفه با قواعد محتوای ممنوع سازگار نیست، یا از داوطلب بیش از کپی کردن، زدن Send و بازگرداندن متن می‌خواهد. |
| `copy.policy.R4.template_required` | Only reviewed templates can be used. Free-form prompts are not available. | فقط الگوهای بازبینی‌شده قابل استفاده‌اند. متن آزاد (پرامپت دلخواه) در دسترس نیست. |
| `copy.policy.R5.commercial_needs_flag` | Commercial use (P2) runs only when this phase allows it and on a service whose reviewed terms permit it. That is not the case now. | کاربرد تجاری (P2) فقط وقتی ممکن است که این مرحله اجازه دهد و سرویسی با شرایط بازبینی‌شدهٔ موافق وجود داشته باشد. در حال حاضر چنین نیست. |
| `copy.policy.R6.training_needs_m2_or_flag` | Training or model-development use (P3) runs only on S0 data and only on a model or service whose reviewed terms permit it. That is not the case now. | کاربرد آموزشی یا توسعهٔ مدل (P3) فقط برای دادهٔ S0 و فقط روی مدل یا سرویسی ممکن است که شرایط بازبینی‌شدهٔ آن اجازه می‌دهد. در حال حاضر چنین نیست. |
| `copy.policy.R7.license_exceeds_service_flags` | The chosen license goes beyond what the reviewed terms of the available service(s) permit, or no approved service is available. | مجوز انتخاب‌شده فراتر از چیزی است که شرایط بازبینی‌شدهٔ سرویس(های) موجود اجازه می‌دهد، یا هیچ سرویس تأییدشده‌ای در دسترس نیست. |
| `copy.policy.R8.volunteer_optin_mismatch` | Few or no volunteers have opted in to this category now, so the quoted window may be longer. | اکنون داوطلبِ کمی (یا هیچ داوطلبی) این دسته را پذیرفته است؛ بنابراین بازهٔ اعلام‌شده ممکن است طولانی‌تر شود. |
| `copy.policy.R9.policy_version_stale` | The rules or a service's status changed after this was admitted. Work was stopped; nothing is approved retroactively. | قواعد یا وضعیت یک سرویس پس از پذیرش این کار تغییر کرد. کار متوقف شد و هیچ چیز به‌طور عطف‌به‌ماسبق مجاز نمی‌شود. |
| `copy.policy.R10.loosen_without_changelog` | A rule may be loosened only with a public change-log entry, a stated reason and the required notice. | سهل‌گیرانه‌تر کردن یک قاعده فقط با ثبت عمومی در تغییرات، ذکر دلیل و رعایت مهلت اعلام ممکن است. |

`R10` text is shown to reviewers and operators, not requesters. `R8` text is shown to requesters as a quote warning (`details.coverage`), never as a rejection. [D]

## 7.5 Job metadata schema, validation and acknowledgements

### 7.5.1 Declared fields (requester) [D]

| Field | Type | Required | Validation | On failure |
| --- | --- | --- | --- | --- |
| `purpose` | enum `P0`..`P3` | yes | S0.8.1 | `REQUIRED` / `ENUM`; at `submit`: `R1.missing_field` / `invalid_enum` |
| `license` | enum `L0`..`L3` | yes | must appear in `pairing[purpose]` (7.6.2) | `R1.pairing_inconsistent` |
| `sensitivity` | enum `S0`..`S3` | yes | S0.8.1 | `R2` after `R1` |
| `service_requirement` | enum `M0`..`M2` | yes | S0.8.1 | as above |
| `pinned_service_ids` | list of `svc_` | `M1`: 1..`policy.max_pinned_services`; otherwise empty | every id exists (`ITEM_UNKNOWN` at the API, else `R1.pinned_*`); approved-ness is `R7`, not `R1` | `R1.pinned_required` / `pinned_forbidden` / `pinned_too_many`, `R7.pinned_service_not_approved` |
| `topic_keys` | list of `TopicCategory.key` | yes, 1..8 | every key active (7.9.3); `general` is the explicit "no special topic" value | `R1.topic_unknown` / `missing_field` |
| `acks` | list of ack keys | yes (may be required to be empty only if none apply) | must contain `required_acks_for_job` (7.5.2) | `R1.ack_missing` |
| `template_version_id` | `tpv_` | yes | exists; `review_status` checked by `R4` | `R4` |
| `size_class`, `deadline_class` | enum | yes | only `standard` (S0.8.6) | `ENUM` |

No free-form requester field enters policy decisions except through the input data, which is screened (7.12). Titles and descriptions the requester writes are display text, escaped on output (S9.*), and are screened with the same rules as input. [D]

### 7.5.2 Acknowledgement keys (data in `PolicyVersion.required_acks`) [D]

| Ack key | Required when | Meaning (copy keys `copy.policy.ack.<key>` in S11.*) | FD source |
| --- | --- | --- | --- |
| `ack.declared_not_guaranteed` | always | The rules below are declared and enforced only as far as technically possible, not guaranteed | FD§5.7(2), Principle 11 |
| `ack.no_ownership_assurance` | always | The project asserts no ownership of outputs and does not promise they are protectable; volunteers waive claims | FD§5.3, Principle 6 |
| `ack.no_personal_data` | sensitivity `S0` or `S1` | No credentials, no personal data of identifiable people, nothing under confidentiality | FD§5.3 S1 |
| `ack.stranger_reads` | sensitivity `S1` | A stranger will read the input inside their own account | FD§5.3 S1 |
| `ack.open_license_reuse` | license `L1` or `L2` | Output is reusable by anyone; downstream use is uncontrolled | FD§5.7(3) |

`required_acks_for_job` is the union over the matching rows. Acks are stored with the `PolicyVersion` id and a timestamp on the job; they are declarations, not proofs. [D]

### 7.5.3 System-added fields (FD§5.2) [D]

| Field | Set by | Notes |
| --- | --- | --- |
| `template_id`, `template_version_id` | wizard | from the `TemplateVersion` |
| `content_hash` | at `job.submitted` | SHA-256 over RFC 8785 canonical JSON of the input manifest (hashes of inputs, glossary, slot values) (S0.6.4) |
| `requester_member_id` | session | internal; never shown to volunteers; provenance carries only `vol_` handles |
| `screened_policy_version_id`, `policy_version_id`, `policy_decision` | engine | 7.7 |
| `eligible_service_ids` | engine | surviving set after `R5`..`R7`; shrinks only (7.7.5) |
| `screen_status` | engine | `auto_running`, `awaiting_reviewer`, `done` (`ISS-75`) |
| `deadline` / window | S6.* | quoted window |
| `no_training`, `downstream_use_uncontrolled` | derived | `no_training = (purpose != P3)`; `downstream_use_uncontrolled = (license in L1, L2)`; carried into the provenance manifest (FD§5.6). `no_training` is contractual, not technically enforced [P] |
| `closure_reason` | S5.* | `policy_stopped`, `service_revoked`, ... (S0.9.2) |

## 7.6 Allowlist of permitted combinations

### 7.6.1 Rows (seed `PolicyVersion` 1) [D]

A row matches a tuple when each axis value is in the row's set. Status: `active` (runs), `locked` (valid but not runnable in this version; the owner rule rejects it), `rejected` (valid and never accepted; owner `R2`). The first matching row wins; rows are listed in precedence order. A tuple that matches no row is `R1.not_allowlisted` (FD§5.1: anything not explicitly allowed is rejected).

| `row_id` | `purpose` | `license` | `sensitivity` | `service_requirement` | Status | Owner rule | Tuples | Note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `A01` | `P0` | `L0` | `S0`, `S1` | `M0`, `M1` | `active` | | 1x2x2 = 4 | Phase 1 profile one (FD§5.7(5)) |
| `A02` | `P1` | `L1`, `L2` | `S0`, `S1` | `M0`, `M1` | `active` | | 2x2x2 = 8 | Phase 1 profile two; includes every Commons job |
| `X01` | any | per `pairing` | `S2`, `S3` | any | `rejected` | `R2` | n/a | Keeps `R1` from masking the `R2` reason |
| `L01` | `P2` | `L3` | `S0`, `S1` | `M0`, `M1` | `locked` | `R5` | 1x2x2 = 4 | Unlock path in 7.6.3 |
| `L02` | `P3` | `L0`, `L1`, `L2` | `S0` | `M0`, `M1`, `M2` | `locked` | `R6` | 3x1x3 = 9 | `S0` only (FD§5.3); license pairing is `ISS-73` |

Active tuples: 4 + 8 = 12. `M2` with `P0` or `P1` has no row, so it is `R1.not_allowlisted` in Phase 1; adding rows is a loosening (7.8). Combinatorial drift is bounded by design: only `A01` and `A02` are active (FD§5.7(5)). [D]

### 7.6.2 Pairing and license-required flags [D]

| `purpose` | `pairing[purpose]` (licenses) | | `license` | `license_required_flags[license]` |
| --- | --- | --- | --- | --- |
| `P0` | `L0` | | `L0` | none |
| `P1` | `L1`, `L2` | | `L1` | `open_publication_of_output` |
| `P2` | `L3` | | `L2` | `open_publication_of_output` |
| `P3` | `L0`, `L1`, `L2` [A] | | `L3` | `commercial_use_of_output` |

The training flag is required by `R6` (purpose), not by a license, so `P3` with `L1` needs `open_publication_of_output` (through `R7`) and `training_use_of_output` (through `R6`). Both must be `yes` on the same service for it to survive the sequential filters. [D]

### 7.6.3 Unlocking a locked row [D]

Two independent changes are both required: (1) a new `PolicyVersion` with the row `status` set to `active` (a loosening: 7.8, public change-log entry, notice, two approvers); (2) a service in `approved` state whose recorded flag for the purpose is `yes` with a saved `TermsCopy`. Neither alone unlocks anything, and neither is implied by the other. Outputs produced before the unlock are never re-labeled. [D]

## 7.7 Policy versioning, stamping and re-check (R9)

### 7.7.1 Stamps and what they prove [D]

| Stamp | Set when | Stored on | Meaning |
| --- | --- | --- | --- |
| `screened_policy_version_id` + `policy_decision` (stage `screen`) | `job.policy_passed` | `Job` | The version under which the input was screened and the quote computed |
| `policy_version_id` + `registry_snapshot_hash` + `eligible_service_ids` (stage `admit`) | `job.escrow_confirmed` | `Job` | The binding stamp (FD§5.4 R9, "stamped at admission"); every later check compares against it |
| `policy_checked_version_id`, `policy_checked_snapshot_hash` | after every successful `R9` run, sweep or inline | `Job` | Last version and registry state under which the job was known to pass |
| `accept_decision` | acceptance | `Cell` | The `policy_decision` of stage `accept`; kept with the provenance (FD§5.6 "policy profile and version") |

A stamp is never rewritten to look newer: re-checks add `policy_checked_*` and leave `policy_version_id` untouched, because R9 says a change "never retroactively legitimizes" work (FD§5.4). [D]

### 7.7.2 Admission (stage `admit`) [D]

1. Guard of `job.escrow_confirmed`, in the same transaction as the `escrow_hold`: run `evaluate("admit", facts, current_version)`.
2. If `current_version != screened_policy_version_id` or the registry snapshot differs from the quote's, `R9` wraps the result: a failure is reported as `policy.R9.policy_version_stale` with `details.underlying` = the specific reason (for example `policy.R7.license_exceeds_service_flags`) and `details.cause` in `policy_version_changed`, `registry_changed`, `both`.
3. On failure: `422 POLICY_REJECTED`, no escrow is posted (the guard and the hold are one transaction), the job stays `quoted` and its quote can only expire or be cancelled. The requester may create a new job pre-filled from it (S11.*).
4. On pass: the binding stamp is written, `eligible_service_ids` is replaced by the new (possibly smaller) set, and the quote is re-validated by S6.* if the set shrank (a smaller supply can lengthen the window; S6.* decides whether the quote still holds).

### 7.7.3 Procedure `stale_recheck` (R9) [D]

```
procedure stale_recheck(stage, subject):            # stage in {admit, accept}; subject = job or cell
  stamp = subject.binding_stamp                      # admit: screened stamp; accept: job.policy_version_id + snapshot
  cur   = current_version(policy_of(subject))       # read inside the deciding transaction; never from a process cache without a version check
  snap  = registry_snapshot(subject.eligible_service_ids + subject.service_id_if_any)
  cause = diff_cause(stamp.policy_version_id != cur.id, stamp.registry_snapshot_hash != hash(snap))
  if cause == none and params.policy.recheck_on_accept:   # constant true
      record(subject, fast_path=true); return pass       # nothing changed: identical inputs give an identical decision
  d = evaluate_core(stage, build_facts(stage, subject), cur)   # R1..R7 only
  if d.result == pass and stage == accept:
      if subject.service_id not in d.eligible_service_ids: return reject("service_not_eligible")
  if d.result == pass:
      subject.policy_checked_* = (cur.id, hash(snap)); narrow_eligible(subject, d.eligible_service_ids); return pass
  return reject(sub_code = d.sub_code, details = {underlying: d.reason, cause: cause})
```

`evaluate_core` is `evaluate` without `R9`, so there is no recursion. An `accept` failure is reported to the requester as `policy.R9.policy_version_stale` and to the volunteer as `reject.policy_changed` (service attested as outside the eligible set: `reject.service_not_eligible`, `ISS-76`). [D]

### 7.7.4 Acceptance (stage `accept`) [D]

Before a cell becomes `accepted` (and therefore before any `mint` or `transfer`, S6.*), `recheckAtAcceptance(cell)` runs inside the acceptance transaction. Outcome table:

| Situation | Result | Credit | Cell | Volunteer-visible reason | Trust and reliability |
| --- | --- | --- | --- | --- | --- |
| Nothing changed | pass (fast path) | as designed | `accepted` | none | normal |
| Changed, still passes, attested service still eligible | pass (full check) | as designed | `accepted` | none | normal |
| Changed and fails, job continues with other eligible services | reject | none | `rejected`, then `requeued` without incrementing `attempt` | `reject.policy_changed` | not touched (no gold/audit observation is recorded) |
| Changed and fails, job stops (`policy_stopped`, `service_revoked`) | reject | none | `voided` | `reject.policy_changed` | not touched |
| Attested service was never in the eligible set | reject | none | `rejected` (counts as an attempt) | `reject.service_not_eligible` | recorded as a check failure (S9.*) |

Why no credit: credit exists only for cells accepted under a valid policy; a ledger entry for a cell that was not accepted has no type in S0.8.5 and would be unbacked. The cost falls on the volunteer; it is limited by showing the reason, by never penalizing it, and by the rarity of tightening. An owner may prefer a goodwill mechanism; none is specified here (`ISS-76`). [D][A]

### 7.7.5 Tightening in flight: what happens to what [D]

Trigger: `policy.version_effective` of a `tighten` version, or any registry event that removes a service (7.10.5), or a `KillSwitch` on `kill.service.<svc_id>` / `kill.template.<tpl_id>` (S14.*). Immediacy is by construction: `admit`, `lease` and `accept` consult the current version inline (7.7.3); the sweep below supplies state transitions, notices and counters.

```
procedure policy_sweep(trigger):                    # idempotent; also run every policy.reconcile_interval_s
  for job in jobs where state not terminal and (policy_checked_version_id != cur.id or snapshot differs):
      if trigger.diff touches screening_rules or prohibited_categories: re-run screening on stored input (job_bound)
      d = evaluate_core("accept" if job.state in (admitted, running, suspended) else "screen", build_facts(job), cur)
      apply(job, d)                                 # table below
```

| Job state | Still passes | Passes with a smaller eligible set | Fails |
| --- | --- | --- | --- |
| `draft`, `screening` | no action | no action | evaluated at the next stage; no transition |
| `quoted`, `waitlisted` | mark checked | mark checked; S6.* re-validates the quote | `job.cancel_requested` by `system`, reason `policy_stopped`, to `cancelled`; no escrow exists, so nothing is refunded |
| `admitted`, `running`, `suspended` | mark checked | replace `eligible_service_ids`; handle cells per 7.10.5 | `job.stop_requested`, `closure_reason` = `policy_stopped`, to `settling` |

Cells of a stopped job (`policy_stopped`): [D]

| Cell state | Action |
| --- | --- |
| `queued`, `suspended` | `cell.voided` |
| `leased` | lease revoked (`lease.revoked`), then `cell.voided`; a late submission returns `reject.policy_changed` and earns nothing |
| `submitted`, `flagged_for_audit` | the `accept` re-check fails, `cell.voided` |
| `accepted` | unchanged: acceptance was valid when it happened; paid credit stays paid; an investigation that finds the original acceptance wrong goes through `Report` and a two-operator `reversal` (S6.*), never through the sweep |
| `exhausted`, `cancelled`, `voided`, `overturned` | unchanged |

After `settling`, unspent escrow is refunded by S6.*; the job ends `failed` (`job.settled_partial`) unless every cell was already accepted. Outputs of accepted cells of a job stopped for `policy_stopped` are withheld from download until a reviewer records `release_partial_deliverable` (logged `AdminAction`); the default is withheld because the tightening may concern the outputs themselves [A]. The requester sees `policy.R9.policy_version_stale` and the change-log reference. [D]

### 7.7.6 Versions in force [D]

`current_version(policy)` = the `PolicyVersion` with `status = effective` and the highest `version`. Version rows are immutable, so a process may cache a parsed version by id; it MUST re-read `Policy.current_version_id` inside every deciding transaction and compare. The version in force is recorded in every event's envelope (S0.9.1). [D]

## 7.8 Tighten immediately, loosen with change-log (R10)

### 7.8.1 Change classes [D]

| Class | Definition | Effective | Public record | Who |
| --- | --- | --- | --- | --- |
| `tighten` | Strictly narrows what is accepted or strictly strengthens a defense; widens nothing | at approval, same transaction | `ChangeLogEntry` created at once, made public within `change.tighten_publish_within_s` (86,400 s initial configurable default); detail may be delayed when disclosure would help an attacker, never the existence of the change | one admin holding `reviewer` (author counts) |
| `loosen` | Widens anything: an allowlist set, a pairing, a flag requirement removed, a prohibited category or screening rule removed or weakened, a check removed or edited | `approved_at + policy.loosen_min_notice_days * 86,400 s` (7 days initial configurable default, FD Principle 5) | public `ChangeLogEntry` with reasons in `fa` and `en`, published when approved, before the version is effective | at least `policy.loosen_min_approvers` distinct admins counting the author (2 initial configurable default), at least one holding `operator` [A] |
| `neutral` | No effect on any decision (copy text, titles, ordering of equal rules) | at approval | public entry, one line | one admin |

A version is exactly one class. A diff that contains both a tightening and a loosening is refused with sub-code `mixed_change`; the author publishes the tightening first and the loosening afterwards. [D]

### 7.8.2 Classifier `classifyChange(old, new)` [D]

The differ works structurally on the data columns of 7.2.1; the class is never typed in. Elements the differ cannot compare mechanically are classified `loosen` (the conservative direction).

| Element | Tighten when | Loosen when |
| --- | --- | --- |
| `allowlist` rows | a row `active` becomes `locked` or `rejected`; a value leaves a set of an active row; an active row is removed | a row becomes `active`; a value enters a set of an active row; an active row is added |
| `pairing` | a pair is removed | a pair is added |
| `license_required_flags` | a required flag is added | a required flag is removed |
| `required_acks` | an ack or a `required_when` condition is added or widened | one is removed or narrowed |
| `prohibited_categories` | a category is added | a category is removed |
| `screening_rules`, `output_rules` | a rule or an element of `patterns` is added; an `action` moves toward `reject` (order: `pass` < `flag_for_review` < `quarantine` < `reject`) | a rule or pattern element is removed; an action moves the other way |
| `wrapper_templates` | a `required_clauses` id is added and present in every variant | a clause id is removed, or a variant lacks a listed clause; text edits that keep all clauses are `neutral` |
| `Rule.checks`, `post_checks` | a check is added | a check is removed |
| `Rule.fail_when`, `keep_where`, `applies_when` | never (cannot be proven) | any edit |
| copy keys, titles | | (`neutral`) |

A pattern element that is edited counts as one removal plus one addition, hence `mixed_change`. Safety net: before approval the server runs the policy test table (7.13) under old and new; if any case moves from reject to pass the version cannot be `tighten` or `neutral`, and if any case moves from pass to reject it cannot be `loosen` or `neutral` (`classification_mismatch`). Only a human reviewer can fix the data, never the class. [D]

### 7.8.3 Publication procedure `publish_guard` (rule `R10`) [D]

```
procedure publish_guard(version):                    # stage publish; returns pass or reject(sub_code)
  cls = classifyChange(version.parent, version)
  if cls == mixed:                                    reject("mixed_change")
  if differential_test(version) contradicts cls:      reject("classification_mismatch")
  if version.parent != current_version:               reject("parent_not_current")
  if cls == loosen:
      if no changelog_entry or not public_ready(entry):           reject("changelog_required")
      if len(entry.reason.fa) < params.policy.loosen_reason_min_chars
         or len(entry.reason.en) < params.policy.loosen_reason_min_chars:  reject("reason_required")
      if count_distinct_admins(version.author, version.approvals) < params.policy.loosen_min_approvers
         or not any(a.role == operator): reject("approvers_insufficient")
      eff = approved_at + params.policy.loosen_min_notice_days * 86400
      if is_exact_revert(version, window=params.policy.revert_window_s): eff = approved_at   # 7.8.5
      version.effective_from = eff
  if cls == tighten:   version.effective_from = approved_at
  if cls == neutral:   version.effective_from = approved_at
  return pass
```

Sub-codes appear as `422 POLICY_REJECTED`, `details.reasons = ["policy.R10.loosen_without_changelog"]`, `details.sub_code` as above. Every approval, rejection of an approval and publication writes an `AdminAction`. Approvals by the author do not count toward the distinctness of a loosening. [D]

### 7.8.4 Version life cycle [D]

```
(none)               --policy.version_created-->    draft              copy of the effective version
draft                --policy.version_proposed-->   awaiting_approval  frozen: content_hash computed, class computed, differential test run
awaiting_approval    --policy.version_approved-->   approved           guard publish_guard passes; ChangeLogEntry linked; effective_from set
approved             --policy.version_published-->  approved           changelog.entry_published emitted (loosen: now; tighten: within change.tighten_publish_within_s)
approved             --policy.version_effective-->  effective          at effective_from; the previous effective version becomes superseded in the same transaction
draft|awaiting_approval|approved --policy.version_withdrawn--> withdrawn     any admin may withdraw a scheduled loosening; the reason is logged
```

A scheduled loosening whose `parent_version_id` is no longer the current version when its `effective_from` arrives is withdrawn automatically with reason `parent_changed` (a tightening published during the notice period always wins; the author re-derives the loosening from the new parent). [D]

### 7.8.5 Reverting a mistaken tightening, emergencies and registry changes [D]

- **Revert.** A version whose data hash equals that of the version before the latest tightening, proposed within `policy.revert_window_s` (86,400 s initial configurable default) of that tightening becoming effective, is an exact revert: notice is waived, the rest of the `loosen` requirements (public entry with reasons, two distinct admins) still apply. Without it a mistaken tightening would bind for the whole notice period.
- **Emergency.** The fast path to stop something is a kill switch (S14.*), not a policy edit; kill switches are not policy and are released by two admins (`security.two_person_actions`).
- **Registry changes are rule inputs and follow R10.** `service.approved` and `service.resumed` are loosenings: public `ChangeLogEntry` with reason at the moment of approval; no notice period [A]; approvals per `service.min_approvers`. `service.rejected`, `service.review_due`, `service.suspended`, `service.revoked` are tightenings: effective at once, public entry within `change.tighten_publish_within_s`.
- **Parameters** keep their own `owner`, `tighten_direction` and notice (S0.10.3); `policy.*` and `screen.*` parameters follow the same classes. A parameter change never edits a `PolicyVersion`.

### 7.8.6 Change-log entry content [D]

`ChangeLogEntry` (S12.* renders it): `kind` (`policy`, `service`), `subject_id` (`plv_` / `svc_`), `change_class`, `reason.fa`, `reason.en`, `diff_summary` (generated from `PolicyVersion.diff`, element names only), `effective_from`, `published_at`, `approver_handles` (admin display names chosen by the admin; no e-mail), `supersedes`. No member data is ever in an entry. [D]

## 7.9 Volunteer opt-in model (R8)

### 7.9.1 Data model [D]

One `OptIn` row per `(member_id, axis, value)`; `axis` in `purpose`, `license`, `sensitivity`, `service_requirement`, `topic`, `service`. Fields: `state` (`granted`, `revoked`), `source` (`default`, `member`), `changed_at`, `row_version`. `service` rows hold the `svc_` ids the member declares they can use; the declaration is attested, never verified, and no credential or session of any service is ever stored (ground rule 3). Every change emits `member.optin_changed` (no history table). A member may revoke any opt-in at any time with no effect on credit or trust (FD§5.5). [D]

### 7.9.2 Defaults and materialization [D]

| Axis | Granted at member creation | Source parameter | FD |
| --- | --- | --- | --- |
| `purpose` | `P0`, `P1` | `optin.default_purposes` | FD§5.4 R8 |
| `sensitivity` | `S0`, `S1` | `optin.default_sensitivities` | FD§5.4 R8 |
| `license` | `L0`, `L1`, `L2` [A] | `optin.default_licenses` | |
| `service_requirement` | `M0`, `M1`, `M2` [A] | `optin.default_service_requirements` | |
| `topic` | every `TopicCategory` with `is_sensitive = false` | `optin.sensitive_topics_default` = false (constant) | FD§5.4 R8 |
| `service` | none; the member declares the services they use | | |

Defaults are copied into explicit rows at `member.created`; later edits of the defaults affect only members created afterwards. This is why a loosening of a default can never silently widen anyone's consent. [D]

**Granting a non-default value** (a `purpose`, `license` or `sensitivity` outside the defaults, or a sensitive `topic`) requires an explicit acknowledgement with the full-text notice for that category (`copy.optin.<axis>.<value>.notice`, S11.*) stored as the `source` = `member` row with the notice version. **Grantable values** are only those that appear in some `active` allowlist row of the current version (`S2`/`S3` are never grantable; `P2`, `P3`, `L3` become grantable only after an unlock, 7.6.3). Revocation is always allowed. [D]

### 7.9.3 Topic categories (data) [D][A]

`TopicCategory`: `key` (natural, `^[a-z][a-z0-9_]{1,31}$`), `title_key`, `is_sensitive`, `status` (`active`, `retired`), `hint_patterns` (alternatives, same format as screening rules, group `topic`), `introduced_in_version`. Editing is a reviewer action in `optin.*` / `policy` ownership (S0.10.5); adding a sensitive category is a tightening for volunteers (opt-in required), removing one is a loosening. The initial set is a starting proposal for reviewers, not a taxonomy claim:

| `key` | `is_sensitive` | Intent |
| --- | --- | --- |
| `general` | false | no special topic |
| `education_study` | false | coursework, study material |
| `science_technology` | false | science and technology texts |
| `software_code` | false | code, documentation |
| `language_literature` | false | linguistic and literary material |
| `business_admin` | false | non-confidential routine business text |
| `health_medical_public` | true | public health information (never personal health data, which is `S3`) |
| `politics_current_affairs` | true | politics and current affairs; framing stays on knowledge access (FD§6.1 rank 2) |
| `religion_belief` | true | religious and belief material |
| `law_regulation` | true | legal and regulatory text (never privileged material, which is `S3`) |
| `adult_mature_themes` | true | mature but lawful themes |
| `violence_conflict` | true | conflict, violence, war reporting |

A job carries the union of: topics the requester declares, the template's default topics (`job_type`), and categories a reviewer adds during screening or that match `hint_patterns` (the latter only as a `flag_for_review` finding that prompts the reviewer to add the category). Categories are only ever added after submission, never removed. Every `Cell` copies `topic_keys` at creation; `gold`, `audit`, `third`, `review` and `rework` cells inherit purpose, license, sensitivity, service requirement, eligible set and topics of the cell they accompany, so that a volunteer cannot tell them apart by policy tuple and R8 holds for them too (requirement on S8.*). [D]

### 7.9.4 How R8 filters cells [D]

```sql
-- visibleCellsFilter(v): the candidate list; stage lease re-runs R8 and R9 fast path on the chosen cell
SELECT c.id
FROM cells c JOIN jobs j ON j.id = c.job_id
WHERE c.state = 'queued' AND j.state IN ('admitted','running')
  AND j.purpose              = ANY(:v_purposes)
  AND j.license              = ANY(:v_licenses)
  AND j.sensitivity          = ANY(:v_sensitivities)
  AND j.service_requirement  = ANY(:v_service_requirements)
  AND j.eligible_service_ids && :v_declared_service_ids      -- at least one service the member declared
  AND c.topic_keys          <@ :v_topics;                    -- every topic of the cell is opted in
```

The SQL is an index-friendly prefilter only; the authority is the evaluator at stage `lease` (the same `R8` rows) plus the staleness check of 7.7.3, run when the lease is issued. A cell that fails R8 at lease time is answered `404 NOT_FOUND`. The service the member will use is chosen from `eligible_service_ids ∩ declared services` and is recorded on the lease; a different service cannot be attested at submission (S9.*). [D]

### 7.9.5 Per-category supply gauge [D]

```
function supplyGauge(tuple t):                        # t = (purpose, license, sensitivity, service_requirement, eligible_service_ids, topic_keys)
  D   = { m in active_volunteers(window = params.admission.active_donor_window_days) where R8(t, optins(m)) passes }
  est = sum(throughput_estimate(m) for m in D)        # cells per day; formula owned by S6.*
  for axis in axes: D_wo[axis] = { m active where R8 passes ignoring the checks of that axis }
  bottleneck = argmax over axis of |D_wo[axis]| - |D|  # the axis whose relaxation would add most volunteers
  return { covered_donors: |D|, est_cells_per_day: est, bottleneck_axis: bottleneck }
```

- The gauge is computed per distinct tuple at job screening, at quote time and at each `metrics.rollup_interval_s`; the per-member list is never exposed. Public and requester views show a band (`none`, `fewer_than_k`, `ok`) using `analytics.min_cohort_k`; the Operator dashboard shows exact counts and the bottleneck axis. Metric: `hamyar_policy_category_supply_donors` (labels: axis, value). [D]
- **Feeding the quote.** S6.* uses `capacity_t = min(global_capacity, est_cells_per_day * window_days)` for the tuple; `covered_donors = 0` yields `422 NO_CAPACITY` with `details.reasons = ["policy.R8.volunteer_optin_mismatch"]` and the bottleneck axis. A tuple with low coverage lengthens the quoted window instead of failing (FD§5.7(8)). [D]
- **Fragmentation guard.** The Operator dashboard shows the weekly share of active volunteers that have revoked each default axis value; a drop is an input to `P1M` measures (decline and opt-out rates by category, FD§9). [H] Opt-out fragmentation starves some categories; tested by that share and by quote-versus-actual windows; kill criterion set in the pre-registration (S13.*).
