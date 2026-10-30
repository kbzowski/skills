> Source: classroom50 commit 34a3d66 / wiki 4d79ad48 (2026-10-21). CLI details verified against `cli/gh-student/` (Go); where the wiki and code disagree, this file follows the code and says so.

# Student side of Classroom 50

How a student joins, accepts, works, submits, collaborates, and reads results, in the web app (classroom50.org) and the `gh student` CLI. Teacher-side detail lives in sibling files:

- `concepts.md`: orgs, classrooms, roster, assignment modes, repo shapes
- `teacher-web.md` / `teacher-cli.md`: what the teacher clicks or runs (close, lock, groups, collect)
- `autograding.md`: runner, tests, Releases, `result.json`, submission modes, milestone tags
- `troubleshooting.md`: full error catalogue, including teacher fixes

## Mental model (read first)

- Everything runs on GitHub. A classroom is a GitHub **organization**, enrollment is membership of the classroom's GitHub team, and an assignment is a repo the student gets in that org.
- There is no server. Assignment data reaches students through the org's GitHub Pages site (public `assignments.json`). Scores live in the student's own repo as GitHub **Releases**. The web app does not display scores itself.
- Org membership and classroom enrollment are separate. Being in the org is not enough; the student must be on the classroom roster (the classroom's student team) to accept.
- Repo names (all lowercase):
  - Individual and **Group (legacy)**: `<classroom>-<assignment>-<username>` (the legacy group repo carries the founder's username)
  - **Group** (team mode): `<classroom>-<assignment>-group-<n>`
  - GitHub caps repo names at 100 characters.
- Repos are **private** unless the teacher opted the assignment into public repos.
- Due date = label only. Late work is accepted, graded, and flagged **late**. Only **Close submission** (read-only repos) or **Lock** actually stops students.

## Prerequisites

- A GitHub account.
- An invitation to the classroom org (emailed by GitHub after the teacher adds the student to the roster). Students cannot join by link alone; an org owner must invite them. Invitations expire after **7 days**.
- For the CLI: GitHub CLI `gh`, plus `git`. Install the extension:

```sh
gh extension install foundation50/gh-student
gh student --help
gh extension upgrade gh-student      # update; or: gh extension upgrade --all
```

If a command fails saying the assignment uses a mode "this version of gh-student does not support", upgrade the extension and retry.

---

# Web app (classroom50.org)

## Join the classroom (accept the org invitation)

Any one of these works:

1. Follow the link in GitHub's invitation email.
2. Sign in to Classroom 50. The home page lists pending invitations. Expand the list and click **Accept and open**.
3. Open the assignment link the teacher shared. The accept page accepts the pending invitation first, then shows the assignment.

If the assignment link says **Not a member yet**, the student has no invitation. The teacher must add them to the roster and invite them. Once the invitation arrives and is accepted, click **Check again**.

## Sign in

- Click **Sign in with GitHub** and authorize Classroom 50 in the popup.
- If that fails, expand **Other sign-in methods**:
  - **Use a device code instead**: copy the one-time code, paste it on GitHub's verification page, return. The app notices within seconds.
  - **Use a personal access token (classic)** / **Use a personal access token (fine-grained)**: skips the sign-in proxy entirely. Use this when a school filter blocks it.
- Sign-in asks for the `repo` scope (all repositories). GitHub offers no narrower classic scope. Teachers and students grant the same set. A fine-grained token scoped to one org is the way to grant less.

## Find assignments

1. Home page lists **Classroom 50 organizations**. On the class org, click **Open**.
2. On **My classrooms**, find the classroom, click **View assignments**.
3. The **Assignments** page shows each released assignment with type (**Individual**, **Group**, **Group (legacy)**), due date, last submitted time, and status:
   - **Not accepted**: button **Accept assignment**.
   - **Accepted**: repo exists, nothing submitted yet. Button **View my submission** (or **View group submission**).
   - **Submitted**: at least one submission. **Last submitted** shows when.
4. Filters: status (**To do**, **Accepted**, **Submitted**), type, due date. Sort by due date or name.

Gotchas:

- A past due date shows red only while nothing is submitted. After any submission it's plain text.
- Status cells fill in progressively (rows shimmer). If a check fails the row keeps **Accepted** and says **Couldn't check submissions**. Refresh to retry.
- Assignments with a future release date, or none, are not listed. They open only from the invite link. After accepting, they appear in the list.

## Accept an assignment

Open the invite link, or click **Accept assignment** in the list. The accept page shows type, due date, **Assignment details** (the teacher's description, rendered Markdown), the signed-in account, and the repo name to be created. Click **Accept assignment**.

- A checklist tracks setup. When done: **Open repository** (GitHub) or **Go to my classroom**.
- Re-opening the link later shows that the assignment is already accepted, with **Open repository**.
- Repair: if autograding isn't running or setup files are missing, expand **Having trouble?** and click **Re-run setup**.

Notices on the accept page:

- **This repository will be public**: the assignment creates public repos. Code, commits, and name are visible to anyone. If the org forbids public repo creation, a private repo is created instead and the teacher can flip it later.
- **GitHub Pages is enabled for this assignment**: accepting turns on a Pages site for the repo. The address is in the notice's tooltip. The **site is public even if the repo is private**, so keep anything private out of the published branch or folder. If Pages can't be enabled (for example, the plan disallows Pages on private repos), the checklist says so. The assignment still works and the teacher can enable the site later.

Blocking messages:

| Message | Meaning / action |
|---|---|
| **This assignment is locked.** | Teacher locked it (often before a timed test). Wait or ask for unlock. Locked also hides it from students who already accepted. |
| **Submissions are closed.** | Teacher closed it. No new accepts. If already accepted, the repo still opens (read-only). |
| **This assignment isn't available to you.** | Not enrolled in this classroom (on the org but not the roster). Ask the teacher. |
| **Assignment not found.** | Wrong link, or not published yet. Check the URL with the teacher. |
| **Not a member yet** | No org invitation yet; see Join. |

## Submit (web)

There is no upload button. Submitting means commit and push to the repo. The **My submission** page has **Submit from the command line**: copyable commands to clone once, then run `gh student submit` inside the clone. See the CLI section below for the details of what gets graded.

Submit-only assignments: a plain push saves work but doesn't grade it (the commit's check says so). Run `gh student submit` or push a `submit/` tag, or a milestone tag the teacher named:

```sh
git tag submit/final && git push origin submit/final
git tag phase1 && git push origin phase1
```

If the teacher changes the grading setup, run `git pull` before the next push.

## View submissions and scores (web)

- In the assignment's left menu: **My submission** (group: **Group submission**).
- The callout at the top says whether you've submitted and when. If not, **Show me how to submit** opens the CLI guide.
- The table shows the repo (group: **Group repository**, with teammates listed above), the submission count, and the last submitted time. Row actions:
  - open repo on GitHub
  - **View submissions**: list of submissions. Each graded one has **View score**. On group work it names the teammate who made each commit.
  - **View autograder details**: latest graded result (only once something is graded)
- From the **Assignments** page: **View my submission**, or for groups **View group submission** / **View group**.
- **View score** and **View autograder details** both open the GitHub **Release**. The app does not show the number itself (browsers can't read Release assets cross-origin; tracked as issue #567).

---

# CLI (`gh student`)

## Command tree (verified in code)

Global: `--verbose` / `-v` (persistent, all commands): per-step API and git output. Also `--version`, `--help`. Errors go to stderr, exit 1.

| Command | Args | Flags (default) |
|---|---|---|
| `whoami` | none | none |
| `login` | none | `-s, --scopes` extra scopes (repeatable or comma-separated; default none) |
| `logout` | none | none |
| `accept` | `<org> <classroom> <assignment>` (exactly 3) | `--key ""`, `--new-team false`, `--team-name ""` |
| `invite` | `<org>/<repo> <username>` (exactly 2) | none |
| `team list` | `<org> <classroom> <assignment>` (exactly 3) | `--key ""` |
| `team add` | `<org> <classroom> <assignment> <username>` (exactly 4) | `--key ""` |
| `submit` | none | `--key ""` |
| `completion` | `<shell>`: `bash`, `zsh`, `fish` | none |

`<classroom>` is the classroom short name (slug), not its display title. `<assignment>` is the assignment slug. Case is normalized; spelling must be exact.

## Auth: `whoami`, `login`, `logout`

```sh
gh student whoami                 # prints your GitHub login
gh student login                  # gh auth login + Classroom 50 scopes
gh student login -s gist          # add extra scopes
gh student logout                 # runs gh auth logout
```

- Scopes requested on top of gh defaults: `admin:org`, `read:org`, `repo`, `workflow`. Same set as `gh teacher login`, so one sign-in covers both.
- `login` replaces the stored github.com token. If one exists it warns and asks for confirmation.
- `login` is optional. `accept` and `submit` reuse a token that already has the scopes, widen an under-scoped gh-managed token in place, or run the login flow if no token exists.
- **Agent gotcha:** login and scope widening need an interactive terminal (stdin and stderr both a TTY). In a non-interactive shell the CLI errors out instead of opening a browser:
  - not signed in: "not signed in to github.com; run `gh student login` from an interactive terminal"
  - missing scopes: it tells you to run `gh auth refresh -h github.com -s admin:org,read:org,repo,workflow`
  - Either have the student run that themselves, or export `GH_TOKEN` with a PAT carrying those scopes. Env-var tokens are user-managed and never rewritten.

## `accept`

```sh
gh student accept <org> <classroom> <assignment>
gh student accept cs50 cs50-fall-2026 hello
gh student accept cs50 cs50-fall-2026 hello --key dhkrm4ih
gh student accept cs50 cs50-fall-2026 project --new-team --team-name "The Sharks"
```

Flags:

- `--key <key>`: access key for a classroom with an **unlisted URL**. It's part of the published Pages path (`<classroom>/<key>/...`). Without it the assignment list can't be found. Normal classrooms need no key. The key is format-checked before any network call.
- `--new-team`: team-mode assignments with **student-formed** groups only. Creates a new group and makes you its founder (GitHub team maintainer). If you're already in a group, the flag is ignored with a warning, so a re-run never creates a second group.
- `--team-name <name>`: display name for the group `--new-team` creates.
- Passing `--new-team` or `--team-name` on a non-team assignment is an error ("do not apply; run accept without them").

What it does, in order:

1. Checks org membership. A pending invitation is auto-accepted (no need to accept the email first).
2. Enrollment gate: you must be on the classroom's student team or a staff team. Org owners bypass.
3. Looks up the assignment in the public published list.
4. Gates: **locked** first, then **closed**. Both refuse even if you already accepted (see gotchas).
5. Team mode: resolves your group, or founds one with `--new-team`.
6. Resolves the autograding workflow: the bundled standard one, or the teacher's custom one downloaded from Pages before the repo is created.
7. Creates the repo: a copy of the starter template, a README-initialized repo (template-less), or a bare repo (empty-repo assignment). Private unless opted public. If public creation is denied, it falls back to private with a warning.
8. Applies repo features (Issues, Wiki, Projects, PRs) as the template had them or as the teacher forced. Best-effort.
9. Enables GitHub Pages if the assignment publishes a site. Best-effort; a refusal is printed and never fails accept. Runs on a fresh create only.
10. One commit with `.classroom50.yaml` (marker) plus `.github/workflows/autograde.yaml` (shim), then verifies both exist. Skipped entirely when the assignment doesn't use the built-in autograder, and for empty-repo assignments.
11. Opens the feedback PR if enabled. Best-effort; otherwise the first graded submission creates it.
12. Sets your role last: `push` for individual, `admin` for legacy group founder. Team mode gets access through the team. The teacher can override this per assignment.
13. Prints clone commands for HTTPS and SSH:

```
Assignment accepted: <org>/<repo>
Clone it with HTTPS:
  git clone https://github.com/<org>/<repo>.git
Or with SSH:
  git clone git@github.com:<org>/<repo>.git
```

Empty-repo assignments print that the repo has no starter files and autograding is disabled. Create and push your own work.

Re-running is safe. A fully set-up repo is left alone (role refreshed) and prints `Assignment already accepted: <org>/<repo>` plus the clone commands. A half-finished setup is repaired. If accept says the marker is missing after setup, just run the same accept again.

Gotchas:

- If you run accept from inside another git repo, it warns you to clone from a parent directory to avoid nesting repos.
- **Closed or locked blocks the CLI re-run too.** The code checks locked/closed before it checks for an existing repo, so `accept` on a closed assignment errors even when your repo exists. The web page instead still offers **Open repository**. Fix: clone directly with `git clone https://github.com/<org>/<classroom>-<assignment>-<you>.git`, or `gh repo view <org>/<repo>`.
- Template edits by the teacher reach only future accepts. Your repo is a copy, not a fork. Only `.gitignore` and `.github/` re-sync (on `submit`).

## Clone and work

```sh
git clone <url printed by accept>
cd <repo>
# edit, then:
git add -A && git commit -m "..." && git push
```

Work on the repo's **default branch** (usually `main`, sometimes `master`). That branch is what triggers grading. Pushes to other branches don't grade.

Codespaces works if the org enabled it. Classroom 50 doesn't manage it.

## `submit`

Run from inside the clone:

```sh
gh student submit
gh student submit --key a1b2c3d4     # only for unlisted classroom AND no .classroom50.yaml
gh student submit -v                 # show git and API detail, signing prompts
```

What it actually does (code):

1. Finds the git root and reads the `origin` remote. The remote must be `https://github.com/owner/repo` or `git@github.com:owner/repo`.
2. Identifies the assignment from `.classroom50.yaml`. If the file is absent, it matches the repo name against the classroom's published list (this needs `--key` for unlisted classrooms).
3. Snapshots your submittable files into a temp work tree: tracked files plus untracked files that aren't ignored (`git ls-files -co --exclude-standard`). Uncommitted edits are included. Ignored build artifacts are not.
4. If the teacher set `allowed_files`, files outside those patterns are left out of the snapshot. Control files (`.classroom50.yaml`, `.github/`, `result.json`, `release-body.md`) always go in. Use `-v` to see "Excluding ..." lines.
5. Overlays the teacher's latest `.gitignore` and `.github/` from the starter template. Skipped when there's no template, or the repo has no marker.
6. Clones the remote into a temp bare repo, commits the snapshot **on top of the remote default branch** with the message `[Classroom 50] Submit <assignment>` (`--allow-empty`), and pushes as a fast-forward. It never force-pushes.
7. Submit-only assignments: also pushes tag `submit/<UTC yyyy-mm-ddThh-mm-ssZ>-<7-char sha>`, reusing an existing `submit/*` tag at that commit so a retry never double-grades. Every-push assignments get no tag from the CLI; the runner mints it.
8. Prints:

```
Submitted assignment "<name>" at 2026-10-24 14:05:09 CEST
View your submission at: https://github.com/<org>/<repo>/commit/<sha>
```

Identity: uses the clone's `user.name` / `user.email` and signing config, so signed commits stay verified. Unset values fall back to the GitHub login and noreply email. `GIT_AUTHOR_*` / `GIT_COMMITTER_*` env vars override both.

### Plain git vs `gh student submit`

| | `git push` | `gh student submit` |
|---|---|---|
| What lands | your commits, with their history | one new commit whose tree is your current working-tree snapshot |
| Uncommitted / untracked (non-ignored) files | not included | included |
| Teacher `.gitignore` / `.github/` refresh | no | yes (template assignments) |
| `allowed_files` filter | no (the runner still enforces it when grading) | yes, client-side |
| Grades on every-push assignment | yes | yes |
| Grades on submit-only assignment | no (check reads "push not graded") | yes (pushes `submit/...` tag) |
| Updates your local clone | yes | **no**: the local branch is now behind origin |
| Conflict detection with remote changes | yes (push rejected if behind) | **none**: the snapshot replaces the tree |

The wiki calls submit "functionally equivalent to `git commit -am 'Submit' && git push`" plus the teacher refresh. Per the code that's only roughly true. Mind these:

- **Pull before submit, especially in groups.** The submit commit's tree is exactly your local files. Teammates' pushes that aren't in your clone are silently dropped from the new commit. History keeps them, but the graded tree loses them. Always `git pull` first.
- **Pull after submit.** Your local branch doesn't contain the submit commit. The next `git push` is rejected until you `git pull`.
- Local commits you never pushed don't reach GitHub as separate commits. Only their content does, inside the snapshot.
- **Every submit creates a commit, even with no changes** (`--allow-empty`). On every-push assignments, each run costs a grading run.
- Files you deleted locally are deleted in the submission.
- Symlinks are copied as the file contents they point to.

Recommended routine:

```sh
git pull
git add -A && git commit -m "work" && git push    # optional, keeps history granular
gh student submit
git pull                                          # sync the submit commit
```

### Grading triggers (what the student sees)

- **Every push (default):** each push to the default branch triggers one graded run on the commit the push ends on. A push of several commits grades once, but the submissions page counts each commit. The runner tags `submit/<timestamp>-<sha>` and publishes a Release a minute or two later.
- Not graded or counted: the acceptance commit (its status says there's nothing to grade yet), the empty "Open Feedback PR" commit from accept, and the small commit the teacher's trigger change lands. Your first `gh student submit` always grades.
- **Submit-only** (`submission_mode: tag`; web label: submission type "A tagged commit"): plain pushes don't grade. You see commit status `classroom50/autograde-skipped` saying "push not graded; run gh student submit", and possibly no workflow run at all. That's normal. Grade with `gh student submit` or a hand-pushed tag.
- **Tags that grade:** `submit/<name>`, plus any milestone patterns the teacher configured (for example `phase1`, `phase2`, `complete`; case-sensitive; up to 20). A milestone push records its result under a canonical `submit/...` Release whose title ends `(via phase1)`.
- Tag matching follows GitHub Actions filter rules: `*` doesn't cross `/`. So `submit/final` grades but `submit/v1/final` does not. (Wiki says "any tag under `submit/`"; the shim filter `"submit/*"` matches one path segment only.)
- A tag that matches nothing shows "tag is not a submission trigger". Check the milestone names with the teacher.
- Teacher switched trigger mode? A small commit lands in your repo. `git pull` before the next push or you'll hit a conflict.

## Group work

### Team mode (web type **Group**; registered with `--mode team`)

One shared repo per group: `<classroom>-<assignment>-group-<n>`, owned by a GitHub team. The first member to accept creates it. Members get push access through the team. Groups have display names. Renaming a group never renames the repo. Every member on the roster gets the same score.

**Teacher-formed groups:**

- Web: the accept page says **You're not in a group yet**. Ask the teacher, then reopen the link.
- CLI: "your teacher assigns the groups for this assignment. Ask your teacher to add you to a group, then run accept again."
- A student who created their own team, and so maintains it, is refused on a teacher-formed assignment. Only teacher-made groups count.

**Student-formed groups, web:**

- Join: under **Join a group**, the accept page lists groups with member counts. **Ask to join** opens the group's GitHub team page. Click **Request to join** there; you can cancel the request on the same page. After approval, come back and click **Check again**.
- Create: optionally fill **Group name (optional)**, click **Create group**. You become the first member and the maintainer.
- Manage: **Manage my group** on the accept page, or **Manage group** in the left menu.
  - The creator (maintainer) alone can **Add** a teammate by username, remove members, and **Review join requests on GitHub**. The creator can't leave; the teacher can move them.
  - Other members: **Leave group**. You type the group name to confirm. You lose repo access (your work stays with the group), and rejoining needs a new request and approval.
- The page shows the member count against the max size. If over the limit (people added directly on GitHub), a warning shows, and the teacher sees it too. Remove members or ask the teacher.
- Teacher-formed groups show a read-only member list.

**Student-formed groups, CLI:**

```sh
# founder
gh student accept <org> <classroom> <assignment> --new-team --team-name "The Sharks"
gh student team add <org> <classroom> <assignment> <teammate>
# each teammate, after being added
gh student accept <org> <classroom> <assignment>
# anyone
gh student team list <org> <classroom> <assignment>
```

Without a group and without `--new-team`, accept says to rerun with `--new-team` or get added by a teammate.

`team list` output:

```
You are in group 3 for project (<team-slug>)
Members (2):
  alice
  bob

Shared repository: <org>/<classroom>-project-group-3
```

`team add` rules (code):

- Only on team-mode assignments. Otherwise: "for a group assignment use `gh student invite`".
- You must be in a group. Only the founder (maintainer) can add. GitHub's 403 is reworded to say so; orgs that sync teams from an identity provider block it entirely.
- The teammate must be enrolled. Otherwise: "<user> is not enrolled in <classroom>: ask your teacher to add them". If the check itself fails, it warns and adds anyway.
- One group per student. If they're in another group (active or pending), it's refused with that group's number; they leave from its GitHub page or the teacher moves them.
- Size cap: "your group is full: it has N member(s), the maximum of M". This is advisory and re-checked at collection.
- Re-adding an existing member: "already in group N, nothing to do".
- On success it prints `Added <user> to group N for <assignment>` and `They can now run: gh student accept ...`.

### Legacy mode (web type **Group (legacy)**; `--mode group`)

No team. The first teammate accepts and becomes **admin** of a repo named after them: `<classroom>-<assignment>-<founder>`. The founder adds the others as collaborators:

- Web: **Edit collaborators** on the accept page, or **Manage group** → **Manage collaborators**. In the **Group collaborators** dialog, add usernames, then **Save collaborators**. Only the founder can do this. The dialog enforces the max size.
- CLI: `gh student invite <org>/<classroom>-<assignment>-<founder> <teammate>`. Each teammate gets `push` and must accept GitHub's repo invitation.
- Collaborators must be org members. Only collaborators enrolled in the classroom get the score.
- Everyone works in and submits from the one repo.
- Legacy groups have no names. Don't rename the repo.

### `invite`

```sh
gh student invite <org>/<repo> <username>
gh student invite cs50/cs50-fall-2026-hello-alice cs50-duck
```

- Adds `<username>` as a **push** collaborator. They must accept GitHub's invitation before pushing. Re-inviting an existing collaborator is a no-op.
- Size check runs only when invoked **from inside the clone** of that assignment's repo, which supplies `.classroom50.yaml`. On a legacy group, a full group is refused with "group is full: ... the maximum of M". The cap is advisory and can be bypassed in the GitHub UI; crediting is decided at collection.
- On a team-mode repo it refuses and points to `gh student team add`, but only when run from inside that repo's clone. Run elsewhere, it just tries to add a collaborator, which would never be credited. (The wiki says it always refuses on team assignments.)
- Adding collaborators needs admin on the repo on GitHub's side. Individual-assignment students normally hold `push`, so a TA or classmate invite there will likely be refused by GitHub unless the teacher granted a higher role. (Inference from the role logic; not stated in the wiki.)

## Feedback pull request

If the teacher enabled feedback:

- One long-lived PR titled **Feedback**. Its base is a frozen branch `feedback` pinned at the accept commit; its head is your default branch. Labeled **Individual Assignment** or **Group Assignment**.
- It's opened at accept time, via an empty commit `[Classroom 50] Open Feedback PR (gh student accept)` marked `[skip ci]` (not graded or counted). If that fails, rerun `accept`, or it appears on the first graded submission.
- It updates itself as you push. The same PR is reused for every submission.
- **Files changed** / **Commits** show everything pushed since accept, the same view the teacher has. On autograded assignments the body links the latest result.
- Click **Subscribe** to get notified when the teacher comments.
- **Don't close or merge it** unless told to. Students can't merge anyway: a `classroom50-feedback-base-lock` ruleset locks `feedback`, and "Merging is blocked" is expected for students. A merge by staff is the "grading done" signal.
- The teacher may use a custom body (`pull_request_template.md` from the template).

## Reading results

Every graded submission produces:

| Where | What |
|---|---|
| **Release** in your repo, on tag `submit/<UTC-timestamp>-<short-sha>` | Score, per-test PASS/FAIL table, failure details, and a `result.json` asset (machine-readable). The only place with the per-test breakdown. This is what **View score** and **View autograder details** open. The latest Release is your most recent graded submission. |
| Commit status `classroom50/autograde` on the graded commit | success / failure / error at a glance (green check or red X on GitHub) |
| **Actions** tab, run "Autograde" | Live progress and the full log. The job log keeps 100,000 characters of output; the Release body and summary only the first 2,000. |
| Teacher's collected scores (`scores.json` in the org's `classroom50` repo) | What the teacher's submissions page and CSV exports show. Updates only when the teacher runs collection, so it lags your Release. |

Where to look:

```sh
gh release list -R <org>/<repo>
gh release view -R <org>/<repo>                      # latest
gh release download <submit/...tag> -R <org>/<repo> -p result.json
gh run list -R <org>/<repo> --workflow Autograde
```

Failure detail depends on the teacher's setting:

- `full` (default): input, plus a diff or expected vs actual output, plus stderr
- `actual-only`: only your own output
- `none`: only the failure kind (wrong output, wrong exit code, timeout, setup failed)

For long build output, read the Actions log, because the Release keeps only 2,000 characters. Programs that buffer stdout (C, Python) can show output out of order or lose it on timeout. Flush before blocking on input.

Integrity: don't create Releases by hand or replace `result.json`. Collection marks any Release not authored by `github-actions[bot]` as **Unverified**, naming the publisher. Deleting the newest Release makes an older score the latest, and that's visible too.

## Late, closed, locked, unenrolled (student view)

- **Due date passed:** you can still accept, push, and submit. Grading still runs. The teacher sees the submission flagged **late**. Submission time is the graded commit's committer date, so the late flag is advisory. Don't game it; it's visible.
- **Closed** (**Close submission**): no new accepts (web: **Submissions are closed.**; CLI: "is closed to new submissions; ask your teacher to reopen it"). Your repo goes read-only: you can view and clone, but pushes fail with permission errors. Work is preserved. The teacher can **Reopen submission**.
- **Locked:** you can't see or accept it, even if you already accepted. The repo itself is kept. For private in-org templates, you also lose read access to the template. Used to stage timed tests.
- **Read-only window:** the teacher may drop repos to read-only temporarily while grading (**Update student repo access**). Pushes fail until restored.
- **Unenrolled:** removed from the roster and team. You can't accept new assignments, but your repos aren't deleted. **Removed from org:** you lose access to all repos (nothing is deleted).

---

# Student problems

Debug first with `gh student <cmd> -v`. For raw HTTP traffic, set `GH_DEBUG=api`. Check githubstatus.com (API, Actions, Pages) before deeper digging.

## Joining and signing in

- **No invitation email / "Not a member yet" / CLI "you're not a member of this organization":** the teacher hasn't invited you, or the invite went to another address. Ask them to add you to the roster and send the invite.
- **Invitation expired (after 7 days):** you can't accept it anymore. The teacher must **Re-invite**. The CLI says "couldn't find your invitation to this organization; ask your teacher to invite you again".
- **Already in the org from an earlier course but "This assignment isn't available to you":** org membership ≠ enrollment. The teacher must enroll you (**Add to classroom** on the Members page). Re-inviting does nothing.
- **classroom50.org won't load or is flagged unsafe:** some ISPs and school filters block the new domain. At home, add an exception or switch DNS to 1.1.1.1 or 8.8.8.8. At school, ask IT to allowlist it. Report the ISP in an issue.
- **"Couldn't reach the sign-in service":** you're offline, or a filter blocks the sign-in proxy. Use **Other sign-in methods** → a personal access token (no proxy).
- **`redirect_uri is not associated with this application`:** a stale auth, often after switching GitHub accounts. Sign out and back in, or use a private window.
- **SAML SSO orgs:** "Couldn't confirm your membership. If your organization uses single sign-on (SSO)..." Sign in to the identity provider, authorize SSO for the org on GitHub (or open the link from the LMS), then retry.
- **Invitation accept blocked (403) or spam detection (422):** GitHub-side. Ask the teacher.

## Accepting

| Symptom | Cause / fix |
|---|---|
| 404 / "Template not found" / "template ... is not accessible to you" | The private template is outside the org or not shared, you aren't on the roster (so not on the team), or the repo isn't marked as a template. Teacher fix. Also check the slug spelling. |
| "the classroom may not exist yet, or its publish-pages workflow may not have run" / page loads forever / "isn't published yet" | The Pages deploy is pending (at least 20 s, more under Actions load). Wait a minute and reload. Confirm your org invite is accepted. Otherwise the teacher checks the publish workflow. |
| "assignment X is not registered" / **Assignment not found.** | Typo in the slug, or not published. CLI args are `<org> <classroom> <assignment>`. Classroom is the slug, not the title. |
| "Couldn't load the classroom's assignments" (web card listing URLs) | The org's Pages uses a custom domain the classroom doesn't know about, or your network blocks the Pages host. Screenshot the card for the teacher. |
| Unlisted classroom: lookup fails | Pass `--key <key>` from the teacher. |
| "autograder `<name>` not published yet" / "is malformed YAML" | Teacher's custom autograder is missing or broken. Nothing was created; retry after the teacher fixes it. |
| "is locked by your teacher" / "is closed to new submissions" | See the late/closed section. Already accepted? Clone directly instead of re-running accept. |
| "isn't available to you" | Not enrolled. Ask the teacher. |
| "You need admin access to the organization before adding a repository to it." | You do **not** need admin. The org blocks member repo creation, or your invite is still pending, or you're an outside collaborator. Teacher fixes **Member privileges → Repository creation** (Private), then you accept again. |
| "repository name ... is over GitHub's 100-character limit" | Slug plus long username exceeds 100 characters. Only the teacher can fix it (rename the slug). Then accept again. |
| "couldn't copy the template ...: it is a fork of a repository in ... organization" | The upstream org's OAuth app restrictions apply. Teacher must replace the template with a non-fork copy. |
| "uses mode ... which this version of gh-student does not support" | `gh extension upgrade gh-student`, then retry. |
| "published details are incomplete/inconsistent ... re-run `gh teacher assignment add`" | Broken assignment config. Teacher fix. |
| "Assignment already accepted" | Not an error. Your work is untouched. Clone using the printed URL. |
| Pages warning during accept | Non-fatal. The teacher can enable the site later from the submissions page. |
| "could not confirm your team ... has access" (team mode) | Rerun accept if teammates can't push. |
| Web: autograding not running or setup files missing | **Having trouble?** → **Re-run setup**. CLI: rerun `accept`. |

## Submitting and grading

- **"not inside a Git repository"** or **"`.classroom50.yaml` not found in this clone, and ... doesn't start with any published classroom's short name":** wrong directory. `cd` into the clone. Or the classroom site isn't published yet.
- **"... uses an unlisted URL":** rerun with `gh student submit --key <key>`.
- **"has no assignment list under the access key you passed":** wrong key, or the classroom isn't unlisted. Retry without `--key`.
- **"--key does not match the access key recorded in .classroom50.yaml":** drop `--key`. The repo already knows its classroom.
- **"matches more than one published assignment":** a name collision. Ask the teacher which assignment it is.
- **"doesn't match any assignment published for classroom":** a hand-made repo or unpublished assignment. Use plain `git push`, or ask the teacher.
- **"this repository was updated by your teacher (it now carries .classroom50.yaml) ...":** the teacher turned the autograder on after you cloned. `git pull`, then submit. Submitting without pulling would delete those files.
- **Push rejected (non-fast-forward) after a submit:** expected, because submit doesn't update your clone. `git pull`, then push.
- **Push rejected with a permission error:** the assignment is closed or read-only, or (legacy group) you haven't accepted the collaborator invite yet.
- **"Submitted" but no score:**
  1. Check the **Actions** tab. The run takes a minute or two.
  2. Submit-only mode: a plain push shows `classroom50/autograde-skipped` "push not graded". Run `gh student submit` or push a `submit/*` tag.
  3. The push landed on a non-default branch. Only the default branch grades.
  4. The tag didn't match ("tag is not a submission trigger"), including nested `submit/a/b` tags.
  5. The assignment is **Manual** or **Not graded**, or uses no built-in autograder (its own CI, or an empty repo). No Release score is expected.
  6. The teacher's page lags until they run **Collect now**. Your Release is the source of truth.
- **"submission pushed (...) but the submit tag failed ...":** the work is safe on the branch. Rerun `gh student submit`. It reuses or creates the tag without double-grading.
- **Warning "could not determine the assignment's submission mode":** if the assignment is submit-only, rerun `gh student submit` so the tag gets pushed.
- **"git timed out, the network connection appears stalled":** no data moved for about 30 s (10-minute backstop; API calls time out at 60 s). Check the VPN or connection and rerun. Submit is safe to repeat.
- **"git timed out while creating the submission commit":** a commit-signing passphrase prompt is hidden behind the spinner. Run `gh student submit --verbose` to answer it.
- **"could not download the teacher's file ... (it is over 1 MB)":** network trouble fetching teacher files. Retry, or ask the teacher.
- **`Invalid workflow file` / `workflow was not found` after the repo went public:** teacher-side runner access. Report it to the teacher.
- **`pytest: not found` / exit 127 in the log:** the grading environment lacks a tool. Teacher fix. Send them the run link.
- **A file is missing from the graded commit:** it's ignored by `.gitignore` (possibly the teacher's refreshed one) or outside `allowed_files`. Check with `submit -v`.
- **Teammate's work vanished from the latest commit:** someone ran `gh student submit` from a stale clone. Recover from history (`git log`, `git checkout <sha> -- <path>`), commit, pull, and resubmit.

## Groups

- **"you are not in a group for this assignment yet":** student-formed: `accept --new-team`, or ask a founder to `team add` you. Teacher-formed: ask the teacher.
- **"your teacher assigns the groups ... group N was not created by your teacher (you maintain it)":** you made your own team on a teacher-formed assignment. Ask the teacher to place you.
- **`team add` 403:** only the founder can add, or the org syncs teams from an identity provider (ask the teacher).
- **"<user> is already in group N":** they must leave that group on its GitHub team page, or the teacher moves them.
- **"your group is full":** ask the teacher to raise the max size.
- **Over-limit warning on the group page:** remove extra members (added outside Classroom 50) or ask the teacher.
- **Legacy: a teammate can't push:** they must accept the GitHub repo invitation, and must be org members. Only enrolled collaborators are credited.
- **Feedback PR "Merging is blocked":** expected for students.
