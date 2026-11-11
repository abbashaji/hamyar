# 8. Templates and verification pipeline: verification (part 8b)

*Spec part 8b · file `spec/08b-verification.md` · provenance: cell C-009 · binding on every part that creates, checks, pays or measures cells. Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0). Nothing here is legal advice; nothing is verified against any provider's terms. Every number is derived by a shown formula or is an `initial configurable default` that exists in the parameter table (S0.10.6) or in 8.37.*

## 8.20 Scope, boundaries and what this part reads

This file is the second half of S8. The template half owns the template format, the first template set and template review. **This half owns what happens to a cell's result after it is pasted back:** the order of checks, gold cells, audits, redundancy, human review, the reliability estimator, adaptive sampling, the error-rate estimators, counting into v, payment, rejection reasons, appeals handoff, the human-review channel and the ban on model-based judging. Sub-headings start at `8.20` so they cannot collide with the template half (`ISS-84`). [D]

| Prompt scope E bullet | Where it is specified |
| --- | --- |
| Automatic checks | 8.22, 8.23 |
| Hidden gold cells: rate g, insertion, reliability | 8.24, 8.28 |
| Sampled audits: rate s, comparator, third execution | 8.25 |
| Adaptive sampling with a floor | 8.29 |
| Blanket redundancy for new donors and high-risk templates | 8.26 |
| Human review cells with their own gold cells | 8.27 |
| Appeals | 8.34 |
| Estimation of donor reliability, false-accept and false-reject rates, with limits | 8.28, 8.30, 8.40 |
| v and rework counting, payment, rejection reasons, channel 2, no model judging | 8.31, 8.32, 8.33, 8.35, 8.36 |

**Boundaries.** [D]

- Lease, nonce, size limit, schema validation, escaping, replay handling, and the detectors for timing anomalies and copy-paste of another donor's output are S9.*. This part consumes their signals (8.23) and decides what an anomaly causes.
- Ledger postings (`mint`, `transfer`, `reversal`), escrow and settlement are S6.*. This part states which cell earns what and when it is accepted; S6.* posts it.
- Policy rules `R1`..`R10` are S7.*. This part only places the `R9` re-check in the order (8.22).
- Appeal states and the review UI are S10.* and S11.*. This part defines the evidence and the effects (8.34).
- Ground rule 3 applies: nothing here reads a volunteer's chat page, stores a credential or session, or submits for a volunteer. The service and model of a result are **attested by the volunteer, never proven**; verification treats them as audit metadata only. [P] FD§5.6

**Fields this part reads from `TemplateVersion`** (the template half owns the format; the object below is embedded under the key `verification`; a different shape is reconciled at assembly, `ISS-84`). [A]

| Field | Type | Meaning |
| --- | --- | --- |
| `verification.risk_class` | enum `standard`, `high` | `high` forces blanket redundancy (8.26). Set by a reviewer at approval; none is `high` by default in Phase 1 (`ISS-85`) |
| `verification.comparator` | id + version | Deterministic comparator for audits and gold (8.25) |
| `verification.subjective` | bool | True when no comparator can decide equivalence; audits become human review (8.27) |
| `verification.auto_checks` | list of ids | Automatic checks in order, each with a reason code (8.23) |
| `verification.gold_pool_min` | int | Minimum number of active gold items before the template may be leased (8.24) |

## 8.21 Vocabulary and definitions [D]

| Term | Definition |
| --- | --- |
| Acceptable output | An output that passes the template's automatic checks and is equivalent to the reference or to the majority under the template's comparator. "Bad" is relative to the template's declared checks, never to absolute truth (limit 8.40-L11) |
| Observation | One pass or fail about one executor, produced by a gold result, a resolved audit or redundancy group, or an accepted review verdict. Inconclusive outcomes are not observations |
| Scope | `exec` (executing cells) or `review` (human-review cells). Reliability, adaptive state and restriction are kept per scope |
| Selection | How a verification event was triggered: `random` (a CSPRNG draw), `forced` (an anomaly or a rule), `blanket` (a redundancy plan). Only `random` events enter the false-accept estimators |
| Inclusion probability `pi` | The probability, in ppm, that this cell was selected for the random audit draw, recorded at draw time |
| Floor band | The part of the draw range `[0, floor)`; events in it are always executed |
| Verification cell | A cell with `cell_kind` in `gold`, `audit`, `third`, `review`, `rework` (S0.8.6) |
| Sponsor job | The job whose pool pays for a gold instance placed into one of its lease slots (8.24) |
| False-accept | An accepted primary cell whose output is bad under the definition above. Rate = bad accepted cells / accepted primary cells |
| False-reject | A good submission that the pipeline rejected. Rate = good submissions rejected / good submissions |

Constants used from S0: `credit.scale_ucr_per_credit` = 1,000,000; ratios are integer ppm; donor earn is exactly 1,000,000 `ucr` per accepted cell of any kind (S0.6.1). Verification stores `*_ppm` integers; floating point appears only inside the Beta quantile (8.28) and is rounded as stated there. [D]

## 8.22 Pipeline order, pseudocode and state transitions

### 8.22.1 Order [D]

| Stage | Name | Owner | Failure result |
| --- | --- | --- | --- |
| P0 | Intake: lease, nonce, size, schema, escaping, replay | S9.* | `submission.schema_failed`; reasons `reject.nonce_invalid`, `reject.lease_expired`, `reject.size_exceeded`, `reject.schema_invalid` |
| P1 | Automatic checks (template list) | 8.23 | `submission.checks_failed`; reason from the failing check |
| P1b | Quarantine screen (links, code to run, requests for action) | S9.* | `submission.quarantined`: no acceptance, no payment, no observation until released |
| P2 | Anomaly intake (timing, duplicate of another donor's output) | S9.* detect, 8.23 decide | `forced` audit, or rejection if S9.* rules say so |
| P3 | Kind dispatch | 8.22.2 | per kind |
| P4 | Verification plan for primary and rework cells: blanket, forced audit, random audit or human review, or none | 8.25, 8.26, 8.27 | `cell.flagged_for_audit` |
| P5 | Policy re-check `R9` (`policy.recheck_on_accept` = true) | S7.* | `cell.voided` with reason `reject.policy_changed`; no payment is posted by this part |
| P6 | Acceptance and payout request to S6.* | S6.* | `cell.checks_passed` or `cell.audit_passed` |

Stages never run out of order and a later stage never overrides an earlier failure: a model verdict, a review verdict or an audit match cannot accept a cell that failed P0, P1 or P1b. [D]

### 8.22.2 Pseudocode

```
function verify_submission(sub):                 # called once per Submission in state checks_passed (P0 done)
  cel = cell_of(sub); tv = template_version_of(cel)
  res = run_auto_checks(sub, tv.verification.auto_checks)           # P1, deterministic, no execution of content
  if res.failed:
      record(sub, method=auto_check, outcome=fail, reason=res.reason, selection=none)
      if cel.kind == gold: record_observation(executor(sub), scope(cel), FAIL, source=gold)   # 8.24
      return reject(cel, res.reason)
  record(sub, method=auto_check, outcome=pass)
  if quarantine_screen(sub): return hold_quarantined(sub)                                    # P1b
  anomalies = s9_anomaly_signals(sub)                                                        # P2
  if anomalies.reject: return reject(cel, anomalies.reason)
  switch cel.kind:                                                                           # P3
    case gold:               return resolve_gold(sub)                                        # 8.24
    case audit, third:       return add_execution_to_group(sub)                              # 8.25, 8.26
    case review:             return accept_review_cell(sub)                                  # 8.27
    case primary, rework:    plan = choose_plan(sub, anomalies)                              # P4
  if plan.kind == NONE:      return accept(cel)                                              # P5, P6
  open_group(cel, plan)                                                                      # Audit row, verification cells created
  emit cell.flagged_for_audit(cel, reason = plan.reason)

function choose_plan(sub, anomalies):
  m = executor(sub); tv = template_version_of(cell_of(sub))
  if blanket_required(m, tv, cell_of(sub)):  return Plan(BLANKET, n = verify.blanket_redundancy_n, reason = blanket_redundancy_pending)
  if anomalies.force_audit:                  return Plan(AUDIT, selection = forced, reason = anomaly)
  (pi, in_floor_band_only) = inclusion_probability(m, cell_of(sub))                          # 8.29
  u = csprng_uniform_ppm()                  # integer in [0, 1_000_000), fresh per submission
  if u < pi:
      return Plan(tv.verification.subjective ? HUMAN_REVIEW : AUDIT, selection = random, pi_ppm = pi, reason = sampled)
  return Plan(NONE)

function blanket_required(m, tv, cel):
  return member_state(m, exec).blanket_remaining > 0          # new donor's first verify.new_donor_blanket_cells cells
      or tv.verification.risk_class == high
      or (cel.kind == rework and cel.overturn_reason == integrity)
```

The draw `u` is made only after P1 to P2 passed, uses the server CSPRNG, and its value and `pi_ppm` are stored on the `Audit` or `VerificationRecord` (`selection`, `inclusion_prob_ppm`). A cell that is not selected stores `selection = random`, `outcome = pass` for the `auto_check` record only, and its `pi` is kept in `cell_sampling_log` (a column pair on the cell, `sampling_pi_ppm`, `sampling_draw_ppm`) so the false-accept estimator can weight it (8.30). [D][A]

### 8.22.3 Cell transitions used (S0.9.3 names, no new states)

| From | Event | To | Condition |
| --- | --- | --- | --- |
| `submitted` | `cell.checks_failed` | `rejected` | P1 or P2 rejection, or a gold fail |
| `submitted` | `cell.checks_passed` | `accepted` | plan NONE; or a gold pass; or an accepted verification cell that needs no group |
| `submitted` | `cell.flagged_for_audit` | `flagged_for_audit` | plan AUDIT, HUMAN_REVIEW or BLANKET; reason one of `sampled`, `anomaly`, `blanket_redundancy_pending` |
| `flagged_for_audit` | `cell.audit_passed` | `accepted` | primary is in the majority, or the audit matched, or the audit slot was exhausted for reason `sampled` (outcome `inconclusive`, recorded as `audit_coverage_gap`) |
| `flagged_for_audit` | `cell.audit_failed` | `rejected` | primary in the minority, or no majority (8.25) |
| `rejected` | `cell.requeued` | `queued` | primary or rework cell, `attempt` below `cell.max_attempts`, or a verification cell rejected by P1 (the slot stays open) |
| `rejected` | `cell.attempts_exhausted` | `exhausted` | attempts spent; **also** every verification cell rejected on content (`reject.gold_mismatch`, `reject.audit_mismatch`, `reject.review_unacceptable`): its single attempt is used up [A] |

A `gold` instance has an attempt limit of 1, an exception to `cell.max_attempts` stated here (`ISS-84`). A gold cell whose lease expires returns to the pool as a new instance for another member. A cell stuck in `flagged_for_audit` for a reason other than `sampled` is never released without a verdict: after `job.max_overrun_ratio` pressure it goes to an operator queue (S14.*), not to `accepted`. [D]

## 8.23 Automatic checks and anomaly intake [D]

Automatic checks are the cheapest stage (FD§4.4 step 1). The template half defines each check; this part fixes the contract.

- A check is a pure, deterministic function `check(output, input, ctx) -> pass | fail(reason_code)`. It never executes submitted content, never calls a model, never fetches a URL. A check that needs execution of submitted code is not allowed in Phase 1 (S9.*); such a template uses parse-level checks only. [D]
- Checks run in the template's order and stop at the first failure. The failing check's `reason_code` maps to a donor-visible reason (8.33). Standard checks: schema validity, length bounds (`cell.envelope.max_output_chars`), language, refusal-pattern detection, format validator, forbidden content.
- Automatic-check failures on organic cells are **not** reliability observations (they are a gate, not a quality sample) but are counted per member in `auto_fail_rate` for support and S9.* abuse tooling. On gold cells they are fails (8.24). [D]

**Anomaly signals consumed from S9.*** (S9.* owns detection and thresholds `verify.timing_min_s`, `verify.duplicate_similarity_threshold`):

| Signal | Meaning | Default action here | Reliability effect |
| --- | --- | --- | --- |
| `timing_below_min` | `submitted_at - leased_at < verify.timing_min_s` | `force_audit` | step-up of the adaptive factor (8.29) |
| `duplicate_of_other_output` | similarity to another member's output ≥ `verify.duplicate_similarity_threshold` | `force_audit`; S9.* may instead reject with `reject.duplicate_of_other_output` | step-up; a rejection counts as one fail with `source = anomaly` |
| `forgery_finding` | S9.* integrity finding | S9.* voids or restricts | `member.restricted` (S10.*, S9.*) |

In every case an anomaly overrides the random draw (`selection = forced`) and **cannot lower** any sampling rate. A `forced` audit that passes is an exonerating observation for the member (counted); it is excluded from the false-accept estimators because selection by suspicion is not random (8.30). [D]

## 8.24 Gold cells

### 8.24.1 The library [D]

`GoldCell` (`gld_`, permanent, S0.7) is a known-answer item. Its reference answer is access-restricted: readable only by the verification worker (`system`) and by reviewers holding `perm.verify.read_gold` (S10.* assigns it; name registered in `ISS-84`).

| Field | Rule |
| --- | --- |
| `status` | `draft`, `active`, `quarantined`, `retired` (machine below) |
| `job_type`, `template_id` | An item belongs to one template; a primary-execution item and a review item are separate (`gold_kind`: `exec`, `review`) |
| `input_ref`, `reference_ref` | Input and reference stored as content-hashed blobs; the reference is never sent to any member |
| `reference_source` | `reviewer_authored`, `deterministic` (a validator or checker defines correctness), `reviewer_approved_consensus` (a majority output a reviewer approved). Consensus without reviewer approval is never a reference: correlated model error would become "truth" (limit 8.40-L6) |
| `polarity` | Review items only: `acceptable` or `unacceptable`, the known verdict |
| `source_license_ref` | The license record of the source text. Input must be `S0` and its license must allow display under any card face it can be attached to [V: reviewer records the license per item] |
| `exposure_count`, `activated_at`, `retired_at`, `leak_flag` | Maintained by 8.24.4 |

```
(none)       --gold_cell.drafted-->      draft
draft        --gold_cell.activated-->    active        guard: approved by a reviewer who is not the author; pool rules pass
active       --gold_cell.quarantined-->  quarantined    leak signal (8.24.5), a defect found on appeal, or a manual flag
quarantined  --gold_cell.reactivated-->  active        guard: reviewer clears it, new `activated_at`
active|quarantined --gold_cell.retired--> retired (T)  exposure cap reached or manual
```

A template may be leased to members only while its active gold pool holds at least `verification.gold_pool_min` items; below that the template is paused for new cells (`template.paused`, kill-switch path S14.*) and an alarm is raised. This keeps gold detectability and rates from degrading silently. [D]

### 8.24.2 Insertion: substitution at lease time [D]

Gold is inserted when a member leases a cell. The member picks a card; the server decides, per lease, whether the lease is a gold instance of the **same template**. The real cell the member picked stays `queued`.

```
function lease_cell(member, selected_cell):              # inside the lease transaction, idempotent per Idempotency-Key
  g = gold_rate_ppm(member, scope_of(selected_cell))      # 8.29
  u = csprng_uniform_ppm()                                # fresh draw, separate from any audit draw
  if u >= g: return create_lease(selected_cell)
  if u >= verify.gold_rate_floor_ppm and sponsor_budget_exhausted(selected_cell.job): return create_lease(selected_cell)  # extras only
  item = pick_gold_item(selected_cell.template_version, member)
  if item is None: alarm(gold_pool_empty, template); return create_lease(selected_cell)
  inst = new_cell(kind = gold, gold_cell_id = item.id, job = selected_cell.job, template_version = selected_cell.template_version)
  return create_lease(inst)                               # the same card face, envelope and lease timeout as a real cell

function pick_gold_item(tv, member):
  eligible = items where status = active and template matches and exposure_count < verify.gold_max_exposures
                   and member has no lease ever for the item and the member's opt-ins (R8) cover the item's metadata
  return uniform_random(eligible)
```

- `g` is a share of **leases**, so gold cells per primary cell are `g / (1 - g)` (used in 8.31). [D]
- The decision is stored with the lease; a replay of the same request returns the same cell, so repeating a request cannot re-roll the draw. [D]
- **Sponsor job.** A gold instance belongs to the job whose slot it takes; that job's verification pool pays for it (8.32). The card face (purpose, license, sensitivity, service, template, expected time, provenance sentence) is rendered from the sponsor job, and the gold input is `S0` with a compatible license (8.24.1), so no field on the card is false. The general volunteer notice says that some cells are hidden reference checks and that the volunteer cannot tell which (copy `copy.verify.hidden_checks_notice`, S11.*, `needs_human_and_legal_review`). [D]
- Unique exposure is enforced by a partial unique index `ux_leases_member_gold` on `leases (member_id, gold_cell_id) WHERE gold_cell_id IS NOT NULL` (column added to `Lease`, `ISS-84`). An exposure counts when the lease is issued, whether or not the member submits. [D]

### 8.24.3 How gold stays hidden [D]

1. No member-facing response, event or log field contains `cell_kind`, `gold_cell_id`, `audit_id` or `selection` for a cell that is unresolved. After resolution a member sees only the outcome and the reason code. S15.* schemas for gold and organic cells are identical (`AC-verify-03`).
2. Same template, envelope, lease timeout, card layout, copy and latency class. Server-side branches that differ by kind must not change response size by more than the natural variation of the template [H: measured in `TEC`].
3. The gold reference, comparator output and sponsor linkage are visible only to the roles in 8.24.1 and to an appeal reviewer for that appeal (8.34).
4. **Published rates, hidden instances.** `verify.gold_rate_g`, the floors and the formulas are public (FD Principle 5); which lease is gold is not.
5. A donor whose gold cell fails sees `reject.gold_mismatch` and so learns that this one cell was a reference check. That cost is accepted because FD§4.4 requires donors to see why (`ISS-86`); the item is burned for that member, the reference is never shown, and failures feed leak detection (8.24.5).

### 8.24.4 Rotation and retirement [D]

- Each item is retired when `exposure_count` reaches `verify.gold_max_exposures` (initial configurable default 20, 8.37). Each member sees an item at most once, ever.
- Retirement rate (items per day) = `g x cells_per_day / verify.gold_max_exposures`. Illustrative inputs from the FD§3.3 example (40 donors x 8 cells a day = 320 cells a day, g = 0.05): 16 gold exposures a day and 0.8 items retired a day, about 24 a month per 320 cells a day. The library must be fed at this rate or the template pauses (8.24.1). These are not measurements.
- `gold_pool_low` alarm when the active pool of a template covers fewer than 7 days of the current retirement rate (derived: 7 x rate; 7 is the `admission.active_donor_window_days` default reused as a look-ahead).
- Reference answers are authored or approved by reviewers (a cost counted in `OPS`); a donor's result is never promoted to a reference without reviewer approval.

### 8.24.5 Leak detection [D][H]

A gold item is "leaked" when its answer circulates or its identity is recognizable. Signals are computed per item over its last `verify.gold_max_exposures` exposures and per template over the window `price.v_window_days`; each is a one-sided test at significance `verify.gold_leak_alpha` (initial configurable default 0.01, 8.37).

| Signal | Test | Reading |
| --- | --- | --- |
| L1 pass-rate drift | Fisher exact test, later half of the item's exposures against the earlier half | Rising pass rate on one item |
| L2 gold versus organic | Two-proportion test: gold pass rate against the random-audit agreement rate of the same template (8.30) | Gold passes more than organic work: gold is easier, recognizable or leaked |
| L3 timing | Median `elapsed_s` of the item's exposures against the template median (rank test) | Answers produced faster than the template allows |
| L4 near-duplicate cluster | Two or more exposures from different invite trees whose outputs meet `verify.duplicate_similarity_threshold` where the comparator does not predict identical outputs | Answer text is being shared |
| L5 decline asymmetry | Decline-or-expiry rate of gold leases against organic leases of the same template (two-proportion test) | Donors recognize gold and avoid it |
| L6 report | A donor, reviewer or operator flags the item | Manual |

On any signal the item goes `quarantined`; no new exposures. Observations that members produced on the item **after the earliest exposure inside the suspect window** are flagged `suspect = true` and removed from every estimator in both directions (no penalty, no credit); payments already made are not reversed. A quarantined item returns to `active` only by reviewer decision with a new `activated_at`. Signals are triage, not proof: tests are not corrected for multiple comparisons and will raise false alarms at roughly `verify.gold_leak_alpha` per test [H]. L2 doubles as the **gold-detectability diagnostic** reported in 8.30.

### 8.24.6 Resolving a gold submission [D]

```
function resolve_gold(sub):
  cel = cell_of(sub); item = gold_item_of(cel)
  verdict = comparator(item.tv.verification.comparator)(sub.output, item.reference)         # deterministic
  if verdict == match:  record(sub, gold, pass);  record_observation(m, scope, PASS, gold);  accept(cel)          # paid 1 credit
  else:                 record(sub, gold, fail, reason=reject.gold_mismatch);  record_observation(m, scope, FAIL, gold)
                        reject(cel, reject.gold_mismatch); consecutive_gold_fails(m) += 1
                        maybe_enqueue_adjudication(sub)                                    # 8.30.3
  if consecutive_gold_fails(m, scope) >= trust.restrict_after_gold_fails: emit member.restricted     # 8.28.4
```

`inconclusive` from a gold comparator is a defect of the item: it is not an observation, the donor is paid, and the item is quarantined. A passing gold cell resets `consecutive_gold_fails`. [D]

## 8.25 Sampled audits, comparator and third execution

### 8.25.1 Comparator contract [D]

`comparator(a, b, ctx) -> match | mismatch | inconclusive`, declared by `TemplateVersion.verification.comparator` and versioned with it. Requirements, each a property test (layer `prop`): deterministic; symmetric (`comparator(a,b) = comparator(b,a)`); reflexive on valid outputs; side-effect free; no execution of content; **no model call and no network access** (8.36). The comparator version is stored on every `VerificationRecord` so a later comparator change never rewrites an old outcome. A comparator that returns `inconclusive` is treated as `mismatch` for the purpose of requesting a third execution. [D]

### 8.25.2 Audit flow [D]

`Audit` states and events are those of S0.9.8; this table gives the transitions.

| From | Event | To | Guard and effect |
| --- | --- | --- | --- |
| (none) | `audit.created` | `pending` | Plan AUDIT chosen (8.22.2). A cell of kind `audit` with the **same input** is created for a different member. The auditor never sees the primary output |
| `pending` | `audit.second_submitted` | `second_executed` | The audit cell passed P1 to P2 |
| `second_executed` | `audit.matched` | `matched` (T) | comparator = `match`: primary `cell.audit_passed`; audit cell accepted; both executors get a PASS observation |
| `second_executed` | `audit.mismatched` | `mismatched` | comparator = `mismatch` or `inconclusive` |
| `mismatched` | `audit.third_requested` | `third_pending` | `verify.third_exec_on_mismatch` = true (constant): a cell of kind `third`, same input, a third member |
| `third_pending` | `audit.third_submitted` | `third_pending` | Informational, no state change (S0.9.1 allows an event without a change) |
| `third_pending` | `audit.resolved` | `resolved` (T) | Majority rule below |
| any non-terminal | `audit.cancelled` | `cancelled` (T) | Job cancelled, cell voided, template paused, or a verification slot exhausted `cell.max_attempts` |

**Majority rule (also used for blanket groups, 8.26).** Let the executions that passed P1 be the nodes of an agreement graph, with an edge where the comparator returns `match`. The majority is the **unique maximum clique** whose size is at least `floor(n / 2) + 1`; a tie between cliques, or no such clique, is `NO_MAJORITY`. [D]

```
function resolve_group(execs):                    # n = len(execs), n in 2..verify.blanket_redundancy_n (at most 5)
  G = agreement_graph(execs); need = floor(n/2) + 1
  C = maximum_cliques(G)                          # brute force is enough for n <= 5
  if len(C) == 1 and len(C[0]) >= need: return MAJORITY(C[0], minority = execs - C[0])
  return NO_MAJORITY
```

| Result | Primary cell | Executors in the majority | Executors in the minority | Observations |
| --- | --- | --- | --- | --- |
| Primary in majority | `cell.audit_passed`, accepted, its output is delivered | accepted, paid 1 credit each | rejected `reject.audit_mismatch`, unpaid, single attempt used up (`exhausted`) | majority PASS, minority FAIL |
| Primary in minority | `cell.audit_failed`, rejected with `reject.audit_mismatch`, then requeued as a fresh attempt | accepted, paid; their outputs are **not** reused for the requeued attempt [A] | rejected as above | same |
| `NO_MAJORITY` | `cell.audit_failed`, rejected with `reject.audit_mismatch` and `details.inconclusive = true`; requeued; appealable | every execution that passed P1 is accepted and paid (nobody was outvoted) | none | **none**: inconclusive is not an observation |
| Slot exhausted | `cell.audit_passed` with outcome `inconclusive` and `audit_coverage_gap` if the reason was `sampled`; otherwise held for an operator (8.22.3) | executions that passed P1 are paid | none | none |

Reusing a majority pair's output for the requeued primary would save one attempt but needs a Cell transition that S0.9.3 does not define; it is not specified [A]. Cost of the waste is visible in v (8.31). [D]

### 8.25.3 Auditor assignment [D]

An audit, third or blanket copy is assigned only to a member who: has `status` `active` and tier other than `restricted`; is not the executor of any earlier execution of this cell; is not in the same invite tree or device group as any earlier executor or, for a member job, as the requester; has opt-ins covering the cell (R8); and, when the pool allows, has tier `established` or `trusted`. If no such member exists the assignment falls back to any active non-restricted member meeting the other conditions and the metric `hamyar_verify_1_degraded_auditor_pool_total` counts it (name per S0.5 scheme). Where opt-ins allow, copies prefer different **attested** services; diversity lowers correlated error but raises benign mismatches [H]. [D][A]

## 8.26 Blanket redundancy

Blanket redundancy executes **every** copy up front, in parallel, instead of sampling (FD§4.4: triple redundancy only for new donors' first cells and high-risk templates). [D]

| Trigger | Rule |
| --- | --- |
| New executor | The first `verify.new_donor_blanket_cells` (default 5) primary cells that a member submits in scope `exec` are executed as blanket groups. A counter `blanket_remaining` starts at that value in `member_state(m, exec)` and decreases when the group resolves or is cancelled by a content verdict; a lost lease does not consume it |
| High-risk template | `TemplateVersion.verification.risk_class = high`: every primary cell of the template |
| Integrity rework | A `rework` cell whose overturned cell had `overturn_reason = integrity` |
| New reviewer | The first `verify.new_donor_blanket_cells` review cells of a member in scope `review` (8.27) |

- Group size `n = verify.blanket_redundancy_n` (default 3). Copy 2 is a cell of kind `audit`, copies 3..n are kind `third`; every copy's `verification_method` is `blanket_redundancy`. The group is resolved by `resolve_group` (8.25.2) once at least `floor(n/2) + 1` executions passed P1; remaining outstanding copies are cancelled and are not paid. [D]
- A blanket group **replaces** the random audit draw for that cell. The primary stays `flagged_for_audit` with reason `blanket_redundancy_pending` until it resolves. [D]
- Assignment follows 8.25.3, and at least `n - 1` copies go to members of tier `established` or `trusted` when available, so new executors do not mainly verify each other. [D][A]
- **Cost.** A blanket group adds `n - 1` paid verification cells per accepted primary. Expected cost share is in 8.31; blanket redundancy on a whole template makes `v >= n - 1 = 2.0` for that template, which `price.v_cap` (0.50) cannot price (`ISS-85`). No template is `high` by default in Phase 1 [A]. The new-executor rule costs `(n - 1) x verify.new_donor_blanket_cells` verification cells per new donor, charged to the jobs those cells belong to.

## 8.27 Human review cells and their own gold cells

Human review is the verification method for subjective templates (`verification.subjective = true`), where no comparator can decide equivalence, and the unit of work of channel 2 (8.35). [D]

**Review cell (`cell_kind` = `review`).** The reviewer sees the template's input, one candidate output, and a fixed rubric; there is no executor identity, service or other verdict on screen. The verdict is `acceptable` or `unacceptable` plus one reason code from the rubric's closed list. **No free text** is accepted (it could carry instructions, personal data or links). Candidate outputs that were quarantined or flagged are never shown to reviewers. [D]

**Flow for a subjective primary cell** (plan HUMAN_REVIEW, chosen by the random draw at the review sampling rate of 8.29, or forced): an `Audit` row with `verification_method = human_review` is created.

| Step | Rule |
| --- | --- |
| R1 | One review cell. `acceptable` = `audit.matched` (the primary is accepted) |
| R2 | `unacceptable` = `audit.mismatched`; a second review cell is created (`audit.third_requested`) |
| R3 | If R1 and R2 disagree, a third review cell is created; majority of the three decides. Two `unacceptable` verdicts reject the primary with `reject.review_unacceptable` |
| Pay | A review cell is accepted and paid when it passes its own checks (closed codes valid, not a gold mismatch) and is not outvoted; outvoted reviewers are rejected unpaid |
| Observation | Reviewer verdict agreement is a reviewer observation in scope `review`. A verdict about a donor's output is a donor observation (source `review`) **only** when the review cell is accepted and the verdict is determinate |

**Review gold.** A separate library (`gold_kind = review`) of candidate outputs with a known verdict. The substitution rule of 8.24.2 applies to review leases with the rate `verify.human_review_gold_rate` (default 0.10) clamped by the same floor and maximum as `g`. The library must keep both polarities: each polarity is at least `verify.review_gold_min_polarity_share` (initial configurable default 0.40, 8.37) of the active review gold, so a reviewer who always answers `acceptable` or always `unacceptable` fails about that share of gold and cannot coast. A review gold fail is `reject.gold_mismatch`; two consecutive review gold fails suspend review eligibility, not the member tier (8.35). [D]

**Subjective templates and audits.** For a subjective template the sampled audit slot is a review panel (R1 to R3), never a comparator audit, so `verification.subjective = true` and a comparator are mutually exclusive in the template half's validation (`ISS-84`). [D]
