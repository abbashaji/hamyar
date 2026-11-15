# 0. Biggest decisions and challenges to the instructions

*Spec part 0 · owner cell C-027 (supersedes C-000) · the short list the prompt asks for before the spec. Names, enums and numbers are fixed in `spec/00-conventions.md`; references below point there.*

## 0.D.1 Decisions and challenges (ten lines)

1. **Build everything, launch nothing.** Milestones `BM0`..`BM9` (conventions 0.12) ship with every `launch.*` switch off; the ledger invariants (`BM1`), the launch-gate machinery (`BM2`) and the Service Registry (`BM3`) come before any job or cell reaches a member; `unreviewed` counts as `no`. This reads the FD§8.3 exit rule (no building beyond a throwaway prototype before `G0` and `G1`) as a rule about launching, as the brief instructs; if no service clears `G0`, the built system stays unlaunched and the FD§8.3 fallbacks apply. [D]
2. **Ledger amounts are integer micro-credits** (1 credit = 1,000,000 `ucr`) and ratios are integer ppm, so p = 1 + v + λ is exact and the FD§3.3 example reproduces to the unit (escrow 276, payout 264, levy 12). [D]
3. **Two FD gaps are closed by design:** donors are paid per accepted cell at acceptance, and settlement only posts levy and refund (`ISS-09`); every gating registry flag is phrased as a permission so that `unknown` = `no` is always the safe direction (`ISS-02`). [D]
4. **Every FD "TBD" is a named, validated, versioned parameter** with an `initial configurable default` and the measurement that replaces it (conventions 0.10); policy rules `R1`..`R10`, kill switches and feature flags are data, not code. [D]
5. **Identity and hosting:** a keypair generated on the device and no passwords for members, WebAuthn passkeys on a separate origin for admins, raw IP addresses never stored, UTC in storage and Jalali only at the display edge, no mandatory third-party host. [D][A]
6. **The Phase 0 calibration tool is built in `BM2`**, ahead of the rest, so the cell envelope, the lease timeout and the timing thresholds can be measured while the system is built (the sampling rates need Phase 1 data, `P1M`). [D]
7. **Challenge to "implement the full system before any experiment":** accepted, but it is the riskiest order. The defaults for the envelope, K, λ, g, s, φ and the lease timeout are guesses until measured, so nothing treats a default as a finding, and a flaw found late (for example in the cost of verification) is rework you carry. [H]
8. **Challenge to the scope of "full":** read as everything in prompt scope A–K. Items the FD itself defers (a marketplace, differential pricing, model-based judging that mints credit, money rewards) stay out; the growth mechanics `V1`..`V6` are still built behind flags (prompt scope G) and only their statistical testing waits for Phase 2 (FD§0.1 item 14, FD§6.2). [A]
9. **Challenge to the team assumption:** the two-person rules (new-template review, launch sign-off, ledger reversal, loosening a parameter) need at least two admins; with one founder they cannot be met, and the owner must decide what replaces them. [A]
10. **Assumptions instead of questions:** the operator's jurisdiction is unknown, so every legal item stays [V] for counsel; hosting is undecided and sits behind interfaces; founders act as Reviewers and Operators in Phase 1; no provider is named anywhere. [P][A]

## 0.D.2 Clarifying questions

None. Nothing blocks the specification; the decisions only the owner can make (jurisdiction, who reviews templates, hosting, number of admins) are listed as assumptions in S3.*.

## Issues raised

None beyond `ISS-01`..`ISS-09` recorded in `spec/00-conventions.md`.
