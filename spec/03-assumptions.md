# 3. Assumptions introduced [A] and open decisions

*Spec part 3 · owner cell C-028 (supersedes C-001) · every [A] tag in the spec has a row here that names the owner decision which could overturn it (S0.2) · nothing here is legal advice, and nothing here has been verified against any provider's terms or any law.*

## 3.1 How to read this part

- There are two kinds of row. `OD-nn` is an open decision that only the owner can make. `ASM-nn` is an assumption [A] the spec introduced because the Founding Document (FD) is silent. Both id schemes are convention gaps reported in `ISS-38`. [D]
- Every open decision has a default that the spec uses meanwhile, so the build is never blocked by a decision that is not yet made. A default is not a recommendation. Any default that touches provider terms, law or member safety is also [V]. [D]
- A decision is recorded where its default lives: a parameter version, an allowlist row, `LaunchGateItem` evidence or a `PreRegistration`. Until then its status is open; every row below is open. [D]
- Later parts list their [A] tags in their own text. Assembly collects them as further `ASM-nn` rows with ids that continue this list, each naming the `OD-nn` that could overturn it. If no existing decision fits, the part adds an `OD-nn` row and reports it (S0.1). [D]

## 3.2 Open decisions only the owner can make

| id | Decision | Why only the owner | Default used meanwhile | Needed before |
| --- | --- | --- | --- | --- |
| `OD-01` | Operator jurisdiction and legal exposure | Counsel's answers depend on it, and only the owner knows it (brief) | None assumed. No jurisdiction is hardcoded; every legal question is [V] for counsel (`CNS`) and is stored as `LaunchGateItem` evidence | `G0` sign-off |
| `OD-02` | Who reviews templates, services and policy; who is the second reviewer and the second sign-off; who writes the topic list (`ISS-26`) and the 12 initial allowlist rows (`ISS-35`) | Only the owner knows the team [V] | At least two distinct admin principals exist: `launch.min_signoffs` = 2, `template.min_reviewers_new` = 2, `service.min_approvers` = 1. If the owner is alone the spec does not lower the numbers; lowering is a `FND` decision with a public change-log entry | First sign-off; first template approval |
| `OD-03` | Hosting, storage, and the countries the service must be reachable from | The owner pays and carries the risk; reachability from Iran is [V] | Stack-agnostic design with storage and hosting behind interfaces; S4 recommends a stack as a recommendation only | First deployment to a public address |
| `OD-04` | Which services to review first, and whether to launch on a documented fallback when no service is Commons-capable (`ISS-11`) | Provider choice is the owner's, and terms are read by a human [V] | The registry ships with every service `unreviewed`; the spec names no provider; no fallback is accepted without a signed `LaunchGateItem` | `G0` sign-off |
| `OD-05` | The Commons backlog: who authors it, the license of each job (`L1` or `L2`), the publication target and the sponsor label (`ISS-22`) | Open licensing and publication are the owner's act, and counsel must check the license text [V] | Operator-authored with second-admin approval; the author declares the license per job; nothing is published until a target is chosen; the sponsor label is the project name | First Commons job; first publication |
| `OD-06` | Reserve start (`ISS-19`): seed it before inviting the pilot, or start with grants paused | The owner and the founders do the seeding work | The Reserve starts at zero; founders donate after their first accepted Commons cells; grants pause while it is empty | Pilot invitations |
| `OD-07` | Whether `ff.channel.human_review` is on for the pilot (`ISS-21`) | It changes who reads members' material and how credit is earned | Off | Pre-registration lock |
| `OD-08` | Whether platform-side sandboxed execution of submitted code is ever allowed (`ISS-12`) | It overturns an FD rule (FD§10) and carries a security risk [V] | No | Never blocks the build |
| `OD-09` | Who bears three costs the FD leaves open: work paid but excluded after a policy tightening (`ISS-27`), verification beyond the pool (`ISS-16`), and credit already spent when an overturn finds fraud (`ISS-17`) | Each is a choice between the requester, the Reserve and nobody | The job's escrow bears the first; the job stops at the second; the third is published as `unrecovered_ucr` and nobody bears it; the Reserve bears none | `BM7` acceptance |
| `OD-10` | Accept or reject the change of the volunteer-handle derivation (`ISS-29`) | It changes an S0 decision and the safety posture | The S0.6.4 formula; exported manifests omit handles in any case | `BM4` acceptance |
| `OD-11` | The founders' thresholds recorded before Phase 1: price-efficiency alarm, claim-ratio threshold, mint-cap cut, false-accept and false-reject alarms, return bars, decision rules, and the switch-off thresholds for review cells (`FND`) | The FD leaves these to the founders before Phase 1 (S0.10.4) | The S0.10.6 values, which are placeholders and not findings | Pre-registration lock, before day 1 of Phase 1 |
| `OD-12` | Retention, logging and compelled-disclosure posture: the `retention.*` numbers and what S10.* promises members | A safety judgment about members in a high-risk setting (`SEC`) [V] | The S0.10.6 values, reviewed by a safety adviser before use | `G1` sign-off |
| `OD-13` | Who reviews the Persian and English copy for language and legal accuracy | It needs a named human, and counsel for promises and notices [V] | Every `copy.*` key keeps `needs_human_and_legal_review`; the launch checklist (S14.*) has an item for it | Launch sign-off |

## 3.3 Assumptions introduced [A]

“Overturned by” names the open decision that could change the assumption, or “spec change” where no owner decision is involved and a change of this spec is enough.

| id | Assumption | Source | If it is false | Overturned by |
| --- | --- | --- | --- | --- |
| `ASM-01` | Caps, rate limits and day boundaries use UTC calendar boundaries; screens show the local equivalent [A] | S0.6.2 | Members near a boundary see resets at odd local times | spec change |
| `ASM-02` | Member keys are Ed25519; admins use passkeys (WebAuthn) on a separate origin [A] | S0.6.4, S0.11.4 | Some target phones or hosts cannot do it [V: `TEC`]; the auth layer changes | `OD-03` |
| `ASM-03` | Retention classes and the `retention.*` numbers [A] | S0.7, S0.10.6 | Data is kept too long or too short for the safety posture | `OD-12` |
| `ASM-04` | Two-person rules: `service.min_approvers` = 1, `launch.min_signoffs` = 2, and the list in `security.two_person_actions` [A] | S0.10.6 | The team cannot meet them | `OD-02` |
| `ASM-05` | Opt-in defaults `L0`..`L2` and `M0`..`M2`; Persian digits as the `fa` default [A][H] | S0.10.6 | Volunteers see cells they did not expect, or find the digits hard to read | `OD-11` |
| `ASM-06` | One credit is 1,000,000 `ucr`, so a price in ppm equals the price in `ucr` [A] | S0.6.1 | Finer fractions are needed; a data migration follows | spec change |
| `ASM-07` | Rate-limit header names `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset` [A] | S0.11.7 | Clients and gateways expect other names | spec change |
| `ASM-08` | `reviewer` is the admin role; executing a review cell is a member activity [A] | S0.8.2, `ISS-21` | Review contributors need permissions the member role lacks | `OD-07` |
| `ASM-09` | A review cell pays one credit like any cell; farming through review is a hypothesis [H] measured by `review_share_of_mint` | `ISS-21` | Review becomes a cheap way to earn credit; the channel is switched off | `OD-07`, `OD-11` |
| `ASM-10` | A service is `commons_capable` when `approved` with open publication and human copy-paste both `yes`; launch counts such services [A] | `ISS-11` | Fewer services qualify and launch waits, or counsel requires more flags | `OD-04` |
| `ASM-11` | Allowlist rows carry their required flags, and the initial active set is 12 rows [A] | `ISS-11`, `ISS-35` | Reviewers want a different starting set | `OD-02` |
| `ASM-12` | The platform never executes submitted content in Phases 1 and 2 [A] | `ISS-12` | The code-change template stays sampled-only and less efficient | `OD-08` |
| `ASM-13` | Redeemable capacity is φ times forecast capacity, and the claim-ratio alarm uses `claim_ratio_redeemable` [A] | `ISS-15` | The alarm fires too early or too late | `OD-11` |
| `ASM-14` | Cap headroom and K headroom are reserved at lease time [A] | `ISS-15`, `ISS-18` | Leasing needs an extra reservation step; accepted work could be unpaid without it | spec change |
| `ASM-15` | K counts escrowed credit, and earning is prevented at K, not clipped [A] | `ISS-18` | Large jobs are harder to fund, or donors at K feel blocked | `OD-11` |
| `ASM-16` | The verification pool is a hard budget, and new-donor blanket redundancy applies only to Commons cells [A] | `ISS-16` | Some jobs stop early; new donors wait before taking member cells | `OD-09` |
| `ASM-17` | Reversals post only against unspent lots; a ban freezes spending and lots expire to the Reserve [A] | `ISS-17` | Fraud losses are not recovered, or sanctions feel too weak or too harsh | `OD-09`, `OD-12` |
| `ASM-18` | Phase 0 makes no ledger entries; the Reserve starts at zero; root invites obey the join switch [A] | `ISS-19` | Early newcomers wait for a grant | `OD-06` |
| `ASM-19` | Commons jobs carry a sponsor label, are operator-authored, second-admin approved, `P1` and `S0` only, with a publication target [A] | `ISS-22` | The backlog cannot be authored by the people available | `OD-05` |
| `ASM-20` | Regional eligibility is a member's own declaration and is not checked by the platform [A][V] | `ISS-23` | Counsel wants a different way to handle region [V: counsel] | `OD-01` |
| `ASM-21` | `volunteer_action_set` is a closed list, and template review lints for it [A] | `ISS-25` | A valid template is wrongly rejected | spec change |
| `ASM-22` | Topics come from the template plus requester additions; reviewers write the list [A] | `ISS-26` | Opt-in by topic is too coarse or too fine | `OD-02` |
| `ASM-23` | A policy re-check passes under the stamped and the current version, and cells submitted before a tightening are paid [A] | `ISS-27` | Escrows pay for work that cannot be delivered | `OD-09` |
| `ASM-24` | The card sentence is worded so that it is true for every cell kind [A] | `ISS-28` | The wording is too vague to inform the volunteer | `OD-13` |
| `ASM-25` | The internal volunteer handle is derived per job from a per-member salt [A] | `ISS-29` | S0.6.4 stands and handles are linkable across jobs internally | `OD-10` |
| `ASM-26` | The sign-off screen lists every parameter still holding an `initial configurable default` [A] | `ISS-31` | Signers do not see which values are guesses | spec change |

## 3.4 Premises and hypotheses inherited, not introduced here

These are not assumptions of this spec. They are listed so a reader sees what the spec leans on and where it is tested. [D]

| Item | Tag | Source | Where it is tested or recorded |
| --- | --- | --- | --- |
| Provider terms, regional availability, pricing, limits and URL parameters are configuration data entered by a human | [P][V] | Brief, ground rule 2 | S7.*, S14.* |
| G0 (provider terms and law) and G1 (safety threat model) are unresolved | [P] | Brief | S14.* |
| Reachability of any host from Iran | [V] | Brief, scope I | `G2` item, S19.* |
| The existing panel repository was not read | [P][V] | Brief, scope J | S4.* |
| A first contribution takes under 60 seconds once practiced | [H] | FD§3.2 (cited in S0.10.6) | `ui.fast_contribution_threshold_s`, S13.* |
| Free allowances cannot be transferred | [P] | S0.2 example | S7.*, `CNS` |
| Simulation output is never evidence about people | [D] | Brief, scope K | S18.* |

## 3.5 When each decision is needed

| Needed before | Decisions |
| --- | --- |
| First deployment to a public address | `OD-03` |
| First sign-off or first template approval | `OD-02` |
| `G0` sign-off | `OD-01`, `OD-04` |
| `G1` sign-off | `OD-12` |
| Launch sign-off | `OD-13` |
| `BM4` acceptance | `OD-10` |
| First Commons job and first publication | `OD-05` |
| `BM7` acceptance | `OD-09` |
| Pilot invitations | `OD-06` |
| Pre-registration lock, before day 1 of Phase 1 | `OD-07`, `OD-11` |
| Never blocks the build | `OD-08` |

## Issues raised

The issues numbered inside the block of this file (S0.13). Their detail and resolutions are in S2.6 and the register in S2.2. [D]

| id | severity | fd_ref | issue | resolution | status |
| --- | --- | --- | --- | --- | --- |
| `ISS-31` | major | FD§8.3 | The exit rule governs building; the brief says build everything and gate launch | The rule governs launching; unmeasured defaults are listed at sign-off | applied |
| `ISS-32` | minor | FD§4.4 | Audit comparators for free text versus no model-based judging | Deterministic comparator per template, tested before approval | proposed |
| `ISS-33` | minor | FD§4.5, FD§4.6 | “Expires quickly” is undefined | `grant.starter_lifetime_days` | applied |
| `ISS-34` | minor | FD§4.8 | Deadline classes are undefined at multiplier 1.0 | One class, `standard` | applied |
| `ISS-35` | minor | FD§5.7 | “Two active profiles” does not match its axes | 12 allowlist rows as data | proposed |
| `ISS-36` | minor | FD§6.1 | Not showing Iran-based members by place needs inference | Place display is opt-in and identical for everyone | proposed |
| `ISS-37` | minor | none | The instruction's issue numbering collides with S0.4 | Part-0 ids kept; this cell uses the inherited blocks | applied |
| `ISS-38` | minor | none | No id scheme for assumptions and open decisions | `ASM-nn` and `OD-nn`, owned by S3 | proposed |
