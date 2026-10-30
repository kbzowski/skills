Source: Classroom 50 wiki commit 4d79ad48 (2026-10-21); pages Web-Teacher-Guide, Staff-TAs-and-Multiple-Teachers, Course-Lifecycle-and-End-of-Term.

# Teacher web app reference (classroom50.org)

Covers every teacher screen in the web app: org setup, classrooms, staff, assignment form, roster, groups, members, submissions, bulk actions, editing, lifecycle and end of term. See also: concepts.md (data model, roles, tokens, privacy), teacher-cli.md (`gh teacher`), student.md, autograding.md (tests, reports, score trust, exports), troubleshooting.md.

Typical order: GitHub org on Team plan → sign in → one-time org setup + service token → create classroom → add staff → create assignments → add students → share links → collect and grade → close / export / archive.

## Prerequisites

- No Classroom 50 servers. All state is in the GitHub org: a private `classroom50` repo holds config, rosters and scores.
- You need a GitHub account and an org on the **Team** or **Enterprise** plan, because the app depends on GitHub Pages and branch protection/rulesets. Free-plan orgs show **Not supported**.
- Verified educators get Team-tier orgs free via GitHub Education.

## Sign in

- **Sign in with GitHub**: the standard browser OAuth flow.
- **Other sign-in methods** expands three alternatives:
  - **Use a device code instead**: copy the one-time code, open GitHub's verification page, paste the code, authorize. The app detects it within a few seconds. Use this on a machine without a browser, or when the redirect can't come back to the page.
  - **Use a personal access token (classic)**: works across every org you own. **Create a classic token** opens GitHub with the needed scopes preselected. Paste it, then **Sign in with token**.
  - **Use a personal access token (fine-grained)**: enter the **Organization name** first, then **Create a fine-grained token**. It covers ONE org only, so copying a template repo from another org fails. Set **Repository access** to **All repositories**.
- Token sign-ins bypass Classroom 50's sign-in service. Every method stores the token in browser local storage.
- A token's permissions are fixed at creation. An action that needs more (e.g. teardown needs `delete_repo`) means making a new token and signing in again.
- When authorizing, grant access to every org you'll use. If the org restricts third-party OAuth apps, request access and have an owner approve it in the org's OAuth settings. Missing org: see troubleshooting.md.

## Organizations page (**Classroom 50 organizations**)

- A set-up org shows **Open**. A token chip appears when the service token needs attention: **No service token**, **Token expiring soon**, **Token expired**. Score collection needs a valid token.
- Card menu: **Manage token**, **Details**, **Hide from home**.
- Pending org invitations are listed above the orgs, each with **Accept and open**.
- **Set up new organization** opens a dialog listing the orgs you own that aren't set up yet, each with **Set up** (Free plan: **Not supported**).
- GitHub only reports orgs you granted Classroom 50 access to.

## One-time organization setup

There are three steps. The current step is derived from what exists on GitHub, so a reload lands on the same step.

1. **Set up** → **Run setup**. This configures org settings (member privileges, GitHub Actions, a **$0 Actions spending cap**, rulesets), creates the private `classroom50` repo, installs the workflow files, and enables GitHub Pages for it. Each step reports a result. A step that couldn't be applied automatically says what to set by hand.
2. **Next: service token**: add the token (below).
3. **Done**: opens the org.

Each org needs its own setup: plan, setup run, and service token.

### Org **Settings** page (owners only)

- **Service token**: shows expiry, plus **Test token** and **Set a new token**.
- **GitHub Actions**: a switch that pauses autograding for EVERY student repo in the org, plus this month's Actions minutes.
- **Member team creation**: the **Allow members to create teams** toggle (see below).
- **Organization policy**: an audit of what setup configured, with **Fix it** for anything changed outside Classroom 50.
- **Re-run setup**: refreshes workflow files and settings after an upgrade. Needed before newer features work, e.g. **Submission release files**, or a **Test token** that reports the check workflow is missing.
- **Danger zone**: tear down the org.

### Service token

- A fine-grained PAT scoped to the org. The score-collection, regrade and token-check workflows use it to read student repos across the org and to push regrade tags. It is stored as the `CLASSROOM50_SERVICE_TOKEN` secret in the `classroom50` repo. The full permission table is in concepts.md.
- In the **Service token** section, click **Set a token**. The dialog has two steps:
  1. Choose **Token expiry** (default **120 days**), then **Generate new access token**. GitHub's page opens with name, expiry and permissions pre-filled. Set **Repository access** to **All repositories** and generate.
  2. Paste into **Paste token** and click **Save token**. It is validated against the `classroom50` repo before saving.
- Rotate with **Set a new token**. The org-page chip warns as expiry nears.
- What saving can and can't check: on save, the app only verifies what it can prove from `classroom50` plus one other repo. Org **Members: Read**, **Actions**, and visibility of each staff team are checked by a read-only workflow, which **Test token** runs, showing the verdict in place.
  - Pass: all permissions present.
  - Fail: lists the missing permissions, with **View run** for the log. Fix by creating a new token with those permissions and saving it via **Set a new token**.
  - Run it after setting or rotating a token, or when collect/regrade fails with 401/403. It only reads, so it is safe to run any time.
  - If it says the org's workflow files lack the check, click **Re-run setup**, then test again.

### Member team creation

- Student-formed groups work because the founding student creates the group's GitHub team at accept time. Setup therefore turns on the org privilege "Allow members to create teams".
- The **Allow members to create teams** toggle mirrors that GitHub setting.
- While it's off, students can't create teams, and the new-assignment form disables the **Group** type with an explanation. In source, the gate applies only when GitHub reports an explicit false (if the setting can't be read, the type stays enabled) and only on create; on edit the type is locked anyway. The gate disables the whole **Group** type, not only the **Students form groups** option.

## Create a classroom

- Open the org card, or go to `https://classroom50.org/ORG`. On **My classrooms**, click **Create classroom**.
- An org can hold many classrooms (per period, section, term).
- Fields:
  - **Classroom name**: the display name.
  - **Classroom slug**: unique, used in URLs and repo names. Auto-filled from the name, with diacritics transliterated ("Álgebra" → "algebra"). **Max 40 characters**, because it prefixes every student repo name and GitHub caps repo names at 100. **The slug can't be changed later.**
  - **Classroom term** (optional): a label that distinguishes offerings.
  - **Use an unlisted link for this classroom** (optional): publishes the classroom's assignment data at an unguessable URL instead of a slug-based one. It reveals an **Access key** (accept the generated one, type your own, or **Regenerate**). The key becomes part of every published URL for the classroom. Changing it later forces students to re-accept their assignments.
  - WARNING: an unlisted link is obscurity, not access control. The files are still public to anyone with the link.
- Result URL: `https://classroom50.org/ORG/CLASSROOM`. Behind the scenes a subdirectory is added to `classroom50` holding the roster and assignment list.

## Staff, TAs, multiple teachers

### Role matrix

| Role | GitHub reality | Can |
| --- | --- | --- |
| **Teacher** | Org **owner**, on the classroom's teacher team | Everything, including org and classroom settings |
| **Head TA** | Org member, on the head-TA team | Write `classroom50`. Manage the classroom: edit assignments, run collection and regrade. Review and merge feedback PRs. Push to student repos. Not an owner |
| **TA** | Org member, on the TA team | Read `classroom50`. View submissions and scores. Review and merge feedback PRs. Push to student repos. Can't change the classroom |
| **Student** | Org member, on the classroom (student) team | Accept and submit assignments |

- A role is just membership in one of the classroom's GitHub teams; there is no role database. Adding staff therefore produces GitHub team invitations, and the role takes effect only after the person accepts.
- Staff teams are visible to org members, because GitHub requires that for the ruleset exemption that lets staff merge feedback PRs. Students can see who the staff are. The student team is secret.
- **Teacher = org owner of the WHOLE org**, not only the classroom. Grant it only to co-teachers you trust with the org itself; give everyone else Head TA or TA. Under FERPA-style rules, keep the teacher role small.
- Head TA covers a trusted grader who manages the classroom without owner power. Graders who only grade get TA.

### Owner-only things (head TA and TA can't)

- Org setup, org settings, org policy, **Members**, **Activity**, org **Settings**, and classroom **Settings** (including **Staff and roles**).
- Writing scores (manual scores and overrides), because the editor is shown only to owners.
- Roster controls (**Upload roster**, **Add member**, **Share**, **Edit**). Head TAs and TAs get a read-only roster.
- Reading pending invitations (a GitHub limit): a TA's roster can't show invited-but-not-joined people, and the app shows a note instead of an incomplete list.
- Submissions bulk actions that write to every student repo: **Open all feedback PRs**, **Update student repo access**, **Update repository features**, **Change repository visibility**, **Enable GitHub Pages**, **Update autograding triggers**, **Add autograding workflow**, **Pause/Resume autograding**, **Close/Reopen submission**.
- **Collect now** / **Collect all** / **Regrade all**: teachers and head TAs only (they dispatch workflows in `classroom50`, which needs write). TAs see **Refresh** instead, which re-reads the last collected data and live repo status, plus a note on whom to ask for a new collection.
- **Published** org page: all staff.

### What staff see

- TAs and head TAs see the same classroom content as teachers: roster, assignments, submissions, scores.
- The student list for non-owners comes from `roster.csv`. A TA or head TA who isn't on the secret student team can't read its membership, so their roster, submissions and counts use `roster.csv` as of its last sync, and the page says so. Newly enrolled students appear after a teacher opens the roster (that syncs the file). Owners always see live membership.
- Staff access to student repos arrives with collection. The collect workflow grants staff teams write on student repos, including shared group repos, as it runs. A freshly accepted repo has no staff access until the next collection, and meanwhile shows as **Not visible** for staff (the student may or may not have accepted). The teacher sees the repo.
- Feedback PRs: the `feedback` branch is locked by an org ruleset that exempts the staff teams, so staff get a normal **Merge** button and students never do. Gotcha: because the exemption skips the lock entirely, staff can also push to or delete a student's `feedback` branch. The lock protects the frozen base from students, not from staff.
- There is no automatic reviewer assignment; TAs pick repos from the submissions page.

### Adding and removing staff

- Classroom **Settings** → **Staff and roles**: enter a **GitHub username**, pick a **Role**, click **Add**. The section links each role's GitHub team and shows pending invitations.
- Or **Roster** → arrow next to **Upload roster** → **Add member**, with **Role** set to **Teacher**/**Head TA**/**TA**. A staff role needs a username in this dialog, not an email.
- Staff by email (web only): **Upload roster** with an email list or a CSV with an `email` column. Set each row's role in the preview's **Role** column, or include a `role` column (`student`, `ta`, `hta`, `teacher`). Rows marked **Teacher** show a warning before confirm, because the role means org ownership. The address becomes a pending row that is matched when the person accepts.
- CLI: `gh teacher staff add ORG CLASSROOM USER --role ta|hta|teacher` (the default is `teacher`). `gh teacher roster invite` has no `--role` flag; it sends student invites only, so a typo can't hand out ownership. With only an address, invite as a student, then `staff add` once they've joined. They stay enrolled as a student until you unenroll them. See teacher-cli.md.
- Web and CLI manage the same teams.
- Removing staff (web staff list or `gh teacher staff remove`) removes the role but not org membership.

### Dual roles (staff who are also enrolled as students)

- Nothing prevents it; it is the usual way to preview the student side. The GitHub teams are authoritative. The `role` column in `roster.csv` is only a display snapshot.
- Roster shows all of the account's role badges, and the account appears under each role filter.
- In-app access follows the highest role: `teacher > hta > ta > student`. "View as" only changes the local preview and never grants access.
- `roster list` and the `role` column record the single highest role. The web app's auto-sync may rewrite the column right after `roster add`; that is the snapshot updating, not an enrollment change.
- Submissions list any student-enrolled account as a student. A pure-staff account appears only after accepting a repo; its row shows a staff role badge, and it is excluded from **Accepted**/**Submitted** counts unless **Include teaching staff** is on.
- **Manage groups** → **Unassigned students** lists students only. A non-enrolled staff member can still be added via a group's **Manage** dialog (under **Teaching staff**).
- **Unenroll** drops only the student side (roster row and student-team membership). The staff role stays.
- Testing gotcha: an org owner keeps `admin` on their own assignment repo (GitHub won't let an owner reduce their own access), so it doesn't match a student's `write` setup. For a faithful test, use a separate GitHub account enrolled as a student.

### Multi-teacher org patterns

- **One org**: a stable teaching team running one course across terms or sections. Use a classroom per term or section with the same staff.
- **Separate org per teacher**: school-wide adoption with unrelated classes. Each teacher owns their org and its staff.
- **One org per academic year**: a very large course. It keeps hundreds of repos per year grouped and lets old years be archived wholesale.
- The Members page covers the whole org, so other teachers' people appear there too (see Members).

## Create an assignment

On the classroom's **Assignments** page, click **Assignment**. The arrow beside it opens **Reuse assignment**, which copies an assignment from another classroom in the org: name, template, tests, runtime and due date come along; student repos and scores don't.

The form has four sections: **Details**, **Repository setup**, **Submission and grading**, **Schedule and access**. Most assignments need only the first two. While creating, a section changed from its defaults shows **Reset**, which restores that section only. Finish with **Create assignment**.

### Details

- **Assignment name**.
- **Assignment slug**: auto-filled from the name (transliterated, and auto-suffixed to stay unique in the classroom). **Classroom slug + assignment slug ≤ 59 characters combined**, so `CLASSROOM-ASSIGNMENT-USERNAME` fits GitHub's 100-character limit for any username. The form warns as you type when the slug is over budget or collides. **It can't be changed after creation**, except for the one-time over-budget fix described under Editing.
- **Description** (optional).
- **Assignment type** (locked after creation):
  - **Individual**: one repo per student.
  - **Group** (**Recommended**): a shared repo owned by a GitHub team that Classroom 50 manages.
  - **Group (legacy)**: an older shared repo managed through repo collaborators.
  - Both group types have **Max group size** (default **2**).
  - **Group** adds **Group formation**:
    - **Teacher assigns groups**: you create groups and add students on **Manage groups**. Students not in a group can't accept.
    - **Students form groups**: the first student creates the group at accept, then adds teammates up to the max.
  - **Group** is disabled while the org disallows member team creation (see Member team creation).

### Repository setup

- **Start with a template**: **No template** (default) or **Template repository**. Search the org's template repos by name, or paste `OWNER/REPOSITORY` or a full GitHub URL for one the search doesn't list. Template requirements: autograding.md / concepts.md.
- **Add a README** (no-template only, default off). With it off, the result depends on the built-in autograder setting:
  - Autograder off: a truly bare repo with no commit, no autograding and no feedback PR, permanently (not just until the first commit). Use it when students build everything, including their own Actions.
  - Autograder on: an initialized repo with only the control files (no README, no starter content) that grades normally.
- **Include all branches** (templated): copies every template branch, not only the default branch.
- **Feedback pull request** (default on): opens one PR per student for review and inline feedback. Unavailable for a bare repo, which has no starter commit to diff against.
- **Advanced settings** (collapsed):
  - **Copy About from template** and **Copy topics from template** (templated, both default on). GitHub's template generation doesn't copy these.
  - **Use the template's pull request template as the Feedback PR body** (templated, feedback PR on). The app looks for `.github/pull_request_template.md`, `pull_request_template.md` or `docs/pull_request_template.md`. It is auto-checked when such a file is found, and you can still toggle it. If the file is missing or unreadable, the built-in body is used. You own the content.
  - **Repository visibility**: **Private** (default) or **Public** (peer review, portfolio, showcase). It is applied at accept time.
    - Students are warned before accepting a public assignment, since code, commits and name become visible to anyone.
    - If the org doesn't allow students to create public repos, accept creates a private repo and tells the student.
    - It affects future accepts only. For existing repos use **Change repository visibility**.
    - GOTCHA: public repos are NOT autograded. GitHub blocks them from running the grading workflow in your private `classroom50` repo, so every run fails with "workflow was not found". Keep repos private while grading, or pair **Public** with **Do not use the built-in autograder**.
  - **GitHub Pages**: configured at accept, so students never need admin. Options:
    - **Off** (default).
    - **GitHub Actions**: deploys via a workflow in the student repo (for sites with a build step). The workflow must grant `pages: write` and `id-token: write` and use `actions/upload-pages-artifact` and `actions/deploy-pages`. Ship it in the template or have students add it. The site is created at accept, so the workflow's first run deploys it.
    - **A branch**: serves branch files directly with no workflow (plain HTML/CSS/JS). Pick the branch (blank = default branch) and folder (`/` or `/docs`).
    - The site is PUBLIC even when the repo is private, and every file in the published branch/folder is served. Only GitHub Enterprise Cloud can restrict who sees a site. Tell students what belongs in the folder.
    - Pages on private repos needs a plan that includes it. On GitHub Free for organizations, pair it with **Public** visibility or the site isn't created (accept tells the student, the assignment still works, and public repos aren't autograded).
    - Not available for an empty repo. Affects future accepts only; for existing repos use **Enable GitHub Pages**. The site URL is `https://<org>.github.io/<repo>/`, and an org with a custom Pages domain serves it there too.
  - **Student repository access**: the student's role on their own repo. Default **Write (push)** for individual assignments, **Admin** for group assignments (so the group owner can add teammates).
  - **Repository features**: per-feature settings for **Issues**, **Wiki**, **Projects**, **Pull requests**. **Inherit from template** (default) re-applies the template's current setting at accept, since generation doesn't copy them; or force **On**/**Off**. Template-less assignments show **GitHub default**. For existing repos use **Update repository features**.

Rule for all repository settings: they are editable after creation but apply only to repos accepted from then on. Existing repos keep their original starter code and setup. When at least one student has accepted, the edit form asks you to confirm and warns that you must update existing repos yourself. The per-setting retrofit actions are **Change repository visibility**, **Enable GitHub Pages**, **Update repository features**, **Update autograding triggers** and **Add autograding workflow** (after turning the built-in autograder on; CLI `gh teacher assignment enable-autograder`; adds the workflow plus the `.classroom50.yaml` marker). **Assignment type** can never change.

### Submission and grading

- **Submission type**:
  - **Every push to the default branch** (default): grades each push. The count includes each student commit on the branch, excluding the tool's own accept and autograding-update commits. A push of several commits is graded once but counted several times.
  - **A tagged commit**: grades and counts only when a student runs `gh student submit` or pushes a `submit/*` tag. Regular pushes cost no Actions minutes, which matters at scale.
  - **Submission tags** (optional, under **A tagged commit**): extra tag names, one per line (e.g. `phase1`, `phase2`, `complete`). A student runs `git tag phase1 && git push origin phase1`, that commit grades, and the result is a normal `submit/*` release titled with the suffix `(via phase1)`. Prefer exact names: `v*` grades every matching tag. Changing the tags later needs the same trigger update as changing the submission type.
  - The trigger is baked into each repo's workflow at accept. See "Changing the submission type later".
- **Grading**: **Not graded** (default), **Manual (enter scores by hand)** (adds **Max points**, default **100**, with scores entered on the submissions page), or **Autograded**. Changeable after creation, but scores recorded under the old mode may read differently.
- **Built-in autograder** (under **Autograded**): **Use the built-in autograder** (preselected) or **Do not use the built-in autograder**.
  - Opting out means accept installs no autograding workflow. A templated assignment runs the template's own CI instead. A README repo has no autograder at all.
  - The submissions page still shows who submitted (collection records submitters, with no scores), and repo actions remain.
  - The choice sticks when you toggle away from Autograded and back.
  - Changeable after creation, for future accepts only. Turning it OFF later makes already-accepted repos' autograde runs fail and drop out of collected scores. Turning it ON later requires **Add autograding workflow** for existing repos.

### Autograding tests (built-in autograder on)

Details are in autograding.md. Form specifics:

- The list is collapsed; click its heading to expand. **Add test** adds one, and saving a test expands the list.
- Per test: **Test name** (shown to students), **Test type** (**Input/Output**, **Run command**, **Python (pytest)**), **Setup command** (optional), **Run command** (runs in the student checkout; uploaded files are under `$CLASSROOM50_BUNDLE_DIR`), **Timeout (seconds)** (0 = 10-second default), **Points**, **Report options**.
- **Report options** per test: **Failure details shown to students** (**Full: diff or expected and actual output** / **Student output only (never the expected output)** / **Failure type only (no output)**), **Output when passing** (**Include output** / **Discard output**), **Command lines** (**Show commands** / **Hide commands**). Each starts from the assignment's report defaults and overrides them for that test only.
- **Input/Output**: **Input (stdin)**, **Expected output**, **Comparison** = **Included** (substring) / **Exact** (equal, ignoring surrounding whitespace) / **Regex** (Python `re.search`, multiline).
- **Run command**: **Required exit code** (empty = 0).
- **Python (pytest)**: runs pytest on test files in the template. Points split across discovered test cases. No extra fields.
- **Report defaults** panel: **Default failure details**, **Include passing test output**, **Show command lines**.
- **Upload test files**: hidden tests and fixtures go in the assignment's folder in `classroom50`, reachable as `$CLASSROOM50_BUNDLE_DIR`. On a saved assignment, **Open upload page** opens GitHub's upload page for that folder (no clone needed). Students can't change these files but CAN read them (they're on the org's public Pages site), so keep full solutions out.

### Advanced settings (autograding environment)

Blank fields use defaults.

- **Runtime environment**: **GitHub-hosted runner** (default) or **Docker container** (a public image provides OS and packages).
- **GitHub runner**: runner label, blank = `ubuntu-latest`. Comma-separated labels select a self-hosted runner, and the form validates them against the org's runners as you type.
- **Docker image** and **Container user** (container only), e.g. `gcc:13`. Set the user to `root` if checkout fails with a permission error. The runner must be an Ubuntu variant or Actions errors.
- **Language versions**: Python, Node, Java, Go, Rust. Blank skips. Python defaults to **3.14** on the hosted runner. Ignored on self-hosted runners.
- **Extra apt packages** (hosted only): comma- or space-separated, installed with `--no-install-recommends`. **Install recommended packages too** handles packages that need their recommends (e.g. pandoc with texlive).
- **Setup command** and **Setup timeout (seconds)**: run once before the tests (compile, install deps). A non-zero exit or timeout marks the autograde run failed without changing the score, and later tests still run. A new setup command defaults to **120 s**. 0 = the runner's 10-second default; otherwise a whole number 1–600.
- **Allowed files**: a `.gitignore`-style list of files kept for setup and grading. Include dependency manifests and project files that setup uses.
- **Submission release files**: exact workspace-relative paths, one per line, attached to each submission's Release after grading. No globs. Basenames must be unique and Release-safe. Missing or unsafe files are skipped with a warning. Existing orgs must **Re-run setup** first.
- **Set a passing threshold** (default off): a percentage of max score. Display only (a **Passing** filter and badges); it doesn't change scores.
- Each command runs in a separate shell process.

### Schedule and access

- **Set a release date** (optional): assignments are hidden from the student list by default, so students accept only via the invite link. A release date lists the assignment for everyone after it passes. Listing only, not access: invite-link holders can accept early, and students who accepted always see it. For a private template in the org, the classroom team can read the template as soon as you save; with a future release date and no lock, the form says so and offers a one-click lock.
- **Set a due date** (optional): a date and time in YOUR local timezone. It marks later submissions **Late** in collected scores. It does NOT block pushes or revoke access, and autograding keeps scoring late work. Enforce with **Close submission**.
- **Lock assignment**: students can't see or accept it, including those who already accepted. For a private template in the org, the classroom (student) team loses read on the template until unlock. Nothing auto-unlocks at the release date; you unlock manually. Saving other settings on a locked assignment keeps it locked.

## Roster (add students)

Students must be on the roster before accepting. Adding one sends a GitHub org invitation, which they must accept. Open classroom → **Roster** in the sidebar.

Toolbar (centered on an empty roster). All controls are owner-only; head TAs and TAs see a read-only roster:

- **Upload roster** (primary): add from a file.
- Arrow next to it → **Add member**: add one at a time.
- **Share**: the invite/sign-in links.
- **Edit** (owners): batch editing.

### Add member

- **Role** (**Student** preselected; also **Teacher**, **Head TA**, **TA**), **GitHub username**, and optional **First name**, **Last name**, **Email**, **Section**. Click **Add member**.
- If a row for the account already exists with only `github_id` or only username (e.g. after a hand-edit of `roster.csv`), the add completes that row instead of duplicating it, and the confirmation names it. Typed fields replace stored ones; blank fields keep them.
- No username yet: enter **Email** only. This creates a pending row that is matched at accept (see Email invitations).

### Upload roster

- Drop or choose a `.csv` or `.txt`. **Read the file as** shows the detected shape:
  - **Roster CSV** (default; the format best understood): a header row plus one row per student. A header-less plain list mixing usernames and emails also works under this option, read line by line.
  - **GitHub usernames (one per line)**: forces every line to be a username, even ones that look like emails.
  - **Email addresses (one per line)**: forces every line to be an email.
  - The two list options are overrides: a non-fitting line is reported, not reinterpreted.
- **Download template**: a five-row example CSV (username only, email only, both).
- Validation runs before anything changes:
  - Any unusable value (invalid address, `github_id` matching no account, a line that is neither username nor email) blocks the WHOLE import. The dialog lists line numbers and imports nothing. Fix and re-upload; re-upload is safe because existing students are left alone.
  - Each identity column is checked independently, so shifted columns are caught.
  - A name with no identifying column is kept as an **Unlinked** row to link or remove later.
  - Only rows with nothing usable at all are skipped.
- Re-uploading is the bulk invitation-recovery tool. Per-email-row preview markers:
  - **Resend invitation (expired)** / **Resend invitation (not delivered)**: a fresh invite is sent. GitHub's failed record is cleared only after the new one is confirmed.
  - **Invitation already pending**: nothing is re-sent. An all-pending upload imports nothing and says so.
  - An address matching a student who already has a GitHub account is linked to that account by default (GitHub skips email invites to existing members). Clear **Link these addresses to the matched GitHub accounts** to opt out; the row then gets an email invite and stays **Unlinked** until linked by hand.
- **Import** greyed out: hover for a tooltip naming the unmet check (nothing to process, a change awaiting confirmation, etc.).
- **Invitation rate cap (GitHub)**: **50 per day** for orgs under a month old or on the free plan, otherwise **500 per day**. When hit, the batch stops, unreached rows are reported, and any invitation cancelled for re-send is restored. Upload the same file again the next day.

### Roster CSV columns

- At least one identifier per row: `github_id`, `username` or `email`. Precedence when several are present: `github_id` > `username` > `email`.
- Headers are case-insensitive, and unknown columns are ignored, so SIS/gradebook exports usually work as-is.
- Save as UTF-8 (Excel **CSV UTF-8**). A non-UTF-8 file is read as Windows-1252 (Excel plain "CSV") with a notice; check accented names.

| Column | Identifier? | Meaning |
| --- | --- | --- |
| `github_id` | 1st choice | Immutable numeric id (as Classroom 50's own `roster.csv` writes it). Resolves the current username, so renamed accounts are found |
| `username` | if no `github_id` | GitHub login |
| `email` | if neither | Email invitation; also stored as the contact email on every row |
| `first_name`, `last_name` | no | Display and exports |
| `name` | no | Full name, split into first/last; use instead of the pair |
| `section` | no | Filterable label |
| `role` | no | `student` (default), `ta`, `hta`, `teacher`; blank for students |

- If `github_id` and `username` disagree, the id wins. The preview shows both and asks for confirmation, and the stored username is corrected. An id matching no account stops the import, with no fallback to the username, which could belong to someone else.
- Examples: a lone `username` column is valid. Mixed rows also work: `583231,octocat,...` (found by id even after rename), `,hubot,,...` (by username), `,,octofez@example.edu,...` (email invite, pending until accept).

### Email invitations

- A row with an account (`github_id`/`username`) is invited and rostered. An email-only row is invited by email and recorded as a pending roster row.
- It is matched to the GitHub account at accept. The recorded address is the one you invited, not necessarily the one on their GitHub account.
- Name and section are kept and are editable while pending. The address itself can't be edited because it identifies the invitation; to change it, cancel and invite the new address.
- Cancelling the invitation removes the row. An expired invitation (GitHub invites last **7 days**) keeps the row with an **Invitation expired** badge for **Re-invite**, link, or remove; the next roster refresh only retires the invitation bookkeeping.
- This is why `roster.csv` can hold rows with no `username`/`github_id`. **Upload roster** re-matches those rows by email. `gh teacher roster import` corrects a pending row's name and section by address without touching the invitation, but skips `github_id`-only rows (import resolves by username) with a notice.
- Each pending email invitation holds the address in a `secret` invite team until the student joins. Clear these with **Clean up invite data** (classroom Settings) before archiving.

### Existing org members

- Re-inviting an existing member does nothing: GitHub says "Already a member", and they are NOT added to this roster.
- Enroll them via org **Members** → select rows → **Actions** → **Add to classroom**.

### Share links (**Share** → **Share classroom links**)

- **Classroom onboarding link**: accept the invite and sign in to Classroom 50 in one step. This is the usual one to share.
- **GitHub organization invitation link**: accept on github.com directly, a fallback when the onboarding link fails.
- Neither link enrolls anyone. Invite from the roster first, then share.

### Roster table

- Columns **Member**, **Username**, **Role**, **Section** (only when some member has a section), **Status**. Click headers to sort and a row for detail.
- **Status** badges:
  - **Enrolled**: in the org and on the classroom team.
  - **Invitation pending**: email invite not yet accepted.
  - **Not enrolled**: in the org but missing from the classroom team, so collection will MISS them.
  - **Not in organization**: on the roster but not an org member (left or removed).
  - **Unlinked**: no GitHub account (name-only upload, an address that couldn't be invited, or an invite no longer live).
  - Extra badges: **Invitation expired** (after 7 days) or **Invitation failed** (undeliverable).
- Clicking an unlinked or expired row explains the case and offers **Re-invite**, **Link account** (attach to an org member) and **Remove row**. Link and Remove each open their own panel.
- Toolbar: **Search** (name, username, email). **Show** filters status (**Enrolled**, **Invitation pending**, **Not enrolled**, **Not in organization**, **Unlinked**, **Invitation expired**, each shown only while such rows exist) and role (**Student**, **Teacher**, **Head TA**, **TA**). A section filter appears when sections exist. **Group by** role or section.
- Selection bar → **Actions**. Each action shows the count it applies to and skips the rest, so mixed selections are safe:
  - **Send invitations (N)**: a pending invite is cancelled and re-sent, an expired one replaced, and a non-member invited. Rows with neither email nor username can't be invited.
  - **Cancel invitations (N)**.
  - **Unenroll (N)**: removes from the classroom.
  - **Remove rows (N)** (when unlinked rows are selected): deletes them from `roster.csv`.
  - Each action confirms first, then reports, with a next step for every skipped row. Bulk actions apply to students only; manage staff in classroom **Settings**.
- **Edit** (owners): names and sections become inputs, and unlinked rows get a username picker built from your classrooms' history. **Save changes** applies everything in one commit. A row that changed underneath you (e.g. an invite was accepted meanwhile) is skipped and reported, not overwritten.
- **Refresh roster**: re-checks the classroom's GitHub teams and invitations (joins, leaves, accepts, role changes) and updates the roster. It also runs automatically on page open. It runs in the background (the page stays usable): the button reads **Refreshing roster…**, and a **Syncing with GitHub…** tag appears if it's slow. The browser warns on tab close mid-sync, but closing loses nothing; the sync reruns on next open. A caption shows when the roster last changed and what the last refresh found. A teacher opening the roster is also what updates `roster.csv` for TAs.

## Manage groups

Open: assignment → **Manage groups** (sidebar), or the **Manage groups** button on the submissions page.

- The list shows the display name, members (full names from the roster), count vs max size, repo status and visibility.
- Badges:
  - **No repository yet**: the shared repo is created when a member accepts (then **Repository created**).
  - **Members changed since the last refresh**: live GitHub membership differs from the record. Refresh.
  - **Over the limit**: more members than the max. The app refuses to add past the limit, but a group's team maintainer can add members directly on GitHub. Use **Manage** to remove members, or grade the group as it is.
- **Create group**: optional **Group name** (blank = numbered name). On teacher-formed assignments, create every group and add students here; ungrouped students can't accept.
- **Copy groups**: recreate another assignment's groups. Pick **Source assignment**; names and members go into an editable plan, and nothing is created until you save. Groups stay per-assignment: the copies are new teams under this assignment's numbering. CLI: `gh teacher team copy`.
- **Refresh group info**: re-reads live membership and updates the `teams.json` snapshot in `classroom50`. It also runs automatically on load when live membership has drifted.
- **Unassigned students**: roster students not in a group. Pick a group with room and add them. Staff without a student enrollment are omitted, and a note gives how many were left out. To let staff test, add them via a group's **Manage** dialog, where the picker lists them under **Teaching staff** and they get a role badge. Viewed by a head TA or TA who can't read the student team, the panel works from `roster.csv` (one role per person) and lists EVERY unassigned roster member rather than guess who is staff.

### Manage one group (**Manage**)

- **Group name** → **Save name**. Changes the display name only; the repo name doesn't change.
- **Visibility**: **Visible** (classmates can browse it and send join requests on GitHub) or **Hidden** (visible only to members and org owners).
- **Members**: stage changes (**Will be added** / **Will be removed**), then **Save changes**.
- **Danger zone** → **Delete group**: deletes the group's GitHub team and the access it granted, after confirmation. The repo is NOT deleted.

### Recover a deleted group team

- If the team was deleted but the repo exists, grading can't credit members. The submissions row shows **Group team missing**; click it to recreate the team at the same group number.
- Members found in the repo's commit history are pre-checked. You can add more from the roster and optionally choose a **Team maintainer** (e.g. the founding student) who can manage members on GitHub.

## Organization Members page (owners)

Org → **Members** in the sidebar. It lists everyone in the GitHub org and their classrooms.

- WARNING: this is the whole org, including other teachers' people (even ones not using Classroom 50). Take care removing anyone.
- Columns: **Name**, **Username**, **Classrooms**, **Roles** (org role **Owner**/**Member**), **Status** (problems only):
  - **Not in organization**: on a roster but not in the org. The row's **Invite** restores access.
  - **Invitation pending**.
  - **Unlinked**: a roster row with no account and no live invite.
  - **Not enrolled**: on a roster but missing from the classroom team, so collection misses them.
  - Plus **Invitation expired** / **Invitation failed**.
- The detail panel explains what happened and links to the person's row on each classroom roster, where **Re-invite**, **Link account** and **Remove row** live. The Members page itself doesn't act on pending or unlinked rows, because an invitation belongs to a classroom.
- The detail shows name, username, GitHub ID, every roster email, and classroom access with links. Actions there: invite an on-roster non-member back (attaching their classroom teams; an existing pending or active state is reported rather than re-sent), or remove from the org.
- If the org's invitation list can't be read, the page says so: pending and expired invites are hidden, and rows may wrongly read as unlinked or not in the org. Retry before inviting anyone.
- **N failed invitations aren't on any roster**: GitHub still holds expired or undeliverable invites that match no row or member (usually the row was removed after expiry). They can't be re-invited from here. **View details**, then **Dismiss** or **Dismiss all** clears them from GitHub's failed list; leave any you sent for other purposes.
- Filters: **Search** (name, username, email). **Show** filters status (**Not in organization**, **Invitation pending**, **Unlinked**, **Invitation expired**, **Not enrolled**) and role (**Owners**, **Members**). A classroom filter offers one classroom or **No classroom**.
- Bulk **Actions** (count-aware, inapplicable rows skipped):
  - **Send invitations (N)**: for on-roster non-members, attaching classroom teams. Email-pending rows and unlinked rows are skipped with a pointer to the classroom **Roster** page.
  - **Add to classroom**: enroll members in a chosen classroom. Skips members already there and non-members.
  - **Remove from classroom**: unenroll from a chosen classroom. A checkbox also removes them from the org in the same run.
  - **Remove from organization**: unenrolls each person from every classroom first (so no roster points at a non-member), then removes them.
  - Each dialog previews counts and skip reasons. Removals require typing `confirm` and warn when the selection includes org owners or people enrolled in other classrooms.
- Neither unenroll nor remove deletes repos. Enroll, unenroll and org removal are separate operations (concepts.md).

## Collect submissions

### Invite link

- On the submissions page, **Share** opens **How students accept** → **Copy accept link** (or expand **Prefer the command line?** for `gh student accept`).
- Or use the link icon in the assignment's row on **Assignments**, which copies directly, including the access key for unlisted classrooms.
- Accepting creates `CLASSROOM-ASSIGNMENT-USERNAME`. Each graded submission produces a Release containing `result.json`. The on-demand score-collection workflow aggregates those into `scores.json`.

### Submissions page

- Freshness strip: **Collect now** (also in **Actions**) is scoped to this assignment only: it walks just this assignment's repos, so it is fast and doesn't rebuild other assignments. The strip shows the per-assignment `collected_at` stamp from `scores.json`, plus an **Out of date** badge when students have pushed since. Collect to grade and score the newest work.
- **View workflow** / **View run** (Actions menu): the Actions run.
- Who can collect: teachers and head TAs. TAs get **Refresh** (re-reads only).
- Header: a submission progress bar (students or groups submitted; click to filter to non-submitters), due date, **Late** count, **Closed** badge, submission type (**Submits on every push** / **Submits by tag**), grading (**Autograded** / **No built-in autograder** / **No autograding**).
- Toolbar:
  - **Search** by student, or by group or member on group assignments.
  - Section filter.
  - Status: **Submitted**, **On time**, **Late**, **Not submitted**, **Accepted**, **Not accepted**.
  - **Passing**/**Failing** (only when a threshold is set).
  - Sort: **Newest first**, **Oldest first**, **By first name**, **By last name**.
- Rows show the latest submission plus full history (newest first): score, date, links to repo, commit, feedback PR (**View feedback PR**; **Review** in the row's manage dialog), and Release (**View autograder details**).
  - **Pending**: pushed after the last collection. Collect to resolve.
  - Group history names the committing member.
- Group assignments: rows titled by group name. The **Members** column shows the live count (click to open the manage dialog), with **Over the limit**, **No repository yet** and **Group team missing** (click to recreate).
- Staff rows show a role badge instead of a student's, so test runs aren't mistaken for student work.
- Reading results in depth (per-test breakdowns, attempts, grading a specific commit): autograding.md.

### Collect the whole classroom (**Collect all**)

- On the classroom's assignments list, a freshness line shows **Collect all**, with **Out of date** when ANY assignment has pushes newer than its own stamp. Each assignment is judged separately, so one fresh assignment can't mask a stale sibling.
- It dispatches a single `collect-scores.yaml` run scoped to the classroom, rebuilding all its scores. Counts refresh when it finishes. It is slower and uses more Actions minutes, so it asks for confirmation. While grading one assignment, prefer **Collect now**.
- Teachers and head TAs only. Hidden on an archived classroom and when there are no assignments; disabled while the roster is empty.
- While running, a top banner reads **Collecting scores for every assignment in** the classroom, keeps tracking across navigation, and links **View run**.
- The table's **Submitted** count = what the last collection found: graded submissions plus repos with pushes or submission tags not yet graded (shown as **Pending** on the submissions page). A student whose autograder run failed or never ran still counts as submitted; the score arrives once a result is published and the assignment is collected again.
- **Accepted**/**Submitted** count enrolled students only; staff test repos are excluded. **Include teaching staff** (next to **Collect all**) counts them. It is a per-browser preference applying to every classroom, and while on, the classroom header shows how many staff are counted. Before any student is enrolled the columns read **No students yet**, and the tooltip says how many staff repos the toggle would count.

### Scores and overrides (owners only)

- The pencil on a score cell opens the score dialog.
  - **Manual** grading: enter a score out of **Max points**.
  - **Autograded**: enter an override. The autograded score is kept and shown, and **Clear override** restores it. If the submission isn't autograded yet, the dialog also asks for the max points.
- An override shows a **Manual** badge, and autograding won't change it until cleared.
- It writes `scores.json` in `classroom50`, and the editor is shown only to org owners. Head TAs can't edit scores even though they can write `classroom50` (confirmed in source: gated on `isOwner`).

### Submissions **Actions** menu (in menu order)

Teachers and head TAs see the collection and lifecycle actions. Actions writing to every student repo are owner-only, and most of those apply to individual assignments only.

- **Metrics**: **Submitted**, **Classroom average**, **Passing**, **Accepted**. Shown only for empty-repository assignments; others show live status in the table.
- **Open all feedback PRs** (owners): opens a feedback PR on every repo lacking one, from the browser, one repo at a time.
- **Collect now**: collection for this assignment.
- **Regrade all**: re-runs the autograder on every submitted repo's LATEST commit. Submission times don't change.
- **View workflow** / **View run**.
- **Update student repo access** (owners): bulk-set the student role (e.g. read-only while grading, then restore write).
- **Update repository features** (owners): re-apply the Issues, Wiki, Projects and Pull requests settings to existing repos.
- **Change repository visibility** (owners): flip all accepted repos public or private. Later accepts follow the assignment's **Repository visibility**. Public repos get a **Public** badge, and one repo can be flipped from its row's manage dialog. Autograding stops while public; to resume, make it private again AND set the assignment's **Repository visibility** back to **Private** so later accepts grade.
- **Enable GitHub Pages** (owners): applies the Pages setting to all accepted repos (those accepted before Pages was on, or whose site failed at accept). Repos that already have a site are left alone. Refusals (e.g. a private repo on a plan without private Pages) are listed with remedies. A row with a site shows **Open GitHub Pages site**, and its manage dialog shows the live URL (plus the default `github.io` URL under a custom domain), build status and a per-repo **Enable GitHub Pages**.
- **Update autograding triggers** (owners): retrofit after a submission-type or tag change (below).
- **Add autograding workflow** (owners): adds `autograde.yaml` to repos lacking it, after the built-in autograder was turned on for an assignment accepted with it off.
  - Existing workflows are untouched, and the commit doesn't trigger grading.
  - Students must pull before their next push.
  - GOTCHA: GitHub only runs a workflow for commits that contain it, so **Regrade all** can't grade earlier work. The student's next push does. To grade now, have each student push once (an empty commit works).
  - Also per row. CLI: `gh teacher assignment enable-autograder`.
- **Pause autograding** / **Resume autograding** (owners): disable or re-enable the built-in `autograde.yaml` in every student repo via GitHub's workflow-disable API. No file changes, and other workflows keep running. Individual assignments using the built-in autograder, after students have accepted; also per row. The org-wide pause is on org Settings.
- **Close submission** / **Reopen submission** (owners): blocks new accepts and sets every student repo read-only (work preserved, students keep read). This is THE due-date enforcement. Reopen restores write.
- **Lock assignment** / **Unlock assignment**: hide and block accept; for a private template, remove the student team's read (restored on unlock). Same toggle as the form.
- **Download scores (CSV)**: all submissions (columns: autograding.md).
- **Download groups (CSV)**: group/team assignments (below).
- **Download all submissions**: each repo's latest submission in one zip, built in the browser one repo at a time. For very large classrooms use `gh teacher download` (clones every repo and writes `scores.csv`). The **Clone all submissions with the CLI** button next to **Actions**, and the download icon on the **Assignments** row, open a dialog with the command pre-filled.
- **Delete assignment**: type the slug to confirm. Student repos are kept, and you land on the assignments list.

### Download groups (CSV)

- One row per group member, joined to the roster. It lines up with LMS group rosters without renaming columns.
- Columns:
  - `group`: `group-<n>` for team assignments, the founder's username for legacy. **Download scores (CSV)** has the same `group` column, so the files join.
  - `group_name`, `team_slug`, `repo`: team assignments only. `repo` is blank before the repo exists. Unnamed teams export as `Group <n>` in English regardless of UI language, matching the CLI.
  - `username`, `first_name`, `last_name`, `email`, `section`, `github_id`, `role`: from `roster.csv`, matched by GitHub id first, then username, so renamed accounts keep their row.
  - `in_roster`: `no` for a collaborator or team member the roster doesn't know (their `username` is the lowercased login). A roster row with the wrong cell count (two or more short, or surplus cells) also counts as unknown, in both web and CLI.
  - `note`: set when membership couldn't be read, so it is never mistaken for an empty group.
- It reads LIVE membership, not the collected snapshot, so unsubmitted groups are included.
- The menu item stays disabled until the roster and all memberships load, and also when the roster or group list failed to load (reload rather than get a file marking everyone unrostered). If only one group fails, the download works, with a single row for that group noting `membership could not be read`.
- CLI equivalent: `gh teacher group list --csv`.

## Editing assignments and classrooms

### From the Assignments list

- Each row has four quick actions: copy invite link, clone submissions, edit, lock. Plus **Manage assignment**, a dialog with those four, **Template access** (review which teams can read the template; re-grant the classroom teams' read), **Reuse in another classroom**, and **Delete assignment**.
- **Slug too long** badge: see the over-budget slug fix below.

### Edit an assignment

- Assignment → **Settings** (page titled **Assignment settings**; the row's pencil goes there too). It is the creation form, pre-filled.
- Provisioning settings (repo source, built-in autograder, grading mode) are editable but affect future accepts only, with a confirm prompt once anyone has accepted.
- **Assignment type** and **Assignment slug** are locked. **Discard changes** reverts unsaved edits.

### Edit a classroom

- Classroom → **Settings**: the creation form, pre-filled. The slug is fixed.
- **Advanced settings** → **Custom Pages domain**.
- **Clean up invite data**: clears addresses held for email invitations never accepted. It writes anything recoverable onto the roster and deletes all remaining invite teams.
- **Archive** / **Unarchive**.
- Delete: type `ORG/CLASSROOM` to confirm.

### Archive a classroom

- It drops out of the default **My classrooms** list (the filter **Archived** or **All** shows it). New assignments, accepts and enrollments stop. Roster and assignments stay read-only. **Unarchive** restores it.
- Student repos are untouched.
- CLI: `gh teacher classroom archive ORG CLASSROOM` / `unarchive`.

### Custom Pages domain

- Student browsers read classroom data (the assignment list that invite links resolve against) from GitHub Pages at `https://ORG.github.io/classroom50/`. If the org's Pages site has a custom domain, GitHub answers `github.io` with a redirect that browsers reject, so invite links stop loading assignment data.
- Fix: classroom **Settings** → **Advanced settings** → **Custom Pages domain**. Enter a bare domain (`pages.example.edu` is read as `https://pages.example.edu/classroom50`), or a full `https://` URL if the site isn't under `/classroom50`. Empty = default `github.io`.
- Browsers try the custom domain first and fall back to `github.io`, so a typo can't lock students out of a working site.
- IMPORTANT: upgrade `gh teacher` everywhere to **1.35.0+** first. Older CLIs don't know the field and can strip it from student discovery on their next sync.

### Act on several assignments at once

- Select rows on **Assignments** (checkboxes, header select-all, Shift-click for ranges). The toolbar shows the count, **Actions** and **Clear selection**. The header checkbox selects what current search and filters show. Selection SURVIVES search and filtering: hidden rows stay selected and are acted on, so the count is always what the action covers.
- **Lock** / **Unlock**: per-assignment lock semantics. A template read that another unlocked assignment in the classroom still uses is kept. Entries with nothing to do are disabled (e.g. a fully locked selection shows only **Unlock**).
- **Reuse**: copy into another classroom or the same one.
- **Delete**: type `delete`. It has no undo in the app. Student repos are kept.
- Each action is one commit (lock, unlock and delete to this classroom's `assignments.json`, reuse to the target's). Lock, unlock and delete are all-or-nothing. Assignments deleted meanwhile (another tab) are skipped and reported. If the template-access change after lock or unlock fails for some, a warning names them; rerun for those.
- Multi-reuse: pick the target classroom, and each copy gets a slug field pre-filled, with a numbered suffix on collision (`hw1` → `hw1-2`), editable. A slug blocks the copy if it is used or reserved (by a renamed assignment) in the target, exceeds the repo-name budget, or duplicates another copy's slug in the run. Copies land in one commit to the target. A copy whose template is no longer visible, or whose slug was taken meanwhile, is left out and reported while the others land. For private templates, the target's student team gets read.

### Fix an over-budget slug (**Slug too long** badge)

- Applies only to assignments created before the limit was enforced (e.g. imports from GitHub Classroom with long names).
- Steps: **Settings** → **Slug update needed** card → **Update slug** → **New slug** (keep the suggestion or type one; a hint shows the room left) → **Update**. One config change renames the assignment, then every existing student repo is renamed, with per-repo progress.
- GitHub redirects old repo names, so clones keep working, and collected scores follow the new slug.
- ONE-TIME only: the old slug stays permanently reserved so redirects survive.
- The assignment stays locked during renames. On any failure the card shows **Slug update incomplete**, and **Finish update** reruns until done.
- Students run `git pull` once before their next submit. CLI: `gh teacher assignment rename`.

### Changing the submission type later

1. Change **Submission type** (or the submission tags) on **Settings** and save. This affects new accepts only, because the trigger is baked in at accept.
2. Submissions **Actions** → **Update autograding triggers**. It rewrites each repo's workflow. The commit is marked, so it neither grades nor counts as a submission. Hand-edited workflows are reported and left untouched, and unaccepted students are skipped. Also per row in the manage dialog.
3. Tell students to `git pull`; clones from before the update conflict on their next push.

Owners only, individual assignments using the built-in autograder only (a custom autograder's workflow is yours to edit). It needs the `workflow` scope in your GitHub authorization; if it reports a permissions problem, sign out and back in.

## Other organization pages (sidebar)

- **Published** (all staff): every file served from the org's Pages site (classroom list, each classroom's assignment list, autograder files, workflow files) with public URL and status. These files are PUBLIC; everything else in `classroom50` stays private.
- **Members** (owners): see above.
- **Activity** (owners): a timeline of config changes, workflow runs and this session's errors, newest first. It has source and type filters, search, **Export CSV**, and **Show diagnostics** (copies technical details for bug reports).
- **Settings** (owners): see org setup.

## Course lifecycle

### Staging and timed assessments

- Default: hidden from the student list, accept only via invite link. **Release date** = listing only. **Lock** = full block (see Schedule and access). CLI: `gh teacher assignment add --locked`, `gh teacher assignment lock` / `--unlock`.
- Timed assessment (in-class test or exam):
  - Prerequisite: the template is **private** and in the classroom's org. Locking with a public template only hides the assignment in Classroom 50; anyone can still read the repo.
  1. Create with **Lock assignment** on (or `--locked`).
  2. At session start, turn **Lock assignment** off in the assignment's settings (or `gh teacher assignment lock --unlock`).
  3. Send the invite link.
  4. At session end, lock again to stop late accepts. Existing repos are kept. The wiki doesn't say lock changes repo write access; to freeze pushes as well, add **Close submission**.
- To rehearse, accept from a separate student account, or add yourself to the roster (dual-role caveats above).

### Due dates vs closing

- A due date is a label: later submissions are marked late, nothing is blocked, and autograding still scores late work (marked late).
- A real cutoff is **Close submission**: no new accepts, repos read-only, read access kept. **Reopen submission** restores write (e.g. when a project continues in a follow-up course).
- **Update student repo access** gives finer control (read-only during grading, then restore write).
- Closing grades nothing. Collect first if you want the final state in exports. Closing is also the first step toward a score students can't have influenced (score trust: autograding.md).

### Updating starter code after students accept

- A student repo is a copy of the template at accept time, not a fork. It has no upstream to pull from.
- Template edits reach future accepts only. Late accepters get the newer content, so freeze the template if identical starting points matter.
- Exception: `.gitignore` and `.github/` are re-fetched from the template on every `gh student submit`, so fixes there reach each student's next submission.
- Grading changes propagate on their own: autograder logic and declarative tests live in `classroom50`, so fix them any time and **Regrade all**.
- Anything else: announce it and let students apply it, or script it (`gh teacher download` to clone, then push a fix or open a PR per student).

### Reusing assignments next term

- Create the new classroom, then use **Reuse in another classroom** (row **Manage assignment**), multi-select **Reuse**, the **Assignment** arrow → **Reuse assignment**, or `gh teacher assignment reuse ORG SLUG --from SRC --to DST`.
- Every field is copied, including template, tests, runtime and due date, so UPDATE THE DUE DATE after copying. Student repos and scores are not copied. The target's team is re-granted read on a private in-org template.
- Groups are NOT copied (they are per-assignment, and the new classroom has a new roster), so a reused group assignment starts with none. Within one classroom, carry groups forward with **Copy groups** or `gh teacher team copy` (same members and names, fresh numbering).

### End of term (in this order)

1. **Close or lock the assignments.** **Close submission** per assignment freezes work (read-only, no new accepts). **Lock** hides instead and works on a selection: select all on **Assignments** → **Actions** → **Lock**.
2. **Collect and export.** Run a final collection, then **Download scores (CSV)**. For the work itself, use **Download all submissions** (zip) or `gh teacher download` (clones plus `scores.csv`).
3. **Clean up invite data, then archive.** If you used email invites, run **Clean up invite data** (classroom Settings) BEFORE archiving, because an archived roster is frozen and nothing can be recorded onto it later. The CLI `gh teacher roster sync ORG CLASSROOM --write` does less (records accepted invites and retires finished teams, but keeps teams with still-pending invites) and is refused once archived. Then **Archive** (or `gh teacher classroom archive`). It hides the classroom from the default list, blocks new accepts (per the lifecycle page, effective after the next publish run), refuses new assignments, and leaves student repos untouched. `unarchive` reverses it.
4. **Optional: archive student repos on GitHub** (read-only for everyone, preserved). There is no Classroom 50 bulk action; use `gh`. List first:
   ```sh
   gh repo list ORG --visibility private --no-archived --limit 1000 \
     --json name,isTemplate -q '.[] | select(.isTemplate == false) | .name' \
     | grep -vE '^(classroom50|KEEP-THIS-REPO)$'
   ```
   This skips `classroom50` and templates; add any other repos to keep to the grep. When the list is right, append `| xargs -I {} gh repo archive ORG/{} --yes`. Note: it lists ALL private non-template repos in the org, not only this classroom's, so check the list in shared orgs.
5. **Optional: remove students.** Unenroll removes a student from the roster and classroom team but not from the org, and never deletes repos. Removing from the org revokes access but also deletes nothing. For a whole classroom: org **Members** → classroom filter → select → **Actions** → **Remove from organization**.
- For pausing grading over a break (org Actions switch, per-assignment pause), see autograding.md / troubleshooting.md on Actions cost.

### Tear down an organization (destructive)

- Web: org **Settings** → **Danger zone** → **Tear down organization**. CLI: `gh teacher teardown`.
- It deletes EVERY repo in the org, not only Classroom 50's (including student work and hand-made repos), permanently, plus each classroom's GitHub teams, after a typed confirmation.
- `classroom50` is deleted last, so an interrupted run can be rerun safely. The CLI also removes leftover invite teams and sweeps group teams.
- It needs the `delete_repo` scope. The web app requests it on demand (a token sign-in needs a new token). The CLI requests it only on opt-in: `gh teacher login -s delete_repo`.
- It exists for dev resets and full decommissioning. Export scores and download submissions FIRST.
