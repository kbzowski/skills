# `gh teacher` CLI reference

Source: classroom50 commit 34a3d66 / wiki 4d79ad48 (2026-10-21). Command tree and flags checked against `cli/gh-teacher` Go source; where wiki and code disagree, this file follows the code (see "Wiki vs code" at the end).

Sibling files: `concepts.md` (data model, repos, teams, Pages), `teacher-web.md` (web app), `student.md` (`gh student`), `autograding.md` (test fields, `autograder.py`, runtime block, result files), `troubleshooting.md`.

---

## 1. Conventions every command shares

- **Invocation:** `gh teacher <command> [subcommand] <positional args> [flags]`. Flags can go before or after positionals (cobra), e.g. `gh teacher download --pull -d out ORG CLS hello`.
- **Placeholders used below:** `ORG` = GitHub organization login, `CLS` = classroom short-name, `SLUG` = assignment slug, `USER` = GitHub login.
- **Global flags:** `-v, --verbose` (persistent, default false) prints per-step API/git detail. `--version` prints the version (`dev` for a source build). `-h, --help` prints full help. A usage error (wrong arg count, unknown flag) prints only the usage line and a pointer to `--help`.
- **Output streams:** data goes to stdout; summaries, progress, warnings, errors go to stderr. Commands with a `-q/--quiet` drop the stderr summary so stdout is the only stream. Where both exist, `--json` wins over `--quiet` (and over `--csv` for `group list`).
- **Exit codes:** 0 success, 1 any failure. The only commands with a 3-state contract are `roster sync` and `roster invite --file` (0/1/2, see there). `audit` exits non-zero when any API-readable lockdown field is unenforced.
- **Error prefix:** `gh-teacher: ...`. When a command fails on a config value this binary doesn't understand (written by a newer client), it may add a line saying whether a newer release exists.
- **Config writes:** everything that edits `<ORG>/classroom50` lands as a single commit on its default branch via an optimistic rebase loop (5 attempts). After 5 conflicts: `... lost the rebase race N times; retry the command`. Same-slug concurrent assignment writes are last-writer-wins; both commits stay in history (`git revert` recovers).
- **Auth:** every command needs a gh token. No token: the CLI runs `gh auth login` for you (interactive only). gh-managed token missing a scope: it runs `gh auth refresh -s <scopes>`, which widens the existing token in place. `GH_TOKEN`/`GITHUB_TOKEN` env token missing a scope: it cannot fix it; error tells you to re-issue the token or unset it and log in.
- **Non-interactive shells:** commands that would prompt (`login`, `init` token prompt, confirmations) fail with a clear error instead of hanging. Use env vars and `--yes`.
- **Colour:** `NO_COLOR` or `CLASSROOM50_NO_COLOR` disables colour.
- **Naming constraints that shape everything:** student repo = `<CLS>-<SLUG>-<USER>`, max 100 chars (GitHub limit). New classroom short-name max 40 chars; `CLS` + `SLUG` share a 59-char budget (worst-case 39-char username). Group repos: `<CLS>-<SLUG>-group-<n>`. Teams: `classroom50-<CLS>` (students), `classroom50-<CLS>-teacher|hta|ta` (staff), `classroom50-group-<hash>-<n>` (team-assignment groups), plus per-invite secret "metadata" teams for email invites.

---

## 2. Install, upgrade, authenticate

Prerequisite: GitHub CLI `gh`. Go only for building from source. No prior `gh auth login` needed.

```sh
gh extension install foundation50/gh-teacher        # install
gh extension install foundation50/gh-student        # optional, for testing student flow
gh teacher --help                                   # verify
gh extension upgrade gh-teacher                     # upgrade (or: gh extension upgrade --all)
gh extension install foundation50/gh-teacher --pin v1.42.0   # pin a release tag
```

- **Upgrade together.** All teachers sharing an org should run the same release: `gh teacher init` reinstalls org rulesets to what the running version expects, so an older binary re-running `init` can undo protections a newer one added (e.g. the staff exemption on the `feedback` branch lock) until the newer `init` runs again or someone clicks **Fix it** in the web app's org settings.
- **Build from source (dev):** `git clone https://github.com/foundation50/classroom50 && cd classroom50/cli/gh-teacher && go build . && gh extension install .`; later just `go build .`.
- **Verify a release binary:** `gh attestation verify PATH --repo foundation50/classroom50` (gh 2.49+; note the monorepo, not the extension repo) or compare SHA-256 with the release's `checksums.txt`.

### `login`

`gh teacher login [-s SCOPES]`

- Wraps `gh auth login`, requesting `admin:org`, `read:org`, `repo`, `workflow` on top of gh defaults. Same set as `gh student login`, so one sign-in covers both.
- `-s, --scopes` (string slice, default none): extra scopes, repeatable or comma-separated. `delete_repo` is not in the default set; it is needed only for `teardown`.
- Always mints a new token and **replaces** stored github.com auth (warns and asks first if one exists). Other commands never do that; they reuse or widen.
- Requires an interactive terminal (opens a browser); errors otherwise.
- Why the scopes: `admin:org` for org-membership endpoints and reading org invitations; `workflow` to commit `.github/workflows/*` files (`init`, `submission-mode`, `enable-autograder`). Scope error on those: `gh auth refresh -s workflow`.

```sh
gh teacher login
gh teacher login -s delete_repo
```

### `logout`

`gh teacher logout` — runs `gh auth logout`. No flags, no args.

### `whoami`

`gh teacher whoami` — prints the authenticated login on stdout. No flags. Good preflight in scripts.

### `completion`

`gh teacher completion bash|zsh|fish` — prints a script that extends gh's own completion (gh completes extension names only). Set up gh's completion first.

```sh
eval "$(gh teacher completion zsh)"                                   # ~/.zshrc after compinit
eval "$(gh teacher completion bash)"                                  # needs bash-completion package
gh teacher completion fish > ~/.config/fish/conf.d/gh-teacher.fish
```

PowerShell is not supported.

---

## 3. Setup flow, in order

1. **Create the org on github.com** (CLI cannot): `https://github.com/account/organizations/new`. Optionally create template repos (Settings → Template repository). A private template must live inside the org.
2. **Log in:** `gh teacher login`.
3. **Create the service token** (fine-grained PAT, from your own account):
   - Resource owner = **the org** (critical).
   - Expiration up to 1 year; set a rotation reminder.
   - Repository access = **All repositories** ("Only select" silently misses student repos created later).
   - Repository permissions: **Contents RW, Actions RW, Workflows RW, Administration RW** (Metadata R auto-added).
   - Organization permissions: **Members: Read** (section appears only after choosing the org as owner).
   - Why: Contents read = collect scores; Contents write = regrade pushes `submit/*` tags; Actions write = regrade re-runs workflows; Workflows write = regrade can tag a commit pushed before a submission-mode change; Administration write = collection grants staff teams access to student repos; Members read = collection lists the classroom team.
   - You must be an org owner for `init`, so your PAT is auto-approved even if the org requires PAT approval.
4. **Preview:** `gh teacher init ORG --dry-run` (read-only checks + step list).
5. **Bootstrap:** `CLASSROOM50_SERVICE_TOKEN=github_pat_... gh teacher init ORG`.
6. **Manual hardening** (4 settings with no API) at `https://github.com/organizations/ORG/settings/member_privileges`:
   - App access requests → Members only (or disabled).
   - Uncheck "Allow repository admins to install GitHub Apps for their repositories".
   - Projects base permissions → No access.
   - Uncheck "Allow repository administrators to rename branches protected by organization rules".
7. **Confirm:** `gh teacher audit ORG`; optionally `gh workflow run probe-token.yaml --repo ORG/classroom50` (read-only, exhaustive token-permission check; red run's log names missing permissions).
8. **Classroom:** `gh teacher classroom add ORG CLS --name "..." --term ...`.
9. **Staff (optional):** `gh teacher staff add ORG CLS USER --role teacher|hta|ta`.
10. **Roster:** `roster add` (known usernames), `roster import` (CSV), `roster invite` / `--file` (emails), then `roster sync --write` after email invitees accept.
11. **Grading (optional, before students accept):** declarative tests (`assignment test add/set`, or `--tests` on add), a per-assignment `autograder.py` (git), or a classroom default (`autograder set-default`). Details: `autograding.md`.
12. **Assignment:** `gh teacher assignment add ORG CLS SLUG --name "..." [--template OWNER/REPO] [--due ...]`. Students then run `gh student accept` (see `student.md`) or use the web invite link.
13. **Collect scores** (no `gh teacher` subcommand; it's a workflow):
    ```sh
    gh workflow run collect-scores.yaml --repo ORG/classroom50                                   # all classrooms
    gh workflow run collect-scores.yaml --repo ORG/classroom50 -f classroom=CLS                  # one classroom
    gh workflow run collect-scores.yaml --repo ORG/classroom50 -f classroom=CLS -f assignment=SLUG  # one assignment (fast)
    ```
    `collect-scores.yaml` is `workflow_dispatch` only (no schedule); scores refresh only when something triggers it (Actions tab, the web **Collect now** button, or the command above). Result: `<CLS>/scores.json`.
14. **Download:** `gh teacher download ORG CLS SLUG` (clones + `scores.csv`).
15. **Regrade** (also a workflow): `gh workflow run regrade.yaml --repo ORG/classroom50 -f classroom=CLS -f assignment=SLUG [-f owner=USER]`. Re-runs each repo's latest autograde run against the current autograder; no new submission is created.

---

## 4. Org-level commands

### `init`

`gh teacher init ORG [--dry-run] [--json] [-q] [--yes]`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--dry-run` | false | Run read-only setup checks and list the steps; change nothing. |
| `--json` | false | Machine-readable summary on stdout; implies `--quiet`. |
| `-q, --quiet` | false | Drop per-step progress; keep warnings and final summary. |
| `--yes` | false | Skip the workflow-file refresh prompt (scripts). |

Behaviour:
- **Preflight (read-only, runs first):** OAuth scopes; org access and **owner** role (non-owner = hard fail); org plan (warning only if the plan can't serve Pages from a private repo; Team/Enterprise Cloud needed); service-token availability. Any hard failure stops before any change: `setup checks failed. Fix these before re-running: ...`.
- **Steps, in order:** (1) member-privilege lockdown: base repo permission `none`; members keep only private-repo creation (so `gh student accept` works), public Pages creation, and team creation (student-formed groups); discussion creation is left alone; plan-gated rejections retried per field and reported. (2) Enable Actions org-wide. (3) $0 Actions budget cap, only if the org has no Actions budget; never fatal; an existing budget is untouched. (4) Allow Actions to create PRs (feedback PRs). (5) Two org rulesets protecting submission history and the frozen feedback base. (6) Create private `ORG/classroom50` (auto-init) or reuse it. (7) Repo-level Actions on. (8) Commit embedded workflows/scripts in one commit. (9) Pages: workflow build, public visibility. (10) Default-branch protection (no force-push/delete). (11) Workflow `GITHUB_TOKEN` to write. (12) Reusable-workflow access for the org. (13) `CLASSROOM50_SERVICE_TOKEN` repo secret.
- **Files committed:** `.github/workflows/{publish-pages,collect-scores,probe-token,autograde-runner,regrade}.yaml`, `.github/scripts/{runner,collect_scores,probe_token,ensure_feedback_pr,materialize_tests,regrade_repos}.py`, `README.md`.
- **Service token source**, in priority order: `CLASSROOM50_SERVICE_TOKEN` env var; else, if the secret already exists, leave it; else piped stdin (one line); else hidden prompt on the terminal. No `--token` flag by design. Token is validated against the org before storing. **If the env var is set on a re-run, it replaces the stored secret** (env wins); without it, a re-run leaves the secret alone.
- **Idempotent:** re-run resumes where it stopped. Workflow/script files that differ from the binary's embedded copies are refreshed after a confirmation prompt (this is how orgs get new features); `--yes` skips the prompt.
- **Output:** prints the Pages URL `https://ORG.github.io/classroom50/`, the four manual-hardening items, and suggests `classroom add`.
- **`--json` keys:** `org, dry_run, ready, plan, config_repo{name,url,created}, pages_url, lockdown_complete, lockdown_manual_steps, feedback_pr_ready, budget_cap, service_token, manual_hardening_required, notes, preflight[], warnings`.
- Before enabling marker-less/no-autograder features on an org set up before v1.56, re-run `init` so collection/runner scripts are current.

```sh
gh teacher init cs50-fall-2026 --dry-run
CLASSROOM50_SERVICE_TOKEN=github_pat_xxx gh teacher init cs50-fall-2026 --yes --json | jq '.ready, .manual_hardening_required'
```

### `audit`

`gh teacher audit ORG [--json]` — read-only re-check of the lockdown `init` applies.

- Each setting is **Verified**, **Action required** (changed outside Classroom 50; fix shown), or **Confirm by hand** (the 4 API-less settings).
- Exit non-zero if any API-readable field is unenforced; manual items never fail it. Safe as `gh teacher audit ORG && ...`.
- `--json` (default false): `{org, plan, read_ok, lockdown_complete, enforced[], unenforced[], manual_unreadable[], budget_cap, settings_url}`, plus optional `default_branch_recommendation`, `repository_defaults_url`, `config_repo_branch_recommendation`, `config_repo_branches_url`. Each setting entry: `{field, desc, critical, fix?}`.

```sh
gh teacher audit cs50-fall-2026 --json | jq '.unenforced'
```

### `rotate-service-token`

`gh teacher rotate-service-token ORG` — no flags.

- Replaces `CLASSROOM50_SERVICE_TOKEN` on `ORG/classroom50` in place. Token from the env var, else piped stdin, else hidden prompt.
- Validates against the org before storing. Fails clearly if `ORG/classroom50` doesn't exist.
- Use before PAT expiry or after suspected leak; collect/regrade 401/403 mid-term usually means an expired token.

```sh
CLASSROOM50_SERVICE_TOKEN=github_pat_new gh teacher rotate-service-token cs50-fall-2026
gh workflow run probe-token.yaml --repo cs50-fall-2026/classroom50
```

### `teardown`

`gh teacher teardown ORG [--yes]` — **destructive dev reset**.

- Deletes **every repository** in the org (not just Classroom 50 ones). Refuses unless `ORG/classroom50` exists.
- Lists all repos, requires typing the org name; `--yes` (default false) skips (scripts only).
- Deletes `classroom50` last, so an interrupted run is safely re-runnable. Then deletes classroom student/staff teams, per-invite metadata teams, and verified group teams.
- Needs `delete_repo`: `gh teacher login -s delete_repo` first.
- Never recommend for a live classroom; use the GitHub UI for selective deletion.

```sh
gh teacher login -s delete_repo && gh teacher teardown classroom50-test
```

---

## 5. `classroom`

A classroom is a root-level directory in `ORG/classroom50` holding `classroom.json`, `assignments.json`, `roster.csv`, `scores.json` (later also `teams.json`, `autograder.py`, `autograders/`). Directories without `classroom.json` (e.g. `.github`) are not classrooms.

### `classroom add`

`gh teacher classroom add ORG SHORT-NAME [--name TEXT] [--term TEXT] [--unlisted] [--key KEY]`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--name` | "" | Display name, e.g. "CS Principles". |
| `--term` | "" | Term id, e.g. `Fall-2026`. |
| `--unlisted` | false | Publish the classroom's Pages resources under an unguessable path segment `<CLS>/<key>/...`. Prompts to accept or replace a generated key. Obscurity, not access control. |
| `--key` | "" | Supply the key yourself (implies `--unlisted`); must match `^[a-z0-9]{4,64}$`. |

- Short-name: `^[a-z0-9][a-z0-9-]{1,99}$`, 2–40 chars for a new classroom (older longer ones keep working). Cannot end in `-teacher`, `-hta`, `-ta`; cannot be `x` when classroom `x-teacher|x-hta|x-ta` exists (team name collisions).
- One commit scaffolding the four files. `roster.csv` header: `username,first_name,last_name,email,section,github_id,role`.
- Creates team `classroom50-<CLS>` (students; read on in-org private templates) and `classroom50-<CLS>-{teacher,hta,ta}`.
- No autograder is installed: assignments grade as a vacuous pass until you add tests or an autograder.
- Refuses to overwrite an existing classroom. Missing `classroom50` repo → points to `init`.

```sh
gh teacher classroom add cs50-fall-2026 cs-principles --name "CS Principles" --term Fall-2026
```

### `classroom list`

`gh teacher classroom list ORG [--all] [--json] [-q]` — read-only.

- One short-name per line; archived ones hidden unless `--all` (then tagged ` (archived)`).
- `--json`: `[{short_name, name, term, active}]`. `-q` drops the stderr `N classroom(s)` line.

```sh
gh teacher classroom list cs50-fall-2026 --all --json
```

### `classroom edit`

`gh teacher classroom edit ORG SHORT-NAME [--name TEXT] [--term TEXT]`

- At least one flag required. Short-name is immutable (it is in repo names); to "rename", create a new classroom. No-op if values already match.

```sh
gh teacher classroom edit cs50-fall-2026 cs-principles --term Spring-2027
```

### `classroom archive` / `classroom unarchive`

`gh teacher classroom archive ORG SHORT-NAME` / `gh teacher classroom unarchive ORG SHORT-NAME` — no flags, idempotent.

- `archive` writes `active: false`; `unarchive` removes the key (absent = active).
- Archived: hidden from default `list`; `assignment add`/`reuse` refuse to write into it; `roster sync --write` refused. Student repos untouched.
- Student accept is blocked only after the next `publish-pages` run republishes the index (documented v1 lag).

```sh
gh teacher classroom archive cs50-fall-2026 cs-principles
```

### `classroom remove`

`gh teacher classroom remove ORG SHORT-NAME [--yes]`

- One commit deleting `<CLS>/` (all config, autograders). Also deletes the classroom's student and staff teams (verified by recorded slug/id; a staff team that isn't the canonical one, or is another classroom's student team, is left with a warning) and drops staff teams from the feedback-base ruleset bypass list.
- Does **not** delete student repos.
- Prompts for the typed short-name; `--yes` (default false) skips.

```sh
gh teacher classroom remove --yes cs50-fall-2026 old-section
```

---

## 6. `roster`

Rows live in `<CLS>/roster.csv`. Identity is the immutable numeric `github_id` (CLI-managed; never hand-edit). Email-invited students have a **pending row** (email only, no username, no `github_id`) until a sync records them. The `role` column is a display snapshot of the account's highest team role (`teacher > hta > ta > student`); the GitHub teams, not this column, decide access. Common errors: missing `classroom50` → `init`; missing `roster.csv` → `classroom add`; bad header printed; unknown user printed; `lost the rebase race` → retry.

### `roster list`

`gh teacher roster list ORG CLS [--json] [-q]` — read-only.

- Default: aligned table (username, name, email, section, github_id, role; empty = `-`) + stderr count.
- `--json`: full rows `{username, first_name, last_name, email, section, github_id, role}`; unresolved `github_id` = 0, unknown role = "".
- `-q`: one username per line, **omits pending email rows** (no username), no summary. Empty roster exits 0.

```sh
gh teacher roster list cs50-fall-2026 cs-principles -q | xargs -n1 echo
```

### `roster add`

`gh teacher roster add ORG CLS USER [--first-name N] [--last-name N] [--email ADDR] [--section S]` (all default "").

- Resolves `github_id` via `GET /users/USER`, upserts by username (case-insensitive), then invites to the org if not a member and not already invited, and adds to `classroom50-<CLS>`.
- **Same-username re-add replaces the whole row**: name/email/section you don't pass are blanked (role and extra web columns kept). Use `roster update` to change one field.
- Row with the same `github_id` but blank/old username: completed in place, unspecified fields keep stored values.
- Row holding this username for a **different** account: nothing written; fix that row first.
- No username match and `--email` equals a pending row's address: that pending row is claimed (its role is not inherited). Without `--email`, an email-invited student ends up listed twice.
- If USER is already staff, prints a note (role column will later show the staff role; enrollment unchanged).
- Errors: classroom/roster missing or malformed, user not found, 5 failed rebases.

```sh
gh teacher roster add cs50-fall-2026 cs-principles alice --first-name Alice --last-name Andersson --email alice@example.edu --section s1
```

### `roster invite`

`gh teacher roster invite ORG CLS EMAIL [--first-name N] [--last-name N] [--section S]`
`gh teacher roster invite ORG CLS --file PATH`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--first-name`, `--last-name`, `--section` | "" | Single-invite only; rejected with `--file`. |
| `--file` | "" | Plain text, one address per line; blank and `#` lines ignored. Replaces the EMAIL positional (pass only ORG CLS). |

- For students with no GitHub account or unknown username. Sends an org invitation carrying two teams: the classroom team and a per-invite secret metadata team that remembers the address (GitHub forgets it on acceptance). Appends a pending row. Same artifacts as the web app's email invite, so either tool can finish or cancel it.
- **Student role only** (cannot invite staff; protects against handing ownership to a typo). Use `staff add` once the person has an account.
- Single address, exit non-zero when: classroom has no usable team in `classroom.json` (nothing sent); the roster already has a pending row for it that GitHub still lists as open, or that was accepted but not yet synced; the invitation fails.
- Exit 0 + "skipped": address already an org member or already has a pending invitation.
- Expired pending row (invitations last 7 days): a new invitation is sent, row kept, GitHub's expired record dismissed after send. Equivalent to web **Re-invite**. Status is determined by asking GitHub, never from row shape.
- Address carried by some *other* row (shared parent/lab address): invitation still sent, exit 0, stderr note, no second row.
- Hand-edited invite team that still has a member: refused for manual check.
- Failure cleanup: a metadata team this run created is deleted, except on rate limit (kept for retry to adopt). If GitHub returns its daily invitation limit, nothing changes. Sent but roster write failed: non-zero, no rollback; `roster sync --write` adds the row.
- **`--file` mode:** all addresses validated first; one bad line → nothing sent. Each address follows the single path, reported as it resolves with file line numbers; successful invites recorded in **one** commit. Already-pending addresses are skips (don't affect exit code). Rate limit: stops sending, waits `Retry-After`, records what was sent, reports the rest. Re-running is safe.
- **`--file` exit codes:** `0` all invited or cleanly skipped; `2` nothing failed but rate limit left addresses uninvited (re-run); `1` an address failed or roster write failed.
- Names/sections for a list: add later with `roster import` (by email, while pending) or `roster update` (after acceptance). Sync never writes names or sections.

```sh
gh teacher roster invite cs50-fall-2026 cs-principles ada@example.edu --first-name Ada --last-name Lovelace --section s1
gh teacher roster invite cs50-fall-2026 cs-principles --file ./section-1-emails.txt; echo "exit=$?"
```

### `roster cancel-invite`

`gh teacher roster cancel-invite ORG CLS EMAIL` — no flags.

- Revokes the pending org invitation, deletes its metadata team, drops the pending row. Same teardown as the web app.
- Only acts on a **pending** invitation. None found → reports, changes nothing, exit 0 (an accepted invite looks identical; run `roster sync` to record the student instead).
- Proves ownership first: metadata team must exist, hold a readable record naming this classroom, and the invitation must carry one of this classroom's teams. Otherwise refuses (non-zero), invitation left intact. Re-run with the right classroom, or revoke from the web roster or `https://github.com/orgs/ORG/people/pending_invitations`.
- Non-zero also if the cancel or following roster write fails.
- Expired invitation: use `roster invite` (resend) or `roster remove ORG CLS EMAIL` (drop row). Rostered student with username: `roster remove` + `gh teacher remove`.

```sh
gh teacher roster cancel-invite cs50-fall-2026 cs-principles ada@example.edu
```

### `roster sync`

`gh teacher roster sync ORG CLS [--write]`

- `--write` (default false). **Without it: dry run, zero write requests.**
- Applies: records accepted email invitees (username + `github_id`) onto their pending row; fills missing `github_id` from classroom-team membership and fixes blank/old usernames from `github_id`; deletes finished metadata teams (only after the roster commit with the address lands); dismisses stale expired-invitation records for addresses that accepted a later invite. If no row claims an accepted invitation, appends one, recording the role of the team the account was found on (highest first).
- Never removes a row; never rewrites an already-recorded role; never adds rows for org members who weren't invited through Classroom 50; never writes names/sections.
- The web app runs the same sync when a teacher opens the roster and additionally refreshes `role` for every row and adds rows for classroom-team members missing from the roster. The CLI does neither.
- Conservative: any degraded read (pending invitations, a team) makes the pass report-only, no team deleted, exit 1. A team whose stored address no longer hashes to its name, or with more than one member, is reported and left. A member-less team is collected only after 24 h with no pending invitation for its address.
- Dry run reports redundant metadata teams and dismissible expired records too; these count as pending changes (exit 2).
- `--write` refused on an archived classroom; dry run still works.

| Exit | Meaning |
| --- | --- |
| 0 | Nothing to do, or `--write` applied everything. |
| 1 | Error, or degraded read (incomplete; nothing deleted). Retry later. |
| 2 | Dry run found pending changes. |

Under `set -e`, guard the call: 2 is a normal outcome.

```sh
set +e; gh teacher roster sync "$ORG" "$CLS"; rc=$?; set -e
[ "$rc" -eq 2 ] && gh teacher roster sync "$ORG" "$CLS" --write
```

### `roster update`

`gh teacher roster update ORG CLS USER [--first-name N] [--last-name N] [--email ADDR] [--section S]`

- Changes only the flags passed; `github_id` and other columns untouched. At least one flag required. Unknown username = error.
- Roster-only: no invite, no `github_id` lookup. `--email ""` clears the address.

```sh
gh teacher roster update cs50-fall-2026 cs-principles alice --section s2
```

### `roster remove`

`gh teacher roster remove ORG CLS USER-OR-EMAIL` — no flags.

- Username: drops the row (case-insensitive). Idempotent (absent → exit 0 with note). **Does not** remove org membership or repo access (deliberate two-step); use `gh teacher remove ORG USER`. Only the student side goes: roster row and student-team membership; staff roles stay.
- Email: drops a dead pending row (web **Remove row**). Checks GitHub first: still-pending invitation → refused (use `cancel-invite`); accepted but unsynced → refused (use `sync --write`); hand-edited team with a member → refused. After dropping, deletes the leftover metadata team (re-checked first) and dismisses GitHub's expired record; those two failing are warnings. An email on a row that has a username → refused, with the username form to run.

```sh
gh teacher roster remove cs50-fall-2026 cs-principles ada@example.edu
```

### `roster import`

`gh teacher roster import ORG CLS PATH-TO-CSV` — no flags.

- Headers matched by name, any order and case. Needs at least one identity column: `github_id`, `username`, `email`. Optional: `first_name`, `last_name`, `name` (split into first/last if split columns absent), `section`, `role`. Other columns ignored (SIS exports and web-written `roster.csv` import as-is). Non-UTF-8 is read as Windows-1252 with a notice.
- Row routing: **username** → resolved via `GET /users/{username}`; a `github_id` cell naming a different account fails that line. **Email only** → updates name/section of the matching pending row; never sends or cancels invites; no pending row → skipped with notice. **github_id without username** → skipped (web **Upload roster** handles id-keyed rows); unusable `github_id` also skipped.
- `role` is carried, never applied, never overwrites a recorded role.
- All bad lines reported in one pass and **nothing committed** until the file is clean. Single commit. Then every username row is added to the classroom team and invited unless already member/invited.
- Username rows use whole-row replace semantics (an empty cell clears that field).

```sh
gh teacher roster import cs50-fall-2026 cs-principles ./sis-export.csv
```

---

## 7. `staff`

Staff teams `classroom50-<CLS>-{teacher,hta,ta}`. `teacher` and `hta` get write on `classroom50` (author assignments); `ta` gets read. Head TAs are members, never owners. Same staff model as the web "Staff & roles" section. Staff access to student repos is granted by score collection runs.

### `staff add`

`gh teacher staff add ORG CLS USER [--role teacher|hta|ta]` (`--role` default `teacher`, case-insensitive).

- Adds USER to the role team; if not an org member, membership is pending until they accept the org invitation.
- Self-heals classrooms predating staff teams: creates/adopts the team, grants its `classroom50` access, records it in `classroom.json`. Replaces a `teams.<role>` record naming some other team, with a warning. Always re-grants a recorded team's `classroom50` access.
- An existing team at the staff name is adopted only if it already has `classroom50` access or is the recorded one; otherwise stops and names it (created outside Classroom 50: review members, delete it or grant access, re-run). If a classroom named `<CLS>-<role>` exists, refuses (that name is its student team).
- Errors: classroom or user not found.

```sh
gh teacher staff add cs50-fall-2026 cs-principles bob --role hta
```

### `staff remove`

`gh teacher staff remove ORG CLS USER [--role teacher|hta|ta]` — removes from the classroom's own role team even if the record names another; org membership untouched; idempotent.

```sh
gh teacher staff remove cs50-fall-2026 cs-principles bob --role hta
```

Dual roles (staff who are also rostered students) are allowed; `roster list` shows the highest role.

---

## 8. `assignment`

Entries live in `<CLS>/assignments.json` (published publicly via Pages; read by `gh student accept` and the autograde runner). Writes use the rebase loop.

### `assignment add`

`gh teacher assignment add ORG CLS SLUG --name TEXT [flags]`

- Slug: `^[a-z0-9][a-z0-9-]{1,99}$`; a **new** slug must fit the budget (`CLS` + `SLUG` ≤ 59 chars combined); slugs retired by `rename` are permanently reserved. A same-slug replace of an existing over-budget entry is allowed, with a warning.
- **Re-add (same slug) rebuilds the entry from the flags given.** Dropped if not re-passed (warned): template, tests, allowed files, pass threshold, student permission (also description, due, runtime, etc. follow the flags). Carried forward if not re-passed: lock state, submission mode and tags, repo visibility, Pages, release assets, and every JSON-only field. Repo-shaping settings only affect future accepts.
- Refuses archived classrooms.

| Flag | Default | Meaning |
| --- | --- | --- |
| `--name` | (required) | Display name. |
| `--template OWNER/REPO` | "" (template-less) | Must be flagged as a template. Omit → initialized repo (README + control files). `@branch` suffix is ignored with a warning; the template's default branch is always used. Private templates must be in ORG; the classroom team gets read. |
| `--description` | "" | One-line description. |
| `--due` | "" | RFC 3339 (`2026-09-15T23:59:00-04:00`) or zone-less local time (`2026-09-15T23:59:00`, interpreted in `$TZ` or system zone). Stored UTC. Bare date rejected. Unresolvable `$TZ` with zone-less value → error. |
| `--available-from` | "" | Same format. Assignments are invite-link-only (not listed) by default; this lists it for all students after the date. Listing only, not access control. |
| `--locked` | false | Register locked (see `assignment lock`). On re-add: `--locked=false` unlocks; omitted keeps stored state. |
| `--mode individual\|group\|team` | `individual` | `team` = shared repo per group owned by a GitHub Team (manage with `team`); `group` = legacy collaborator-based shared repo. |
| `--max-group-size N` | 0 | Required (2–100) for group/team; must be unset for individual. Enforced by Classroom 50 clients only. |
| `--team-formation teacher\|student` | "" | Required with `--mode team`. `teacher`: you create groups (`team create`); ungrouped students can't accept. `student`: first student runs `gh student accept --new-team`. |
| `--autograder NAME` | `default` | Picks shim `<CLS>/autograders/<NAME>.yaml` (rare; for toolchains use `--runtime`). Missing file → error. |
| `--runtime PATH\|-` | "" | JSON runtime (`runs-on`, toolchains, `apt`, `container`). Omitted = ubuntu-latest + Python 3.14. See `autograding.md`. |
| `--tests PATH\|-` | "" | Declarative tests: bare JSON array or `tests.json` envelope. Mutually exclusive with a per-assignment `autograder.py`. |
| `--feedback-pr` | true | One feedback PR per student repo. `--feedback-pr=false` disables. |
| `--empty-repo` | false | Bare repos: no README, marker, shim; no autograding, no feedback PR. Errors with `--template`, `--tests`, `--allowed-files`, `--pass-threshold`, `--pages`, `--submission-mode`, `--submission-tag`, and explicit `--feedback-pr=true` (the default silently becomes false). |
| `--allowed-files PATTERN` | none (all files) | Repeatable, ordered gitignore-style; last match wins; `!` re-includes. Runner deletes disallowed files before grading; `gh student submit` filters too. |
| `--student-permission ROLE` | push (individual) / admin (group) | `pull\|triage\|push\|maintain\|admin` on own repo at accept. `admin` lets students change settings/collaborators (org lockdown still blocks visibility changes). Future accepts only. |
| `--submission-mode every-push\|tag` | `every-push` | `tag`: only `submit/*` tag pushes grade (cost lever). Change later with `submission-mode`. |
| `--submission-tag PATTERN` | none | Repeatable extra trigger tags (`phase1`, `v*`; exact names safer). Graded record still lands as a `submit/*` release. |
| `--repo-visibility private\|public` | `private` | Visibility at creation. **Public repos are not autograded** (GitHub won't let them call the private `classroom50` workflow: "workflow was not found"). Falls back to private if org policy blocks public. Re-add without flag keeps stored value. |
| `--pages off\|workflow\|branch` | `off` | Configure Pages on each student repo at accept (best-effort, warns on refusal). `workflow` = Actions deploy (needs `pages: write`, `id-token: write`); `branch` = publish a branch. Site is public even on a private repo; private-repo Pages needs a paid plan. |
| `--pages-branch NAME` | "" (default branch) | With `--pages branch`; branch must exist in the generated repo. |
| `--pages-path /\|/docs` | `/` | With `--pages branch`. |
| `--pass-threshold 0-100` | off | Advisory passing bar for the web submissions page. Omitted = off (distinct from 0). |

JSON-only fields (no flag; set in web form or by editing `assignments.json`; carried forward on re-add): `no_autograder`, `init_shim`, `include_all_branches`, `release_assets`, `copy_about`, `copy_topics`, `feedback_pr_template`, `closed` (web **Close submission**), `grading`. Shapes and exclusivity: `concepts.md`.

Errors: template 404 (make public or copy into org); private template outside org rejected; repo not flagged as template (names the setting); `--runtime`/`--tests` validation names the bad field.

```sh
gh teacher assignment add cs50-fall-2026 cs-principles hello --name "Hello" \
  --template cs50/hello-template --due 2026-09-15T23:59:00-04:00 --submission-mode tag
gh teacher assignment add cs50-fall-2026 cs-principles project --name "Project" \
  --mode team --team-formation teacher --max-group-size 4
```

### `assignment list`

`gh teacher assignment list ORG CLS [--json] [-q]` — read-only. One slug per line; `--json` = full entries array (all fields). `-q` drops stderr count.

```sh
gh teacher assignment list -q cs50-fall-2026 cs-principles | xargs -I{} gh teacher download cs50-fall-2026 cs-principles {}
```

### `assignment remove`

`gh teacher assignment remove ORG CLS SLUG` — idempotent. Student repos untouched; only new accepts stop finding it. Re-adding the slug later is not a clean reset (existing repos keep old behaviour, e.g. a changed `--empty-repo`; warned).

```sh
gh teacher assignment remove cs50-fall-2026 cs-principles hello
```

### `assignment reuse`

`gh teacher assignment reuse ORG SOURCE-SLUG --from SRC-CLS --to DST-CLS [--slug NEW] [--name TEXT] [--json]`

- `--from`, `--to` required; same org only.
- Copies the record verbatim (including unknown future fields); only slug/name may change. No repos or scores copied.
- No `--slug`: keeps source slug, trimmed to target budget, auto-suffixed `-2`, `-3`... on collision (case-insensitive). Explicit `--slug` refuses collisions, over-budget, or reserved slugs.
- Re-grants target classroom team read on a private in-org template. Refuses archived target.
- `--json`: `{org, classroom, slug, source_slug, auto_suffixed, template}`. Read the final slug here, not from prose.

```sh
gh teacher assignment reuse cs50-fall-2026 hello --from cs-principles-2025 --to cs-principles-2026 --json | jq -r .slug
```

### `assignment rename`

`gh teacher assignment rename ORG CLS OLD-SLUG NEW-SLUG [--dry-run] [--yes] [-q]`

- Only for over-budget slugs (refuses if OLD fits). One rename per assignment; old slug recorded as `renamed_from` and reserved forever (protects GitHub's redirects).
- Steps: (1) one config commit: slug changed, `renamed_from` set, `scores.json` bucket re-keyed, `autograders/<slug>/` moved, assignment **locked**; (2) per student repo (prefix match, verified via `.classroom50.yaml` marker): marker rewritten with `[skip ci]`, repo renamed (GitHub redirects old names indefinitely); (3) lock restored.
- Marker-less (no built-in autograder) repos are matched by prefix only: delete repos of removed assignments whose slug extends this one first. Repos whose marker names another assignment, or unreadable marker, are skipped.
- Per-repo failures don't abort; re-run the same command to resume/heal. Stays locked while any repo is unrenamed.
- Confirmation: type the new slug; `--yes` skips. `--dry-run` prints the plan.
- Students with a marker run `git pull` once before next `gh student submit`. Old scores kept.

```sh
gh teacher assignment rename cs50-fall-2026 cs-principles problem-set-three-with-a-long-name ps3 --dry-run
```

### `assignment lock`

`gh teacher assignment lock ORG CLS SLUG [--unlock]` (`--unlock` default false).

- Locked: web accept page, student list, submission view, and `gh student accept` refuse it for everyone, including those who already accepted. Client-side only (manifest is public), except: for a **private in-org template**, the student team's read on the template is removed (unlock re-grants). Staff teams untouched; repos not deleted.
- Use for timed assessments: add with `--locked`, unlock at start, lock at end.

```sh
gh teacher assignment lock cs50-fall-2026 cs-principles midterm --unlock
```

### `assignment submission-mode`

`gh teacher assignment submission-mode ORG CLS SLUG (--every-push | --tag) [--update-shims=BOOL] [--user LOGIN] [--dry-run] [-q]`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--every-push` | false | Grade every default-branch push (and `submit/*` tags). |
| `--tag` | false | Grade only `submit/*` tag pushes. |
| `--update-shims` | true | Rewrite `.github/workflows/autograde.yaml` in existing repos; `=false` flips only the field. |
| `--user` | "" | Only `<CLS>-<SLUG>-<LOGIN>`. |
| `--dry-run` | false | Report, write nothing. |
| `-q, --quiet` | false | Drop per-repo and summary lines. |

- Enrollment from the classroom team. Idempotent. Retrofit commit has `[skip ci]` (never grades).
- Hand-edited shims (unrecognized trigger block) reported and left alone.
- Custom autograders (teacher-authored shim) refused: edit its `on:` yourself, then re-run with `--update-shims=false` (field still tells submit clients to push the tag).
- `empty_repo` assignments rejected. Needs `workflow` scope. Tell students to `git pull`.

```sh
gh teacher assignment submission-mode cs50-fall-2026 cs-principles hello --tag --dry-run
```

### `assignment enable-autograder`

`gh teacher assignment enable-autograder ORG CLS SLUG [--add-workflows=BOOL] [--user LOGIN] [--dry-run] [-q]`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--add-workflows` | true | Add the workflow to existing repos lacking it; `=false` only clears `no_autograder`. |
| `--user` | "" | One student's repo. |
| `--dry-run` | false | Report only. |
| `-q, --quiet` | false | Quiet. |

- Clears `no_autograder` (no-op if the web app did it), adds the default `autograde.yaml` (rendered for current submission mode and tags) plus `.classroom50.yaml` marker if missing, in one `[skip ci]` commit. Existing workflow files never rewritten. Idempotent.
- Baseline unchanged (submissions and feedback PR still measure from the root commit) only if org scripts are current: run `gh teacher init ORG` first for marker-less repos.
- Already-pushed work grades on the student's **next** push; **Regrade all** can't reach commits made before the workflow existed. Have students push (empty commit OK). The published manifest can lag ~1 minute; an early push fails and grades next time.
- Refused: custom autograders, group/team assignments (use per-row web action), `empty_repo`. Needs `workflow` scope. Students must `git pull`.
- Web equivalent: **Add autograding workflow** on the submissions page.

```sh
gh teacher assignment enable-autograder cs50-fall-2026 cs-principles reflection --dry-run
```

### `assignment feedback-pr`

`gh teacher assignment feedback-pr ORG CLS SLUG [--user LOGIN] [-q]`

- Opens or repairs the feedback PR (base = frozen `feedback` branch at accept commit, head = default branch) on every existing student repo; identical to accept-time PRs so the runner adopts it. Repos with any existing feedback PR left alone. Enrollment from classroom team; repos not yet accepted skipped. Needs owner/admin on the org's repos.
- Output states: **Blocked** (student pre-created `feedback` at the wrong commit: an org admin must delete that branch; re-running never fixes it); **Setup incomplete** (accept never wrote `.classroom50.yaml`: student must open the assignment link and choose **Re-run setup**, then re-run); failed (transient, re-run).

```sh
gh teacher assignment feedback-pr --user alice cs50-fall-2026 cs-principles hello
```

### `assignment test add | set | list | remove`

Manage the assignment's declarative `tests` block (field semantics and examples: `autograding.md`). Never commit a `tests.json` under `<CLS>/autograders/<SLUG>/`; Publish Pages generates it. That directory holds fixtures/scripts, reachable at grade time through `$CLASSROOM50_BUNDLE_DIR` (not copied into the student checkout).

`gh teacher assignment test add ORG CLS SLUG --name N --type io|run|python --run CMD [options]` — upsert by name. Fails if the slug isn't registered or a per-assignment `autograder.py` exists.

| Flag | Default | Meaning |
| --- | --- | --- |
| `--name` | (required) | Unique within assignment. |
| `--type` | (required) | `io` stdout compare, `run` exit code, `python` pytest (points split across cases). |
| `--run` | (required) | Command. |
| `--setup` | "" | Command before `--run`. |
| `--points` | 0 | Points. |
| `--timeout` | 0 (= 10 s) | Seconds. |
| `--input` / `--input-file` | "" | io: inline stdin / bundled fixture. |
| `--expected` / `--expected-file` | "" | io: inline expected stdout / bundled fixture. |
| `--comparison` | "" | io: `included\|exact\|regex`, required for io, no default. |
| `--exit-code` | 0 | run: required exit code (0–255). |
| `--failure-details` | assignment default | `full\|actual-only\|none`. |
| `--show-output` | false | Include setup/run output even on pass (`=false` opts out of a default). |
| `--show-command` | false | Show commands in report (may reveal the check). |

`gh teacher assignment test set ORG CLS SLUG --tests PATH|-` — replace all tests, nothing else changes. Bare array keeps `test_defaults`; `tests.json` envelope sets them from `defaults` (cleared if absent). `[]` removes all. Same refusals as `add`.

`gh teacher assignment test list ORG CLS SLUG [--json] [-q]` — read-only; names one per line, `--json` full specs.

`gh teacher assignment test remove ORG CLS SLUG TEST-NAME` — idempotent; errors only if slug not registered.

```sh
gh teacher assignment test add cs50-fall-2026 cs-principles hello --name "prints hello" --type io \
  --setup "gcc -o hello hello.c" --run ./hello --expected "Hello, world!" --comparison included --points 2
gh teacher assignment test list cs50-fall-2026 cs-principles hello --json > hello-tests.json
gh teacher assignment test set cs50-fall-2026 cs-principles hello --tests hello-tests.json
gh teacher assignment test remove cs50-fall-2026 cs-principles hello "prints hello"
```

Grading precedence (low effort → high): declarative tests → `<CLS>/autograders/<SLUG>/autograder.py` → classroom default `<CLS>/autograder.py`. None → vacuous pass (0/0).

---

## 9. `team` (team-mode assignments) and `group`

All `team` subcommands take `ORG CLS ASSIGNMENT` and require `mode: team` (else error). Groups are secret teams `classroom50-group-<hash>-<n>` owning `<CLS>-<ASSIGNMENT>-group-<n>`. A `TEAM` argument is the counter (`2`, ≥1) or full slug. Membership writes also update `<CLS>/teams.json` (intended-membership snapshot); GitHub Teams remain authoritative for push access. If the snapshot write fails after the GitHub change, a warning says to re-run. Web **Manage groups** edits the same teams.

### `team create`

`gh teacher team create ORG CLS ASSIGNMENT [--name TEXT] [--member USER]...`

- Creates the next free team. `--name` (default "") is a display name only (never in slug/repo). `--member` repeatable.
- Non-rostered usernames skipped with warning; a member already in another group of this assignment refused before creation; capped by `max_group_size`.
- Repo is attached when a student accepts. For `--team-formation teacher`, create groups before sharing the link.
- Partial member-add failure: team exists; use `team add`, not `create` again.

```sh
gh teacher team create cs50-fall-2026 cs-principles project --name "The Sharks" --member alice --member bob
```

### `team list`

`gh teacher team list ORG CLS ASSIGNMENT` — read-only. Counter, name, members, count vs `max_group_size`, drift vs snapshot; snapshot rows with no live team noted. No `--json`.

### `team add` / `team remove`

`gh teacher team add ORG CLS ASSIGNMENT TEAM USER` / `gh teacher team remove ORG CLS ASSIGNMENT TEAM USER`

- `add`: must be rostered; one group per student per assignment; size cap; already on team = no-op. `remove`: not on team = no-op.

```sh
gh teacher team add cs50-fall-2026 cs-principles project 2 carol
```

### `team delete`

`gh teacher team delete ORG CLS ASSIGNMENT TEAM` — deletes the team, drops it from `teams.json`; shared repo untouched. Guarded: live team must match group-team shape, recorded id, and a verified `classroom50/group/v1` record. Already gone = success (stale row dropped).

### `team copy`

`gh teacher team copy ORG CLS ASSIGNMENT --from SOURCE-ASSIGNMENT` (`--from` required)

- Recreates source groups (members + names, fresh counters) for the target. Both must be team assignments in the same classroom. Non-rostered members and those already grouped in the target skipped; a group with everyone skipped not created; a source group over target's `max_group_size` fails the copy. Web **Copy groups** = same with preview.

```sh
gh teacher team copy cs50-fall-2026 cs-principles project2 --from project
```

### `group list`

`gh teacher group list ORG CLS ASSIGNMENT [--json | --csv]` — read-only, for group or team assignments.

- One row per member. Team mode: live teams (empty or repo-less teams still get a row). Legacy group mode: existing group repos with founder + direct collaborators.
- Joined to `roster.csv` by `github_id`, then username. `in_roster=no` flags unknown accounts.
- `--csv` header: `group,group_name,team_slug,repo,username,first_name,last_name,email,section,github_id,role,in_roster,note` (same as web **Download groups (CSV)**). `group` = `group-<n>` or legacy founder login; joins with `scores.csv` `group` column. `note` set when membership couldn't be read. `--json` same keys, wins over `--csv`.

```sh
gh teacher group list cs50-fall-2026 cs-principles project --json | jq '.[] | select(.in_roster == "no")'
```

---

## 10. `autograder` (classroom default)

Manages `<CLS>/autograder.py`; lists `<CLS>/autograders/`. Named shims (`<name>.yaml`) and per-assignment overrides (`<slug>/autograder.py`) are **read-only from the CLI**: author/delete them with git. Authoring details: `autograding.md`.

| Command | Flags (defaults) | Behaviour |
| --- | --- | --- |
| `autograder set-default ORG CLS` | `--from PATH\|-` (none = diagnostic stub) | Replaces `autograder.py` in one commit; identical content skips commit. Stub echoes runner env and emits vacuous pass (pipeline check). Live after next publish-pages run (~30 s). Classroom must exist. |
| `autograder show ORG CLS` | `--json` (false), `-q` (false) | Body to stdout; `--json` = `{path, exists, is_stub, size, sha}`. Missing default: empty stdout, exit 0. Read-only. |
| `autograder list ORG CLS` | `--json` (false), `-q` (false) | `<name>.yaml` and `<slug>/` entries; `--json` = `{name, kind, path}`. Default not listed. Read-only. |
| `autograder remove ORG CLS` | `--yes` (false) | Deletes the file (not the same as stub). Prompts unless `--yes`. Idempotent. Assignments without tests/override fall back to vacuous pass. |

```sh
gh teacher autograder set-default cs50-fall-2026 cs-principles --from ./autograder.py
gh teacher autograder show cs50-fall-2026 cs-principles --json | jq .is_stub
```

---

## 11. Org/repo membership: `invite`, `remove`, `member list`

These act on real GitHub membership, not the roster. Prefer `roster add` for students (rosters + invites + team).

### `invite`

`gh teacher invite ORG[/REPO] USER [--admin] [-p PERM] [-q]`

| Flag | Default | Meaning |
| --- | --- | --- |
| `--admin` | false | Org invite as owner/admin (org targets only; error with a repo target). |
| `-p, --permission` | `push` | Repo targets only: `pull\|triage\|push\|maintain\|admin`; error if passed with an org target. |
| `-q, --quiet` | false | No success output. |

- Invites by resolved user id. Org invite = `direct_member` unless `--admin`. Repo invites idempotent (re-run updates permission). Org invites aren't: already member / pending become actionable messages. Needs `admin:org`.
- Use for co-teachers (`--admin`) or ad-hoc cases; `staff add` for classroom roles.

```sh
gh teacher invite --admin cs50-fall-2026 coteacher
gh teacher invite -p maintain cs50-fall-2026/hello-template ta-login
```

### `remove`

`gh teacher remove ORG[/REPO] USER [-q]`

- Org form: removes from org (all repo access, all teams, cancels pending invite). Repo form: removes collaborator. Idempotent (non-member / 404 → exit 0).
- Pair with `roster remove` to fully drop a student.

```sh
gh teacher remove cs50-fall-2026 alice
```

### `member list`

`gh teacher member list ORG[/REPO] [--json] [-q]` — read-only.

- Org: members + pending invitations (`kind` = `member`/`invitation`, `role`); reading invitations needs `admin:org`. Repo: collaborators (`kind` = `collaborator`, `role` = read/triage/write/maintain/admin).
- `--json`: `{login, kind, role, github_id}`; on invitation rows `github_id` is the **invitation id**, not an account id; don't join with roster. `-q`: one login per line.
- Use to diff intended (roster) vs actual (e.g. students who never accepted).

```sh
gh teacher member list cs50-fall-2026 --json | jq -r '.[] | select(.kind=="invitation") | .login'
```

---

## 12. `download`

`gh teacher download ORG CLS ASSIGNMENT [-d DIR] [--pull] [--by-pattern] [-q]`

| Flag | Default | Meaning |
| --- | --- | --- |
| `-d, --dir` | `<CLS>-<ASSIGNMENT>_submissions_<timestamp>/` | Destination, used literally (no timestamp). |
| `--pull` | false | Fast-forward existing clones (`git pull --ff-only`) instead of skipping. |
| `--by-pattern` | false | Clone every org repo named `<CLS>-<ASSIGNMENT>-*`; no team lookup, no result refresh, no `scores.csv`. |
| `-q, --quiet` | false | Quiet; passes `--quiet` to git. |

- **Default (team-driven):** members of the classroom team → expected repo per member → `gh repo clone` (uses current gh auth). Missing repos reported (`Missing: USER (...)`), not fatal. Refreshes `<repo>/result.json` (latest) and `<repo>/results.json` (all submissions, newest first) from `submit/*` releases.
- A `submit/*` release not published by the autograde workflow is still recorded, with `provenance_warning` naming the publisher in `results.json` and a stderr line; `result.json` keeps the newest score unmarked. A non-`classroom50/result/v1` asset is treated as missing (`result_problem` explains).
- Writes `scores.csv` at destination root: one line per submission per member (newest first), group members repeat the shared lines, non-submitters get one blank-score line. `roster.csv` only supplies name/section/email metadata. `scores.csv` `provenance_warning` column comes from the last collection run, not this download. Columns: `autograding.md`.
- Existing clone dirs are skipped (still get `result.json` refresh). `--pull` on a diverged clone (force-push, local commits) reports failure and leaves it; fix with git or delete and re-run.
- Use `--by-pattern` when `classroom50` isn't bootstrapped or to grab everything regardless of roster; `--pull` works with it.
- `scores.csv` reflects releases; run `collect-scores` for `scores.json`.

```sh
gh teacher download --pull -d hello-subs cs50-fall-2026 cs-principles hello
```

---

## 13. What the CLI cannot do (web app, workflow, or GitHub UI)

- **Score collection / regrade / token probe:** `gh workflow run collect-scores.yaml|regrade.yaml|probe-token.yaml --repo ORG/classroom50 ...` or web buttons (**Collect now**, **Regrade all**).
- **Manual score override:** edit `<CLS>/scores.json`, set the entry's `score`, add `"override": true`, commit. Collection preserves overridden entries.
- **Web-only roster actions:** refresh `role` column for all rows; add rows for classroom-team members missing from the roster; **Link account** for unlinked rows; **Upload roster** with id-only rows; invite **staff** by email.
- **Assignment fields with no flag:** `no_autograder`, `init_shim`, `include_all_branches`, `release_assets`, `copy_about`, `copy_topics`, `feedback_pr_template`, `closed` (**Close submission**), `grading`. Web form or edit `assignments.json`.
- **Existing-repo changes:** **Change repository visibility**, **Enable GitHub Pages** (submissions page). Group/team repos: **Add autograding workflow** per row.
- **Named shims and per-assignment `autograder.py`:** git only.
- **Org creation, template-repo flag, 4 member-privilege settings, deleting individual student repos:** GitHub UI.
- **Ruleset repair after version skew:** newest `init` or web **Fix it**.

---

## 14. Gotchas and safety behaviours

Refusals and guards:
- `init` needs org **owner**; preflight aborts before any change.
- No token flag anywhere; tokens via env var, piped stdin, or hidden prompt. Non-interactive + no env var → `init` preflight fails fast.
- `classroom add` never overwrites; short-name rules incl. `-teacher|-hta|-ta` suffix ban.
- Archived classroom: `assignment add`/`reuse` and `roster sync --write` refused.
- `roster invite` can't invite staff; `--file` validates every line before sending.
- `roster cancel-invite` refuses invitations it can't prove belong to this classroom.
- `roster remove EMAIL` refuses if anything could still accept.
- `roster sync` degraded read → nothing deleted; never removes rows.
- `roster import` commits nothing until every line is valid.
- `assignment rename` refuses in-budget slugs and second renames; old slug reserved.
- `--empty-repo` mutual exclusions; `--repo-visibility public` disables autograding.
- `test add/set` refused when a per-assignment `autograder.py` exists.
- `submission-mode`/`enable-autograder` refuse custom autograders; `enable-autograder` refuses group/team and `empty_repo`.
- `team delete` verifies team identity; `team` subcommands require team mode.
- `teardown` requires `classroom50` marker repo, typed org name, and opt-in `delete_repo` scope.
- `classroom remove`, `autograder remove`, `assignment rename`, `teardown` prompt; `--yes` skips. `init` prompts only for workflow refresh.

Idempotent / safe to re-run: `init`, `rotate-service-token`, `classroom archive/unarchive/edit`, `roster add` (but see whole-row replace), `roster invite --file`, `roster remove`, `staff add/remove`, `assignment remove/lock`, `submission-mode`, `enable-autograder`, `feedback-pr`, `rename` (resumes), `test remove`, `autograder set-default/remove`, `team add/remove/delete`, repo-form `invite`, `remove`.

Silent-data traps:
- `roster add` on an existing username blanks unspecified name/email/section; use `roster update`.
- `assignment add` same-slug re-add drops template/tests/allowed-files/pass-threshold/student-permission not re-passed (warned). Restore tests with `assignment test set`.
- `CLASSROOM50_SERVICE_TOKEN` exported in your shell when re-running `init` overwrites the stored secret.
- `roster list -q` omits pending email rows.
- `member list --json` invitation rows carry invitation ids.
- `--available-from` only lists; `--locked` is the gate (and only enforceable for private in-org templates).
- Archive, unlisted, and `assignments.json` changes reach students only after publish-pages redeploys; roster-only commits don't trigger a redeploy (roster isn't published).
- `roster remove` keeps org access; `gh teacher remove` drops it. Both needed to fully remove a student.
- `assignment remove` leaves repos; re-adding the slug isn't a reset.
- After `submission-mode`/`enable-autograder`/`rename`, students must `git pull`.
- Collection is team-driven: a student not on `classroom50-<CLS>` isn't collected even if rostered; staff who accepted are collected.

---

## 15. Wiki vs code discrepancies found (commit 34a3d66 vs wiki 4d79ad48)

1. **`init` service-token re-run:** wiki says a re-run leaves an existing secret untouched. Code (`service_token.go`): if `CLASSROOM50_SERVICE_TOKEN` is set, it is validated and **replaces** the secret even when one exists; untouched only when the env var is absent. Code's own message confirms ("or set CLASSROOM50_SERVICE_TOKEN and re-run").
2. **Token from piped stdin:** code accepts the token as one line on piped stdin for `init` and `rotate-service-token`; the wiki mentions only env var and interactive prompt.
3. **`init` lockdown, help text vs code:** `init --help` says members keep only private-repo and public-Pages creation; code (`orgpolicy`) also keeps `members_can_create_teams` on. The wiki matches the code.
4. **`classroom remove`:** `--help` says it deletes only the directory; code also deletes the classroom's student/staff teams and revokes staff teams from the feedback ruleset. The wiki matches the code.
5. **`teardown`:** `--help` mentions only repos; code also deletes classroom, invite, and group teams (wiki matches code).
6. **`roster add` re-run:** wiki says "safe to re-run" without mentioning that a username-matched re-add replaces the whole row (unspecified name/email/section blanked). Code (`UpsertRosterRow`) and `roster update --help` confirm the blanking.
7. **`--empty-repo` exclusions:** the wiki flag table omits `--pages` (mentioned only under `--pages`); `--help` omits `--feedback-pr`. Code rejects both `--pages` and an explicit `--feedback-pr=true`; a defaulted `--feedback-pr` silently becomes false.
8. **`group list` missing from the wiki's "Commands at a glance" table** (it has its own section; the command exists in code).
9. **`download` missing-repo message:** wiki says `Missing: <username>`; `--help` says `not yet accepted`. Actual output is `Missing: USER (no repo at ORG/REPO; not accepted yet?)` (plus group/team variants).
10. **`--max-group-size` range:** code flag help says "at least 2"; validation caps it at 100 (matches wiki's 2–100). Not a conflict, but `--help` doesn't show the cap.
