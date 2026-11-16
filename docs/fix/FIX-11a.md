# FIX-11a

Section 15.E.13 (Path index for the verdict check) was appended at the end of spec/15f-api-reconcile-measurement.md. It adds one verdict row per item and sub-resource path of the operations in 15.E.5 to 15.E.11, plus the path of `recordClientEvents`, so that scripts/check_refs.py finds a backticked /v1 path first in the row and a NEW cell, and part 13 no longer cites undefined paths. Nothing was renamed, changed or deleted.

Section appended: 15.E.13

Open point: the owner of S15 confirms the calibration proposals path

Result: DONE
