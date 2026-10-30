> Source: classroom50 commit 34a3d66 / wiki 4d79ad48 (2026-10-21). Paraphrased from the GPL-3 wiki and the JSON schemas in `schemas/`.

# Classroom 50: concepts, storage, and GitHub integration

Conceptual reference: what Classroom 50 is, where every piece of state lives, how roles map onto GitHub, which tokens are involved, and what it cannot do. Procedures are in sibling files:

- `teacher-web.md`: web app teacher workflows (classroom50.org)
- `teacher-cli.md`: `gh teacher` commands
- `student.md`: student accept/submit (web and `gh student`)
- `autograding.md`: runner, tests, `result.json`, regrade, feedback PRs, Actions cost
- `troubleshooting.md`: error messages and fixes

---

## 1. Mental model

**No server. GitHub is the backend.**

| Component | What it is | Holds state? |
|---|---|---|
| Web app (`classroom50.org`, also `preview.classroom50.org`) | Static site on GitHub Pages; runs entirely in the browser | Only browser `localStorage`: the GitHub token, auth method/scopes, UI prefs (theme, language), analytics consent |
| `gh teacher`, `gh student` | GitHub CLI extensions (Go, `go-gh`) on the user's machine | Reuse the `gh` credential store; nothing else |
| `classroom50` repo | Private repo in the org: per-classroom config files, scripts, workflows | Yes: settings, roster, assignments, scores, group snapshots |
| GitHub teams / org membership | Enrollment, roles, groups, pending email invites | Yes: authoritative for who is who |
| Student repos | Normal GitHub repos; commits, `submit/*` tags, Releases with `result.json` | Yes: submissions and grades |
| GitHub Pages of the `classroom50` repo | Public mirror of selected config + grading scripts | Derived (published by a workflow) |
| GitHub Actions | Grading (in student repos), score collection, regrade, publish, token probe (in `classroom50`) | No (writes results back to repos) |
| Cloudflare Worker proxy (`classroom50.fifty-foundation.workers.dev`) | Stateless helper for exactly two browser-hostile GitHub calls | No |

Consequences an agent must internalize:

- **Nothing happens while nobody is signed in** except Actions workflows that were dispatched. There are no webhooks, no background sync, no notifications.
- **Interactive actions run as the signed-in user's token**, limited by that user's GitHub permissions (create classroom, add student, save assignment, accept).
- **Background actions run as GitHub Actions** in the `classroom50` repo (publish Pages, collect scores, regrade, probe token) or in student repos (autograde). Collection/regrade/probe need the **service token** secret.
- **Web app and CLI are equivalent front ends** over the same files and teams. Anything created in one is manageable in the other. Mixing is fine.
- **Administering Classroom 50 ≈ administering a GitHub org.** Teachers are org owners.
- When something "didn't take", the usual cause is a workflow still running or a Pages deploy (about 20 s to a few minutes) still in flight, not a lost write.
- The web app warns before tab close during multi-write operations (accept, roster import, bulk actions, long downloads). Self-started syncs show a **Syncing with GitHub…** tag when slow.

### When state refreshes

| Surface | Behavior |
|---|---|
| Web app page load | Reads live GitHub state (roster, teams, config). Opening a classroom **as an org owner** also runs sync/repair upkeep. |
| Web app org list | Cached 10 minutes; **Refresh** forces it. |
| CLI reads (`roster list`, `classroom list`, `member list`, …) | Snapshot of what is committed/on GitHub at that instant. Never write, never sync. |
| CLI writes (`roster add`, `staff add`, `assignment add`, …) | Commit to `classroom50` and update teams immediately, but only for the thing changed. No broad sync. |
| `gh teacher roster sync <org> <classroom> --write` | The one CLI command that syncs (mainly: completes accepted email invitations). Without `--write` it only reports. |
| Scores | Change only when collection runs: **Collect now** (one assignment), **Collect all** (one classroom), or a `collect-scores.yaml` dispatch. |

If the web app shows a newer roster than `roster list` did a minute ago, somebody (or a sign-in sync) committed in between.

---

## 2. Storage map

| Concept | Stored as |
|---|---|
| Classroom (settings, name, term, unlisted key, archive flag) | `<classroom>/classroom.json` in the `classroom50` repo |
| Assignments | `<classroom>/assignments.json` |
| Roster details (names, sections, contact email, pending invites) | `<classroom>/roster.csv` (display metadata; not the enrollment authority) |
| Who is enrolled | Membership of the secret team `classroom50-<classroom>` (plus org membership) |
| Staff roles | Membership of `classroom50-<classroom>-teacher` / `-hta` / `-ta` (teacher also = org owner) |
| Group membership (`team` mode) | Membership of `classroom50-group-<hash>-<n>` teams; intended membership snapshot in `<classroom>/teams.json` |
| Group membership (legacy `group` mode) | Repo collaborators on the founder's repo |
| Pending email invitation | Org invitation + secret team `invite-<hash>` (description holds the address) + pending row in `roster.csv` |
| Submissions | Commits and `submit/*` tags in the student repo; each graded run publishes a GitHub Release with a `result.json` asset |
| Gradebook | `<classroom>/scores.json`, written by `collect-scores.yaml` |
| Manual/override scores | Entries in `scores.json` with `override: true` |
| Grading logic | `<classroom>/autograder.py`, `<classroom>/autograders/<slug>/`, or `tests` in `assignments.json` |
| Access control | GitHub permissions: org base permission, team grants, repo collaborator roles, rulesets |
| Service token | Actions secret `CLASSROOM50_SERVICE_TOKEN` on the `classroom50` repo (+ web-only Actions variables for expiry/name) |
| Student-side discovery data | JSON record in the description of the student team (no Pages round-trip needed) |
| Accept marker in each student repo | `.classroom50.yaml` |

Classroom 50 has no data of its own to export or delete. All of the above is the org's.

---

## 3. The `classroom50` config repository

Private repo named exactly `classroom50` in the org, created by `gh teacher init` (or web setup). Layout:

```text
classroom50/                         (private; default branch has classic protection: no force-push, no delete)
├── README.md                        skeleton readme
├── .github/
│   ├── workflows/
│   │   ├── publish-pages.yaml       push to default branch (roster-only commits skipped) + workflow_dispatch
│   │   ├── collect-scores.yaml      workflow_dispatch; inputs: classroom?, assignment?
│   │   ├── regrade.yaml             workflow_dispatch; inputs: classroom (req), assignment (req), owner?
│   │   ├── probe-token.yaml         workflow_dispatch; read-only token permission check
│   │   └── autograde-runner.yaml    reusable workflow called by every student repo's autograde.yaml
│   └── scripts/                     org-level, shared by all classrooms (nested under .github so it can't collide with a slug)
│       ├── runner.py                grading bootstrap (published to Pages root)
│       ├── materialize_tests.py     expands declarative `tests` into autograders/<slug>/tests.json at publish time
│       ├── ensure_feedback_pr.py    maintains feedback PRs (published to Pages root)
│       ├── collect_scores.py        score collector
│       ├── regrade_repos.py         regrade fan-out
│       └── probe_token.py           service-token probe
└── <classroom>/                     one directory per classroom; dir name == short_name
    ├── classroom.json               classroom metadata
    ├── assignments.json             assignment manifest (published to Pages)
    ├── roster.csv                   roster (never published)
    ├── scores.json                  gradebook (never published)
    ├── teams.json                   group-team snapshot (team-mode assignments)
    ├── autograder.py                optional classroom-default autograder (published)
    └── autograders/
        ├── <slug>/                  optional per-assignment bundle dir: autograder.py and/or fixtures; tarred to <slug>.tar.gz
        └── <name>.yaml              optional, rare: non-default autograder workflow shim
```

`classroom add` scaffolds `classroom.json`, `assignments.json` (`{"schema":…,"assignments":[]}`), `roster.csv`, `scores.json` (`assignments: {}`); `teams.json` appears with group work (`assignments: {}` at scaffold). Autograder files appear only when the teacher adds them.

**Hand-editing:** discouraged. Some state is derived from both files and live GitHub, and the tools rewrite files to keep them consistent. The one documented hand-edit is a score override in `scores.json`. Writers follow a "tolerate and preserve" rule: unknown top-level fields in `classroom.json`, assignment entries, `teams.json`, and extra roster columns survive read-modify-write. Closed sub-objects (`runtime`, `template`, `due_meta`, `test_defaults`, `repo_features`, `pages`, each test, `team`/`teams`) reject unknown keys; an unknown `runtime` key makes the whole `assignments.json` unparseable for older readers.

Commits to the config repo use tree commits with rebase retry (GitHub git data API).

### 3.1 `classroom.json` (`classroom50/classroom/v1`)

Required: `schema`, `name`, `short_name`, `term`, `org`.

| Field | Type | Meaning |
|---|---|---|
| `schema` | const `classroom50/classroom/v1` | |
| `name` | string, min 1 | Display name |
| `short_name` | `^[a-z0-9][a-z0-9-]{1,99}$` | Slug; directory name and Pages path segment. New classrooms are capped at 40 chars in code (see §8). |
| `term` | string (may be empty) | Free-form, e.g. `Fall 2026` |
| `org` | string | Owning org login |
| `team` | `{id, slug}` | The secret student team. Absent on very old classrooms. |
| `teams` | `{teacher?, hta?, ta?}` each `{id, slug}` | Staff teams (`closed`). Tooling finds staff teams by slug whether or not recorded here. |
| `secret` | `^[a-z0-9]{4,64}$` | Access key for an **unlisted** classroom: Pages path becomes `<classroom>/<secret>/…`. Obscurity only. Cannot be changed later without students re-accepting. CLI: `classroom add --unlisted`. |
| `pages_base_url` | `^https://[^\s?#]{1,110}$` | For orgs with a custom Pages domain. Everything before `/<classroom>[/<secret>]/…`, no trailing slash: `https://<domain>/classroom50` (org-root domain) or `https://<domain>` (CNAME on the `classroom50` repo). Browsers try it first, then fall back to `https://<org>.github.io/classroom50`. Gotcha: old `gh teacher` releases strip it from the student-team description on their next reconcile; upgrade every teacher's CLI before setting it. |
| `active` | boolean | `false` = archived. Absent/true = active. Archived classrooms drop off default lists, block new assignments/edits, and (once published) the student accept page refuses them. |
| `migrated_from` | object | Written only by the retired `gh teacher classroom migrate` (GitHub Classroom import): `source`, `classroom_id`, `original_name`, `original_org_login`, `url?`, `migrated_at`. Kept so migrated classrooms validate. |

### 3.2 `assignments.json` (`classroom50/assignments/v1`)

Root: `{ "schema": "classroom50/assignments/v1", "assignments": [ … ] }` (root is closed). Published publicly to Pages, so treat everything in it as readable by anyone with the URL.

Required per entry: `slug`, `name`, `mode`, `autograder`. Inexpressible rules enforced in code: test names unique per assignment; names ≤ 100 UTF-8 **bytes**; `release_assets` basenames unique; `release_assets` path strings ≤ 8,192 bytes total. Writers must emit normalized forms (non-empty `autograder`, no `release_assets: null`).

**Identity and shape**

| Field | Values | Notes |
|---|---|---|
| `slug` | shortName pattern | Repo-name budget applies (§8). |
| `name` | string | |
| `description` | string | |
| `mode` | `individual` \| `group` \| `team` | `individual` = repo per student. `team` = current **Group** (GitHub-Team-backed; web "Group"). `group` = **Group (legacy)** (founder-owned repo, collaborators). Older clients reject unknown modes on purpose. |
| `team_formation` | `teacher` \| `student` | Required for `team`; forbidden otherwise. |
| `max_group_size` | integer ≥ 2 | Required for `group` and `team`; forbidden for `individual`. Advisory, not a security cap. |
| `autograder` | shortName | Workflow shim name; `default` = universal shim. Not the grading logic. |
| `template` | `{owner, repo, branch}` (all required) | Starter repo; must be flagged **Template repository**. Private templates must live in the org. |
| `renamed_from` | shortName | Previous slug after the one-time rename. Reserved forever in the classroom (keeps GitHub's redirects from old repo names working). Collection still accepts old `result.json` carrying it. A renamed assignment can't be renamed again. |
| `migrated_from` | object | `source, classroom_id, assignment_id, original_slug, starter_repo, invite_link, migrated_at` (retired migrate command). |

**Dates** (RFC 3339; writers should store UTC; `*_meta` = provenance only)

| Field | Notes |
|---|---|
| `due` | Advisory. Collection marks later submissions `late`. Blocks nothing. |
| `due_meta` | `{input, zone?, offset, source: explicit-offset\|auto-detected\|migrated}` |
| `available_from` | Release date. Absent or future = **not listed** on students' assignment pages; reachable only via invite link. Already-accepted students always see it. Listing gate only, not access control. CLI `--available-from`. |
| `available_from_meta` | Same shape as `due_meta`. |

**Access and lifecycle flags** (booleans are collapsed on the wire: absent == false; accept explicit false too)

| Field | Effect |
|---|---|
| `locked` | All student clients refuse the assignment for everyone, including past accepters. For a private in-org template, also removes the student team's read on the template (staff teams untouched); unlocking re-grants. Public or template-less assignments are UX-gated only. Repos are kept. Set at creation: template read is never granted until first unlock. |
| `closed` | Only effect in the file: new accepts are refused. The **Close submission** action additionally downgrades every accepted student to `pull` on their repo (per repo, not recorded here). Independent of `locked`. |
| `student_permission` | `pull`\|`triage`\|`push`\|`maintain`\|`admin`. Role the accepter gets on their own repo. Absent = `push` (individual), `admin` (legacy group), `push` (team). Legacy group clamps anything below `admin` up to `admin`. Accept-time only. |
| `repo_visibility` | `private` (default, omitted) \| `public`. Accept-time only; on a rejected public create, accept retries private. Public repos are **not autograded**. |

**Repo provisioning** (all accept-time only; never retrofitted to existing repos)

| Field | Effect / constraints |
|---|---|
| `empty_repo` | Bare repo: no commit, no README, no marker, no shim. No autograding, no feedback PR, regrade skips, collection records presence only (`detected`). Excludes `template`, `tests`, `allowed_files`, `release_assets`, `pass_threshold`, `pages`, and forces `feedback_pr` false. |
| `no_autograder` | Initialized repo (template content or README) with **no** Classroom 50 files. No grading; collection uses `detected`; baseline = root commit. Allows feedback PR. Requires `autograder: default`; excludes `empty_repo`, `init_shim`, `tests`, `allowed_files`, `release_assets`, `pass_threshold`. Clearing it later: `gh teacher assignment enable-autograder` or the web bulk action backfills the shim. |
| `init_shim` | Template-less repo with only the marker and default shim (no README). Grades normally. Requires `autograder: default`, no template; excludes `empty_repo`, `no_autograder`. |
| `include_all_branches` | Copy all template branches on generate. Requires template; excludes `empty_repo`, `init_shim`. |
| `copy_about` / `copy_topics` | Copy template description / topics on fresh create (GitHub's generate doesn't). Require template. Best-effort. |
| `repo_features` | `{issues?, wiki?, projects?, pull_requests?}` tri-state: absent = inherit template's setting (generate doesn't copy them), true/false = force. Gotcha: inheriting from a private template copies its wiki/issues content too. |
| `pages` | `{source: workflow\|branch, branch?, path?}`. Configures a Pages site on each new repo before the setup commit (students need no admin). `workflow` forbids `branch`/`path`. `path` is `/` or `/docs`. Excluded with `empty_repo`. Never fails accept. |

**Grading-related** (detail in `autograding.md`)

| Field | Notes |
|---|---|
| `tests` | Declarative tests: `name`, `type` (`io`\|`run`\|`python`), `run` required; also `setup`, `input`, `input-file`, `expected`, `expected-file`, `comparison` (`included`\|`exact`\|`regex`), `timeout` (1–600 s, default 10), `exit-code`, `points` (default 0), `failure-details`, `show-output`, `show-command`. Mutually exclusive with `<classroom>/autograders/<slug>/autograder.py`. |
| `test_defaults` | `{failure-details: full\|actual-only\|none, show-output, show-command}`; defaults `full`, false, false. |
| `runtime` | Closed: `runs-on`, `container`, `python`, `node`, `java`, `go`, `rust`, `apt`, `apt-recommends`. Omit for ubuntu-latest + Python 3.14. |
| `submission_mode` | `every-push` (default, omitted) \| `tag` (only `submit/*` and milestone tags grade/count). Baked into each repo's shim at accept; changing needs a shim retrofit (`gh teacher assignment submission-mode` or web bulk action) and students must re-pull. |
| `submission_tags` | Milestone tag patterns (Actions tag-filter subset, no `!`). `submit/*` always counts too. Same retrofit caveat. |
| `allowed_files` | Ordered `.gitignore`-style patterns; last match wins. Runner deletes non-matching files before grading (best-effort, fails open). Hygiene, not secrecy. |
| `release_assets` | Workspace paths attached to each submission Release. |
| `pass_threshold` | 0–100, advisory display only. Absent = no pass/fail concept (not 0). |
| `grading` | `{mode: auto\|manual\|off, max_points?}`. Absent = `auto`. `max_points` (≥ 1) required iff `manual`. Intent only; collection ignores it. |
| `feedback_pr` | Long-lived feedback PR opened at accept. Product default ON (writers set it), but absent reads as false. |
| `feedback_pr_template` | Use the template repo's PR template as the PR body. Requires `feedback_pr: true` and a template. |

### 3.3 `roster.csv`

No JSON schema; the contract lives in Go (`configrepo/students_csv.go`) and the web parser, pinned by shared fixtures.

- On-disk header, always written in this order: `username,first_name,last_name,email,section,github_id,role`. Extra columns are preserved wherever they sit.
- Identity columns (need at least one in a header): `github_id` (preferred), `username`, `email`. Precedence when several are present: `github_id` → `username` → `email`.
- `github_id`: immutable numeric id, tool-managed (`GET /users/{username}` on add/import, or from team membership on sync). Survives username renames. Don't hand-edit.
- `role`: `student` (default/blank), `ta`, `hta`, `teacher`. Display snapshot only, refreshed from teams by sync; nothing reads it for logic. Dual-role accounts record the highest role.
- `email`: optional per row; for invited rows it is the address **you invited**, not necessarily the account's email.
- Row kinds: **linked** (has username/id), **pending** (email only, invitation outstanding), **unlinked** (name but no account, e.g. an expired invitation, flagged **Invitation expired** in the web app). A row with no identity and no name is an error.
- Cells are defanged against CSV formula injection on write and restored on read.
- Import (web upload / `roster import`): headers case-insensitive; unknown columns ignored; `name` column splits into first/last; non-UTF-8 is read as Windows-1252 with a notice. If `github_id` and `username` disagree, the id wins (with confirmation); an id matching no account stops the import.
- `roster.csv` is **never published** to Pages; commits touching only it don't trigger a Pages deploy.

### 3.4 `scores.json` (`classroom50/scores/v1`)

Written by `collect_scores.py`, read by the web gradebook and `gh teacher download`. Writes are atomic per classroom. Legacy layouts are rejected, not migrated.

```text
{ schema, assignments: { <slug>: { type, entries[], collected_at?, detected[]? } } }
```

| Level | Fields |
|---|---|
| bucket | `type` (`individual`\|`group`\|`team`, mirrors `mode`), `entries`, `collected_at` (UTC; stamped whenever a run walks this assignment, even with no change), `detected` |
| entry | `owner` (lowercased repo-owner key; for `team` it is `group-<n>`), `member_usernames` (group/team only: credited roster members), `team_slug` (team only), `submissions[]` (newest first; `[0]` is latest), `override` (true = frozen, never refreshed; false = explicit keep-refreshing) |
| submission record | a `result/v1` payload minus `assignment`: `schema` (`classroom50/result/v1`), `classroom`, `assignment_type`, `owner`, `submission` (`submit/<UTC-timestamp>-<short-sha>`), `commit`, `release`, `review` (URLs), `datetime` (graded commit's committer date, invariant across regrades), `graded_at?`, `score`, `max-score`, `tests[]` (`test-name`, `passed`, `score`, `max-score`, plus extras), `submitted_by? {username, id}`, collection-added `late?` and `provenance_warning?` |
| detected record | `owner`, `count` (≥ 1; zero-count repos omitted), `kind?` (`commit`\|`tag`), `latest_datetime?`, `late?`, `member_usernames?`, `team_slug?`. Presence only, never a score. Used for `empty_repo`/`no_autograder` assignments and for autograded repos with pushes but no Release yet. An owner never appears in both `entries` and `detected`. |

`provenance_warning` is stamped when the Release author or the `result.json` uploader isn't `github-actions[bot]` (shown as **Unverified**). Any copy inside `result.json` is stripped.

Related per-repo files written by `gh teacher download` next to each clone: `result.json` (latest payload) and `results.json` (bare array of `{tag, result}` envelopes, newest first; `result` keeps `assignment`; null if a Release lacked a valid asset).

### 3.5 `teams.json` (`classroom50/teams/v1`)

Snapshot of **intended** group membership for `team`-mode assignments. GitHub Teams remain authoritative for push access and grading.

```text
{ schema, assignments: { <slug>: { teams: [ { slug, id?, name?, members[], formation? } ] } } }
```

- `slug`: `^classroom50-group-[0-9a-f]{16}-[1-9][0-9]*$`; hash must match this classroom+assignment.
- `id`: live team id at creation; destructive deletes verify it first (a reused slug is never clobbered).
- `name`: display name only.
- `members`: lowercased usernames; may be `[]` (placeholder team). Lists are disjoint within an assignment.
- `formation`: `teacher` \| `student` (audit trail if `team_formation` changes).
- Teacher formation: this file is the source of truth tooling reconciles teams against. Student formation: it is the drift baseline (absent key = no baseline yet). Drift shows as **Members changed since the last refresh**. The snapshot also lets cleanup attribute and recover deleted group teams.

### 3.6 Autograder files

Resolution order at grading time: `<classroom>/autograders/<slug>/` (bundle with `autograder.py` or materialized `tests.json`) → `<classroom>/autograder.py` (classroom default, `gh teacher autograder set-default`) → vacuous pass (score 0/0, still tags and publishes a Release). The bundle directory is exposed as `$CLASSROOM50_BUNDLE_DIR`, never enters student repos, but **is publicly served by Pages**. Details: `autograding.md`.

### 3.7 Published Pages site

`publish-pages.yaml` builds an **allow-list** site (new files are private by default). It only triggers on push to the default branch or manual dispatch, never on PRs. Base: `https://<org>.github.io/classroom50/` (or the custom domain).

| Path | Content |
|---|---|
| `classrooms-index.json` | `{classrooms: [...]}` with only public keys: `schema, name, short_name, term, org, active, migrated_from` (every classroom, listed or not; never `secret`/`team`) |
| `runner.py`, `ensure_feedback_pr.py` | Org-level scripts |
| `<prefix>/classroom.json`, `<prefix>/assignments.json` | Copied verbatim |
| `<prefix>/autograder.py` | Classroom default, if any |
| `<prefix>/autograders/<name>.yaml` | Non-default shims |
| `<prefix>/autograders/<slug>.tar.gz` | Per-assignment bundles (incl. materialized `tests.json`) |

`<prefix>` = `<classroom>` or `<classroom>/<secret>` for unlisted classrooms. Concurrency group `pages`, queued, never cancelled (a cancelled deploy can block the next one ~10 min).

Custom Pages domain gotcha: GitHub answers `github.io` with a 301 that browsers reject on CORS. Set the classroom's **Custom Pages domain** (`pages_base_url`). CLIs and Actions follow redirects and don't care.

### 3.8 JSON records in GitHub team descriptions

GitHub team descriptions (~250-char limit) carry small records so non-owners can work without reading the private repo. All are re-derived on write (unknown fields tolerated on read, not preserved).

| Team | Schema | Fields | Purpose / trust |
|---|---|---|---|
| `classroom50-<classroom>` (secret student team) | `classroom50/team/v1` | `name?`, `term?`, `active?` (omitted when true), `secret?`, `pages_base_url?` | Lets a student (who can't read `classroom50`) list their classrooms and get the unlisted key before accepting. Projection of `classroom.json`. Readable only by team members and owners. |
| `classroom50-group-<hash>-<n>` | `classroom50/group/v1` | `classroom`, `assignment`, `name?` | Makes a group team attributable/deletable after its config is gone. Student-formed maintainers can edit it, so readers verify the classroom+assignment hash against the team name. |
| `invite-<hash>` (secret) | `classroom50/invite/v1` | `email` (trimmed, lowercased), `classroom` | Bridges email invite → account. The accepted invitee can edit it, so readers schema-validate and require the email to match the name hash. Web app and CLI must produce byte-identical records. |

### 3.9 Artifacts in each student repo

| Artifact | Notes |
|---|---|
| `.classroom50.yaml` (`classroom50/repo-config/v1`) | Accept marker. Required: `classroom`, `assignment`. Optional: `schema`, `secret` (copied at accept), `owner {username, id, accepted_at}` (`accepted_at` is client-generated, not trustworthy), `source {owner, owner_id, repo, branch}` (template coordinates so `gh student submit` can re-fetch `.gitignore` and `.github/`). Absent for `empty_repo`/`no_autograder` shapes. |
| `.github/workflows/autograde.yaml` | Shim calling `classroom50/.github/workflows/autograde-runner.yaml`. |
| `feedback` branch | Frozen base of the feedback PR (accept commit / baseline). Locked by ruleset. |
| `submit/<UTC-timestamp>-<short-sha>` tags | One per graded submission. |
| Releases | One per submission, with `result.json` asset; latest = current score. |
| Tool commits | Feedback-PR opener empty commit, shim retrofits, `[Classroom 50] Add autograde workflow (enable-autograder)`: all carry `[skip ci]` and don't count as submissions. |

---

## 4. Roles are GitHub teams

There is no role database. Team membership **is** the role.

| Role | GitHub construct | `classroom50` repo | Student repos | Can |
|---|---|---|---|---|
| Teacher | Org **owner** + `classroom50-<c>-teacher` | write (owner: everything) | all (via ownership) | Everything, incl. org and classroom settings, writing scores in the web app, pending invitations, **Open all feedback PRs** |
| Head TA | Org member + `classroom50-<c>-hta` | write | push, granted by each collection run | Manage the classroom (edit assignments, run Collect/Regrade), review/merge feedback PRs. Not owner. |
| TA | Org member + `classroom50-<c>-ta` | read | push, granted by each collection run | View roster/submissions/scores, review/merge feedback PRs. Can't run collection (sees **Refresh** instead). |
| Student | Org member + `classroom50-<c>` | none | own repo only (default push) | Accept, submit |

Gotchas:

- Granting **teacher** makes the person an **org owner** over the whole org, not just the classroom. Keep it small; use head TA/TA for graders.
- Staff additions arrive as GitHub team invitations the person must accept.
- `gh teacher staff add <org> <c> <user> --role teacher|hta|ta` (default `teacher`). `staff remove` removes the role, not org membership.
- Staff can be invited **by email only from the web app** (roster upload with a role). `gh teacher roster invite` is always a student invite (no `--role`), so a typo can never hand out ownership. CLI path: invite as student, then `staff add` after they join (they stay enrolled as a student until unenrolled).
- Org settings and classroom settings pages are teacher-only (hidden client-side for TA/HTA).
- Head TA/TA who aren't on the secret student team can't read its membership: their roster/submission views use `roster.csv` as of the last sync, and the page says so. Owners always see live membership.
- A freshly accepted repo has **no staff access** until the next collection run; staff see that student as **Not visible**.
- Because the ruleset exemption skips the lock entirely, staff can push to or delete a student's `feedback` branch.

### Team naming

| Team | Name | Privacy | Notes |
|---|---|---|---|
| Student (classroom) team | `classroom50-<classroom>` | `secret` | Enrollment authority. Read on private in-org templates. Description holds `team/v1`. |
| Staff teams | `classroom50-<classroom>-teacher`, `-hta`, `-ta` | `closed` (visible to org) | Must be visible: GitHub only accepts visible teams as ruleset bypass actors. So students can see and @mention staff. |
| Group teams | `classroom50-group-<hash>-<n>` | `secret` if teacher-formed, `closed` if student-formed | `<hash>` = first 16 hex of SHA-256 over lowercased classroom + assignment slugs; `<n>` from 1. |
| Invite teams | `invite-<hash>` | `secret` | `<hash>` = first 16 hex of SHA-256 of `<classroom>\0<lowercased-email>`; one per (classroom, address). |

**Staff-team authenticity rule.** A team at a staff name counts as Classroom 50's only if it **has access to the `classroom50` repo** (a grant only an owner-run flow, a repo admin, or a maintainer of an already-granted team can make). A team an ordinary member created at that name is never exempted, made visible, or granted student-repo access; Classroom 50 warns instead. Override: if a classroom literally named `<short>-<role>` exists, the team at that name is that classroom's **student** team, and any staff access an older release gave it is removed on the next visit. New short names can't end in a role suffix, and can't collide with an existing classroom's staff team name. Setup, **Fix it**, collection, and the classroom page's team repair all apply this rule.

### Dual roles (staff who are also students)

Allowed. Teams decide; `role` column is a snapshot. In-app access follows the highest role (`teacher > hta > ta > student`); "View as" is a local preview only. Unenroll drops only the student side. A pure-staff account shows in submissions only after accepting (with role badge) and is excluded from Accepted/Submitted counts unless **Include teaching staff** is on. An org owner keeps `admin` on their own assignment repo (GitHub won't let owners drop their own access), so test the real student experience with a separate account.

---

## 5. Visibility matrix

Base permission is **No permission**, so nobody sees anything not explicitly granted.

| Resource | Teacher (owner) | Head TA | TA | Student |
|---|---|---|---|---|
| `classroom50` repo (roster, scores, settings) | read/write | read/write | read | none |
| Private in-org templates | all | read (pull, granted at add/reuse and collection) | read | read, own classrooms only (needed by accept) |
| Student assignment repos | all | push, granted at each collection run | push, granted at each collection run | own repo only |
| Other students' work | all | after a collection run | after a collection run | never (except `repo_visibility: public` assignments) |
| Pending org invitations | yes | no | no | no |
| Published Pages files (assignments.json, bundles) | anyone with the URL | same | same | same |
| Student team membership | yes | only if on it | only if on it | members of it |
| Staff team membership | visible to all org members | | | |

Consequences:

- Students can browse their classroom's private templates **including history**. Never commit solutions to a template. Locked assignments are the exception (no template grant until unlock).
- Template read also reaches the template's **private forks** (GitHub gives forks the upstream's team permissions). GitHub Classroom repos created since 2024 are forks of their starter, so registering an old starter exposes past students' work. Register a fresh, fork-free copy. Tools warn when a private template has forks.
- TAs can't see invited-but-pending students; they may look missing.
- Collection's staff grant is scoped like the run: a per-assignment run only touches that assignment's repos and template.

---

## 6. Org lockdown, rulesets, and other setup

### Member-privilege lockdown (`PATCH /orgs/{org}`, applied by `init`/web setup, verified by `gh teacher audit`)

| Setting | Value | Why |
|---|---|---|
| `default_repository_permission` | `none` | No implicit read on other repos |
| `members_can_create_repositories` | true | Master switch; on Team/Free it gates both public and private |
| `members_can_create_private_repositories` | true | Accept creates the repo as the student |
| `members_can_create_public_repositories` | false on Enterprise Cloud; forced true on Team/Free | Team/Free couple public+private creation |
| `members_can_create_internal_repositories` | false (Enterprise) | |
| `members_can_create_pages`, `members_can_create_public_pages` | true (enforced, reset on re-run) | `classroom50` must publish a public Pages site |
| `members_can_create_private_pages` | false | Never needed |
| `members_can_delete_repositories` | false | |
| `members_can_change_repo_visibility` | false | Makes repo `admin` for students safe |
| `members_can_delete_issues` | false | |
| `members_can_create_teams` | true | Student-formed groups (founder creates the team). If off, the web form hides that mode. |
| `members_can_view_dependency_insights` | false (where controllable) | |
| `members_can_invite_outside_collaborators` | false (where controllable; Team: owners only) | |
| `readers_can_create_discussions` | left at org setting | Deliberately untouched |
| Private-repo forking | not enforced | Dropped after tug-of-war with GitHub Classroom; private templates work either way |

**Four settings have no API** (`init` prints them; `audit` reports **Confirm by hand**). Set at `https://github.com/organizations/<org>/settings/member_privileges`:

1. App access requests → **Members only** (or disable).
2. Uncheck **Allow repository admins to install GitHub Apps for their repositories**.
3. Projects base permissions → **No access**.
4. Uncheck **Allow repository administrators to rename branches protected by organization rules**.

`gh teacher audit <org>`: read-only; per setting **Verified** / **Action required** / **Confirm by hand**; non-zero exit if any API-readable setting is off; `--json` available.

### Two org-wide rulesets (all repos in the org)

| Ruleset | Target | Blocks | Bypass |
|---|---|---|---|
| `classroom50-protect-submission-history` | Default branch of every repo | Force push, branch deletion | Org owners |
| `classroom50-feedback-base-lock` | `feedback` branch | Updates, deletion | Org owners + every classroom's staff teams (teacher, hta, ta); each staff team is added when created, and re-running setup rebuilds the list |

Plus classic branch protection on the `classroom50` repo's default branch (no force push, no deletion). If **Fix it** can't apply it, an enterprise policy is usually pinning it; the check is advisory.

### Other things setup configures

- Enables GitHub Actions (org and `classroom50` repo).
- Creates a **$0 Actions budget** cap if the org has none (Enterprise-billed orgs: "Couldn't verify the Actions spending cap", `read failed (400)`, advisory).
- Org **Allow GitHub Actions to create and approve pull requests** + `default_workflow_permissions=write` (feedback PRs are opened by student-repo workflows).
- `classroom50` repo reusable-workflow access = `organization`.
- Creates private `classroom50`, commits workflows/scripts (needs `workflow` scope), enables Pages as **public**. First deploy needs `publish-pages.yaml` to run once (push or dispatch).
- Uploads `CLASSROOM50_SERVICE_TOKEN` (libsodium-encrypted, never written to disk).
- If an enterprise policy blocks the Actions settings, apply by hand:

```sh
gh api -X PUT /orgs/ORG/actions/permissions/workflow -F default_workflow_permissions=write -F can_approve_pull_request_reviews=true
gh api -X PUT /repos/ORG/classroom50/actions/permissions/access -f access_level=organization
```

**Settings flipping back** usually means another tool (historically GitHub Classroom) or an org/enterprise policy manages the same org.

### Why students get broad access to their own repo

| Mode | Student access | How |
|---|---|---|
| Individual | `push` (configurable via `student_permission`) | Student creates the repo (becomes admin), accept downgrades to write |
| Group (`team`) | push via the group team | Founder's transient creator-admin is dropped once the team is attached |
| Group (legacy `group`) | Founder keeps `admin` | Needed to add teammates as collaborators |

Safe only because of the org lockdown: even a repo admin can't delete, transfer, or change visibility, or reach other private repos.

---

## 7. Repository naming and slug budgets

| Repo | Name |
|---|---|
| Individual | `<classroom>-<assignment>-<username>` (all lowercase) |
| Group (`team`) | `<classroom>-<assignment>-group-<n>` (never changes when the display name does) |
| Group (legacy) | `<classroom>-<assignment>-<founder-username>` |
| Config | `classroom50` |

Budget math (from `contract.go`, mirrored in the web app):

- GitHub repo name max = 100; GitHub login max = 39; two hyphens → classroom slug + assignment slug ≤ **59** chars combined.
- New classroom short names ≤ **40** chars (write-time rule; existing classrooms up to 100 stay readable).
- New assignment slugs must fit `59 - len(classroom)`.
- Imported slugs that don't fit are auto-shortened.
- Pre-budget over-long assignments: one-time slug rename (web **Updating an over-budget assignment slug**, or `gh teacher assignment rename`) renames every student repo consistently and records `renamed_from`.

Tracking is **by repo name**. A student renaming their repo makes it vanish from submissions; rename it back. Slugs: lowercase, web derives them from the name and transliterates diacritics; CLI calls the classroom slug **short-name**.

Student repos are generated copies, **not forks**: template updates can't be pulled into accepted repos (except `.gitignore` and `.github/`, re-fetched by `gh student submit`). Existing scripts that operate on `<classroom>-<assignment>-<username>` repos (as with GitHub Classroom) generally keep working.

---

## 8. Enrollment and invitations

### Chain (by username)

1. Creating a classroom creates its teams (including secret `classroom50-<c>`).
2. Adding a student sends an **org invitation carrying the classroom team** and records the row immediately (the username is the identity).
3. On acceptance GitHub adds the student to the org **and** team in one step → enrolled.

Gotcha: inviting someone directly on github.com skips the team, so they become an org member but not enrolled. Fix by enrolling them from the org's **Members** page in the web app.

Students can't self-join via link: only owners can invite org members. Invite links (assignment accept links; the classroom-level one is the **onboarding link**) only work for people already in the org; they never enroll anyone. Shortcut: an address that another classroom's roster in the same org already links to an account is enrolled directly instead of invited.

### By email

GitHub can't look up an account from an address, and the acceptor may use any account. Mechanism:

1. Create secret team `invite-<hash>` whose description holds `{email, classroom}`. If this fails, no invitation is sent.
2. Send the org invitation by email, carrying both the classroom team and the invite team.
3. Write a **pending row** (email + role, no username) to `roster.csv`.
4. On acceptance the student lands on both teams. The invite team has exactly one member, so a **sync** writes that account into the pending row and deletes the invite team. If the acceptor turns out to be staff on the classroom, a row the sync creates records that staff role.

Rules:

- Web app and CLI read each other's invite teams; invite from one, complete or cancel from the other. Web: **Roster** page. CLI: `gh teacher roster invite` (one address, or `--file` with one address per line). `roster import` never sends email invitations; on email-only rows it only updates name/section.
- Cancel (web roster or `gh teacher roster cancel-invite`) deletes the invite team and pending row at once; leftovers are cleared by the next sync. The CLI first proves the invitation belongs to this classroom (metadata names it and the invitation carries one of its teams), else refuses.
- Expired invitations: the invite team is cleaned up once it is > 24 h old and GitHub no longer lists the invitation as pending. A pending invitation is never touched. The roster row stays as an unlinked row (**Invitation expired**) until re-invited, linked, or deleted. **A sync never removes a row.**
- Re-inviting an address another row already holds is allowed (shared addresses like a parent's); the invitation is sent but no second row is written (one row per address).
- Invite teams are the only place an address not yet linked to an account is stored outside the roster. Before acceptance the team has no members; afterwards only the student and owners can read it.

### What triggers a sync

GitHub doesn't notify Classroom 50 of acceptances. All triggers are idempotent:

| Trigger | Where |
|---|---|
| Opening a classroom's roster, or **Refresh roster** | Web app |
| Entering a classroom as an org owner (also repairs missing teams, re-grants staff teams' `classroom50` access) | Web app |
| **Clean up invite data** | Classroom **Settings** (clear stored addresses early) |
| `gh teacher roster sync <org> <c> --write` | CLI; scriptable / schedulable. Reports only without `--write`. |

Sync is conservative: on a degraded read it reports and removes nothing. It fills missing `github_id`s and retires finished invite teams. Deleting a classroom in the web app removes its invite teams; `gh teacher classroom remove` leaves them for the next sync or `teardown`. Sync ≠ **Collect now** (scores).

### Enroll / unenroll / remove / delete are separate

| Action | Roster + classroom team | Org membership | Repos |
|---|---|---|---|
| Unenroll | removed | kept | kept |
| Remove from org | (access gone) | removed | kept, but student loses access to all org repos |
| Delete repo | n/a | n/a | always a separate manual action |
| Tear down organization | n/a | n/a | deletes **every** repo in the org (not just Classroom 50's); needs `delete_repo` and a typed confirmation |

Per-member and bulk actions live on the org's **Members** page.

---

## 9. Group assignments

| | Group (`mode: team`) | Group (legacy, `mode: group`) |
|---|---|---|
| Backing | GitHub team `classroom50-group-<hash>-<n>` owning `<c>-<a>-group-<n>` (team's push access is the authoritative link) | Founder's repo + repo collaborators |
| Names | Display names ("The Sharks"), metadata only | None |
| Pre-assigned groups | Yes (teacher formation) | No |
| Who credited | Live team members who are on the classroom roster (never collaborators) | Roster-intersected collaborators, owner always |
| Student admin | No | Founder keeps admin |

Formation (`team_formation`):

- `teacher`: only owners create teams/memberships (Teams page or `gh teacher team`); teams `secret`; a student not in a group can't accept. Clients also refuse to let a student found a team or accept with a maintainer-role membership (a student could forge a shape-matching team, since the name is derivable from public data).
- `student`: first accepter founds the team (becomes maintainer), names it, adds roster teammates up to `max_group_size`; teams `closed` so classmates can browse and use GitHub's native **request to join** (the accept page's **Ask to join** opens the team page). Requires `members_can_create_teams`.

Drift containment (GitHub can't stop a maintainer editing membership): **Members changed since the last refresh** flags, **Over the limit** errors on submissions/Manage groups pages and a warning to members, grading credits only rostered members, size re-checked on every client add.

---

## 10. Tokens and sign-in

### Scope set (OAuth and classic PAT)

One scope set for everyone (teacher and student), because one person can hold both roles; capabilities are gated afterwards by org/classroom role, not by scopes.

| Scope | Grants | Used for | Who exercises it |
|---|---|---|---|
| `read:user` | Public profile | Identify the user | Everyone (web) |
| `read:org` | Org/team memberships | Role resolution; student accepts own org invitation | Everyone |
| `repo` | **Full control of all the user's repos**, every org. Can't be narrowed. | Create student repos, commit config/setup files, read private Releases, collaborators | Everyone |
| `workflow` | Write `.github/workflows/` | Teacher `init`; student accept commits the autograde shim (default-autograder assignments only) | Everyone (students: only default-autograder accepts) |
| `admin:org` | Administer owned orgs | Invite/remove members, teams, org policy. Implies `read:org`. | Teachers only (inert for plain members) |
| `delete_repo` | Delete repos | Only **Tear down organization**; requested on demand, never at sign-in | Teachers, on demand |

Student real footprint: `read:user`, `read:org`, `repo`, plus `workflow` for default-autograder accepts. The token can touch all their repos; Classroom 50 only acts on classroom ones.

### Web sign-in options

| Method | Path | Proxy? | Notes |
|---|---|---|---|
| **Sign in with GitHub** (OAuth redirect) | default button | yes (token exchange) | Base scopes above |
| **Use a device code instead** | sign-in card | yes (token exchange) | Same scopes |
| **Use a personal access token (classic)** | **Other sign-in methods** | no; validated against `api.github.com` | Pre-filled link: `repo, workflow, admin:org, read:org, read:user` (no `delete_repo`). Multi-org. |
| **Use a personal access token (fine-grained)** | **Other sign-in methods** | no | **One org only** (it becomes the resource owner); Repository access **All repositories**. Tightest grant. |

Fine-grained sign-in token permissions (pre-filled by the app):

| Group | Permission | Access |
|---|---|---|
| Repository | Administration | Read and write |
| Repository | Contents | Read and write |
| Repository | Workflows | Read and write |
| Repository | Pages | Read and write |
| Repository | Secrets | Read and write |
| Repository | Variables | Read and write |
| Repository | Actions | Read and write |
| Repository | Pull requests | Read and write |
| Repository | Issues | Read and write |
| Organization | Administration | Read and write |
| Organization | Members | Read and write |
| Organization | Plan | Read-only |

Gotcha: Repository Administration write already permits deletion, so a fine-grained sign-in token grants deletion up front, unlike OAuth. Conversely, a PAT can't be widened by the app: for teardown with a PAT, create a new one with `delete_repo` (classic) or Administration write (fine-grained) and sign in again.

The token stays in browser `localStorage`; nobody but the user can act with it. Enterprise orgs may restrict OAuth apps; an owner/enterprise admin must approve Classroom 50 if the org doesn't appear.

### CLI authentication

- `gh teacher login` wraps `gh auth login -s admin:org -s read:org -s repo -s workflow`. `gh student login` uses the same set, so one login covers both CLIs.
- `delete_repo` is opt-in: `gh teacher login -s delete_repo` (for `teardown`).
- Usually unnecessary: every command reuses sufficient `gh` credentials and widens an under-scoped gh-managed token in place via `gh auth refresh`. `login` itself always re-runs `gh auth login`, which **replaces** the stored github.com token, so it asks for confirmation if one exists.
- CLIs read the `gh` auth store, not `GITHUB_TOKEN`. `GH_DEBUG=api` logs REST traffic.

### Service token (`CLASSROOM50_SERVICE_TOKEN`)

Fine-grained PAT created from a teacher's own account (no service account), stored as an Actions secret on `classroom50`. One per org; same token whether provisioned by web or CLI. Used by `collect-scores.yaml`, `regrade.yaml`, `probe-token.yaml`.

| Setting | Value | Reason |
|---|---|---|
| Resource owner | The teaching org | Token only reaches the owner's repos |
| Repository access | **All repositories** | "Only select repositories" misses repos created later by accept |
| Contents | Read and write | Read Releases (collect); push `submit/*` tags (regrade) |
| Actions | Read and write | Regrade re-runs autograde |
| Workflows | Read and write | Regrade may tag a commit pushed before a submission-mode change; GitHub refuses that ref otherwise. No read-only probe exists, so a missing grant only shows up at regrade. |
| Administration | Read and write | Collection grants staff teams push on student repos and pull on templates |
| Metadata | Read (auto) | List org repos; legacy group collaborators; staff team repo lists |
| Organization → Members | Read | List classroom/staff/group team members. Separate **Organization permissions** section, shown only once the org is the resource owner. A Contents-only token fails the first collection call. |
| Expiry | ≤ 1 year (365/366 days) | Set a rotation reminder |

- Provision: web org **Settings → Service token** (pre-filled link, tracks expiry) or `CLASSROOM50_SERVICE_TOKEN=github_pat_... gh teacher init ORG` (env var only, never a flag: shell history). Rotate: `gh teacher rotate-service-token ORG`.
- Expiry countdown uses Actions variables `CLASSROOM50_SERVICE_TOKEN_EXPIRES_AT` and `CLASSROOM50_SERVICE_TOKEN_NAME`, written only by the web app. A CLI-provisioned token shows no tracked expiry.
- Verify after init/rotation or on 401/403: web **Test token**, or `gh workflow run probe-token.yaml --repo ORG/classroom50`. Read-only; a red run names the missing permission.
- Group assignments need nothing extra. A failed legacy collaborator read still scores the owner (with a warning); a failed group-team read skips the repo and keeps its previous credit.
- Workflows also use the automatic `GITHUB_TOKEN` (tags, statuses, Releases, feedback PR in student repos) and `GITHUB_REPOSITORY_OWNER` / `GITHUB_API_URL` (Enterprise Server support).

---

## 11. Network, proxy, and what leaves the browser

### The proxy

Two GitHub endpoints refuse browser cross-origin calls, so exactly these two go via `classroom50.fifty-foundation.workers.dev` (Fifty Foundation Cloudflare Worker):

| Operation | Why | What passes through |
|---|---|---|
| OAuth sign-in (redirect and device code) | Token endpoint has no CORS, and the exchange needs the OAuth client secret | One-time login code and the returned access token |
| Repo archive (zip) download | Archive endpoint redirects to `codeload.github.com`, which lacks CORS | The user's token (for that one request) and the streamed zip |

The proxy is stateless, stores nothing, and only accepts the web app's origins. Everything else goes browser → `api.github.com` directly. CLIs never use it. Self-host: build with `VITE_GITHUB_PROXY_BASE` pointing to your own deployment of `cloudflare_worker.js`. Upstream fixes tracked in issue #877 (GitHub Apps SPA support; codeload CORS).

If `workers.dev` is blocked: browsing still works; normal sign-in, device code, and in-app downloads break. Workaround: PAT sign-in (classic or fine-grained), or self-host the proxy on an allowed domain (restores both).

### Allowed domains for filtered school networks

| Domain | Used by | For |
|---|---|---|
| `classroom50.org`, `preview.classroom50.org` | Web | The app |
| `classroom50.fifty-foundation.workers.dev` | Web | Proxy (sign-in, downloads) |
| `github.com` | Web, CLI | OAuth, CLI auth |
| `api.github.com` | Web, CLI, Actions | All REST calls |
| `*.github.io` (+ the org's custom Pages domain, if any) | Web, Actions | Published manifest, autograders, runner |
| `codeload.github.com` | Web (via proxy) | Zip downloads |
| `www.githubstatus.com` | Web | Outage banner (best-effort) |
| `www.googletagmanager.com`, `*.google-analytics.com`, `static.cloudflareinsights.com`, `cloudflareinsights.com` | Web | Optional analytics; blocking is harmless |

Some ISPs/filters flag `classroom50.org`; add an exception or change DNS resolver (see `troubleshooting.md`).

### Data flow by surface

| Surface | Where data goes |
|---|---|
| Web app | Browser ↔ `api.github.com`; sign-in and downloads via the stateless proxy (PAT sign-in skips it) |
| CLIs | Machine ↔ GitHub directly; no analytics |
| Autograding, collection | GitHub Actions inside the org; results stored in org repos |

---

## 12. Privacy and FERPA

- Classroom 50 collects, stores, and processes no student records; it has no server, database, or accounts. Nothing to request/export/delete from Classroom 50. For a DPA, the counterparty is **GitHub** (GitHub Data Protection Agreement).
- Classroom 50 can't make a course FERPA compliant by itself. Levers:
  - **Pseudonymous GitHub accounts**; keep the pseudonym↔student mapping in institutional systems.
  - **Minimal roster**: only a username or id is required; omit names; use non-identifying `section` labels. Email invites send the address to GitHub.
  - **Small teacher role** (owners reach every repo); graders as head TA/TA.
  - **End-of-term cleanup**: archive or delete student repos.
- `repo_visibility: public` exposes future accepters' names, emails, and commit history publicly; confirm before enabling.
- Org Pages sites for student repos are public on the internet even for private repos (only Enterprise Cloud offers private sites).

Usage analytics (classroom50.org and preview only, opt-in bar on first visit, nothing runs until chosen; GPC/DNT disables without asking; change in **Settings → Cookies and analytics** or `/privacy`):

| Collected | Not collected |
|---|---|
| Page paths and dwell time, referrer, country, browser/OS/device/language, load time; GA only: random-ID cookie (2-year expiry, removed when GA is turned off) | Query strings (sign-in codes, invite keys, searches), GitHub username/email, roster data, cross-site tracking |

Cloudflare Web Analytics: no cookies, counts visits; full data 7 days, sample 6 months. Google Analytics (via GTM): event data up to 14 months. Functional storage (sign-in, settings, consent) stays in the browser regardless.

---

## 13. Prerequisites and plans

- Teacher GitHub account; each student needs their own (free) account.
- **Org on Team or Enterprise** is the documented requirement (Pages from the private `classroom50` repo). The org is created on github.com manually; the CLI never creates orgs. `init` warns (advisory) if the plan isn't Team/Enterprise Cloud.
- Free Team plan via **GitHub Education** teacher verification: apply with a school email and clear proof of role (faculty ID photo, employment letter; blurry/expired docs are the top rejection cause); allow 1–2 weeks; then upgrade the specific org through Education benefits. A personal teacher benefit doesn't upgrade an org by itself.
- Enterprise orgs: expect advisory warnings for the spending cap (billing at enterprise level) and possibly branch protection (pinned by policy); OAuth app approval may be needed.
- Student-repo Pages on GitHub Free orgs only works for **public** repos, and public repos aren't autograded: Pages or autograding, not both.
- One org can hold many classrooms. Choose: one org for a stable team (classroom per term/section); one org per teacher for school-wide adoption; one org per academic year for very large courses. Each org needs its own setup and service token.
- Integrates only with GitHub (github.com; workflows support `GITHUB_API_URL` for Enterprise Server), not other Git hosts.

---

## 14. Known limitations

**Roster and enrollment**

- No account lookup by email; email invites stay pending rows until a sync after acceptance. Collect usernames up front (a signup form) to avoid this.
- The stored address is the invited one, not a verified account email.
- No self-service join link; owners must invite. Accept links work after the student joins the org.
- No roster self-identification at accept (GitHub Classroom's "I am this roster entry"); identity is the GitHub account.

**Visibility and feedback**

- Students can't see scores inside the app: Release assets redirect to storage without CORS. Use the repo's Releases page, the feedback PR, or the student view's **View score** link (issue #567).
- No notifications or webhooks from Classroom 50; GitHub's own notifications (watching `classroom50`, feedback PRs) still work.
- State refreshes only on page load; scores only on collection.

**Templates and student repos**

- Students can read private in-org templates and their history (except while locked).
- That read extends to the template's private forks.
- Grading bundles are tamper-proof but **not secret** (served publicly by Pages; unlisted only obscures the URL). Keep solutions/private data out; use `failure-details` to limit leakage.
- Autograded scores come from repos students can write. Hand-made Releases or replaced `result.json` are collected but marked **Unverified**; a student can still delete the newest honest Release so an older one becomes latest unmarked, code running during grading can forge a result, and submission time is a student-controlled commit date. For trustworthy grades: **Close submission** after the due date, `gh teacher download`, run tests yourself.
- Student repos aren't forks; template changes can't propagate (except `.gitignore`/`.github/` on submit).
- Public student repos aren't autograded (public repos can only call workflows in public repos; `classroom50` must stay private because it holds the roster). Make public after grading, or pair **Public** with **Do not use the built-in autograder**.
- Renaming a repo breaks tracking; only the one-time over-budget slug rename is supported.
- Students can re-enable paused workflows (write access includes Actions). **Pause autograding** and Actions policies are cost controls, not enforcement; use **Close submission**.
- Legacy group repos have no names and no pre-assigned groups.

**Group assignments**

- Join requests live on GitHub (no API for team join requests); Classroom 50 can't list or approve them.
- A student-formed group's maintainer can change membership on GitHub; contained by drift flags, over-limit errors, roster-only crediting, and size checks at add time.

**Timing**

- Pages deploys take ~20 s to a few minutes; a fresh accept link can briefly fail or show stale data. Wait and retry.

**Requested but architecturally hard**

- LTI/LMS grade passback (needs a server); use CSV exports / `scores.json`.
- Live in-app scores for students (CORS, #567).
- Roster self-selection (needs an identity arbiter).
- Per-org classic OAuth grants (`repo` is all-or-nothing); use a fine-grained PAT.
- Separate teacher/student sign-in profiles (design avoids choosing a role at sign-in).
- Fully proxy-free web app (#877).

Other behavioral limits worth remembering: the due date never blocks; `available_from` and client-side `locked` gates are best-effort because `assignments.json` is public; `max_group_size` is advisory.

---

## 15. Glossary

| Term | Meaning |
|---|---|
| Classroom | One course's students, assignments, roster, scores. A directory in `classroom50` plus teams. Many per org. |
| Assignment | Coursework in a classroom: individual or group, optional starter code, due date, autograding. |
| Slug / short-name | Lowercase id used in URLs and repo names. CLI calls a classroom's slug its short-name. |
| Individual assignment | One repo per student. |
| Group assignment | Web "Group", CLI mode `team`: shared repo owned by a group team; display names, capacity, formation setting. |
| Group (legacy) | CLI mode `group`: first accepter creates the repo and adds collaborators; no team, no names. Prefer Group for new work. |
| Group team | `classroom50-group-<hash>-<n>`; owns the group repo; credits rostered live members. |
| Group formation | **Teacher assigns groups** vs **Students form groups**. |
| Group display name | Human name of a group; never affects slugs or repo names. |
| Group info snapshot | `<classroom>/teams.json`. |
| Founder | Student who creates a student-formed group (team maintainer) or, in legacy mode, the first accepter (repo admin). |
| Roster | Student list backed by `roster.csv`; the classroom team is the enrollment authority. No roster identifiers. |
| Pending row | Roster row for an email invitee who hasn't accepted: address + role, no account. |
| Unlinked row | Row with a name but no account (e.g. expired invite), kept for manual linking. |
| Invite team | Secret `invite-<hash>` team holding one invited address until acceptance/cancel/expiry. |
| Sync | Pass that catches `roster.csv` up with GitHub (accepted invites, missing ids, retired invite teams). Never removes rows. Not Collect now. |
| Invite link / onboarding link | Accept URL (assignment) / classroom-level link. Works only for existing org members; never enrolls. The only way to reach an assignment with no release date. |
| Organization (org) | The GitHub org hosting the setup. |
| `classroom50` repository | The private config repo; the only backend. |
| Published resources | Files served via the org's Pages site (assignment list, workflow shims, bundles); public. The web **Published** page browses them; **Publish Pages** regenerates them. |
| Unlisted classroom / access key | Classroom published under `<classroom>/<key>/…`; students pass `--key` to the CLI; invite links carry it. Obscurity, not access control. Immutable in practice. |
| Custom Pages domain | Classroom setting (`pages_base_url`) for orgs whose Pages use a custom domain. |
| Teacher / Head TA / TA / Student | See §4. |
| Template repository | Repo flagged as template supplying starter code. Template-less assignments start with README + autograding setup. |
| Due date | Optional; later submissions marked late; never blocks. |
| Release date | `available_from`; listing only. CLI `--available-from`. |
| Locked assignment | Hidden/refused for all students; private in-org template loses student read until unlock. For timed assessments. |
| Closed submission | No new accepts; every accepted repo set read-only until **Reopen submission**. The real enforcement step. |
| Submission type | **Every push to the default branch** (`--submission-mode every-push`, default) or **A tagged commit** (`--submission-mode tag`; only `submit/*` tags, pushed by `gh student submit`). **Milestone tag** (`--submission-tag`, e.g. `phase1`) adds extra grading tag patterns. |
| Submission | Each push triggers one graded run (tag + Release); the submissions page counts per student commit past the starter (excluding tool commits), so one push of several commits = one grade, several counts. |
| Autograder | Grading logic: declarative tests or a teacher Python script. |
| Grading mode | **Autograded**, **Manual** (out of **Max points**), **Not graded**. |
| Declarative tests | io / run / pytest-style checks defined on the assignment; replace GitHub Classroom's `autograding.json` presets. |
| Bundle directory | `<classroom>/autograders/<assignment>/`; fetched fresh each run as `$CLASSROOM50_BUNDLE_DIR`. Web: **Upload test files**. |
| Runner | Shared grading engine in Actions. |
| Feedback pull request | Optional long-lived per-repo PR for inline review ("Feedback PR"). |
| Score / collected scores | `score` out of `max-score`; `scores.json` is the record of all submissions; downloadable as CSV. |
| Score override | Teacher-set score stored in collected scores; autograding leaves it alone; the autograded result is restored when cleared. |
| Service token | Fine-grained PAT secret for collection/regrade/probe; **Test token** checks it. |
| Workflow files | Actions files in `classroom50` and each assignment repo (e.g. `autograde.yaml`). |
| Accept | Student action creating their repo from the template. |
| Submit | `gh student submit`, a plain `git push`, or a `submit/*` tag. |

### Coming from GitHub Classroom: term mapping

| GitHub Classroom | Classroom 50 |
|---|---|
| Hosted service + dashboard | No backend; directory in `classroom50` + GitHub teams |
| Classroom (usually one org per course) | Classroom = directory; one org can hold many |
| Roster identifiers, student self-linking at accept | None; roster rows name GitHub accounts (`github_id`/username) or pending emails |
| Invite link that lets students self-join | Owner invites to the org (roster add/upload); accept links work afterwards |
| Cutoff date (blocks access) | Due date (marks late only) + **Close submission** (enforces) |
| Download grades | Score CSV export / `scores.json` / `gh teacher download` |
| Hosted autograder, `autograding.json` presets | Declarative tests or `autograder.py`, run by GitHub Actions in each student repo; keep an existing `autograding.json` via a custom runner workflow |
| Teams (group assignments) | Group (`team` mode) backed by `classroom50-group-*` teams with display names; or Group (legacy) named after the founder |
| "Grant students admin access" checkbox | `student_permission` (full GitHub role ladder; `--student-permission`) |
| Student repos as forks of starter code (since 2024) | Generated copies (not forks) |
| Starter code / template repository / accept / individual / group | Same words, same idea |

Migration notes:

- GitHub Classroom has shut down; `gh teacher classroom migrate` is retired. Migrated classrooms/assignments still carry `migrated_from`.
- **Don't register old GitHub Classroom starter repos directly** if private and in the same org: they have student forks that would inherit the classroom team's read. Create a new repo, copy contents, flag as template, register the copy. If already registered: switch the assignment to the fork-free copy **first**, then remove the forks from the classroom team (Teams → team → Repositories → select forks → **Remove from team**). Order matters: removing the team from the template leaves grants on forks (locking doesn't help), and re-adding the team to the template (unlock, re-save, **Fix template access**) re-grants every fork.
- GitHub Classroom was the usual cause of org settings flipping back (notably private forking); if both still manage an org, expect audit drift.
- Scripts that work on `<classroom>-<assignment>-<username>` repos generally carry over.
- Separate orgs per course are optional now.

---

## 16. Source inconsistencies (wiki vs schema/code at this commit)

1. **Staff access to student repos.** How-Classroom-50-Works "Who sees what" table says HTA/TA get **Read** at each collection run. Code (`collect_scores.py` `STAFF_TEAM_PERMISSIONS = {"hta": "push", "ta": "push"}`), the Glossary, the Staff page, and the service-token table all say **write/push** (needed to merge feedback PRs). This file uses push.
2. **Plan requirement.** GitHub-Integration step 1 says Free orgs work for public templates and Team/Enterprise Cloud is needed only for private-repo Pages; FAQ, Glossary, and Prerequisites say Team/Enterprise is required and "Free organizations can't host a classroom". `init` only warns. Treat Team/Enterprise as required.
3. **Classroom short-name length.** `classroom-v1` `shortName` allows 2–100 chars and its description calls repo-name budgeting "an open question (#691)". Code (`contract.go`) and the wiki enforce a 40-char cap on new classrooms and a 59-char combined slug budget. Write-time code rule, not in the schema.
4. **Student-repo Pages visibility.** The wiki says a private repo's site is private "on plans that support it" and lists Pages on private repos as available on Team; the `assignments-v1` `pages` description says the site is public on the internet even for a private repo (only Enterprise Cloud has private sites).
5. **Glossary mapping.** How-Classroom-50-Works and the FAQ point to a term-by-term mapping (cutoff date, Download grades, roster identifiers, teams) in the Glossary's "Coming from GitHub Classroom?" section, but that section is only a short paragraph here. The table above is assembled from the individual Glossary entries.
6. **"Four files" per classroom.** The skeleton README and CLI guide list four per-classroom files; `teams.json` is a fifth (group assignments). The README also labels `classroom.json` "(public)". `publish-pages.yaml` copies it verbatim (including `team`/`teams` ids and `secret`) under the classroom's own path; only `classrooms-index.json` is filtered to public keys.
7. **No roster schema.** There is no `roster` JSON schema. `roster.csv` is defined by `RosterColumns` in `cli/gh-teacher/internal/configrepo/students_csv.go`.
