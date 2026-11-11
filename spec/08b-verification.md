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
