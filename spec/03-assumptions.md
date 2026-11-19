# 3. Assumptions introduced [A] and open decisions

*Spec part 3 · owner cell C-028 (supersedes C-001) · every [A] tag in the spec has a row here that names the owner decision which could overturn it (S0.2) · nothing here is legal advice, and nothing here has been verified against any provider's terms or any law.*

## 3.1 How to read this part

- There are two kinds of row. `OD-nn` is an open decision that only the owner can make. `ASM-nn` is an assumption [A] the spec introduced because the Founding Document (FD) is silent. Both id schemes are convention gaps reported in `ISS-38`. The `OD-nn` ids of this part are local to S3: S19.9 numbers its own owner decisions `OD-01`..`OD-12` with different meanings, so a reference across parts is written `S3 OD-nn` or `S19 OD-nn`. From FIX-24 on, prose that cites an id of either series uses that form; the key is in 3.6, no id is renumbered, and `OD-15` to `OD-31` exist only in S3. [D]
- Every open decision has a default that the spec uses meanwhile, so the build is never blocked by a decision that is not yet made. A default is not a recommendation. Any default that touches provider terms, law or member safety is also [V]. [D]
- A decision is recorded where its default lives: a parameter version, an allowlist row, `LaunchGateItem` evidence or a `PreRegistration`. Until then its status is open; every row below is open. [D]
- Later parts list their [A] tags in their own text. Assembly collects them as further `ASM-nn` rows with ids that continue this list, each naming the `OD-nn` that could overturn it. If no existing decision fits, the part adds an `OD-nn` row and reports it (S0.1). [D]

## 3.2 Open decisions only the owner can make

| id | Decision | Why only the owner | Default used meanwhile | Needed before |
| --- | --- | --- | --- | --- |
| `OD-01` | Operator jurisdiction, entity form and legal exposure | Counsel's answers depend on it, and only the owner knows it (brief) | None assumed. No jurisdiction or entity form is hardcoded; every legal question is [V] for counsel (`CNS`) and is stored as `LaunchGateItem` evidence | `G0` sign-off |
| `OD-02` | Who reviews templates, services and policy; who is the second reviewer and the second sign-off; who writes the topic list (`ISS-26`) and the 12 initial allowlist rows (`ISS-35`) | Only the owner knows the team [V] | At least two distinct admin principals exist: `launch.min_signoffs` = 2, `template.min_reviewers_new` = 2, `service.min_approvers` = 1. If the owner is alone the spec does not lower the numbers; lowering is a `FND` decision with a public change-log entry | First sign-off; first template approval |
| `OD-03` | Hosting, storage, and the countries the service must be reachable from | The owner pays and carries the risk; reachability from Iran is [V] | Stack-agnostic design with storage and hosting behind interfaces; S4 recommends a stack as a recommendation only | First deployment to a public address |
| `OD-04` | Which services to review first, and whether to launch on a documented fallback when no service is Commons-capable (`ISS-11`) | Provider choice is the owner's, and terms are read by a human [V] | The registry ships with every service `unreviewed`; the spec names no provider; no fallback is accepted without a signed `LaunchGateItem` | `G0` sign-off |
| `OD-05` | The Commons backlog: who authors it, the license of each job (`L1` or `L2`), the publication target and the sponsor label (`ISS-22`) | Open licensing and publication are the owner's act, and counsel must check the license text [V] | Operator-authored with second-admin approval; the author declares the license per job; nothing is published until a target is chosen; the sponsor label is the project name | First Commons job; first publication |
| `OD-06` | Reserve start (`ISS-19`): seed it before inviting the pilot, or start with grants paused | The owner and the founders do the seeding work | The Reserve starts at zero; founders donate after their first accepted Commons cells; grants pause while it is empty | Pilot invitations |
| `OD-07` | Whether `ff.channel.human_review` is on for the pilot (`ISS-21`) | It changes who reads members' material and how credit is earned | Off | Pre-registration lock |
| `OD-08` | Whether platform-side sandboxed execution of submitted code is ever allowed (`ISS-12`) | It overturns an FD rule (FD§10) and carries a security risk [V] | No | Never blocks the build |
| `OD-09` | Who bears three costs the FD leaves open: work paid but excluded after a policy tightening (`ISS-27`), verification beyond the pool (`ISS-16`), and credit already spent when an overturn finds fraud (`ISS-17`); also whether the Reserve may pay restitution for an overturned rejection or ban, or goodwill for a policy change (`ISS-56`, `ISS-76`) | Each is a choice between the requester, the Reserve and nobody | The job's escrow bears the first; the job stops at the second; the third is published as `unrecovered_ucr` and nobody bears it; the Reserve bears none; no `appeal_restitution` entry, so an overturned rejection after escrow close pays nothing and the donor bears it (`ISS-56`); `ISS-27` stands over `ISS-76` (02e A4, A6) | `BM7` acceptance |
| `OD-10` | Accept or reject the change of the volunteer-handle derivation (`ISS-29`) | It changes an S0 decision and the safety posture | The S0.6.4 formula; exported manifests omit handles in any case | `BM4` acceptance |
| `OD-11` | The founders' thresholds recorded before Phase 1: price-efficiency alarm, claim-ratio threshold, mint-cap cut, false-accept and false-reject alarms, return bars, decision rules, and the switch-off thresholds for review cells (`FND`) | The FD leaves these to the founders before Phase 1 (S0.10.4) | The S0.10.6 values, which are placeholders and not findings | Pre-registration lock, before day 1 of Phase 1 |
| `OD-12` | Retention, logging and compelled-disclosure posture: the `retention.*` numbers and what S10.* promises members | A safety judgment about members in a high-risk setting (`SEC`) [V] | The S0.10.6 values, reviewed by a safety adviser before use | `G1` sign-off |
| `OD-13` | Who reviews the Persian and English copy for language and legal accuracy | It needs a named human, and counsel for promises and notices [V] | Every `copy.*` key keeps `needs_human_and_legal_review`; the launch checklist (S14.*) has an item for it | Launch sign-off |
| `OD-14` | The project name and public descriptor: whether `Hamyar` is used publicly, and whether the words "cooperative" and "bank" are ever used (FD§0.3, FD§8.2 row 12) | The choice of name is the owner's; availability of the name and the legal meaning of those words are unchecked [V] | `Hamyar` stays a provisional working name [D, provisional] (FD§0.3); public copy says "commons" and "contribute / request" and does not use "cooperative" or "bank"; "deposit / withdrawal" stay internal; counsel is asked (`CNS`) | Public exposure |
| `OD-15` | What e-mail is for, and how members are told of expiry and other notices (`ISS-44`, `ISS-102`, e-mail half) | It sets what the platform may send and store about a member [A] | In-app notices only; the platform sends only a message a member asks for; e-mail is opt-in, for notices only, never a login or recovery factor | First member invitation |
| `OD-16` | Quote basis of the verification pool before any measurement exists, and whether any template is `high` risk in Phase 1 (`ISS-85` (a), (b), (e); `ISS-16` item 2) | It sets how much of a job's price pays for verification, and a shortfall stops the job (`S3 OD-09`) [A] | max(measured v, `price.v_prior`, v_floor) [A] | `BM7` acceptance |
| `OD-17` | Approval guard: whether approval needs `human_copy_paste_use` and `access_pooling_or_crediting` both `yes`; whether a `no` on `regional_availability` blocks approval (`ISS-71`, `ISS-72`) | It decides which services may be used, and terms and region are read by a human [V: counsel] | The stricter guard of S7 7.10.3: approval needs both `yes`, no override; regional availability never blocks and is shown as a declared-terms notice, with no workaround | `G0` sign-off |
| `OD-18` | License pairing for `P2` and `P3` (`ISS-73`) | License choice needs counsel [V] | `P0` with `L0`; `P1` with `L1`, `L2`; `P2` with `L3`; `P3` with `L0`, `L1`, `L2` [A]; no `P2` or `P3` rows in Phases 1 and 2 | Before any `P2` or `P3` row is added |
| `OD-19` | Whether a human review of the panel repository clears G4 (`ISS-49`) | The repository was not read here, and every fact about it stays [V] | The G4 `LaunchGateItem` stays open until a human signs off | `G4` sign-off |
| `OD-20` | Penalty or fee for a late cancel or no-show on a reservation (`ISS-66`) | Whether a reservation can cost a member anything is the owner's choice [A] | No money; a cooldown after a late cancel or an expiry; one live reservation per member | Before `ff.job.reservations` is enabled |
| `OD-21` | `lease.max_job_share_ratio`: value, rounding and whether it is public (`ISS-105`, `ISS-16107`) | It limits how much of a job one member can take [A] | The initial configurable default 0.34, replaced by `P1M`; cells allowed = max(1, floor(x x N)) [A]; hidden | First `S1` job |
| `OD-22` | When the recovery key is shown (`ISS-113`) | It trades a short join path against the risk of a lost key [A] | After the first accepted cell, with a "key not saved" marker [H] | `BM8` acceptance (member screens) |
| `OD-23` | What a requester gets when a job is cancelled or fails (`ISS-115`) | It splits money between the requester and the donors [A] | In-flight cells finish and accepted ones are paid; refund = unstarted primary pay + unspent pool + levy not earned; a partial `Deliverable` | `BM7` acceptance |
| `OD-24` | Minimum member age (`ISS-119`, in 11d) | An age rule is a legal question [V: counsel] | `identity.min_age_years` = 0; the age line is not rendered | Launch sign-off (copy review, `S3 OD-13`) |
| `OD-25` | A member-specific token to randomize V3 acquisition; any reward that moves money in Phase 2 (`ISS-124`, `ISS-127`) | It changes the measurement design, and money rewards are a legal question [V: counsel] | V1 measured from account creation to first verified cell; V2 randomizes only the in-app widget; V3 descriptive; no reward specified | `G1` sign-off; Phase 2 |
| `OD-26` | A cap on pilot size (`launch.max_members` would be new); the minimum number of G5 interviews (`ISS-179`, `ISS-141`) | The owner decides how large the pilot is and what counts as enough demand evidence [A] | Pilot size held by invite supply [A]; the tool records the interview count and the signers' attestation, with no minimum | Pilot invitations; `G5` sign-off |
| `OD-27` | Who acts on each alarm and in what interval; the method of the reachability test from Iran (`ISS-194`, `ISS-197`; `S19 OD-03`, `S19 OD-04`) | It depends on who is on the team, and a tester inside Iran may be at risk [V] | Every tripwire names who acts and the interval is left to the owner; the test is repeated before public exposure (`CHK-41`) and `launch.members_may_join` stays `false` | Launch sign-off; `G2` sign-off |
| `OD-28` | The ledger store under one serialization point (`ISS-43`) | It fixes where the ledger runs; the nearest existing decision is `S3 OD-03` (storage behind interfaces) [A] | One ledger, one chain; a capacity formula and a load test decide the store (S4 4.6.2) | Before the ledger store is fixed (S4 4.6.2) |
| `OD-29` | File names and heading numbers of S5 (`ISS-52`) | Assembly belongs to the owner, not to the part cells [A] | The cell path is authoritative; S5a numbers 5.1 to 5.16 | Assembly |
| `OD-30` | Whether `invite.strike_window_days` is split into a strike window, an issuing suspension and a tree-freeze window; whether `report.decision_sample_rate` has a floor (`ISS-16009`, `ISS-16020`) | A floor of 0 removes the second look at reports, and a split changes the invite rules [A] | One parameter with three roles (S10a may add `invite.suspension_days` and a freeze window later); range 0..1 as S10b states it, lowering is a loosening, no floor | Before the S16 seed runs; first report sampling |
| `OD-31` | The type, unit, range, default and public flag of `abuse.admin_lookup_rate`, and whether `session.admin_stepup_s` is an alias [V]; one name for the lifetime of a pending two-person approval (`ISS-16015`, `ISS-16017`) | No value may be invented, so the 11c owner or the owner supplies it [A] | The row has no value and none is invented; the 11c owner or C-036 supplies it before the seed runs (`AC-param-02`); `launch.approval_window_s` for the launch flow, the two `security.*` names left to their cell | Before the S16 seed runs (`AC-param-02`) |

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
| Free allowances cannot be transferred | [P] | FD§8.1 (also the example in S0.2) | S7.*, `CNS` |
| Simulation output is never evidence about people | [D] | Brief, scope K | S18.* |

## 3.5 When each decision is needed

| Needed before | Decisions |
| --- | --- |
| First deployment to a public address | `OD-03` |
| First sign-off or first template approval | `OD-02` |
| `G0` sign-off | `OD-01`, `OD-04`, `OD-17` |
| `G1` sign-off | `OD-12`, `OD-25` |
| Launch sign-off | `OD-13`, `OD-24`, `OD-27` |
| Public exposure | `OD-14` |
| `BM4` acceptance | `OD-10` |
| First Commons job and first publication | `OD-05` |
| `BM7` acceptance | `OD-09`, `OD-16`, `OD-23` |
| Pilot invitations | `OD-06`, `OD-26` |
| Pre-registration lock, before day 1 of Phase 1 | `OD-07`, `OD-11` |
| Never blocks the build | `OD-08` |
| First member invitation | `OD-15` |
| `G2` sign-off | `OD-27` |
| `G4` sign-off | `OD-19` |
| `G5` sign-off | `OD-26` |
| `BM8` acceptance | `OD-22` |
| First `S1` job | `OD-21` |
| Before `ff.job.reservations` is enabled | `OD-20` |
| Before any `P2` or `P3` row is added | `OD-18` |
| Before the ledger store is fixed (S4 4.6.2) | `OD-28` |
| Before the S16 seed runs | `OD-30`, `OD-31` |
| First report sampling | `OD-30` |
| Phase 2 | `OD-25` |
| Assembly | `OD-29` |

## 3.6 Cross-reference to S19.9

The series `OD-01`..`OD-12` of S19.9 and `OD-01`..`OD-14` of this part are numbered separately, and most equal numbers mean different decisions (`docs/audit/A13.md` findings 2 and 22; `ISS-195`). Neither series is renumbered. Prose that cites an id writes `S19 OD-nn` or `S3 OD-nn`. The last column is the spec's reading of which decisions are the same [A]; where this part holds the decision, this part is authoritative (`ISS-38`). The same table is in S19.9. [D]

| nn | `S3 OD-nn` means (3.2) | `S19 OD-nn` means (19.9) | Same decision? Counterpart |
| --- | --- | --- | --- |
| 01 | Operator jurisdiction, entity form, legal exposure | Build while G0 and G1 are open | No. `S3 OD-01` overlaps `S19 OD-05` (which counsel, in which jurisdiction); `S19 OD-01` has no S3.2 row (the exit-rule question stays with `ISS-31`, `ISS-171`, `ISS-192` and `ASM-26`) |
| 02 | Who reviews templates, services and policy; second reviewer and second sign-off | Second-reviewer rule for a template one founder wrote | Yes: `S3 OD-02` = `S19 OD-02` (this one is wider) |
| 03 | Hosting, storage, countries the service must be reachable from | Who is on call, who may engage a kill switch, alarm escalation | No. `S3 OD-03` = `S19 OD-08` (hosting and storage vendors); `S19 OD-03` = `S3 OD-27` |
| 04 | Which services to review first; fallback if none is Commons-capable | How the reachability test from Iran is run | No. `S19 OD-04` = `S3 OD-27`; `S3 OD-03` covers the countries (related); `S3 OD-04` is related to `S19 OD-06` (fallback and stop-loss) |
| 05 | The Commons backlog (author, license, target, sponsor label) | Which counsel, in which jurisdiction | No. `S3 OD-05` = `S19 OD-10` (a Commons sponsor or other source of Commons jobs); `S19 OD-05` overlaps `S3 OD-01` (jurisdiction and entity decide which counsel) |
| 06 | Reserve start | Stop-loss and fallback among FD§8.3 (i) to (iv) | No. `S19 OD-06` has no S3.2 row; `S3 OD-04` is related |
| 07 | Whether `ff.channel.human_review` is on | Keep, wrap or replace the existing panel | No. `S19 OD-07` has no S3.2 row; `S3 OD-19` (human review of the panel repository for G4) is adjacent |
| 08 | Whether platform-side sandboxed execution is ever allowed | Hosting and storage vendors | No. `S19 OD-08` = `S3 OD-03` |
| 09 | Who bears three costs the FD leaves open | Who advises on the threat model and member-facing notice | No. `S19 OD-09` has no S3.2 row; `S3 OD-12` (safety adviser reviews the retention numbers) is adjacent |
| 10 | Volunteer-handle derivation | A Commons sponsor or another source of Commons jobs | No. `S19 OD-10` = `S3 OD-05` |
| 11 | Founders' thresholds recorded before Phase 1 | Phase 1 thresholds and decision rules | Yes: `S3 OD-11` = `S19 OD-11` |
| 12 | Retention, logging and compelled-disclosure posture | Stance on legal demands for member data | Yes: `S3 OD-12` = `S19 OD-12` (this one also holds the `retention.*` numbers) |
| 13 | Who reviews the Persian and English copy | none | Not applicable: no S19 counterpart |
| 14 | Project name and public descriptor | none | Not applicable: no S19 counterpart |

`S3 OD-15` to `S3 OD-31` were added to 3.2 after the audit; only `S3 OD-27` matches an S19 decision. Decisions with no counterpart in either direction stay open with the defaults in their rows. [D]

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
