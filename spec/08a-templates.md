# 8. Templates and verification pipeline

*Spec part 8a · template format and first templates · names bound by S0 · written against Founding Document draft v0.1 (FD). This file fixes what a template is, how it is reviewed and versioned, and the first five concrete templates. The verification pipeline itself (gold insertion, audits, adaptive sampling, reliability and error-rate estimation, human-review cells, appeals) belongs to the sibling file(s) of part S8; this file defines only what a template must declare so that pipeline can run. No template here is claimed to work: every effectiveness statement is a hypothesis [H]. Nothing here is legal advice.*

## 8.1 Scope and how to read this file

| In this file | Not in this file (owner) |
| --- | --- |
| Template and `TemplateVersion` data model fields (8.3) | Final column types and indexes of all entities (`S5.*`) |
| Template document schema: slots, prompt, delimiters, output, checks, comparator, envelope reference, gold declaration, review status, version (8.4) | Input-screening rules, link and instruction-pattern lists, quarantine handling (`S9.*`) |
| Render, extraction and check-evaluation algorithms (8.5, 8.6) | Gold insertion rate `g`, audit rate `s`, adaptive sampling, reliability and error-rate estimation (`S8.*` sibling file) |
| R3 conformance of every prompt (8.7) | Policy evaluator and allowlist (`S7.*`) |
| Template review workflow, second-reviewer rule, versioning, deprecation (8.8) | Admin screens for the review queue (`S11.*`), kill-switch machinery (`S14.*`) |
| Shared glossary object (8.9) and the five first templates (8.10 to 8.14) | The `human_review` job type: its template is specified in the sibling file(s) of `S8.*` using the format of 8.4 [A] |

Reading rules [D]

1. Names, ids, enums, states, events and parameters are those of `S0.*`, used exactly. Names this file adds are collected in 8.17 so they can be folded back into `S0.*` as convention gaps.
2. This file uses headings `8.1` to `8.17`. Sibling files of part S8 continue at `8.18` and do not repeat the top-level heading `# 8.` [A].
3. A template is data, never code. Executable behavior lives in platform check and comparator implementations that a template only references by `type` (8.6) [D].
4. Numbers inside a template document (budgets, ratios, thresholds) are template data: stored in the versioned, reviewed `TemplateVersion.body`, each labeled `initial configurable default` with a `calibration_source` measurement code (`S0.10.4`) that replaces it. They are not system parameters and are not in the parameter table; see `ISS-83` [A].
5. Every hypothesis in 8.10 to 8.14 is written as: claim [H], then Measurement, Success criterion, Kill criterion. Success and kill criteria reuse existing parameters (`verify.false_accept_alarm`, `verify.false_reject_alarm`, `calibration.min_samples_per_service`) or defer to a `PreRegistration` (`FND`); no new threshold number is invented here [D].
6. Persian text in this file is a draft for a Persian-fluent reviewer and is marked `needs_human_and_legal_review` [V: reviewed by a Persian-fluent reviewer; result stored as the review checklist item RC-02 in the `AdminAction` that approves the version].

## 8.2 Decisions summary [D]

| # | Decision | Reason |
| --- | --- | --- |
| 1 | Prompts exist only as reviewed `TemplateVersion`s; free-form prompts do not exist in Phase 1 | R4, FD§5.4 |
| 2 | A cell's rendered prompt is a pure function of (template version, slot values, variant, delimiter token); nothing else is concatenated | Auditability: the volunteer sees exactly what the reviewer approved plus declared data (FD§5.5) |
| 3 | Every requester-influenced string sits inside a delimiter block whose marker contains a per-render random token | A requester cannot pre-write a matching end marker (FD§5.5 injection note) |
| 4 | The only volunteer actions a template may require are copy prompt, press Send, copy answer, paste back; this is a constant in the schema, not a field a template can extend | R3, FD§5.4, ground rule 3 |
| 5 | The model is asked to echo the per-render token inside its result block; the token is a format check and a weak copy-paste-of-another-cell signal, never proof of anything | Cheap, deterministic, anti-forgery support (FD§8.2 risk 9) |
| 6 | Verification is declared per template: ordered automatic checks, a deterministic comparator, a gold-cell construction method, a risk class | FD§4.4 |
| 7 | Checks and comparators are deterministic functions of data; no model call ever decides acceptance or credit | `verify.model_judge_mints_credit` = false |
| 8 | Checks that execute code run only in an isolated runner, only for `code_change_tests`, only after non-executing checks pass, and never on the volunteer's device | `ISS-81`; ground rule 3 |
| 9 | A template version is immutable once review starts; any edit is a new version | Reviewers approve a hash, not a draft |
| 10 | New templates need `template.min_reviewers_new` approvals from distinct reviewers who are not the author; the first set is not pre-approved | FD§5.7 failure mode 10 |
| 11 | Loosening a template (larger envelope, weaker check, added profile) is announced and delayed; tightening is immediate | R10 applied to templates [A] |
| 12 | Each template names its known risks and its effectiveness hypotheses; the registry refuses `approved` without them | Principle 11: claim only what can be shown |
| 13 | Persian prompt variants are first-class so a Persian-reading volunteer can read exactly what they send | FD§5.5 (the full prompt is one tap away), FD§10 |

## 8.3 Template entities, identity and versioning

Fields this part requires of `Template` and `TemplateVersion` (the complete column list, types and indexes are in `S5.*`; a missing field there is a convention gap) [A].

**`Template`** (`tpl_`, table `templates`, retention `permanent`)

| Field | Type | Rule |
| --- | --- | --- |
| `slug` | text | Unique, `^[a-z][a-z0-9_]{2,40}$`. For the seed set it equals the `job_type` value |
| `job_type` | enum | `S0.8.6` |
| `active_version_id` | `tpv_` or null | The one `approved` version that new jobs use; null while none is approved |

**`TemplateVersion`** (`tpv_`, table `template_versions`, retention `permanent`)

| Field | Type | Rule |
| --- | --- | --- |
| `template_id` | `tpl_` | Foreign key |
| `version_number` | int >= 1 | Unique per template; assigned by the server, gapless |
| `body` | json | The document of 8.4; contains no personal data and no provider terms facts |
| `body_hash` | text | `sha256:<hex>` over the RFC 8785 canonical JSON of `body` (`S0.6.4`) |
| `review_status` | enum | `draft`, `in_review`, `awaiting_second_review`, `changes_requested`, `approved`, `rejected`, `paused`, `retired` (`S0.9.5`) |
| `change_class` | enum or null | `tighten`, `loosen`, `neutral`; null for version 1; computed by the diff rules of 8.8.5 |
| `change_note` | json | `{ "en": text, "fa": text }`, public through the change log |
| `author_admin_id` | `adm_` | The principal that created the version; never counted as an approver |
| `supersedes_version_id` | `tpv_` or null | Previous approved version |
| `approved_at`, `effective_from`, `retired_at` | timestamptz or null | `effective_from` per 8.8.5 |
| `retired_reason` | enum or null | `superseded` or `withdrawn` (8.8.7) |

Constraints [D]

- `body` and `body_hash` are immutable once `review_status` leaves `draft` and `changes_requested`; the database rejects an update that changes them in any other state.
- At most one `TemplateVersion` per template is `approved` at a time; approving a newer version retires the older one with `retired_reason` = `superseded` in the same transaction.
- A `Job` stamps `template_id`, `version_number` and `body_hash` at admission (FD§5.2, R9) and keeps rendering from that version even after it is superseded (8.8.7).
- No template row is ever deleted; a template that must never run again is `retired` with `retired_reason` = `withdrawn`.
