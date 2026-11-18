# FINAL-2a: re-audit round 2, slice A (FIX-01 to FIX-09)

## Checked

Logs of the slice: FIX-01, FIX-02, FIX-03, FIX-04, FIX-05, FIX-06, FIX-07, FIX-07a, FIX-08, FIX-09 (ten files).

**FIX-01 (all 12 applied edits opened and present).** The edits are in the part files, but at lines about 33 (S0) and 24 (S16) higher than the log cites, see finding 6. S0 `spec/00-conventions.md`: `price.eta_alarm_threshold` validation `(0,1]` at :629; `change.notice_days_default` `1..90` at :673; `change.notice_days_price` `1..90` at :674; `retention.ip_hash_ttl_days` `1..30` at :750; `launch.min_signoffs` `2..5` at :795; `launch.min_approved_services` `1..20` at :796. S16 `spec/16-parameters.md`: `(0,1]` with the F-01 floor clause at :185; `1..30` with the F-06 clause at :337; `2..5; C19` with the F-14 clause at :413; `1..20` with the 16.D.8.1 clause at :414; `1..90; C20` with the F-07 clause at :415; `1..90` with the F-07 clause at :416. Every default lies inside its new range.

**FIX-05 (31 applied edits listed, 30 opened and present, 19d skipped-not-found not re-searched).** In `spec/10a-identity.md` the cited lines are exact: prefix `hamyar:v1:` at :62; single `challenge` field at :63; seven purposes at :67; `POST /v1/identity-challenges` returning `{challenge, expires_at}` at :69; registration block with `create`, `public_key`, `recovery_public_key`, `proof`, `recovery_proof` at :78-84; recovery-checksum label at :110 and salt at :114; recovery rotation rows at :138-139 (see finding 3); rotation call at :167; device-link states at :191-192 and calls at :194-195, :199, :205; limit table of four rows at :214-217 (the wrong-secret row is gone); `GET /v1/member-keys` at :221; recovery call block at :227-231 (the log says 228-232); admin sign-in at :479-480; export sentence at :592; operation table rows at :712, :718-723, :727-728; event list at :732 with the three `admin.approval_*` events and the annotated `admin_action.executed`.

Count so far: 2 logs checked in the part files, 42 applied edits confirmed (12 + 30). Logs FIX-02, FIX-03, FIX-04, FIX-06, FIX-07, FIX-07a, FIX-08 and FIX-09 are covered by the lines added below.

## Findings

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | major | spec/10a-identity.md:95 | Registration check 4 still requires challenge `purpose` = `register_device`, while FIX-05 edit 2 makes the client request purpose `create` (:79, :83-84) and :67 lists seven purposes without `register_device`; read literally, every registration fails check 4 | change check 4 to `create` |
| 2 | minor | spec/10a-identity.md:168, :200, :206 | purposes `rotate_device_key`, `link_claim`, `link_approve` are not among the seven purposes of :67 (`rotate`, `device_link`, `step_up`); the log lists them as residual but they now contradict :67 | rename to the S15.B.3.1 purposes |
| 3 | minor | spec/10a-identity.md:139, :162, :182 | log edit 14b says the old key is `retiring` until the grace ends; the file says `rotated`, and names the new key `pending`; :162 lists key statuses `active`, `rotated`, `revoked` while :182 says `active or retiring` | settle the key-state names against S15.B.3.1 and make :139, :162, :182 and the log agree |
| 4 | minor | spec/10a-identity.md:192, :201 | `attempts exhausted` leads to `denied` and :201 counts `attempts`, but edit 8e dropped the only limit row that gave a number of attempts, so nothing says when attempts are exhausted | define the limit or remove the transition and the counter |
| 5 | minor | spec/00-conventions.md:572 | the `notice_days` row of 0.10.3 names the areas `price`, `admission`, `credit` only, while the row at :674 and S16 :416 also list `reservation.*` | add `reservation` to :572 |
| 6 | minor | docs/fix/FIX-01.md (edit and read-back tables) | the file:line values no longer hold: the log says S0 rows at 596, 640, 641, 717, 762, 763 and S16 rows at 161, 313, 389-392; the rows are now at 629, 673, 674, 750, 795, 796 and 185, 337, 413-416 (S0 :596 is a heading); the log states the lines had not drifted | correct the citations in the log |

## Not checked

The remaining logs FIX-02, FIX-03, FIX-04, FIX-06, FIX-07, FIX-07a, FIX-08 and FIX-09 are not yet opened in the part files; the list of unopened places is written when the audit is complete.

Verdict: NOT READY
