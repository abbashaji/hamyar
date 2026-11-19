# FINAL-2c: re-audit round 2, slice C (FIX-19 to FIX-27)

## Checked

Interim state: the nine logs docs/fix/FIX-19.md to docs/fix/FIX-27.md were read completely (9 of 9). Part files opened and found right so far:

- FIX-27: all 56 edits of the log, in spec/04-architecture.md (lines 17, 46, 60, 86-96, 116, 125, 161, 178, 187, 234, 259-266, 298, 766, 817, 852, 889, 895, 941, 956, 960, 966), spec/08a-templates.md (lines 36, 124-125, 278, 284, 303-327, 839-875, 929-977, 1097-1123, 1143-1171) and spec/09-result-return.md (lines 304, 812). Submitted-content execution is absent from the places read.
- FIX-19: spec/00-conventions.md lines 393, 399, 424, 436-448, 490, 499, 521, 525-543.
- FIX-20: spec/00-conventions.md lines 176-177, 238, 495, 769, 771, 783, 924, 954, 970.
- FIX-21: spec/10b-safety.md headings 10.21, 10.27, 10.28, 10.29 and the Issues raised note; spec/11c-admin-tools.md heading 11.51 to 11.69 and its tool table; spec/11d-i18n-copy.md headings 11.70 to 11.87 and ISS-118.

## Findings

| # | severity | file:line | defect | action |
| --- | --- | --- | --- | --- |
| 1 | major | spec/08a-templates.md:303-306 | The new check types diff_applies_cleanly and path_allowlist (FIX-27 E-27) cannot fail: the platform computes the diff between the supplied snapshot and the returned file and then applies it to the same snapshot, so the result always equals the returned file; the paths of that one computed diff are always the one allowed file. Only static_parse and forbidden_patterns can reject code. The text claiming strong static checks (04:259-266, 09:304, 08a:1097) overstates verification | logged-needs-owner |
| 2 | major | spec/11c-admin-tools.md:9 and spec/11d-i18n-copy.md:836-838 | ISS-117, ISS-118 and ISS-119 still name two different issues each (FIX-21 E15 skipped it); 11c cites ISS-117 both for heading numbering and for the two_person_actions growth, 11d defines ISS-117 as the heading plan | logged-needs-owner |
| 3 | major | other spec files (not enumerated) | FIX-21 E17 left every pointer to the old numbers S10.11 to S10.19 (now 10b S10.21 to S10.29), S11.41 to S11.59 (11c) and S11.40 to S11.57 (11d) in other parts unmapped; the map exists only in the log. Pointers that cite a renumbered section can now point to the wrong file | logged-cross-part |
| 4 | minor | spec/08a-templates.md:841-859 | Slug row code_change_tests says sampled audit; 8.13.3 Audit row says blanket where risk_class is high, and both slugs are high, so the two slug rows and the contract disagree and the slugs are not distinguishable | logged-cross-part |
| 5 | minor | spec/08a-templates.md:~1155 | 8.17 still lists the validation field code flaky_tests that 8.13.4 calls unused; tests_holdout and template.exec.* also remain as runner leftovers (logged by FIX-27 E-39, E-49) | logged-cross-part |
| 6 | minor | spec/00-conventions.md:772 | template.min_reviewers_edit still allows 1..5 against the one-step review machine of 0.9.5; the same range remains in spec/08a-templates.md for template.min_reviewers_loosen. FIX-20 capped only three parameters | logged-cross-part |

## Not checked

Interim: FIX-22 to FIX-26 part-file places and everything not named above are still to be opened.

Verdict: READY WITH LOGGED ITEMS
