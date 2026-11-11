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

## 8.4 Template document format

The document is authored as YAML and stored and hashed as canonical JSON. This is its schema (JSON Schema, draft 2020-12 subset: no remote `$ref`, no `format`, patterns must be RE2-safe) [D].

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:hamyar:template_version_body:1",
  "type": "object", "additionalProperties": false,
  "required": ["format_version","job_type","title","profiles","risk_class","quality_class","volunteer_steps","envelope","slots","split","prompt","delimiters","output","checks","comparator","gold","claims","known_risks","hypotheses"],
  "properties": {
    "format_version": { "const": 1 },
    "job_type": { "enum": ["translation_glossary","classify_extract","summarize_schema","code_change_tests","format_convert_validator","human_review"] },
    "title": { "$ref": "#/$defs/i18n" },
    "profiles": { "type": "array", "minItems": 1, "items": { "type": "object", "additionalProperties": false,
      "required": ["purposes","sensitivities","service_requirements"],
      "properties": { "purposes": { "type": "array", "items": { "enum": ["P0","P1","P2","P3"] } },
        "sensitivities": { "type": "array", "items": { "enum": ["S0","S1"] } },
        "service_requirements": { "type": "array", "items": { "enum": ["M0","M1","M2"] } } } } },
    "risk_class": { "enum": ["standard","high"] },
    "quality_class": { "enum": ["objective","mixed","subjective"] },
    "volunteer_steps": { "const": ["copy_prompt","press_send","copy_answer","paste_back"] },
    "envelope": { "type": "object", "additionalProperties": false, "required": ["input_ref","output_ref","expected_time_ref"],
      "properties": { "input_ref": { "const": "cell.envelope.max_input_chars" },
        "output_ref": { "const": "cell.envelope.max_output_chars" },
        "expected_time_ref": { "const": "cell.envelope.expected_time_s" },
        "output_budget_share_ppm": { "type": "integer", "minimum": 1, "maximum": 1000000 } } },
    "slots": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/slot" } },
    "split": { "$ref": "#/$defs/split" },
    "prompt": { "type": "object", "additionalProperties": false, "required": ["canonical","variants"],
      "properties": { "canonical": { "const": "en" },
        "variants": { "type": "object", "required": ["en"], "additionalProperties": false,
          "properties": { "en": { "type": "string", "maxLength": 4000 }, "fa": { "type": "string", "maxLength": 4000 } } } } },
    "delimiters": { "type": "object", "additionalProperties": false, "required": ["blocks","result_block"],
      "properties": { "blocks": { "type": "array", "items": { "type": "string", "pattern": "^[A-Z_]{3,16}$" } },
        "result_block": { "const": "RESULT" }, "echo_token": { "type": "boolean" } } },
    "output": { "$ref": "#/$defs/output" },
    "checks": { "type": "array", "minItems": 1, "items": { "$ref": "#/$defs/check" } },
    "comparator": { "$ref": "#/$defs/comparator" },
    "gold": { "$ref": "#/$defs/gold" },
    "claims": { "type": "array", "items": { "$ref": "#/$defs/i18n" } },
    "known_risks": { "type": "array", "minItems": 1, "items": { "type": "object", "required": ["id","text","mitigation"],
      "properties": { "id": { "type": "string" }, "text": { "type": "string" }, "mitigation": { "type": "string" } } } },
    "hypotheses": { "type": "array", "minItems": 1, "items": { "type": "object", "required": ["id","claim","measurement","success","kill"],
      "properties": { "id": { "type": "string" }, "claim": { "type": "string" }, "measurement": { "type": "string" },
        "success": { "type": "string" }, "kill": { "type": "string" } } } },
    "execution": { "type": "object", "additionalProperties": false, "required": ["mode"],
      "properties": { "mode": { "enum": ["none","server_sandbox","requester_side"] }, "runner_profile": { "type": "string" } } }
  },
  "$defs": {
    "i18n": { "type": "object", "required": ["en"], "properties": { "en": { "type": "string" }, "fa": { "type": "string" } } },
    "slot": { "type": "object", "additionalProperties": false, "required": ["id","kind","source","visibility"],
      "properties": {
        "id": { "type": "string", "pattern": "^[a-z][a-z0-9_]{0,31}$" },
        "kind": { "enum": ["text","enum","int","bool","rows","glossary","code","system"] },
        "source": { "enum": ["requester","upload_split","system"] },
        "visibility": { "enum": ["prompt","server_only"] },
        "required": { "type": "boolean" },
        "values": { "type": "array", "items": { "type": "string" } },
        "block": { "type": "string" },
        "budget_share_ppm": { "type": "integer", "minimum": 1, "maximum": 1000000 },
        "max_items": { "type": "integer", "minimum": 1 },
        "multiline": { "type": "boolean" },
        "screen": { "type": "array", "items": { "enum": ["urls","pii","instruction_patterns","delimiter_collision","marker_collision","bidi_controls"] } } } },
    "split": { "type": "object", "required": ["strategy"],
      "properties": { "strategy": { "enum": ["paragraph_pack","row_pack","single_unit","file_unit"] },
        "unit_budget_share_ppm": { "type": "integer" }, "id_prefix": { "type": "string" } } },
    "output": { "type": "object", "required": ["kind"],
      "properties": { "kind": { "enum": ["json","jsonl","marked_segments","text"] },
        "schema": { "type": "object" }, "max_chars_share_ppm": { "type": "integer" } } },
    "check": { "type": "object", "additionalProperties": false, "required": ["id","type","on_fail"],
      "properties": { "id": { "type": "string" }, "type": { "type": "string" }, "params": { "type": "object" },
        "on_fail": { "enum": ["reject","quarantine","flag_for_audit","note"] },
        "reason": { "type": "string", "pattern": "^reject\\.[a-z_]+$" },
        "calibration_source": { "enum": ["CAL","P1M","FND","SEC","TEC","OPS","CON"] } } },
    "comparator": { "type": "object", "required": ["type"],
      "properties": { "type": { "type": "string" }, "params": { "type": "object" }, "calibration_source": { "type": "string" } } },
    "gold": { "type": "object", "required": ["kinds","construction"],
      "properties": { "kinds": { "type": "array", "items": { "enum": ["exact","property","reference_tolerant"] } },
        "construction": { "type": "array", "items": { "type": "string" } } } }
  }
}
```

Field rules the schema cannot express (enforced by the template linter, which runs on `template.review_requested` and again at every render; a failure blocks the transition) [D]

| Rule | Statement |
| --- | --- |
| LR-01 | `volunteer_steps` equals the constant; no field anywhere may add a volunteer action (R3) |
| LR-02 | Every placeholder `{{id}}` in a prompt variant names a declared slot or the reserved `{{dlm}}`; every slot with `visibility` = `prompt` is used at least once; `server_only` slots appear in no variant |
| LR-03 | A slot with `source` = `requester` or `upload_split` and `kind` in `text`, `rows`, `glossary`, `code` MUST declare a `block` listed in `delimiters.blocks`, and its placeholder MUST be inside that block's open and close lines |
| LR-04 | All variants have the same placeholder multiset and the same delimiter lines (variant parity) |
| LR-05 | `size`: slot budgets are shares of the data budget (8.5.2); the sum of `budget_share_ppm` of prompt slots is at most 1,000,000; `max_items` and shares are checked against a worst-case render |
| LR-06 | Every `check.type` and `comparator.type` exists in the registries of 8.6; every `reason` is in `S0.8.4` or in 8.17 |
| LR-07 | `checks` contains the checks required by `output.kind` (8.6.1 column "required for") in the mandatory order of 8.6.2 |
| LR-08 | `execution.mode` other than `none` is allowed only for `job_type` = `code_change_tests`; `risk_class` = `high` is required when `mode` = `requester_side` |
| LR-09 | `claims` and every user-facing string contain no word of the forbidden list ("guarantee", "guaranteed", "guarantees", and the Persian equivalents held in the lint data) (Principle 11) |
| LR-10 | The R3 lint of 8.7 passes on every variant |
| LR-11 | `hypotheses` ids are unique and each has non-empty `measurement`, `success`, `kill` |
| LR-12 | `profiles` only lists combinations that the active `PolicyVersion` allowlist contains; a template cannot widen policy (R8, `S7.*`) |

### 8.4.1 Slot semantics [D]

| Kind | Meaning | Charset and sanitation |
| --- | --- | --- |
| `text` | Requester or split data, free text | NFC normalized; C0 and C1 controls removed except `\n` and `\t`; bidi embedding and override controls (U+202A to U+202E) removed; ZWNJ (U+200C), LRM, RLM kept because Persian orthography needs them [A] |
| `enum` | One of `values` | Exact match; shown verbatim |
| `int`, `bool` | Scalar | Canonical decimal or `true`, `false` |
| `rows` | Ordered records, each `id<TAB>text`, ids assigned by the platform | As `text` per field; tab and newline escaped inside a field |
| `glossary` | Rendered subset of a `Glossary` (8.9) | As `text`; one entry per line |
| `code` | Source code text | As `text` but tabs kept; no normalization of whitespace; NFC not applied to identifiers [A] |
| `system` | Value computed by the platform (language names, label list rendering, id lists) | Taken from a template `values` table or the job metadata, never from free text |

`visibility` = `server_only` means the value is stored with the cell and used by checks (for example hold-out tests) but is never placed in any rendered prompt [D].

### 8.4.2 Annotated skeleton (authoring form)

```yaml
format_version: 1
job_type: translation_glossary
title: { en: "Translation with a shared glossary", fa: "ترجمه با واژه‌نامهٔ مشترک" }
profiles: [ { purposes: [P0, P1], sensitivities: [S0, S1], service_requirements: [M0, M1] } ]
risk_class: standard          # high => blanket redundancy per verify.blanket_redundancy_n
quality_class: mixed          # subjective or mixed => verify.human_review_rate applies
volunteer_steps: [copy_prompt, press_send, copy_answer, paste_back]
envelope: { input_ref: cell.envelope.max_input_chars, output_ref: cell.envelope.max_output_chars, expected_time_ref: cell.envelope.expected_time_s }
slots:    [ ... ]             # 8.4.1
split:    { strategy: paragraph_pack }
prompt:   { canonical: en, variants: { en: "...", fa: "..." } }
delimiters: { blocks: [GLOSSARY, SOURCE], result_block: RESULT, echo_token: true }
output:   { kind: marked_segments }
checks:   [ { id: c01, type: extract_result, on_fail: reject } ]   # 8.6.1
comparator: { type: segment_overlap, params: { ... } }            # 8.6.3
gold:     { kinds: [property], construction: [ ... ] }            # 8.10.7 etc.
claims: []                    # user-facing statements; must say "declared", never "guaranteed"
known_risks: [ ... ]
hypotheses: [ ... ]
```
