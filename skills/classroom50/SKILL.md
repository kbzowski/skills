---
name: classroom50
description: >-
  Provides complete operating knowledge of Classroom 50 (classroom50.org), the open-source GitHub
  Classroom replacement from the Fifty Foundation (CS50). Covers teachers (org setup, service token,
  classrooms, rosters and email invites, TA roles, individual and group assignments, templates,
  autograding tests, score collection, feedback PRs, due dates, end of term) and students (joining,
  accepting, submitting, groups, results), in the web app and the `gh teacher` / `gh student` CLIs,
  plus troubleshooting by symptom. Use when the user mentions Classroom 50, classroom50, gh teacher,
  gh student, leaving GitHub Classroom, or running and autograding a programming course on GitHub,
  e.g. "jak założyć klasę w Classroom50", "dodaj studentów", "autograder", "student nie widzi
  zadania", "zbierz oceny".
metadata:
  source:
    repo: foundation50/classroom50
    commit: 34a3d66ad16f53be16450c8682c860079b0784df  # 2026-10-21 20:43 +0100
    wiki: foundation50/classroom50.wiki
    wiki_commit: 4d79ad48e83eb2734329febb3ec43ecbb61124e4  # 2026-10-21 19:35 UTC
---

# Classroom 50

Classroom 50 distributes and autogrades programming assignments on GitHub. It has **no server and no
database**: the web app (classroom50.org) is a static site on GitHub Pages and the CLI is a pair of
`gh` extensions running locally. Every piece of state is ordinary GitHub data in the teacher's
organization. Nearly every "why does it behave like this" question comes back to that one fact.

This skill and every file in `references/` were written from these exact sources:

- code: `foundation50/classroom50` @ `34a3d66ad16f53be16450c8682c860079b0784df` (2026-10-21)
- wiki: `foundation50/classroom50.wiki` @ `4d79ad48e83eb2734329febb3ec43ecbb61124e4` (2026-10-21)

The project moves fast; for anything version-sensitive, check what changed since then (see
"Fresher information" below).

## Mental model in one table

| Thing | Lives as |
| --- | --- |
| Classrooms, assignments, roster, scores | Files in the private `classroom50` repo in the org, one directory per classroom: `classroom.json`, `assignments.json`, `roster.csv`, `scores.json`, `teams.json` (groups) |
| Enrollment | Membership in the secret team `classroom50-<classroom>` (the source of truth; `roster.csv` only adds names, sections, pending emails) |
| Staff roles | Teams `classroom50-<classroom>-teacher` / `-hta` / `-ta` (visible teams) |
| Groups | One GitHub team per group, `classroom50-group-<hash>-<n>`, owning repo `<classroom>-<assignment>-group-<n>` |
| Pending email invite | A secret team `invite-<hash>` + a roster row without a username |
| Student work | Repo `<classroom>-<assignment>-<username>` (lowercase): commits and Releases |
| Grading result | A GitHub Release carrying `result.json`, gathered into `scores.json` by `collect-scores.yaml` |
| Background jobs | GitHub Actions in the `classroom50` repo, authenticated by the service token secret `CLASSROOM50_SERVICE_TOKEN` |

Two kinds of work follow from this:

- **Interactive** (create a classroom, add a student, save an assignment, accept): runs immediately as
  the signed-in user and is limited by that user's GitHub permissions.
- **Background** (collect scores, regrade, publish Pages): runs in Actions, takes a minute or more, and
  needs a valid service token. "My change didn't show up" is usually a workflow still running, or a
  page not yet reloaded, not lost work.

Nothing syncs while nobody is looking. Accepted email invitations get linked to the roster only when an
owner opens the classroom or roster, clicks **Refresh roster**, or runs
`gh teacher roster sync <org> <classroom> --write`. Scores refresh only on **Collect now** /
**Collect all** / `collect-scores.yaml`.

The web app and CLI are equal front ends over the same files and teams. Anything created in one is
manageable in the other.

## Roles

| Role | GitHub construct | Can |
| --- | --- | --- |
| Teacher | Org **owner**, on `-teacher` team | Everything, incl. org settings, roster edits, score overrides, bulk repo actions |
| Head TA | Org member, `-hta` team | Write `classroom50` repo, manage classroom, collect scores, merge feedback PRs |
| TA | Org member, `-ta` team | Read `classroom50` repo; push access to student repos, granted by each collection run (not at accept); merge feedback PRs |
| Student | Org member, classroom team | Accept and push to their own repos only |

Several actions need an **owner** even though head TAs can otherwise manage things: editing the
roster, overriding scores, granting a private template to the classroom team, and bulk actions that
write to every student repo. When a head TA saves an assignment with a private template, students get
404 on accept until an owner saves it again.

## Requirements

- An organization on the **Team** or **Enterprise** plan (free for verified teachers through GitHub
  Education; the org's plan is separate from the personal teacher benefit). Free-plan orgs show
  **Not supported**.
- The teacher must be an org owner. Students need only free GitHub accounts.
- On filtered school networks the browser must reach GitHub and the app's domains; if `workers.dev`
  is blocked, sign in with a personal access token instead of **Sign in with GitHub**.

## Happy paths

Teacher, first term (web app or CLI, any mix):

1. One-time org setup: **Set up** → **Run setup** (CLI: `gh teacher init <org>`). It locks the org down
   (base permission "No permission", $0 Actions spending cap, two rulesets), creates the `classroom50`
   repo with workflows, and turns on Pages.
2. Add the **service token** (fine-grained PAT, Repository access = **All repositories**, default
   expiry 120 days). Without it, score collection and regrade can't run. **Test token** checks it.
3. Create a classroom (slug ≤ 40 chars; it prefixes every student repo name).
4. Optionally add staff in classroom **Settings** → **Staff and roles**.
5. Add students on **Roster** (one by one, CSV upload, or by email). Each one gets an org invitation
   that carries the classroom team; they must accept it before accept links work.
6. Create an assignment (individual / group / legacy group; optional template; optional tests).
7. Share the accept link (**Share** → **Copy accept link**) or the `gh student accept` command.
8. Students push. Grading runs per the submission type. Teacher clicks **Collect now**, reviews,
   overrides if needed, downloads CSV.

Student:

1. Accept the GitHub org invitation (or use the classroom onboarding link the teacher shares).
2. Open the assignment accept link (or `gh student accept <org> <classroom> <assignment>`). This creates
   their repo, plus the feedback PR if enabled.
3. Work and push. On "tagged commit" assignments, only `gh student submit` or a pushed `submit/*` tag
   (or a teacher-defined submission tag) grades. Results appear as a Release on their repo.

CLI equivalents (install: `gh extension install foundation50/gh-teacher` / `foundation50/gh-student`;
full flags in `references/teacher-cli.md` and `references/student.md`):

```bash
gh teacher login
CLASSROOM50_SERVICE_TOKEN=github_pat_... gh teacher init ORG      # --dry-run first
gh teacher classroom add ORG CLS --name "Intro to CS" --term "Fall 2026"
gh teacher staff add ORG CLS USER --role teacher|hta|ta
gh teacher roster import ORG CLS roster.csv                      # or: roster add / roster invite --file
gh teacher roster sync ORG CLS --write                           # link accepted email invites
gh teacher assignment add ORG CLS SLUG --name "Hello" --template ORG/hello-template
gh workflow run collect-scores.yaml --repo ORG/classroom50 -f classroom=CLS -f assignment=SLUG
gh workflow run regrade.yaml --repo ORG/classroom50 -f classroom=CLS -f assignment=SLUG
gh teacher download ORG CLS SLUG                                 # clones + scores.csv
gh student accept ORG CLS SLUG
gh student submit                                                # inside the assignment clone
```

Score collection and regrade have no `gh teacher` subcommand; they are workflows in the
`classroom50` repo.

## Gotchas worth knowing before answering anything

- **Inviting a student directly on github.com skips enrollment**: they join the org but not the
  classroom team. Fix from the app's org **Members** page → **Actions** → **Add to classroom**.
  Re-inviting an existing member does nothing ("Already a member").
- **Due date only marks Late**; it never blocks pushes. To actually stop submissions use
  **Close submission**. **Lock** hides an assignment even from those who already accepted.
- **Students can read their classroom's private templates and the teacher-only test files** (the
  bundle is published on the org's public Pages site). Never put solutions in either.
- **Public student repos are not autograded**: every run fails with "workflow was not found".
- **Assignment settings changes apply only to repos accepted afterwards**. Existing repos need the
  matching bulk action on the submissions page (e.g. **Add autograding workflow**,
  **Update autograding triggers**, **Update repository features**). The assignment type and slug are
  locked after creation.
- **`gh student submit` is not `git commit && git push`** (the wiki says it is; the code doesn't
  agree). It clones the remote into a temp dir, commits the student's current working tree on top
  of the remote default branch (`--allow-empty`) and pushes. The local clone falls behind, so the
  next `git push` is rejected until `git pull`. A teammate's unpulled remote changes are silently
  overwritten in the snapshot. Each submit is a new commit, so on every-push assignments it costs
  a grading run even with no changes.
- **Test commands run under `/bin/sh -c`** (dash on Ubuntu runners), not bash: no `[[ ]]`, arrays or
  `<(...)`. Wrap in `bash -c '...'` when needed. `points` defaults to 0 if omitted.
- **Unenroll ≠ remove from org ≠ delete repo.** Nothing in Classroom 50 deletes student repositories.
- **Slug budget**: classroom slug + assignment slug ≤ 59 characters (repo names cap at 100, usernames at 39).
- **GitHub invite limits**: 50 per day for orgs under a month old or on the free plan, otherwise 500.
  Invitations expire after 7 days.
- **Settings flipping back** means another tool or an enterprise policy is managing the same org.
- **"Every push" submission type costs Actions minutes on every push**; at scale prefer tagged
  submission. Setup sets a $0 Actions spending cap.
- Pre-release users (before 2026-07-01) must delete the org's `classroom50` repo and start over.

## Reference files

Load only what the question needs. Each file is 500-1000 lines, so list its headings first
(`grep -n '^##' references/<file>`) or grep for the exact label, command or error text, then read
just that section.

| File | Read when |
| --- | --- |
| `references/concepts.md` | Data model, config repo file formats, roles and visibility, org lockdown and rulesets, tokens and sign-in methods, privacy/FERPA, allowed domains, known limitations, glossary, mapping from GitHub Classroom terms |
| `references/teacher-web.md` | Any teacher task in the web app: every screen, field, default, bulk action; staff and multi-teacher setups; due dates, locking, timed exams, end of term, reuse next term |
| `references/teacher-cli.md` | `gh teacher`: install, auth, full command and flag reference with examples, scripting |
| `references/student.md` | Anything the student does, in the web app or `gh student`, and student-side problems |
| `references/autograding.md` | Writing tests and custom autograders, runtimes and Docker, submission types and tags, regrade, feedback PRs, templates, Actions cost, recipes per language |
| `references/troubleshooting.md` | A symptom, badge or error message. Grep it for the exact error text first |

## How to help

- First pin down the **role** (teacher / head TA / TA / student) and the **front end** (web or CLI);
  the answer differs. Use the exact UI labels and command spellings from the references.
- If the user has `gh` authenticated, you can inspect real state read-only: e.g.
  `gh api repos/<org>/classroom50/contents/<classroom>/assignments.json`, `gh api orgs/<org>/teams`,
  a student repo's Releases, or the Actions runs of `collect-scores.yaml`. Prefer reading state over
  guessing.
- Before running anything that changes the org, ask. Confirm explicitly for destructive steps:
  `gh teacher teardown`, removing members from the organization, deleting classrooms, groups or
  repositories, bulk visibility or permission changes.
- Write autograder tests that you have dry-run locally where possible (run the student command in a
  checkout of the template) before telling the teacher to save them.

## Fresher information

The references are a snapshot. When a detail matters and might have changed (new flags, new UI
sections, release notes), check the source of truth:

```bash
# what changed in the code since this skill's snapshot (commit list + touched files)
gh api repos/foundation50/classroom50/compare/34a3d66ad16f53be16450c8682c860079b0784df...main \
  --jq '.status, .ahead_by, (.commits[].commit.message | split("\n")[0]), .files[].filename'
# the wiki is a separate git repo; clone it and diff against the snapshot
gh repo clone foundation50/classroom50.wiki
git -C classroom50.wiki diff --stat 4d79ad48e83eb2734329febb3ec43ecbb61124e4 HEAD
gh teacher <command> --help                               # exact flags of the installed version
```

When you update the references from a newer source, update both hashes here and in the frontmatter.

Questions and ideas go to github.com/foundation50/classroom50/discussions, bugs to its issues.
