# Architecture decisions

Fixed decisions every cell must follow. Agents cannot edit this file (protected).

## What this repo is
Each cell WRITES ONE PART OF THE HAMYAR PRODUCT SPECIFICATION (markdown under `spec/`). Cells do not build the product and do not run any experiment. The final document "Hamyar — Product Specification.md" is assembled from `spec/*.md` by `scripts/assemble.py` (not by agents).

## Source of truth (read as the cell names them)
- `docs/source/prompt.md` — the full task statement (scope A–K, ground rules, style). Read the ground rules and only the scope letters your cell names.
- `docs/source/Hamyar - Founding Document.md` — source of truth; never contradict silently; section numbers (§4.2 etc.) refer to it.
- `docs/source/panel-review.md` — facts about github.com/abbashaji/panel read by the owner's tooling. Cite it; do not assume anything it lists under "could not determine". Everything about the panel stays [V].
- `spec/00-conventions.md` — shared names, IDs, enums, parameter names, API prefix. Every cell MUST use these exactly (written by C-000).

## Ground rules (from the prompt, binding on every cell)
1. Do not invent provider terms, regional availability, pricing, limits, URL parameters or legal rules. Such facts are configuration data recorded by a human reviewer; mark dependence [V] and say what must be verified and where the answer is stored.
2. Never specify anything that automates a volunteer's account, reads/scrapes their chat page, stores their provider credentials or session, submits on their behalf, or helps bypass regional/technical restrictions. The human presses Send. If a feature would need otherwise, say so and exclude it.
3. Evidence tags: [D] decision, [H] hypothesis, [V] verify, [P] premise, [A] assumption introduced by the spec. Every number is derived by a shown formula or labeled "initial configurable default". No invented statistics.
4. TBD parameters (cell envelope, K, λ, g, s, φ, G, mint cap, lease timeout) are named, validated, versioned configuration parameters with a safe initial default and the measurement that replaces it. Never hardcode.
5. Promises in user-facing copy say "declared", never "guaranteed". No legal conclusions: flag [V] for counsel.
6. Build order must always leave a working, testable system; launch-gate machinery and ledger invariants come early.
7. Do not simplify for a pilot or defer components "because the pilot is small". Phase 1 is a configuration of the full system.

## Style
Precise, not padded. Tables, schemas, pseudocode, text state diagrams, Given/When/Then. Every section contains decisions, not generalities. Write in English; Persian only where a cell says so (RTL-safe, correct Persian, marked "needs human and legal review").
Challenge the Founding Document where warranted: record each problem as an "Issue" with ID `ISS-nn` following `spec/00-conventions.md`, and tell C-001 via a `## Issues raised` list at the end of your file (id, one line, proposed resolution). C-001 consolidates them.
Heading format: top-level heading of each file is `# <section number>. <title>` so assembly can order files; sub-headings `## <n>.<m> ...`.

## Mechanics
- A file over ~150 lines is written in several appends/commits. Spec files are long; that is expected.
- Acceptance runs `python scripts/check_spec.py` (stdlib only). Meeting it is necessary, not sufficient: the content must be complete for the cell's goal.

## Seeded draft (owner note)
`spec/00-conventions.md` (950 lines) and `spec/00-decisions.md` were drafted on branch `cell/C-000` and copied to main so the work is not lost. The cell that owns them is C-027. Its job: check them against its goal and the ground rules above, fix gaps with small edits (do not rewrite, do not pad `00-decisions.md`, which stays a short list), then submit. Milestone IDs are `BM0`..`BM9` (see conventions 0.12); other parts use these, not `M0..Mn`.
## Checker notes
`scripts/check_spec.py --require` is case-insensitive. Acceptance commands only prove structure; the cell's goal defines completeness.
