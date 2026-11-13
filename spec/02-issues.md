# 2. Issues found in the Founding Document, and resolutions

*Spec part 2 · owner cell C-028 (supersedes C-001) · consolidates the `## Issues raised` tables of the other parts · every finding below was checked against the text of the Founding Document draft v0.1 (FD) and cites the section it rests on. Nothing here is legal advice, and nothing here has been verified against any provider's terms or any law.*

## 2.1 How issues are recorded

- An issue is a conflict inside the FD, a gap that blocks an implementation, a rule that cannot be implemented or tested as written, or a conflict between the FD and the brief. Each has one resolution that every part applies. [D]
- A finding is listed only if the FD text it rests on was read and cited. Where the FD is silent the issue says “gap”, not “contradiction”. Items that were examined and found consistent are in 2.7, so the reader can see what was checked. [D]
- A resolution is a decision of this spec [D] unless it carries another tag. Where it introduces a number, the number is derived by a shown formula or is an `initial configurable default` already in S0.10.6.
- Where a resolution needs a name that S0 lacks, the name is listed in 2.8 as a convention gap (S0.1). Where a resolution would change an S0 decision, the issue says so and its status is `proposed` until the owner accepts it; until then every part uses the S0 text.

**Numbering.** `ISS-01`..`ISS-09` are the part-0 issues, kept with their ids and consolidated in 2.3. The findings of this part are numbered inside the three blocks inherited from the superseded first cell (S0.13): `ISS-11`..`ISS-19`, `ISS-21`..`ISS-29` and `ISS-31`..`ISS-38`, in order of severity and then of FD section. Blocks `ISS-41` onward belong to the later parts (S0.13). See `ISS-37`. [D]

| Severity | Meaning (S0.4) |
| --- | --- |
| `blocking` | Cannot be implemented as written |
| `major` | Changes a design |
| `minor` | Naming, wording, counting |

| Status | Meaning |
| --- | --- |
| `applied` | Already embodied in S0 or in the text of this spec |
| `proposed` | Resolution is applied by the parts until the owner accepts or replaces it |
| `needs_owner` | Rests on a decision only the owner can make; listed in S3.2 with the default used meanwhile |
| `accepted`, `rejected` | Set by the owner after review; none yet |

## 2.2 Register

| id | severity | FD ref | One-line finding | status | Detail |
| --- | --- | --- | --- | --- | --- |
| `ISS-01` | minor | prompt | `M0`..`M2` clash with build milestones | applied | 2.3 |
| `ISS-02` | major | FD§5.3, FD§8.3 | “Unknown is no” is safe only for permission-phrased flags | applied | 2.3 |
| `ISS-03` | major | FD§4.2, FD§4.3 | Do verification cells inside Commons jobs mint? | proposed | 2.3 |
| `ISS-04` | minor | FD§3.3, FD§4.3 | v times N is rarely a whole number of cells | proposed | 2.3 |
| `ISS-05` | minor | FD§4.3 | “Rework cell” is undefined | proposed | 2.3 |
| `ISS-06` | major | FD§4.6, FD§6.2 | Referral bonus has no funding source | proposed | 2.3 |
| `ISS-07` | major | FD§4.5, FD§4.8 | Escrow versus credit expiry | proposed | 2.3 |
| `ISS-08` | minor | FD§4.6 | No ledger operation seeds the Reserve | applied | 2.3 |
| `ISS-09` | major | FD§3.2, FD§4.2 | When donors are paid | proposed | 2.3 |
| `ISS-11` | blocking | FD§4.2, FD§5.4 R7, FD§8.3 | The exit rule can pass while no service can run a Commons cell, so nothing can mint | proposed | 2.4 |
| `ISS-12` | blocking | FD§2, FD§4.4, FD§5.5, FD§10 | The code-change template needs test execution; the FD forbids executing submitted content and quarantines code | proposed | 2.4 |
| `ISS-13` | major | FD§4.1, FD§4.3 | A fractional price against a one-credit unit | applied | 2.4 |
| `ISS-14` | major | FD§4.2, Principle 2 | “Every unit traces to a Commons cell” cannot be checked for fungible credit | proposed | 2.4 |
| `ISS-15` | major | FD§4.2, FD§4.7, FD§4.8 | “Redeemable capacity” is undefined, circular with φ, and the cap has no exhaustion rule | proposed | 2.4 |
| `ISS-16` | major | FD§4.3, FD§4.4 | v does not say who funds blanket redundancy or third executions, and the pool is fixed while the need is random | proposed | 2.4 |
| `ISS-17` | major | FD§4.4, FD§5.7 | No rule for credit already paid when a result is overturned or a member is banned | proposed | 2.4 |
| `ISS-18` | major | FD§4.5 | K ignores escrow and has no rule when earning would exceed it | proposed | 2.4 |
| `ISS-19` | major | FD§4.6, FD§9 | The Reserve cannot be seeded in Phase 0 under the launch gates | needs_owner | 2.4 |
| `ISS-21` | major | FD§2, FD§3.1, FD§4.4, FD§6.4 | “Reviewer” means two roles, and review cells pay a credit though they use no allowance | proposed | 2.5 |
| `ISS-22` | major | FD§4.2, FD§5.2 | Commons jobs have no requester, declarant or publisher | needs_owner | 2.5 |
| `ISS-23` | major | FD§5.3, FD§8.3 | G0 has 11 questions, the registry 7 flags; approval names a flag that does not exist; the region flag has no consumer | proposed | 2.5 |
| `ISS-24` | major | FD§5.3, FD§5.6 | M2 has no registry record and no proof of the model | proposed | 2.5 |
| `ISS-25` | major | FD§5.4 R3, FD§3.2 | R3 forbids links to open, yet the flow says “open the prompt”; the rule is not testable | proposed | 2.5 |
| `ISS-26` | major | FD§5.4 R8, FD§5.2 | R8 filters on topic, but no declaration or source of topic exists | proposed | 2.5 |
| `ISS-27` | major | FD§5.4 R9 | Which policy version the re-check uses, and who is paid for in-flight work | proposed | 2.5 |
| `ISS-28` | major | FD§5.5, FD§4.4 | The fixed card sentence is untrue for gold and Commons cells and for unreviewed data | proposed | 2.5 |
| `ISS-29` | major | FD§5.6 | The scope of the salted volunteer ID is undefined | proposed | 2.5 |
| `ISS-31` | major | FD§8.3 | The exit rule governs building; the brief says build everything and gate launch | applied | 2.6 |
| `ISS-32` | minor | FD§4.4 | Audit comparators for free text versus “no model-based judging” | proposed | 2.6 |
| `ISS-33` | minor | FD§4.5, FD§4.6 | “Expires quickly” is undefined; the default grant buys two cells | applied | 2.6 |
| `ISS-34` | minor | FD§4.8 | Deadline classes are undefined at a multiplier of 1.0 | applied | 2.6 |
| `ISS-35` | minor | FD§5.7 | “Two active profiles” does not match the axes it lists | proposed | 2.6 |
| `ISS-36` | minor | FD§6.1 | “Iran-based members are not shown by place” needs inference of location | proposed | 2.6 |
| `ISS-37` | minor | none | The cell instruction's issue numbering collides with S0.4 | applied | S1 |
| `ISS-38` | minor | none | S0 has no id scheme for assumptions and open decisions | proposed | 2.6 |

Counts: 9 part-0 issues, 2 blocking, 18 major in total across both groups, 14 minor in total; the rows above are the whole register. [D]
