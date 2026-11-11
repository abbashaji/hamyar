# 10. Safety, secrets, hosting and abuse process

*Spec part 10, second file (`10b`) · owner cell C-012 · prompt scope I · binding on every part that stores data about members, handles a secret, chooses a host or moderates. Written against Founding Document draft v0.1 (FD) and `spec/00-conventions.md` (S0.*). Nothing here is legal advice and nothing here has been checked against any law, provider term or host: every legal point is [V] for counsel, and every statement about the existing panel repo is [V] because it rests on a static reading (`docs/source/panel-review.md`, cited as "panel-review §n") in which nothing was executed.*

## 10.11 Scope, boundaries and how to read this file

**What this file decides (prompt scope I)** [D]

| Topic | Where | Reason |
| --- | --- | --- |
| Threat model table (`THR-nn`) | S10.12 | FD§8.3 G1 requires a written threat model before any build beyond a throwaway prototype |
| Member safety design, exact disclosure inventory, what the platform cannot promise | S10.13 | FD Principle 8; `RISK-05` (FD§8.2) |
| Secrets inventory, storage, rotation, rotate-before-exposure rule, launch-gate items | S10.14 | FD§10 step 1; FD§8.3 G4 |
| Hosting interfaces, reachability, low bandwidth, no third-party resources | S10.15 | FD Principle 7; `RISK-14` (FD§8.2) |
| Abuse reporting, takedown, ban and appeals | S10.16 | FD§5.5, FD§5.7 items 1 and 10 |
| Acceptance criteria, added parameters and enums, register of unverified items | S10.17 to S10.19 | prompt K; ground rules 2 and 4 |

**What this file does not decide.** Identity mechanics (keys, recovery key, sessions, invites, device linking, the permission matrix, the exact logged fields) belong to the identity file of S10.*. Where this file states a constraint on them it says "constraint on S10.*", and the stricter reading applies until assembly records a decision (`ISS-104`). [D]

**Reading rules** [D]

- Tags follow S0.2. Every `[V]` in this file is collected in S10.19 with who verifies it and where the answer is stored; every `[A]` is collected there with the owner decision that could overturn it.
- Names (entities, enums, states, events, parameters, error codes, ID formats) are used exactly as in S0.*. Names this file adds are listed in S10.18 and reported under `## Issues raised`.
- User-facing promises say "declared" and "minimization", never "anonymous", "private", "secure" or "guaranteed" (FD Principle 8 and 11). A copy lint for these words is `AC-safety-14`.
- Every number is derived by a shown formula, taken from the parameter table in S0.10.6, or listed in S10.18 as an `initial configurable default`.

### 10.11.1 Assets [D]

| Asset | Why it matters | Defended mainly by |
| --- | --- | --- |
| Member safety (physical, legal, social) | Participation may carry personal risk in Iran (`RISK-05`); safety outranks growth (FD Principle 8) | S10.13 |
| Unlinkability of a pseudonym from a person | The only privacy property the design tries to protect, and only as minimization, never as anonymity | S10.13 |
| Ledger integrity | Trust is the asset (FD Principle 11); every credit traces to an accepted Commons cell (FD§4.2) | `THR-12`, S6.* |
| Volunteers' provider accounts | A suspended or exposed account harms the volunteer, not the project | `THR-09`, `THR-31`, S7.* |
| Requesters' S0 and S1 inputs | A stranger reads them by design (FD§5.3 S1) but they must not carry personal data of others | `R1`..`R3`, `THR-07` |
| Secrets and signing keys | Their compromise defeats other controls | S10.14 |
| Reviewer and admin authority | Capture changes rules, flags, bans and parameters | `THR-13`, `THR-23` |
| Availability and reachability | Members who cannot reach the host cannot join (`RISK-14`) | S10.15 |

### 10.11.2 Actors [D]

| Actor key | Capability assumed | Motive considered |
| --- | --- | --- |
| `network_observer` | Sees traffic between a member's device and the host (ISP, local network, state-level monitoring); may block or throttle | Identify or block participants |
| `host_provider` | Controls the machines, disks, snapshots and provider-level network logs the system runs on, and can be compelled | Commercial, or compelled |
| `external_attacker` | Internet reach, commodity tools, phishing | Theft, disruption, credit |
| `volunteer_malicious` | A valid member who runs cells | Free credit, harvesting inputs, attacking requesters or reviewers |
| `requester_malicious` | A valid member who submits jobs | Evade policy, inject, extract volunteers' data |
| `other_member` | Any member, sees only what the product shows | Curiosity, harassment, de-anonymization |
| `reviewer_insider` | `AdminUser` with the `reviewer` role | Error, bribery, coercion, capture |
| `operator_insider` | `AdminUser` with the `operator` role; deploy and database reach | Abuse of power, coercion |
| `authority` | Legal power in some jurisdiction over the operator, the host or a member | Obtain data, stop the project |
| `provider_service` | The AI service a volunteer uses (outside this system) | Account enforcement, data use |

### 10.11.3 Trust boundaries (text diagram) [D]

```
 member device (key pair, session token)
    |  TLS only, no third-party hosts                       <- network_observer sees this hop
    v
 edge / TLS terminator (optional adapter, S10.15)           <- sees plaintext requests and IPs if it terminates TLS
    |
    +--> app, member surface /v1/*        --> database (roles: app, ledger_append, readonly, migrate)
    +--> app, public surface /v1/public/*  --> cached aggregates only
    +--> admin origin /v1/admin/* (separate origin, WebAuthn, two-person actions)
 member device --human copy, Send, paste--> provider_service     <- OUTSIDE this system; never automated, never read
```

### 10.11.4 Priority order and residual-risk scale [D]

Priority when objectives conflict: (1) member safety, (2) ledger integrity, (3) integrity of verification, (4) confidentiality of S0 and S1 inputs, (5) availability. Reason: FD Principle 8 ("a growth tactic that endangers members loses"), FD§6.1 rank 5, FD Principle 11.

| Residual risk | Meaning | Required handling |
| --- | --- | --- |
| `low` | The control works unless there is a bug or an unrelated compromise; an `AC-safety-nn` case tests it | Monitor |
| `moderate` | A determined, resourced actor still partly succeeds; detection and a bounded loss exist | Alarm and a named owner |
| `high` | Cannot be reduced inside this design | Members are told in plain words (S10.13.7); the founders record acceptance (code `SEC`) as evidence on the G1 `LaunchGateItem`; without it G1 stays open |

