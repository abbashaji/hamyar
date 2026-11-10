# Blueprint Panel: source review (facts only)

Repo reviewed: /home/claude/abbashaji/panel (read-only; single git author, `git log` has 1 commit in the clone).
Method: static reading. NOTHING was executed, deployed or tested by me. Line numbers are from the files as cloned.
Sections 1-7 and 9 are facts or explicit "could not determine". Section 8 is opinion and is marked as such.
No secret values were found in tracked files (see 4.7 for the only secret-looking strings).

## 1. Stack and layout

Runtime: Cloudflare Worker, TypeScript, `nodejs_compat`, compat date 2026-08-01 (wrangler.toml:1-4). Name `blueprint-mcp`.
Deps (package.json): `@cloudflare/workers-oauth-provider`, `@modelcontextprotocol/server`, `agents` (only `createMcpHandler` is used, src/index.ts:4), `yaml`, `zod`.
Web: React 18, Vite, Tailwind 4, Radix, `@xyflow/react`, dagre, TanStack Query, Vitest (web/package.json). Launcher: C# .NET 8 WinForms (launcher/App/App.csproj:6).
The repo was built by its own cell system: 88 cell files `cells/C-*.yaml` (C-060 absent), `blueprint.yaml`, `BLUEPRINT.md`.

Worker (src/):
- index.ts: entry. `/panel/*` answered first by panel router, everything else goes to `OAuthProvider` (apiRoute `/mcp`, endpoints `/authorize`, `/token`, `/register`) (index.ts:18-34).
- auth.ts: OAuth default handler: `/health`, `/ext/*` passthrough, owner-consent `/authorize` page (password = MCP_AUTH_TOKEN) (auth.ts:38-76).
- tools.ts: `Env` type, MCP tool registration (24 tools), repo allow-list wrapper, steward and self-heal handler sets, LIMIT_WARNING wrapper.
- engine.ts: facade; init_blueprint, read_files, submit_cell, preflight, ci_result, checkAdmin, resolveRepo, publishPlan.
- plan.ts (815 lines): config/cell loading, validation, graph helpers, `computeState()`, `parseRuns`, `claimsFromBranches`.
- claim.ts: tryClaim, tryTakeover, next_cell (plain, pinned, peek), KV reservation helpers.
- apply.ts: apply_changes (fenced commits). signal.ts: cell_signal heartbeat/release/feedback. takeover.ts: owner/steward takeover.
- common.ts: plan cache, freshSnapshot, cleanPath, mergedOf. resume.ts: RESUME text. trailers.ts: commit-message trailers.
- github.ts / api.ts: `GitHubApi` interface and its GitHub implementation (one GraphQL snapshot query plus REST writes). github.ts is not covered against real GitHub (docs/panel-integration.md:15).
- steward.ts, steward_code.ts, takeover.ts, signal.ts: "Steward" role (lease branch `steward/lease`), one-time start codes, `authorizeSteward`.
- selfheal.ts, selfheal_fix.ts: `cell_help/note/sync/clear/fix` tools, authority = cell_id + base + live lease, no admin key.
- ext.ts: legacy `/ext/ping|release|warn` for the retired browser extension; 404 unless secret `EXT_TOKEN` is set (ext.ts:148).
- longpoll.ts: next_cell with bounded wait (max 60 s, max 6 polls) (longpoll.ts:9-12). protocol.ts: agent RULES text. kit.ts: GENERATED embed of the kit files `init_blueprint` installs into other repos (kit.ts:1). zip.ts: not read in detail.
- panel/router.ts: routes `/panel/*` (login, authenticated JSON API, static SPA via `ASSETS`). panel/auth.ts: login, cookie, rate limit. panel/state.ts: builds `PanelState`. panel/actions.ts: reserve, release, clear-feedback, steward-release, steward-code. panel/types.ts: shared types (also imported by web).

web/src (structure): `core/` (typed API client api.ts, store, status mapping, mock data, storage wrappers), `graph/` (dagre LR layout + cards + bottleneck banner), `inspector/` (cell details, ReleaseDialog), `shell/` (header, sidebar, repo switcher, palette, steward chip, activity panel), `table/` (table + timeline), `launch/` (blueprint:// URL builders protocol.ts, start/startmany dialogs, OwnerKeyDialog, auto-send help), `e2e/fakeWorker.ts`. `web/public/blueprint-autosend.user.js` is the opt-in userscript (337 lines). SPA is built flat into `web/dist` (gitignored) and served by Workers Static Assets (wrangler.toml:25-28).

launcher/: `Core/` (ProtocolParser, PromptBuilder, LaunchCommand, BrowserCatalog/Profiles/ExeLocator, CellRecords, LauncherSettings), `App/` (WinForms: Program, StartForm, StartManyForm, OpenForm, Theme), `Core.Tests/` (xUnit), `install.ps1`, `build-install.ps1`.
tools/ (Python, run in CI, embedded into target repos): blueprintlib.py (625 lines, reference graph logic), cell_gate.py (merge gate), next_cell.py (CLI reference of next_cell), validate_graph.py.
scripts/: release.sh / release.ps1 (test, build, secret-name check, deploy), e2e-smoke.mjs (needs a live Worker), embed_kit.py.
docs/: panel-contracts.md, panel-design.md, panel-integration.md, decisions.md, autosend.md, deploy.md, e2e-runbook.md, e2e/*, design/*.png, blueprint-mcp-README.md.

## 2. Data model and storage actually used

There is NO database. grep for D1, R2, Durable Objects, cron/scheduled: no hits in src/ or wrangler.toml. The only Cloudflare binding besides assets is one KV namespace.

2.1 Git as state (GitHub repo(s) named in each call; one `GITHUB_TOKEN` for all)
- Plan: `blueprint.yaml` (project config) and `cells/C-NNN.yaml` (immutable cell specs) on `main` (plan.ts:117-142, engine.ts publishPlan "cells are immutable").
- Cell lock/lease: branch `cell/C-NNN`; tip commit's `committedDate` = heartbeat (api.ts BranchInfo comment; plan.ts:804-813). Lock commit subjects: `claim(C-NNN): lock <uuid>`, `takeover(...)`, `adopt(...)` (claim.ts:14-32). Other subjects: `hb(...): alive`, `release(...): ...`, `feedback(...): ...`, `WIP: ...` (apply.ts:62), `sync(...)`, `heal(...)`, `steward(C-NNN): note` (signal.ts, selfheal.ts, trailers.ts).
- Commit-message trailers carried forward: `next:`, `attempt:`, `req:`, `held:` (trailers.ts:1-40, 85-90).
- Done = a commit on main whose subject matches `cell(C-NNN)` (plan.ts SUBJECT_RE; mergedFromSubjects) OR a merged PR (title/head ref) read by GraphQL (github.ts:59, 226-241). History window = HISTORY_PAGES x 100 commits (wrangler.toml:23).
- Steward role: branch `steward/lease`; planning lock: branch `steward/plan-lock`, 90 s lease (steward.ts:23, selfheal_fix.ts:17-18).
- Branch listing is `refs/heads/cell/` first:100 plus up to 5 more pages (github.ts:62, 207-213).
- Merge result return: artifact `test-results/output.log` of a workflow run (see 5).
- Worker writes straight to `main` with non-force ref updates in `init_blueprint` and `publish_plan` (engine.ts:46-52, 326-363); requires the token to be allowed to push main.

2.2 KV namespace binding `OAUTH_KV` (id in wrangler.toml:9; a resource id, not a secret)
Keys written by this code (exact names):
- `reserve:<owner/repo>:<C-NNN>` = JSON `{who, at}`, TTL 600 s (claim.ts:42, 61-78). Advisory.
- `warn:<repo>:<cell>` = JSON `{at, resets_at}`, TTL 1800..21600 s (ext.ts:34, 107-134). Advisory flag appended as LIMIT_WARNING.
- `panel-login-fail:<cf-connecting-ip|unknown>` = failure count, TTL 900 s (panel/auth.ts:90-100, 120).
- `stewardcode:<repo>:<sha256 hex of code>` = "1", TTL 600 s (steward_code.ts:35-45).
- `stewardcode-rate:<repo>:<minute-bucket>` = count, TTL 120 s (panel/actions.ts:178-181).
- `steward-seen:<repo>` = JSON array of problem cell ids, TTL 86400 s (tools.ts:134-144).
- Plus keys owned by `@cloudflare/workers-oauth-provider` (clients, grants, tokens). Their layout is the library's; I did not read it.

2.3 In-memory (per Worker isolate, lost on restart)
- Panel state cache keyed `<repo>@<main>`, valid while main oid + all cell-branch tips are unchanged AND age < 60 s (panel/state.ts:28-30, 178-185). `reservedBy` and steward status are recomputed on every call (state.ts:156-162).
- Plan cache, 20 entries, key `repo@mainOid@mainBranch` (common.ts planCache).
- Login-failure fallback map when KV throws (panel/auth.ts:78).

2.4 Browser (panel): localStorage keys `bp_who`, `bp_repo`, `bp_repos`, `bp_theme`, `bp_panels`, `bp_own`, `bp_show_replaced` (web/src/core/store.tsx:112-114,179; shell/Header.tsx:12; launch/index.tsx:10-11) and, optionally, `bp_owner_key` (see 4.5).

2.5 Wire shapes: `PanelState` / `PanelCell` in src/panel/types.ts (state fields include status, critical, wave, depends, blockedBy, directDependents, transitiveDependents, sha{lock,tip,merged}, lease, attempts, lastCommit, reservedBy, pr, resumable, supersededBy, heals, stalled, steward, healLog). `sha.merged` is always `null` (state.ts:321).

## 3. Cell / lease / status semantics as implemented

3.1 Status values (panel/types.ts:3-10; state.ts:262-269): `done`, `running`, `ready`, `expired`, `waiting`, `needs_human`, `needs_split`.
Computed per request from git by `computeState()` (plan.ts:640-727); nothing stores a status.
- waiting: any hard dependency not merged (kind `implementation` and `after`; `contract` inputs do not block) (plan.ts:681-689, hardGraph).
- needs_human: cell is `feedback` (tip is a `feedback(` commit) and no blockers (plan.ts:690-693).
- running (locked): branch exists and tip age < lease, OR a workflow run for the cell is active and younger than `max_ci_minutes` (plan.ts:699-705). Run->cell id comes from head branch or run title `gate cell/C-NNN` / `preflight C-NNN` (plan.ts:32, 780-793).
- needs_split: expired (not released) and `attempt:` >= `max_attempts` (plan.ts:706-707).
- ready: unclaimed; `expired` (reclaim=true): lease over; also ready when tip is a `release(` commit (plan.ts:701, 709).
- superseded cells (`supersedes:`) stay `waiting` and are excluded from counts (panel/state.ts:228-231, 340).

3.2 Timeouts (defaults plan.ts:45-58; this repo's blueprint.yaml sets lease_minutes 60, max_ci_minutes 45, bottleneck_threshold 4, max_attempts default 3)
- Lease = cell `lease_minutes` or project `lease_minutes` (60); critical cells capped at `critical_lease_minutes` (15) (plan.ts:699-700).
- Critical = direct dependents >= `bottleneck_threshold` (4), or chain length-1 >= 3, or transitive >= 5 (plan.ts:667-669).
- CI keeps the lease alive up to 45 min (plan.ts:703-705).
- Reservation TTL 600 s (claim.ts:42). Steward start code TTL 600 s (steward_code.ts:12). Steward lease uses project lease_minutes (steward.ts via leaseMinutesOf).
- Hand-out order: class 0 = expired critical or released; class 1 = fresh or expired >= `park_max_minutes` (120); class 2 = younger expired non-critical; then priority desc, chain depth desc, id (plan.ts:711-722).

3.3 Who enforces: nobody actively. There is no scheduler. Expiry is evaluated lazily whenever someone calls next_cell/ready_cells/state, from the branch tip's committed date (plan.ts:804-813). Hard enforcement is git itself:
- Claim: each claimer creates its own lock commit then `POST git/refs`; GitHub refuses a second create, so one wins (claim.ts:14-19; github.ts:307-309).
- Fencing: writes need `base` = 7+ hex of current tip; `PATCH git/refs ... force:false` fast-forward only (apply.ts:73-75, 94-98; github.ts:314-317). A stale chat gets CONFLICT.
- takeover of expired lease: one new commit on the old tip + fast-forward; attempt counter +1 only for `takeover`, not `adopt` (claim.ts:21-32).
- Path rules: ops limited to the cell's `allowed_paths`, never `protected_paths` (default protects `cells/**`, `blueprint.yaml`, `BLUEPRINT.md`, `tools/**`, `.github/**`, `acceptance/**`, `docs/decisions.md`; plan.ts:36-44); apply.ts:87-88. Limits: 30 ops/call, 200 kB/file, 400 kB/call (apply.ts:20-22).

3.4 Release / hand over
- Agent side: `cell_signal kind=release` -> empty commit `release(C-NNN): <text>` with required `next:` (signal.ts:22-24, 45-55). Cell is expired at once, served first (plan.ts:701, 711-717).
- Owner side (panel "Release"/"Hand over"): `POST /panel/api/release` -> `takeover(handoff:true)` -> empty commit `release(C-NNN): handoff` fast-forwarded onto the tip (panel/actions.ts:113-116; takeover.ts:43-51). Success text must start `RELEASED` or `RESUME` (actions.ts:229).
- The panel never passes `force`, so takeover.ts:27-37 returns `CI_RUNNING` while a workflow for the cell is active (<45 min). A cell with feedback returns `NEEDS_HUMAN` unless `clear_feedback` (takeover.ts:39-42; panel route `/clear-feedback`).
- Release also deletes the KV reservation; with no branch it answers `UNRESERVED <cell>` (actions.ts:229-253).
- Pinned claim (`next_cell cell_id=`): claims exactly that cell or replies `NOT_READY <id> <reason>` / `RESERVED <id> by <name>`; never falls back (claim.ts:175-200). RESERVED only if both reservation.who and caller `who` exist and differ (claim.ts:187). The launcher prompt has no `who` (PromptBuilder.cs:17-20), so a launcher-pinned call does not hit RESERVED (acknowledged: panel-integration.md:20, panel-contracts.md:168).
- Plain next_cell skips reserved cells (claim.ts:215-219).
- Reserve endpoint needs only the panel cookie (no admin key) and any `who` matching `^[\w .-]{1,40}$` (actions.ts:164-168, 203-205).

3.5 Bottleneck (panel): not-done, non-superseded cell with max transitive dependents (>0) (state.ts:341-345).

## 4. Auth and the four secrets

Overview of entry points
- `/panel/api/login`: password vs `PANEL_TOKEN`, constant-time via SHA-256 hash compare (panel/auth.ts:131; auth.ts:19-28 same technique).
- `/panel/api/*` other: cookie `bp_panel` required (router.ts:34).
- `/mcp`: OAuth 2 through workers-oauth-provider; consent page checks MCP_AUTH_TOKEN; issued grant has `userId: "owner"`, `props: {}`, scope `mcp` (auth.ts:62-71; index.ts:25).
- `/ext/*`: bearer EXT_TOKEN, off if unset (ext.ts:148-150). EXT_TOKEN is a fifth secret not in the README's "four".

4.1 PANEL_TOKEN (panel login password)
- Read: panel/auth.ts:39 (makeSession), 45 (verifySession), 119 (503 if unset), 131 (compare). Declared panel/types.ts:151-153.
- Also the HMAC key of the session cookie: value `"<exp-seconds>.<hmac-sha256-hex>"` over `bp_panel.<exp>` (panel/auth.ts:38-51). Cookie: HttpOnly; Secure; SameSite=Strict; Path=/panel; 12 h (auth.ts:52-53; SESSION_SECONDS :6).
- Logged: no `console.*` anywhere in src/ (grep: 0 hits). Never echoed.
- Failure limit: 5 failures per 900 s per `cf-connecting-ip` key (auth.ts:8-9, 120-123).

4.2 ADMIN_TOKEN (owner key)
- Read: engine.ts:289-299 `checkAdmin` (fails closed when unset); steward_code.ts:77-95 `authorizeSteward`; panel/actions.ts:168 (release, clear-feedback, steward-release, steward-code gate); tools.ts:23,103,183 (redaction lists).
- Panel flow: `admin_key` typed into a dialog and sent in the POST body per action; compared in constant time (actions.ts:166-169). Not logged or echoed (actions.ts:3, 174 comments; no logging calls).
- Used by MCP tools `takeover` and `publish_plan` (tools.ts:82-83) and optionally `steward_*`.

4.3 GITHUB_TOKEN
- Read: tools.ts:40 (every MCP tool), panel/actions.ts:45,190, panel/state.ts:168, ext.ts:175. Sent as `Authorization: Bearer` only from github.ts:107.
- Error text masks the token: github.ts:136 (`fail()`); steward `redact()` strips `gh[pousr]_...`/`github_pat_...` patterns (steward.ts:392-398); ext.ts:37-45 `safeDetail`.
- Scope of the token: NOT determinable from code. Repo scope is chosen by `ALLOWED_REPOS`.

4.4 MCP_AUTH_TOKEN (connector consent password)
- Read: auth.ts:45 (500 if unset), 62 (compare). Also in redaction lists tools.ts:103,183 and ext.ts:146.
- Not logged. The 401 re-renders the consent form (auth.ts:62-64).

4.5 Weaknesses visible in code (each is an observation, with the code that shows it)
1. Single shared password for the whole panel; no user identity. `who` is a free-text display name typed in the browser (actions.ts:203-205; Header.tsx WHO_KEY). Reservation, and thus ownership display, is self-declared.
2. Session cookie is stateless and not revocable except by rotating PANEL_TOKEN (panel/auth.ts:38-51). It is not bound to a user, IP or device.
3. Login rate limit is read-then-write on KV (panel/auth.ts:80-100), so concurrent attempts can exceed 5 (KV is eventually consistent per panel-integration.md:23). Requests lacking `cf-connecting-ip` share one bucket "unknown" (auth.ts:120).
4. No failure counter on the admin key: release/clear-feedback/steward-release can be retried unlimited times by anyone holding a valid cookie (actions.ts:150-169; the only limiter is on steward-code, actions.ts:21,178-181). No limiter on POST `/authorize` password attempts in this repo's code (auth.ts:52-72); the library's behaviour is unknown to me.
5. Admin key can persist in `localStorage` key `bp_owner_key` when the user ticks "remember" (web/src/launch/OwnerKeyDialog.tsx:4-5, 38-45; launch/index.tsx:495). This contradicts "never stored in the page or cookie" (panel-contracts.md:54; README.md deploy step 1).
6. Legacy Steward prompt tells the chat "ask me to paste [the admin key]" (launcher/Core/PromptBuilder.cs:60-69), which would put ADMIN_TOKEN into a claude.ai transcript. The newer prompt uses a one-time code instead (PromptBuilder.cs:72-83). The code itself is placed in the `claude.ai/new?q=` URL (PromptBuilder.cs:79,85-86), i.e. in browser history/URL for up to 10 min; it is single-use and stored only as SHA-256 (steward_code.ts:39-59). The sync consume is get-then-delete, not atomic (steward_code.ts:52-54).
7. All MCP clients that pass consent are the same principal `owner` with the full tool set (auth.ts:65-71). Dynamic client registration endpoint `/register` is enabled (index.ts:25).
8. `ALLOWED_REPOS = "abbashaji/*"` (wrangler.toml:19) with one GITHUB_TOKEN: every repo of that owner reachable by any consented MCP client or logged-in panel user (engine.ts:302-321).
9. `cell_fix` lets any holder of a live cell + `base` publish new cell files to `main` without the admin key (selfheal_fix.ts header 1-6; publishPlan engine.ts:326-363). Cell `acceptance` strings are executed with `subprocess.run(cmd, shell=True)` in CI (tools/cell_gate.py:100-103) with a read-only token (cell-checks.yml:141 area) but with network. Validation of cell content is structural (plan.ts:410-424: non-empty command), I saw no allow-list of commands.
10. The panel exposes `sha.tip` (the fencing `base`) of every branch to every panel user (state.ts:321; types.ts `sha`). Writing with it still needs an MCP OAuth grant (item 7).
11. `read_files` with no `cell_id` reads any path on `main` of any allowed repo, only path-sanitised (engine.ts:58-110, common.ts:100-108).
12. Static `/panel/` HTML is served without auth by design (router.ts:3-17); no CSP / security headers are set on panel responses (grep for CSP/X-Frame in src: only auth.ts:15). web/index.html loads Google Fonts from googleapis/gstatic.
13. CI: `cell-gate.yml` is `pull_request_target` (cell-gate.yml:14) and its `verdict` job has `contents: write` and merges (cell-checks.yml:159, ~212-225). Agent code runs only in the `accept` job (read-only token, `persist-credentials: false`) per the design comments (cell-checks.yml:80-89).
14. Lease clock = branch tip `committedDate` (plan.ts:804-813). Who sets that date for API-created commits is GitHub's; I could not confirm from code.
15. `.github/blueprint-setup.sh` is run from the trusted checkout inside the work dir for each acceptance job and runs `npm ci` / `npm install` on agent-controlled `package.json` (blueprint-setup.sh, install() function, lines ~16-27). Lifecycle scripts of agent-supplied dependencies would run in the `accept` job (no secrets there per the design).

4.6 What is logged / returned
- Worker: no `console.*`; Cloudflare `[observability]` is not configured in wrangler.toml (so default platform behaviour; I cannot say what Cloudflare retains).
- Tool errors returned to the agent: `ERROR: <message first 400 chars>` (tools.ts:45). Panel errors: JSON `{error: <=200 chars>}` (router.ts:41-43).
- Launcher: `launcher.log` in `%LOCALAPPDATA%\BlueprintLauncher`, one line per REJECTED sync (time + reason, never the URL), capped 64 kB (App/Program.cs:12-13,72-96).
- Userscript: one `console.info` per decision, never prompt/q/repo names (autosend user.js:46-47 comment).

4.7 Secret-looking strings found in tracked files (values NOT reproduced)
- web/src/e2e/fakeWorker.ts:7: a fake admin key constant in a test fixture.
- wrangler.toml:9: the KV namespace id (infrastructure id, not a credential).
- No `.env`, `.dev.vars` or key files tracked (git ls-files check). No `ghp_`/`github_pat_` patterns outside test assertions and redaction regexes.

## 5. Result return path as implemented

There is no output storage of its own. Returns are:
1. Code/work output = commits on branch `cell/C-NNN` via `apply_changes` (apply.ts), later a squash-merge to `main`.
2. `submit_cell` opens a PR titled `cell(C-NNN): <title>`, body = agent summary (<=2000 chars) (engine.ts:151-185).
3. `preflight` dispatches workflow `cell-preflight.yml` (engine.ts:188-202); real gate runs on `pull_request_target`.
4. CI verdict: job `verdict` writes one `summary/output.log` and uploads artifact `test-results` (cell-checks.yml:~190-205). `ci_result` waits up to 90 s (default 45, poll 5 s), finds the newest run by title `gate|preflight C-NNN`, downloads artifact `test-results/output.log` and returns its text (engine.ts:209-285). Failures also commented on the PR (cell-checks.yml ~ "Comment failure on the PR").
5. Gate merges with `gh pr merge --squash --delete-branch --match-head-commit <sha>`, up to 6 attempts, then dispatches `validate-plan.yml` (cell-checks.yml:~222-235). `ci_result` returns `MERGED #n`, `MERGE_PENDING`, `MERGE_RETRY` (re-runs failed jobs) or `MERGE_STUCK` (engine.ts:262-285).
6. Panel sees results only through git state (status `done` when merged, PR number/state, last commit subject + `next:`), refreshed by polling (contracts say 5 s, panel-contracts.md:158; client polling interval itself not checked by me). `sha.merged` is null (state.ts:321).
7. Agents receive replies as plain text from MCP tools; panel actions return `{ok, result<=200 chars, cell?}` (actions.ts:228-253).
8. Result of the Windows launcher: none returned to the Worker (offline). A pasted chat link is stored locally only (6).

## 6. Launcher

6.1 Protocol: custom scheme `blueprint://`, registered under `HKCU\Software\Classes\blueprint` with command `"<exe>" "%1"` (launcher/install.ps1:20,40-45). No admin rights. Commands (ProtocolParser.cs:6,34-38, 80-88): `start` (repo, cell, who), `open` (repo, cell), `sync` (repo, merged=C-..,..), `startmany` (repo, who, cells<=12 distinct), `steward` (repo, who, optional code). `steward` is NOT in docs/panel-contracts.md section 4 (only in code and web/src/launch/protocol.ts:50-56).
Validation: ASCII only, no whitespace/control, no `#`, exact key sets, no duplicates, repo/cell/who regexes, length 400 (2000 for sync) (ProtocolParser.cs:28-30, 41-47, 56-110). Browser argument is passed as an argument list, not a shell string (LaunchCommand.cs:3-12; Program.cs:`Run` with `UseShellExecute=false`).
6.2 What it opens: a Chromium-family browser (chrome, edge, brave, yandex) with `--profile-directory=<folder> <url>`; Opera: URL only; Firefox: `-P <profile> <url>` (LaunchCommand.cs:16-34). Host is fixed `https://claude.ai/new?q=` (PromptBuilder.cs:9; LaunchCommand.cs:42-50). Profiles listed from the browsers' `Local State` (`profile.info_cache`: folder, name, theme colour; avatar file path) (BrowserProfiles.cs:20-80). Browser exe from registry / standard dirs (BrowserExeLocator).
6.3 Prefill URL: prompt built locally from a fixed template with only validated repo and cell inserted, `<`/`>` stripped, `Uri.EscapeDataString`:
`Repo: {repo}\nFollow BLUEPRINT.md.\nCall next_cell with repo and cell_id={cell} (reserved for me).\nDo only that cell. Begin your next message with the CLAIMED line.` (PromptBuilder.cs:11-24,98). `who` is not in the prompt. The user sees a confirm window with the prompt and picks a profile before launch (StartForm.cs:63,201). The user must press Send, unless auto-send is on.
6.4 Auto-send (opt-in, default off): appends `&autosend=1` only to a URL that exactly equals `BuildUrl(repo,cell)` (PromptBuilder.cs:27-57). The click is done by a separate userscript for `https://claude.ai/new*`: strict template regex, allow-listed repos in GM storage `bp_allowed_repos`, 3 s cancel countdown, max 12 sends per 10 min (user.js CONFIG lines ~19-37). Never applied to the Steward (StartForm.cs:197 `!_steward`).
6.5 What it stores (all under `%LOCALAPPDATA%\BlueprintLauncher\`): `cells.json` (per "<repo> <cell>": browser, profileFolder, profileName, startedAt, optional chatUrl matching `^https://claude\.ai/chat/<36 hex/dash>$`; purged when merged via `sync` or after 14 days) (CellRecords.cs:5-62); `settings.json` (only `autoSend`) (LauncherSettings.cs); `last-choice.txt` (browser + folder) (Program.cs:`SaveLastChoice`); `launcher.log` (rejected sync reasons). It does not persist the Steward code (the StartForm shows it masked; PromptBuilder.cs:89-93).
6.6 Network: "opens no network connection" is asserted by a test that scans launcher sources for `System.Net`, `HttpClient`, `Socket`, `WebClient` and by Core having no PackageReference (Core.Tests/NoNetworkTests.cs). The browser it starts of course connects.
6.7 Inconsistency: decisions.md:8 and panel-contracts say "self-contained single exe", `build-install.ps1` publishes `--self-contained false` (build-install.ps1:~21); App.csproj makes self-contained only with `-p:BlueprintPublish=true` (App.csproj:14-22). build-install's optional `--self-test` branch is skipped because no source mentions it (grep: only the script itself).

## 7. Tests and CI present

7.1 Worker tests: `npm test` = `node --test test/*.test.ts` (package.json). 40 test files in test/ (about 660 `test(`/`it(` occurrences by grep count, not a run result) against `test/fakegh.ts`, an in-memory GitHub fake (418 lines), plus `test/fixtures.json.gz` + `test/gen_fixtures.py` for Python/TS parity (test/parity.test.ts, panel_parity.test.ts). Areas: engine, claim/pin/reservation, trailers, apply, steward, selfheal, ext, longpoll, panel auth/state/actions/integration, adversarial.
`test/contracts.test.ts` is skipped when sibling folders `blueprint-kit`/`blueprint-limit-ext` are absent (contracts.test.ts:8-13).
7.2 Web tests: Vitest in web/src (`*.test.ts(x)`, jsdom), incl. `integration.test.tsx`, `e2e/app.integration.test.tsx` with `fakeWorker.ts`. Userscript test: web/src/userscript/autosend.test.ts.
7.3 Launcher tests: xUnit, 7 test classes, about 116 `[Fact]/[Theory]` by grep (launcher/Core.Tests).
7.4 Smoke: scripts/e2e-smoke.mjs needs a live Worker + env (WORKER_URL, PANEL_PASSWORD, REPO). docs/e2e-runbook.md + docs/e2e/E-00x.yaml are manual runbooks.
7.5 GitHub workflows (.github/workflows): `cell-gate.yml` (PR gate), `cell-checks.yml` (reusable: plan / accept matrix / verdict+merge), `cell-preflight.yml` (dispatch), `validate-plan.yml` (push main: `python tools/validate_graph.py --waves`). There is NO workflow that runs `npm test`, `web` tests or `dotnet test` on push/PR as such; those run only as per-cell `acceptance` commands inside the gate (e.g. cells/C-001.yaml:28-30). The Worker/web/launcher test suites are therefore not run for human PRs to this repo by any workflow here.
7.6 Release: scripts/release.sh runs test/build/secret-name check then `wrangler deploy` (release.sh:18-50).

## 8. Reusable / wrappable / replace for a public multi-user commons (OPINION, not fact)

Likely reusable as-is
- Cell DAG model and `computeState` (plan.ts) and its Python twin (tools/blueprintlib.py) with parity fixtures: a compact, tested scheduler that needs no DB.
- Git-as-lock pattern: unique lock commit + create-ref, fast-forward fencing with `base` (claim.ts, apply.ts).
- Gate design: trusted plan/tools checkout, untrusted code in a no-secret job, merge `--match-head-commit` (cell-checks.yml).
- Launcher URL parser/validator and fixed-template prompt (ProtocolParser.cs, PromptBuilder.cs) and its tests; graph UI (web/src/graph) and status colour/label system.
- `redact()`, constant-time compare helpers, bounded bodies.

Wrappable (keep, put a layer around)
- `GitHubApi` interface (api.ts) is a clean seam: a wrapper could back it with per-user/per-repo GitHub App installation tokens instead of one PAT.
- `toolHandlers`/`buildServer` could sit behind a per-user MCP auth proxy; `resolveRepo` could become a policy callback.
- Panel `buildPanelState` is pure over a snapshot; usable behind a read-only public view.

Likely must be replaced for a public multi-user commons
- Identity and auth: shared PANEL_TOKEN, shared MCP_AUTH_TOKEN, single `owner` principal, self-declared `who`, stateless unrevocable cookie, no per-user rate limits or audit. Needs real accounts/OAuth (e.g. GitHub login), per-user grants, revocation, per-user quotas.
- Admin key model (one ADMIN_TOKEN typed into the browser, optionally kept in localStorage) -> role-based authorization.
- Single GITHUB_TOKEN with owner-wide `ALLOWED_REPOS` -> per-project, least-privilege tokens or GitHub App.
- Reservation in eventually consistent KV keyed by display name -> authoritative store (e.g. Durable Object/DB) keyed by user id.
- `cell_fix` / `publish_plan` trust model and `shell=True` acceptance commands: for untrusted public contributors these need sandboxing, command allow-lists or review before cells reach `main`.
- Lazy, read-time lease expiry with per-request GitHub GraphQL + per-cell REST calls (state.ts:272-306 does `findPr` and up to 5 commit pages per cell) will not scale to many users/projects; needs caching/webhooks/a store.
- Windows-only launcher dependency for "start a cell"; browser-profile coupling; reliance on claude.ai `?q=` prefill and a selector-based userscript.
- No observability/audit config, no security headers, no CI for the repo's own test suites.

## 9. Things I could NOT determine

- Whether anything has ever run against real GitHub or a deployed Worker: docs/panel-integration.md:58-68 says not; I did not verify live.
- Whether `/panel/*` routing next to `OAuthProvider` works when deployed (docs say not verified).
- Internal behaviour of `@cloudflare/workers-oauth-provider` (KV key layout, rate limiting on `/authorize` and `/token`, token lifetimes, DCR restrictions, whether `props: {}` is fine).
- Scopes/type of the real GITHUB_TOKEN, and whether `main` is branch-protected (the Worker pushes to main in init_blueprint/publish_plan).
- GitHub behaviour: `committedDate` semantics for API-made commits, GraphQL schema fit for the merged-PR query, rate-limit headroom, 100-branch/5-page limits in practice.
- Cloudflare plan in use and subrequest budget (longpoll.ts:11 assumes a Free plan; CHANGELOG recommends paid).
- Whether Cloudflare Workers Logs/observability is enabled in the dashboard (not in wrangler.toml).
- Panel client polling interval actually implemented (contract says 5 s; I did not trace the hook).
- `blueprint://` prompt behaviour in real Chrome/Edge, `--profile-directory` correctness, and whether claude.ai honours `?q=` prefill (documented unverified).
- Whether the userscript selectors currently match claude.ai.
- Test pass/fail status: I ran nothing.
- Git history/provenance: the clone has one commit, so authorship/review practice is unknown.
- Why cells/C-060.yaml is missing, and the contents of the unlisted `docs/e2e-runbook.md` beyond its title.
