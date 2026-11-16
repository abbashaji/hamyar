# FIX-07a

In spec/15c-api-reconcile-core.md, section 15.B.2 (Verdict table, every cited path), a new row was inserted directly after the existing `/v1/policy` row: `/v1/public/policy` | NEW | `getPublicPolicy` (15.B.8). The check script reads only the first backticked /v1 path of a verdict row, so the old row defined only /v1/policy and the real path /v1/public/policy, cited in 11b, counted as undefined. The old row was left unchanged and nothing was renamed or deleted.

Row added: yes

Result: DONE
