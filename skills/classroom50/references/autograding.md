Source snapshot: repo commit `34a3d66`, wiki `4d79ad48` (2026-10-21). Formats below were checked against `schemas/*.json`, `runner.py`, `autograde-runner.yaml`, `materialize_tests.py`, `collect_scores.py`, `regrade_repos.py`. Where the wiki and the code disagree, this file follows the code and says so.

# Autograding, tests, and templates

Everything an agent needs to write working tests and autograders for a teacher, debug a grading run, and keep GitHub Actions cost down.

Sibling files: `concepts.md` (data model, repos, teams), `teacher-web.md` (web app screens and buttons), `teacher-cli.md` (`gh teacher` commands), `student.md` (accept/submit from the student side), `troubleshooting.md` (symptom-indexed fixes).

Placeholders: `ORG` = organization, `CLASSROOM` = classroom short name, `ASSIGNMENT` = assignment slug, `USERNAME` = student login.

---

## 1. The pipeline end to end

### 1.1 Where things live

| Thing | Location |
|---|---|
| Assignment config (tests, runtime, submission mode, ...) | `CLASSROOM/assignments.json` in the private `ORG/classroom50` repo |
| Teacher-only grading files (fixtures, hidden scripts, `autograder.py`) | `CLASSROOM/autograders/ASSIGNMENT/` in `ORG/classroom50` |
| Classroom default autograder | `CLASSROOM/autograder.py` in `ORG/classroom50` |
| Custom caller workflow (rare) | `CLASSROOM/autograders/NAME.yaml` in `ORG/classroom50` |
| Reusable grading workflow | `ORG/classroom50/.github/workflows/autograde-runner.yaml` |
| Runner bootstrap | `ORG/classroom50/.github/scripts/runner.py`, published to `https://ORG.github.io/classroom50/runner.py` |
| Student-side caller ("shim") | `.github/workflows/autograde.yaml` in each student repo, written once at accept |
| Accept marker | `.classroom50.yaml` in each student repo (classroom, assignment, optional `secret`, owner, template source) |
| Per-submission result | GitHub Release on tag `submit/<UTC-timestamp>-<short-sha>` in the student repo, asset `result.json` |
| Gradebook | `CLASSROOM/scores.json` in `ORG/classroom50` |

Published Pages paths (base `https://ORG.github.io/classroom50`). `SEG` is `CLASSROOM`, or `CLASSROOM/SECRET` when `classroom.json` carries a `secret` (unlisted classroom):

- `SEG/assignments.json`, `SEG/classroom.json`
- `SEG/autograders/ASSIGNMENT.tar.gz`: tarball of the whole `CLASSROOM/autograders/ASSIGNMENT/` directory (internal layout `ASSIGNMENT/<files>`), plus the generated `tests.json`
- `SEG/autograder.py`: classroom default, if installed
- `SEG/autograders/NAME.yaml`: custom caller workflows
- `runner.py`, `ensure_feedback_pr.py` at the site root

### 1.2 Step by step

1. **Teacher edits config.** Web form or `gh teacher` writes `assignments.json` (and optional files under `autograders/`) to `ORG/classroom50`.
2. **Publish Pages** (`publish-pages.yaml`, on every push to the config repo except roster-only commits) copies an allow-list of files to Pages, runs `materialize_tests.py` (writes `CLASSROOM/autograders/ASSIGNMENT/tests.json` from each assignment's `tests` + `test_defaults`), then tars each `autograders/<slug>/` directory. The CDN can take about 10 minutes to serve new content; a submission in that window may grade with the old bundle or old `runner.py`.
3. **Student pushes.** The shim fires on push to the default branch and on `submit/*` tags (every-push mode), or only on submission tags (tag mode). It calls `ORG/classroom50/.github/workflows/autograde-runner.yaml@<config-branch>` as a reusable workflow. Permissions granted: `contents: write`, `statuses: write`, `pull-requests: write`.
4. **`setup` job** (always `ubuntu-latest`, GitHub-hosted): full-depth checkout, Python 3.14, PyYAML. Then:
   - Detects the acceptance commit and shim-retrofit commits (via `runner.py --detect-acceptance`, fail-open) and skips them.
   - Reads `.classroom50.yaml` (strict regex validation, org pinned to the repo owner), fetches `SEG/assignments.json`, finds the entry. Fails if the assignment is `empty_repo` or `no_autograder`.
   - Re-validates `tests`, `test_defaults`, `runtime`, `feedback_pr`, `allowed_files`, `release_assets`, `submission_mode`, `submission_tags`. A bad hand-edited value fails here with a field-specific `::error::`.
   - Classifies the trigger: tag-mode + branch push = suppressed; tag matching neither `submit/*` nor a milestone pattern = suppressed.
   - Probes whether anything grades (tests present, or bundle / classroom default return non-404). If nothing, the grade job still runs but skips toolchain installs.
   - Mints the tag: on a branch push or milestone tag, creates `submit/<YYYY-MM-DDTHH-MM-SSZ>-<sha7>` at the commit (reusing an existing `submit/*` tag at that SHA). A pushed `submit/*` tag is reused verbatim. Tags pushed with the Actions token fire no new workflow.
5. **`grade` job** on the `runs-on` from the runtime block, optional `container`, `timeout-minutes: 15`, `shell: bash`:
   - Checkout at `github.sha`, full history, no persisted credentials.
   - `setup-python` / `setup-node` / `setup-java` (temurin) / `setup-go` / `dtolnay/rust-toolchain` / `apt-get install` per the runtime block. All skipped on self-hosted runners and when nothing grades.
   - **Check runner tools**: fails if `curl`, `python3` or `gh` is missing; warns if `git` is missing.
   - **Grade details**: curls `runner.py` from Pages and runs it. `runner.py`: computes owner (from repo name `<classroom>-<assignment>-<owner>`), commit/release/review URLs, submission time (committer date of the graded commit), baseline; deletes any stale `result.json`/`release-body.md` in the checkout; enforces `allowed_files`; downloads and extracts the bundle into `$RUNNER_TEMP/classroom50-runtime/`; resolves the entrypoint (section 2.2); grades; validates `result.json`; writes `release-body.md`, `status=`/`summary=` to `$GITHUB_OUTPUT`; mirrors the body to the run Summary; stages `release_assets`.
   - **Post commit status** (always): context `classroom50/autograde`, state `success`/`failure`/`error` (missing output = `error`, "Autograde did not complete").
   - **Publish submission release** (only if the job succeeded and status is not `error`): deletes and recreates the Release at the tag (unless immutable), title `Submission <tag>` or `Submission <tag> (via <milestone>)`, assets `result.json` + staged extras, body `release-body.md`, marked latest.
   - **Ensure Feedback PR** (if `feedback_pr` and baseline != head), posts `classroom50/feedback-pr` status.
6. **Collection** (`collect-scores.yaml`, teacher-triggered: **Collect now**, **Collect all**, or `gh workflow run collect-scores.yaml -R ORG/classroom50`): walks classroom team members (student + staff teams) x assignments, pages each `<classroom>-<assignment>-<username>` repo's non-draft `submit/*` Releases, downloads and validates each `result.json` (10 MB cap), stamps `late` and `provenance_warning`, upserts into `CLASSROOM/scores.json`, commits. Job timeout 30 minutes. Uses `CLASSROOM50_SERVICE_TOKEN`.
7. **Reading**: submissions page and both CSV exports read `scores.json`; per-test detail lives only in the Release and `result.json`.

Grading changes never require touching student repos: the runner, bundle, runtime and tests are fetched at run time. Only the trigger (`on:` block of the shim) is baked into each student repo.

Grading and publishing share one job and token, so student code that runs during grading can, in principle, publish a forged result under the workflow identity. Detectable (Actions tab), not prevented. See section 9.6.

### 1.3 What propagates when

| Change | Edit | Takes effect |
|---|---|---|
| Declarative tests / report defaults | `tests`, `test_defaults` on the assignment | Next Pages publish (+ CDN lag), then next submission |
| Hidden files, fixtures | `CLASSROOM/autograders/ASSIGNMENT/*` | Next Pages publish, then next submission |
| Per-assignment `autograder.py` | `CLASSROOM/autograders/ASSIGNMENT/autograder.py` | Next publish, next submission |
| Classroom default | `CLASSROOM/autograder.py` (`gh teacher autograder set-default`) | Next publish, next submission |
| Runtime (toolchains, runner, container) | `runtime` on the entry | Next submission (setup job reads the published `assignments.json`) |
| `allowed_files`, `release_assets` | entry fields | Next submission or regrade |
| Submission mode, milestone tags | entry fields | New accepts only, until you retrofit existing repos (section 7.4) |
| Template `.gitignore` / `.github/` | template repo | Each student's next `gh student submit` |
| Old results | | Only after a regrade (section 8) |

---

## 2. Choosing how to grade

### 2.1 Options

| Need | Use |
|---|---|
| Output checks, exit codes, a pytest suite, compile-and-run | Declarative tests (section 3). Default choice. |
| Hidden grading script students must not edit | Declarative `run` test calling `"$CLASSROOM50_BUNDLE_DIR/check.sh"` (section 3.9) |
| Custom scoring logic, weights, external tools (check50, image diff) | Per-assignment `autograder.py` (section 4) |
| One grader for every assignment in a classroom | Classroom default `CLASSROOM/autograder.py` (section 4.5) |
| Different pipeline entirely, or keep GitHub Classroom `autograding.json` | Custom runner workflow, `--autograder NAME` (section 4.7) |
| Template's own CI, no Classroom 50 grading | `no_autograder: true` (web: **Do not use the built-in autograder**) |
| Hand-entered scores | `grading: {"mode": "manual", "max_points": N}` |

### 2.2 Entrypoint precedence (runner.py `resolve_entrypoint`)

1. `CLASSROOM/autograders/ASSIGNMENT/autograder.py` present in the bundle: wins, always.
2. Generated `tests.json` in the bundle: built-in declarative grader.
3. `CLASSROOM/autograder.py` (classroom default).
4. None: vacuous pass. `result.json` with `score 0`, `max-score 0`, `tests: []`, status `success`, summary "submitted, no autograder configured". Still tagged and released, so the submission is recorded.

The CLI refuses `assignment test add`, `test set`, and `--tests` while a per-assignment `autograder.py` exists. A non-CLI writer must probe for it before writing tests.

### 2.3 Grading modes (`grading` block)

| `grading.mode` | Meaning |
|---|---|
| absent or `auto` | Autograded. The CLI writes no `grading` block. |
| `manual` | Teacher types scores on the submissions page out of `max_points` (required, >= 1). Stored as `override: true` entries in `scores.json`. The built-in workflow still runs on submissions unless the built-in autograder is also off. |
| `off` | Not graded. Releases and feedback PR still happen. The web form preselects **Not graded** for new assignments. |

`grading` records intent only. Collection and regrade key off `empty_repo` / `no_autograder` / `init_shim`, not this field.

`pass_threshold` (0-100, optional): advisory "passing" percentage for badges and filters in the web app. Never changes a score. Absent = no passing concept (different from 0).

---

## 3. Declarative tests

### 3.1 Two files, do not confuse them

| File | Location | Shape | Author |
|---|---|---|---|
| `--tests` input file | Anywhere outside `ORG/classroom50` | Bare JSON array of test objects (also accepts the envelope below) | You |
| `CLASSROOM/autograders/ASSIGNMENT/tests.json` | Inside the published bundle | Envelope `{"schema": "classroom50/tests/v1", "tests": [...], "defaults": {...}}` | Publish Pages workflow only |

Tests are stored on the assignment entry (`tests` array in `assignments.json`). Never commit a `tests.json` into `CLASSROOM/autograders/ASSIGNMENT/`:

- Assignment has tests: publishing overwrites it and logs a warning.
- Assignment has no tests: the runner reads your file, rejects it (`tests.json is a bare test array, the --tests file format...` or `tests.json is not a JSON object`), and every submission ends as `error` until you delete it.

### 3.2 Authoring

Web: assignment form, **Autograding tests** section; per-test **Report options**; **Report defaults** panel; **Setup command** under **Advanced settings**.

CLI:

```sh
gh teacher assignment test add ORG CLASSROOM ASSIGNMENT \
  --name compiles --type run --run "gcc -o hello hello.c" --points 1
gh teacher assignment test add ORG CLASSROOM ASSIGNMENT \
  --name "prints hello" --type io --setup "gcc -o hello hello.c" \
  --run ./hello --expected "Hello, world!" --comparison included --points 2
gh teacher assignment test list ORG CLASSROOM ASSIGNMENT [--json]
gh teacher assignment test remove ORG CLASSROOM ASSIGNMENT "prints hello"
gh teacher assignment test set ORG CLASSROOM ASSIGNMENT --tests tests.json   # replace all; '-' = stdin
gh teacher assignment add ORG CLASSROOM ASSIGNMENT --name ... --tests tests.json
```

- `test add` with an existing name replaces that test in place. `test remove` of a missing name is a no-op (exit 0).
- `test list --json > f.json` then `test set --tests f.json` round-trips.
- `test set` with a bare array leaves `test_defaults` alone; with an envelope it replaces them from `defaults` (clears them if `defaults` is absent).
- `test add` flags: `--name --type --run --setup --input --input-file --expected --expected-file --comparison --timeout --exit-code --points --failure-details --show-output --show-command`.
- Re-running `gh teacher assignment add` rewrites the whole entry: re-pass `--tests`, `--allowed-files`, `--runtime` etc. to keep them.

### 3.3 Field reference (one test object)

Closed object: unknown keys are rejected (CLI, setup job, schema).

| Field | Type / range | Applies to | Notes |
|---|---|---|---|
| `name` | string, 1-100 UTF-8 **bytes**, no control chars | all | Required. Unique within the assignment. Becomes `test-name` in `result.json`. |
| `type` | `io` \| `run` \| `python` | all | Required. |
| `run` | non-empty string | all | Required. Shell command, cwd = student checkout. |
| `setup` | string | all | Optional pre-command, runs before `run` for **this test only**. Non-zero exit or timeout = test fails, `run` is skipped. |
| `input` | string | io | Inline stdin. Mutually exclusive with `input-file`. |
| `input-file` | string (path relative to the bundle dir) | io | stdin from a bundled fixture. |
| `expected` | string | io | Inline expected stdout. Mutually exclusive with `expected-file`. |
| `expected-file` | string (bundle-relative path) | io | Expected stdout from a bundled fixture. |
| `comparison` | `included` \| `exact` \| `regex` | io | **Required for io**, no default (web form preselects `included`). `included`/`regex` need non-empty `expected`/`expected-file`. |
| `timeout` | int 0-600 | all | Seconds. 0 or omitted = 10 s. Applies to `setup` and `run` **separately**. |
| `exit-code` | int 0-255 | run | Expected exit status. Omitted = 0. Rejected on `io` and `python`. |
| `points` | int 0-1000 | all | Omitted = 0 (informational). The CLI always writes it. |
| `failure-details` | `full` \| `actual-only` \| `none` | all | Default `full`. See 3.6. |
| `show-output` | bool | all | Default false. Writers omit false. |
| `show-command` | bool | all | Default false. Writers omit false. |

Limits: at most 100 tests per assignment. io-only fields on a `run`/`python` test are rejected.

Assignment-level `test_defaults` (closed object): `{"failure-details": ..., "show-output": bool, "show-command": bool}`. A test's own value wins; an explicit `"show-output": false` on one test opts it out of a `true` default. Copied into the envelope as `defaults`.

### 3.4 Execution model (verified in runner.py)

- Each `setup` and `run` is `subprocess.run(command, shell=True)`: **`/bin/sh -c`** on Linux and macOS (dash on Ubuntu, not bash), `cmd.exe` on Windows. Bash-only syntax (`[[ ]]`, `set -o pipefail`, `source`, `<(...)`, brace expansion) fails unless you write `bash -c '...'` or put it in a script run with `bash script.sh`.
- cwd is always the student checkout root. Every command is a fresh process: files and installed packages persist across tests; `cd`, `export`, aliases, venv activation do not. Writing to `$GITHUB_ENV` does nothing for later tests (all tests run inside one step).
- Environment: the job env plus `CLASSROOM50_BUNDLE_DIR` (absolute path of the extracted bundle `.../classroom50-runtime/ASSIGNMENT`). Job env includes `CLASSROOM`, `ASSIGNMENT`, `SUBMISSION_TAG`, `PAGES_BASE_URL`, `SECRET`, `MODE`, `ALLOWED_FILES`, `RELEASE_ASSETS`, all `GITHUB_*`.
- stdin: `input-file` contents, else `input`, else empty string. A program that reads input with no `input` gets EOF immediately (Python `input()` raises `EOFError`).
- Streams: `run` and `python` tests and every `setup` capture stdout+stderr merged (`2>&1`). `io` tests keep stdout (compared) and stderr (shown) apart. Buffered stdout (C, Python when not a TTY) can appear after stderr; a process killed on timeout loses unflushed stdout.
- Tests run sequentially in list order; a failing test never stops later tests.
- Text decoded as UTF-8 with replacement; universal newlines (CRLF becomes LF).
- Fixture paths are resolved inside the bundle dir; `..` escapes are rejected ("fixture path escapes the bundle"); missing file = test fails with "fixture file not found".

### 3.5 Pass rules and scoring

| Type | Passes when | Score |
|---|---|---|
| `run` | exit code == `exit-code` (default 0) | `points` or 0 |
| `io` | stdout matches `expected` per `comparison` (exit code is ignored) | `points` or 0 |
| `python` | all pytest cases pass | `round(points * passed / total)`, capped at `points - 1` unless all pass |

Comparison modes:

- `included`: raw, case-sensitive substring test, `expected in stdout`. No trimming.
- `exact`: `stdout.strip() == expected.strip()`. Only leading/trailing whitespace of the whole output is ignored; inner spacing, trailing spaces on inner lines, and case matter. Failure detail is a unified diff.
- `regex`: Python `re.search(expected, stdout, re.MULTILINE)`. `^`/`$` anchor at lines; `.` does not cross newlines (use `(?s)`); case-insensitive needs `(?i)`. Remember JSON escaping: `"^hello,\\s+Alice\\b"`. A bad pattern fails the test ("invalid regex in expected").

`python` type details:

- Before running, installs missing `pytest` / `pytest-json-report` into the runner's interpreter with `pip install` (budget `max(timeout, 120)` s). Add your own install in `setup` only to pin versions.
- Appends ` --json-report --json-report-file=<tmp>` to the **end of the `run` string** unless the string already contains `--json-report`. So `run` must end with a pytest invocation: `python -m pytest -q`, `PYTHONPATH=src python -m pytest -q tests/`, `cd sub && python -m pytest`. Something like `python -m pytest; echo done` or `make test` gets the flags in the wrong place.
- Score comes from the report's `summary.total` and `summary.passed`; the pytest exit code is ignored when a report exists. `total` counts every reported case, so skipped and xfail cases reduce the score.
- No parseable report (plugin not importable by the interpreter that ran pytest, e.g. a venv at `.venv/bin/python -m pytest` without the plugin, or a collection error with zero cases) falls back to all-or-nothing on the exit code, with detail "no JSON report ... scored on exit code".

Overall:

- `score` = sum of test scores, `max-score` = sum of `points`.
- Status `success` if every test passed (including zero-point tests), else `failure`. A failing 0-point test (for example the web **Setup command**) turns the status red without changing the number.
- Infrastructure problems (bad `tests.json`, bundle fetch failure, grader crash) give status `error` and **no Release** (section 9.4).

### 3.6 Report options (what students see)

Surfaces: Release body and run Summary keep 2,000 characters per captured block (then "... (truncated)"); the grade job log (step **Grade details**) keeps 100,000. Quiet noisy commands (`make -s`, `pytest -q`) so the verdict fits the Release body.

`failure-details`:

| Value | Failing `io` test shows | Failing `run`/`python` test shows | Timeout shows |
|---|---|---|---|
| `full` (default) | the input, then a unified diff (`exact`) or expected + actual blocks (`included`/`regex`), plus stderr | combined output | input (io) + partial output |
| `actual-only` | only actual stdout + stderr (never expected, diff, or input) | combined output | partial output, no input |
| `none` | only the failure kind line ("exit 1; comparison=exact", "timed out after 10s", "setup exited 2") | same | same |

Use `actual-only` or `none` for hidden test cases: `full` leaks inputs and expected answers.

`show-output: true`: passing tests get a collapsed "Test output" section with setup and run output (Release, Summary, log). On a test failing in `run`, also adds setup output to the failure details. Turn on while authoring, off for production if output is noisy.

`show-command: true`: prints `setup`/`run` command lines at the top of the failure details and the show-output block. Hidden when effective `failure-details` is `none` (except in a passing test's show-output block). On a setup failure only the setup command is printed. Off by default because commands can reveal hidden script names or assertions; turn on for `make test`-style commands students should reproduce.

Log rendering: a PASS/FAIL line per test, then a `::group::FAIL: <name>` per failing test and `::group::OUTPUT: <name>` per passing show-output test. Release body: score heading, table `| Test | Result | Score |`, `<details>` "Failure details", `<details>` "Test output", `Status:` line, and an appended "Removed N file(s)..." section if `allowed_files` deleted anything.

### 3.7 Validation layers

1. CLI / web form at save (Go `tests.go`, web validator).
2. Setup job at submission (inline Python mirror): unknown keys, duplicate names, ranges, io/run constraints. Fails the setup job with `::error::entry 'ASSIGNMENT': tests[i]...`.
3. `runner.py load_tests` before executing: envelope schema, non-empty list, types. Fails as `error` result.

Common rejections: io without `comparison`; `included`/`regex` with empty expected; `exit-code` on io/python; `timeout` > 600; `points` > 1000; name > 100 bytes; two tests with the same name; both `input` and `input-file`.

### 3.8 Complete annotated example

`--tests` file (bare array). Template contains `greet.py` and `test_greet.py`; bundle dir `CLASSROOM/autograders/greet/` contains `names.txt` and `expected-greetings.txt`.

```json
[
  { "name": "imports", "type": "run",
    "run": "python3 -c \"import greet\"", "points": 1 },

  { "name": "greets Alice (included)", "type": "io",
    "setup": "python3 -m py_compile greet.py",
    "run": "python3 greet.py", "input": "Alice\n",
    "expected": "hello, Alice!", "comparison": "included", "points": 2 },

  { "name": "greets World (exact)", "type": "io",
    "run": "python3 greet.py", "input": "World\n",
    "expected": "hello, World!", "comparison": "exact", "points": 2 },

  { "name": "greets Bob (regex)", "type": "io",
    "run": "python3 greet.py", "input": "Bob\n",
    "expected": "^hello,\\s+Bob!", "comparison": "regex", "points": 1 },

  { "name": "hidden case", "type": "io",
    "run": "python3 greet.py",
    "input-file": "names.txt", "expected-file": "expected-greetings.txt",
    "comparison": "exact", "failure-details": "actual-only", "points": 2 },

  { "name": "explicit exit code", "type": "run",
    "run": "python3 -c \"import sys; sys.exit(42)\"", "exit-code": 42, "points": 1 },

  { "name": "pytest suite", "type": "python",
    "run": "python3 -m pytest -q test_greet.py", "timeout": 120, "points": 4 },

  { "name": "hidden checks", "type": "run",
    "run": "bash \"$CLASSROOM50_BUNDLE_DIR/check.sh\"",
    "failure-details": "none", "points": 3 }
]
```

What each line demonstrates: `run` test as compile/import gate; per-test `setup`; the three comparisons; bundled fixtures with redacted failure output; non-zero expected exit; pytest with partial credit and raised timeout; teacher-only script through the bundle variable.

What Publish Pages generates from it (never write this yourself), with `test_defaults: {"show-command": true}` on the entry:

```json
{ "schema": "classroom50/tests/v1",
  "tests": [ ...the same objects, verbatim... ],
  "defaults": { "show-command": true } }
```

Check the published bundle (include `SECRET/` for an unlisted classroom):

```sh
curl -fsSL "https://ORG.github.io/classroom50/CLASSROOM/autograders/greet.tar.gz" | tar -tz
# greet/tests.json  greet/names.txt  greet/expected-greetings.txt  greet/check.sh
```

### 3.9 Setup command, dependencies, environment

- The web **Setup command** is stored as the **first** test: `{"name": "setup", "type": "run", "run": "<cmd>", "points": 0, "timeout": 120}`. Timeout 0 = 10 s, else 1-600. Its failure sets status `failure`, score unchanged; later tests still run (and usually fail).
- Python deps: `python3 -m pip install -r requirements.txt`; packaged project or `src/` layout: `python3 -m pip install -e .`.
- Venv: create once (`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`), then call `.venv/bin/python -m pytest -q` in later tests (Windows: `.venv\Scripts\python.exe`). The pytest JSON plugin must be installed in that venv too, or scoring falls back to exit code.
- One-off env var: `PYTHONPATH=src python3 -m pytest -q` (POSIX), `set "PYTHONPATH=src" && python -m pytest -q` (Windows).
- Per-test `setup` runs again for every test that has it; put shared compiles in the Setup command or a first `run` test to save time.

### 3.10 Teacher-only test files

Anything in the template is readable and editable by students (a test script there can be changed to `exit 0`). Put grading files in `ORG/classroom50` under `CLASSROOM/autograders/ASSIGNMENT/`. The runner downloads a fresh bundle on every run, so students cannot alter it.

- Nothing from the bundle is copied into the checkout. Reach it through the variable: `bash "$CLASSROOM50_BUNDLE_DIR/check.sh"`, `python3 "$CLASSROOM50_BUNDLE_DIR/check.py"`. `bash check.sh` fails with `No such file or directory`. Windows runner: `%CLASSROOM50_BUNDLE_DIR%`.
- `input-file` / `expected-file` are already bundle-relative; no variable needed.
- Hidden pytest: `python3 -m pytest -q "$CLASSROOM50_BUNDLE_DIR"` as a `python` test; make student modules importable with `sys.path.insert(0, os.getcwd())` in a bundled `conftest.py`, or `pythonpath`/`rootdir` config.
- Invoke scripts through their interpreter; the executable bit may not survive.
- Upload: web, saved assignment, **Upload test files**, **Open upload page** (GitHub upload UI); or commit from a clone:

```sh
git clone https://github.com/ORG/classroom50 && cd classroom50
mkdir -p CLASSROOM/autograders/ASSIGNMENT && cp check.sh CLASSROOM/autograders/ASSIGNMENT/
git add . && git commit -m "ASSIGNMENT: grading script" && git push
```

- Do not put an `autograder.py` in the same directory unless you mean to replace the declarative tests (it wins, and the CLI then refuses test edits).
- Bundle limit: the tarball download is capped at **10 MB**; over that the submission ends as `error` ("bundle fetch failed: ... exceeds ... ceiling"). Symlinks inside the bundle are unsafe (rejected on Python < 3.12, constrained by tar `filter="data"` on newer).
- Example `check.sh`:

```sh
set -euo pipefail
test "$(python3 add.py 2 3)" = "5"
test "$(python3 add.py -1 1)" = "0"
```

**Visibility caveat.** "Hidden" means tamper-proof, not secret. The bundle is served by the org's GitHub Pages site; anyone who guesses or finds the URL can download it (an unlisted classroom only adds a secret path segment, and `.classroom50.yaml` in every student repo contains that secret). Never put full solutions, answer keys you care about, or private datasets in the bundle. `assignments.json` (including every test's `run`, `input`, `expected`) is public on Pages too, so inline `expected` values are readable by a determined student; `show-command`/`failure-details` only control the report.

### 3.11 Dry-run tests locally before publishing

The runner's grader is importable. With a clone of `ORG/classroom50` (or the upstream repo) and a student checkout:

```python
# grade_local.py  usage: python3 grade_local.py tests.json BUNDLE_DIR CHECKOUT_DIR
import importlib.util, json, pathlib, sys
spec = importlib.util.spec_from_file_location("r", "classroom50/.github/scripts/runner.py")
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
tests_path, bundle, checkout = map(pathlib.Path, sys.argv[1:4])
raw = json.loads(tests_path.read_text())
env = raw if isinstance(raw, dict) else {"schema": "classroom50/tests/v1", "tests": raw}
tmp = pathlib.Path("tests.envelope.json"); tmp.write_text(json.dumps(env))
tests = r.load_tests(tmp)
g = r.DeclarativeGrader(workspace=checkout, fixtures_dir=bundle, classroom="c", assignment="a",
    username="u", submission="submit/local", commit_link="x", release_link="x")
result, outcomes = g.grade(tests)
status, summary = r.derive_status_and_summary(result)
print(r.render_declarative_body(result, outcomes, summary)); print(status)
```

Upstream ships the same as `examples/declarative-tests/grade-local.py` and `local-verify.sh`. Local runs use your machine's shell and interpreter, so they do not prove the runtime block is right; finish with a real submission from a test student account.

---

## 4. Custom autograders (`autograder.py`)

### 4.1 Scopes

| Path | Scope | Used when |
|---|---|---|
| `CLASSROOM/autograders/ASSIGNMENT/autograder.py` | one assignment | present in the bundle (beats declarative tests) |
| `CLASSROOM/autograder.py` | whole classroom | no per-assignment `autograder.py` and no tests |

### 4.2 Contract

Invocation: `<runner python> autograder.py`, cwd = student checkout, after `allowed_files` enforcement. The interpreter is the job's `python3` (setup-python version on hosted runners, the image's `python3` in a container, the runner's own on self-hosted).

Environment provided:

| Var | Value |
|---|---|
| `CLASSROOM`, `ASSIGNMENT` | slugs |
| `SUBMISSION_TAG` | `submit/<ts>-<sha7>` (always canonical, even when a milestone tag triggered) |
| `PAGES_BASE_URL` | `https://ORG.github.io/classroom50` |
| `USERNAME`, `OWNER` | repo owner (repo-name tail; `group-<n>` for team assignments) |
| `ASSIGNMENT_TYPE` | `individual` \| `group` \| `team` |
| `COMMIT_URL`, `RELEASE_URL`, `REVIEW_URL` | links (`REVIEW_URL` = baseline...commit compare, or the commit URL) |
| `CLASSROOM50_BUNDLE_DIR` | extracted `CLASSROOM/autograders/ASSIGNMENT/` (for the classroom default: that folder if published, else the default's own dir) |
| `SECRET`, `MODE`, `ALLOWED_FILES`, `RELEASE_ASSETS`, `GITHUB_*` | job env |

Sibling files of a per-assignment autograder are at `Path(__file__).parent`.

Must produce `./result.json` (in the checkout root). Optional: `./release-body.md` (otherwise synthesized: score heading + PASS/FAIL table), `status=` and `summary=` lines appended to `$GITHUB_OUTPUT` (otherwise derived: `success` if every test passed or there are none, else `failure`). If you write `status=` yourself it is used as-is.

Exit codes: 0 = ran to completion (pass/fail lives in `result.json`). Non-zero = infrastructure error: runner synthesizes an empty `error` result, status `error`, no Release.

Runner overwrites before validating: `owner`, `assignment_type`, `datetime` (committer date of graded commit), `graded_at` (now), `submitted_by` (from `GITHUB_ACTOR`/`GITHUB_ACTOR_ID`; dropped if unknown). You cannot misattribute a result, and you need not compute these.

Not enforced: `score` equal to the sum of test scores. Only `score <= max-score` and per-test `score <= max-score` are checked. Keep them consistent anyway.

### 4.3 `result.json` (schema `classroom50/result/v1`)

Closed top level (`additionalProperties: false` in the schema; collection tolerates extras in stored records, but do not add top-level fields). Test rows are open: extra diagnostic keys (`message`, `output`) are preserved verbatim.

| Field | Type | Rule |
|---|---|---|
| `schema` | string | exactly `classroom50/result/v1` |
| `classroom`, `assignment` | string | must equal the repo's identity (env `CLASSROOM`, `ASSIGNMENT`) |
| `assignment_type` | enum | stamped by runner |
| `owner` | string | stamped by runner; must match repo-name owner |
| `submission` | string | starts with `submit/`; use `SUBMISSION_TAG` |
| `commit`, `release`, `review` | non-empty string | use the env URLs (`review` falls back to `commit`) |
| `datetime` | `YYYY-MM-DDTHH:MM:SSZ` | stamped by runner (submission instant, fixed across regrades) |
| `graded_at` | same format | optional, stamped |
| `score`, `max-score` | int >= 0, not bool | `score <= max-score` |
| `tests` | array | `[]` allowed |
| `tests[].test-name` | non-empty string | |
| `tests[].passed` | bool | |
| `tests[].score`, `tests[].max-score` | int >= 0 | `score <= max-score` |
| `submitted_by` | `{username, id: int\|null}` | optional, stamped |

Minimal valid example:

```json
{
  "schema": "classroom50/result/v1",
  "classroom": "cs-principles", "assignment": "hello",
  "assignment_type": "individual", "owner": "alice",
  "submission": "submit/2026-06-01T14-32-05Z-a1b2c3d",
  "commit": "https://github.com/ORG/cs-principles-hello-alice/commit/SHA",
  "release": "https://github.com/ORG/cs-principles-hello-alice/releases/tag/submit%2F2026-06-01T14-32-05Z-a1b2c3d",
  "review": "https://github.com/ORG/cs-principles-hello-alice/compare/BASE...SHA",
  "datetime": "2026-06-01T14:32:01Z", "graded_at": "2026-06-01T14:33:11Z",
  "score": 4, "max-score": 5,
  "tests": [
    { "test-name": "compiles", "passed": true, "score": 4, "max-score": 4 },
    { "test-name": "outputs_correct", "passed": false, "score": 0, "max-score": 1, "message": "got 'hi'" }
  ]
}
```

Collection re-validates each Release's `result.json` the same way. Identity mismatch (classroom/assignment/owner) = rejected; `assignment_type` mismatch = warned and skipped.

### 4.4 Templates

Minimal custom grader:

```python
import datetime, json, os, subprocess
from pathlib import Path

subprocess.run(["gcc", "-o", "hello", "hello.c"], check=True)   # compile error -> non-zero exit -> 'error'
p = subprocess.run(["./hello"], capture_output=True, text=True, timeout=10)
ok = p.stdout.strip() == "Hello, world!"
tests = [{"test-name": "prints_hello_world", "passed": ok, "score": int(ok), "max-score": 1}]
Path("result.json").write_text(json.dumps({
    "schema": "classroom50/result/v1",
    "classroom": os.environ["CLASSROOM"], "assignment": os.environ["ASSIGNMENT"],
    "submission": os.environ["SUBMISSION_TAG"],
    "commit": os.environ["COMMIT_URL"], "release": os.environ["RELEASE_URL"],
    "review": os.environ.get("REVIEW_URL") or os.environ["COMMIT_URL"],
    "datetime": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "score": sum(t["score"] for t in tests), "max-score": sum(t["max-score"] for t in tests),
    "tests": tests}, indent=2))
```

Better practice than the wiki's `check=True` on the compile: catch the compile failure and emit a failing test row, so students get a red score instead of an `error` with no Release.

Weighted pytest grader (drop next to hidden `test_*.py` in the bundle dir):

```python
import datetime, json, os, subprocess, sys
from pathlib import Path
HERE = Path(__file__).parent; REPORT = HERE / "report.json"
WEIGHTS = {"test_edge_cases": 3}; DEFAULT = 1
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pytest", "pytest-json-report"], check=True)
subprocess.run([sys.executable, "-m", "pytest", str(HERE), "-q", "--no-header",
                "--json-report", f"--json-report-file={REPORT}"], check=False)  # cwd = student checkout
if not REPORT.is_file():
    sys.exit("pytest produced no report")          # -> status error
rows = []
for t in json.loads(REPORT.read_text()).get("tests", []):
    w = WEIGHTS.get(t["nodeid"].split("::")[-1], DEFAULT); ok = t.get("outcome") == "passed"
    rows.append({"test-name": t["nodeid"], "passed": ok, "score": w if ok else 0, "max-score": w})
# ...write result.json exactly as in the minimal template, with tests=rows
```

Hidden tests importing student code need the checkout on `sys.path` (a bundled `conftest.py` with `sys.path.insert(0, os.getcwd())`).

### 4.5 Classroom default

```sh
gh teacher autograder set-default ORG CLASSROOM --from path/autograder.py   # commit + publish
gh teacher autograder set-default ORG CLASSROOM          # diagnostic stub: prints env, vacuous pass
gh teacher autograder show ORG CLASSROOM
gh teacher autograder remove ORG CLASSROOM
```

The default is downloaded to the runtime root, not inside a bundle, so read per-assignment fixtures through `$CLASSROOM50_BUNDLE_DIR`, not `Path(__file__).parent`. It applies only to assignments with no per-assignment `autograder.py` and no tests. The diagnostic stub is a quick way to prove the pipeline works end to end.

### 4.6 Worked example: CS50 check50 (upstream `examples/autograders/cs50/`)

- `autograder.py` as classroom default: runs `check50 --local --output=json cs50/problems/2026/x/<ASSIGNMENT>` (note `--output=json` glued: check50's `--output` is `nargs="+"`), maps each check to a 1-point row named by its `description`.
- Assignment runtime: `{"container": {"image": "cs50/cli:latest", "user": "root"}}`. `user: root` because the image runs as uid 1000 and `actions/checkout` hits EACCES under `/__w/_temp`.
- Assignment slug must equal the problem name (`mario`, `cash`, `tideman`). Edit the year prefix each year and re-run `set-default`.
- Like any container, `cs50/cli` must provide `gh`, `curl`, `bash`, `python3`; the first run's **Check runner tools** step confirms it.

### 4.7 Custom runner workflow (`--autograder NAME`, rare)

Replaces the student-side caller instead of the grading script.

1. Add a callable workflow (`on: workflow_call`) under `ORG/classroom50/.github/workflows/` with any name except `autograde-runner.yaml`.
2. Add a caller at `CLASSROOM/autograders/NAME.yaml` with your own `on:` triggers and `jobs.<id>.uses: ORG/classroom50/.github/workflows/<file>.yaml@main`. It is copied verbatim at accept (no placeholder substitution), so hard-code org and branch. Grant the permissions your workflow needs (`contents: write`, `statuses: write`, `pull-requests: write` for parity).
3. `gh teacher assignment add ORG CLASSROOM ASSIGNMENT --autograder NAME ...`. The caller is fetched from Pages at accept; accept fails with "autograder `<name>` not published yet" until Publish Pages has deployed it.

To be collected, your pipeline must publish like the built-in one: a Release on a `submit/*` tag with a `result.json` asset (schema above), both created with the job's `GITHUB_TOKEN`. Anything published with a PAT is collected but flagged **Unverified**. `submission-mode` retrofits never rewrite custom callers (use `--update-shims=false` to flip only the field; edit `on:` yourself).

Keeping GitHub Classroom's `autograding.json`: point a custom caller at a workflow that runs your existing grading action, and ship `.github/classroom/autograding.json` plus fixtures in the **template**. Classroom 50's built-in runner never reads `autograding.json`.

Never name a template workflow `.github/workflows/autograde.yaml`; that path is reserved for the shim.

---

## 5. Runtime block

Optional `runtime` object on the assignment (web **Advanced settings**, CLI `--runtime file.json`). Closed contract: an unknown key makes the setup job fail ("runtime has unsupported keys").

```json
{ "runs-on": "ubuntu-latest", "python": "3.14", "node": "20", "java": "21",
  "go": "1.23", "rust": "stable", "apt": ["valgrind"], "apt-recommends": false }
```

| Field | Rule | Effect |
|---|---|---|
| `runs-on` | string label or array of 1-10 labels, each `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$`; `""` and `[]` rejected | grade job runner; arrays are AND-ed. No allow-list: a typo queues forever waiting for a matching runner. |
| `python`, `node`, `java`, `go`, `rust` | `^[A-Za-z0-9._+-]{1,32}$` | `setup-python`, `setup-node`, `setup-java` (Temurin), `setup-go`, `dtolnay/rust-toolchain` |
| `apt` | array of Debian package names | `sudo apt-get update -qq && apt-get install -y --no-install-recommends ...`; Linux hosted runners only; forbidden with `container` |
| `apt-recommends` | bool, requires `apt` | `true` drops `--no-install-recommends` (e.g. `pandoc` + `texlive`) |
| `container` | `{image, user?}` only | grade job runs inside a public image |

Defaults: omitted runtime = `ubuntu-latest` + Python 3.14 on the host. With `container`, Python is not installed unless you set `python` (then `setup-python` installs it inside the container).

Containers:

- `image` (required, `^[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,255}$`) must be publicly pullable; private registries are impossible (no safe way to deliver pull secrets to student repos).
- `user` uses `docker run --user` syntax and becomes `options: --user <value>`. Set `"user": "root"` for any image that does not run as root, or checkout fails with a permission error.
- Linux only: `runs-on` labels starting `macos-`/`windows-` are rejected with a container.
- The image must contain `bash`, `curl`, `python3`, `gh` (GitHub CLI), and ideally `git`. Stock `gcc` / `python` images lack `gh`; build your own image.

Self-hosted runners:

- All managed setup (setup-* actions, apt, even default Python) is skipped when `runner.environment == 'self-hosted'` (agent v2.294.0+). Bake toolchains into the runner.
- Runner needs `bash`, `curl`, `python3` + `pip`, `gh` (no login needed; steps set `GH_TOKEN`), and `git` (without it: no `allowed_files` enforcement, no review link, submission time = grading time).
- The **Check runner tools** step lists all missing tools at once.
- The `setup` job still runs on GitHub-hosted `ubuntu-latest` (see section 11).

Windows / macOS runners: declarative commands run under `cmd.exe` on Windows; `apt` is skipped off Linux; runner-level steps still use bash. Avoid unless the course needs them (cost, see section 11).

Hard ceiling: the grade job has `timeout-minutes: 15`, covering toolchain setup, every test, and publishing. Per-test timeouts do not extend it. 100 tests x 600 s cannot fit; keep the sum of worst-case timeouts well under 15 minutes.

Runtime values come from the teacher's config repo, never from the student repo, so a permissive `runs-on` does not let students choose runners.

---

## 6. Submission scope and Release extras

### 6.1 `allowed_files`

Ordered `.gitignore`-syntax allowlist (max 100 patterns, last match wins, `!` re-includes):

```sh
gh teacher assignment add ORG CLASSROOM hello --name Hello --template ORG/hello-template \
  --allowed-files '*' --allowed-files '!hello.py'
```

- One `--allowed-files` per pattern; do not comma-join. Omit or empty = all files allowed.
- Enforced before grading by deleting disallowed working-tree files (walks nested repos too). Always kept: `.classroom50.yaml`, `.github/` (and `.git/`), `result.json`, `release-body.md`. Removals are listed in the Release body ("Removed N file(s) outside the assignment's allowed files").
- Everything the tests read from the checkout must be allowlisted: `requirements.txt`, `pyproject.toml`, `Makefile`, starter scaffolding, the template's own test files, and any file named in `release_assets`.
- Fails open (git missing, matcher error, timeout): the full tree is graded. `gh student submit` also filters before pushing, but a plain `git push` bypasses that. Hygiene tool, not a security boundary.

### 6.2 `release_assets`

Attach generated files (PDF, plots, logs) from the checkout to each Release: `"release_assets": ["report.pdf", "plots/chart.png"]` (web: **Submission release files**).

- Resolved after grading, so the autograder or a test can generate them. Uploaded under their basenames.
- Limits: max 50 paths, 8 KiB total path bytes, unique Release-safe basenames (`[A-Za-z0-9._-]`, no leading/trailing dot, no `..`, not `result.json` / `release-body.md`), relative `/`-separated paths, no `.git/`. 100 MiB total content at runtime.
- Missing, unsafe, oversized or failed files warn (`::notice::release_assets: attached X of Y`) without changing the score.
- A file that is itself a `classroom50/result/*` document is refused (anti-forgery).
- Immutable releases: assets are attached in the same `gh release create`, so they work, but a regrade cannot refresh them (section 8).

---

## 7. Submission type (which commits grade)

### 7.1 Modes

| `submission_mode` | Web label | Shim triggers | What grades |
|---|---|---|---|
| `every-push` (default; writers omit it) | **Every push to the default branch** | push to default branch + `submit/*` tags (+ milestone patterns) | every default-branch commit except tool commits; every submission tag |
| `tag` | **A tagged commit** | `submit/*` tags (+ milestone patterns) only | only tag pushes; plain `git push` runs nothing |

In tag mode the student submits with `gh student submit` (commits, pushes, then pushes `submit/<UTC-ts>-<sha7>` with the student's own token) or by hand: `git tag submit/final && git push origin submit/final`. In every-push mode `gh student submit` does not push a tag (the branch push already grades; a tag would double-grade).

Tag pattern caveats:

- The shim filter is `submit/*`; GitHub's `*` does not match `/`, so `submit/a/b` does not trigger.
- GitHub creates no push events when more than three tags are pushed at once; `git push --tags` with many tags can grade nothing. Push one tag at a time.
- Tags are case-sensitive.

### 7.2 Milestone tags (`submission_tags`)

Up to 20 patterns, e.g. `["phase1", "phase2", "complete"]` (CLI `--submission-tag`, repeatable; web field shown only under **A tagged commit**, but the CLI allows them with either mode). Syntax: GitHub tag-filter subset `*` (no `/`), `**`, `?`, `+`, `[...]`; no `!`; no leading `?`/`+`; no stacked quantifiers like `v*+`; charset `[A-Za-z0-9._/*?+\[\]-]`. Prefer exact names; `v*` grades every release tag a student pushes.

A milestone tag triggers grading, but the record is still a canonical `submit/<ts>-<sha7>` tag minted at that commit (Release title "... (via phase1)"). `submit/*` always keeps working alongside.

### 7.3 Commits that never grade, and the statuses that say so

| Situation | Runner behavior | Commit status |
|---|---|---|
| Acceptance commit (adds only `.classroom50.yaml` + shim, nothing on top) | skip, notice in Actions | `classroom50/autograde` success "acceptance commit: nothing to grade yet" |
| Shim retrofit commit (touches only `.github/workflows/autograde.yaml`; normally `[skip ci]` so no run) | skip | `classroom50/autograde` success "autograder trigger updated" |
| Feedback-PR empty commit, enable-autograder backfill | `[skip ci]`, no run | none |
| Tag-mode assignment, branch push via stale shim | no tag, no grade | `classroom50/autograde-skipped` success "tag-mode assignment: push not graded; run gh student submit" |
| Tag matching nothing (stale or hand-edited shim) | no grade | `classroom50/autograde-skipped` success "tag is not a submission trigger" |
| Nothing configured to grade | vacuous pass, Release published | `classroom50/autograde` success "submitted, no autograder configured" |
| Commit message with `[skip ci]` etc. | GitHub fires nothing | none |

`autograde-skipped` is a separate context on purpose: real work exists but was not graded, so it must never show green under `classroom50/autograde`. Detection of acceptance is fail-open: when unsure, it grades.

### 7.4 Changing the trigger on existing repos

The shim is written at accept and never refreshed by submit, so changing `submission_mode` or `submission_tags` needs a retrofit:

- CLI: `gh teacher assignment submission-mode ORG CLASSROOM ASSIGNMENT --tag` (or `--every-push`), optional `--user USERNAME`, `--dry-run`, `--update-shims=false` (field only). Needs the `workflow` OAuth scope: `gh auth refresh -s workflow`.
- Web: change **Submission type**, then submissions page **Actions** > **Update autograding triggers** (or per-row **Update autograding trigger**).
- Surgical: only trigger lines change; hand-edited shims are reported and left alone; custom callers never rewritten. Commits with `[skip ci]`.
- Students must `git pull` afterwards, or their next push conflicts.
- Until retrofitted, the runner's stale-trigger suppression keeps tag-mode honest, but each suppressed push still starts a run (setup job minutes).

### 7.5 Cost implication

Every-push grades every push: 5 pushes = 5 runs = 5 Releases. Tag mode costs nothing for ordinary pushes. Details in section 11.

---

## 8. Regrade and grading a specific commit

- Every attempt keeps its own frozen Release; to see the score for a past commit, open its `submit/*` Release.
- Grade an arbitrary commit: push a tag at it: `git tag submit/regrade-me SHA && git push origin submit/regrade-me` (student, or anyone with push). Creates a new submission at that commit.
- **Regrade** (row action, or **Actions** > **Regrade all**; workflow `regrade.yaml`, inputs `classroom`, `assignment`, optional `owner`) re-runs each repo's **latest graded** autograde run via the Actions rerun API: same commit, freshly fetched runner and bundle. `datetime` and `late` unchanged; `graded_at` moves. Newer ungraded pushes are not graded by a regrade.
- Never-graded repo with pushed work: the latest commit is first-graded (re-runs a suppressed branch run, or pushes a fresh `submit/*` tag with the service token). Nothing pushed since accept: skipped.
- Regrade does not collect. Run **Collect now** after the regraded runs finish; collecting too early reads the old Releases.
- GitHub refuses to re-run runs older than about a month ("created over a month ago"); regrade warns and skips those repos. Workaround: push a fresh `submit/*` tag at that commit.
- Immutable releases (org/repo setting or ruleset): the Release cannot be refreshed; the new score appears only in the commit status and job summary, and collection keeps the old score. The runner deliberately does not delete immutable Releases (the tag name would be burned forever).
- First-grading a commit pushed before a submission-mode change needs `Workflows: Read and write` on the service token (GitHub's rule for refs whose workflow file differs from the default branch). Regrade names the repos; otherwise the student pushes once.
- Regrade job timeout 120 minutes; safe to re-dispatch.
- Do not force-push or delete `submit/*` tags; collection and history key on them.

Catching up after a pause: work pushed while autograding was paused is not graded retroactively. **Regrade all** grades one run per repo (latest submission, or latest commit if never graded), then **Collect now**.

---

## 9. Reading results

### 9.1 Three records per graded submission

| Record | Where | Contents |
|---|---|---|
| Release | student repo, tag `submit/<ts>-<sha7>` | score heading, PASS/FAIL table, failure details, `result.json` asset, extra assets. The only per-test breakdown. Linked as **View autograder details** / **View score**. |
| Commit status | graded commit, context `classroom50/autograde` | `success` / `failure` / `error` + "classroom50 autograde: 7/10 (3/4 tests passed)"; links to the run |
| Collected score | `CLASSROOM/scores.json` after collection | what the submissions page and CSVs show |

Releases and statuses appear when grading finishes; collected scores lag until collection. "I submitted but there is no score" usually means: collect first.

Debug path for one submission: commit status > run link > `setup` job (config/trigger problems) or `grade` job **Grade details** step (test output, 100k chars) > Summary tab (same as Release body).

```sh
gh api repos/ORG/REPO/commits/SHA/status --jq '.statuses[] | {context,state,description}'
gh release view -R ORG/REPO                       # latest submission
gh release download TAG -R ORG/REPO -p result.json -O - | jq .tests
gh run list -R ORG/REPO --workflow autograde.yaml
gh run view RUN_ID -R ORG/REPO --log
```

The grade log line `runner: grading per-assignment declarative tests ...`, `runner: using per-assignment entrypoint ...`, `runner: using classroom default entrypoint ...` or `runner: submitted, no autograder configured` tells you which entrypoint ran.

### 9.2 `scores.json` (schema `classroom50/scores/v1`)

```json
{ "schema": "classroom50/scores/v1",
  "assignments": {
    "hello": {
      "type": "individual",
      "collected_at": "2026-06-02T10:00:00Z",
      "entries": [
        { "owner": "alice",
          "submissions": [ { "...result.json minus 'assignment'...": "", "late": false } ],
          "override": false } ],
      "detected": [ { "owner": "bob", "count": 2, "kind": "commit",
                      "latest_datetime": "2026-06-01T09:00:00Z", "late": false } ] } } }
```

- Buckets keyed by assignment slug; `type` mirrors `mode`.
- One entry per repo owner (lowercased); `submissions` newest first (`[0]` = latest); each is a result payload minus `assignment`, plus collection-added `late` (when the assignment has `due`) and `provenance_warning`.
- Group entries: `member_usernames`; team entries also `team_slug` (`classroom50-group-<hash16>-<n>`), owner `group-<n>`.
- `override: true`: entry frozen, never refreshed (manual grades, corrections). `false` explicit = keep refreshing.
- `detected`: repos with pushes/tags but no graded Release (no-autograder / empty-repo assignments, or autograded ones whose runs did not publish). Presence and count only, never a score.
- `collected_at`: last time collection walked that assignment.

`late` = submission `datetime` (committer date, student-controlled) after `due`; exactly at `due` is on time. Advisory only.

### 9.3 Downloads and CSVs

- Web **Download scores (CSV)**: one row per student/group, latest submission: `name first_name last_name usernames score max_score submissions submitted_at late commit review release provenance_warning group`.
- `gh teacher download ORG CLASSROOM ASSIGNMENT`: clones every repo, writes `scores.csv` (one line per attempt, newest first, plus blank lines for non-submitters: `username first_name last_name email section score max_score datetime submission_tag submitted_by review_url late override provenance_warning group`), and per repo `result.json` (latest) and `results.json` (array of `{submission_tag, result, result_problem?, provenance_warning?}`, newest first, `result` raw incl. `assignment`, or null).
- Per-test data is in neither CSV; use Releases or the JSON files.

### 9.4 Failure paths

| What failed | Result |
|---|---|
| Hand-edited config invalid (tests, runtime, release_assets, ...) | setup job fails with field-specific `::error::`; no tag, no Release, no grade status |
| `.classroom50.yaml` missing/malformed | setup fails ("Was this repo created by `gh student accept`?") |
| Assignment missing from published `assignments.json` | setup fails ("not registered ... Ask your teacher to run `gh teacher assignment add`"); often Pages not yet deployed |
| `runner.py` fetch fails in grade job | status `error` "Autograde did not complete" |
| Bundle fetch/extract fails, bad `tests.json`, grader crash, autograder non-zero exit, invalid `result.json` | status `error`; synthesized 0/0 result; **no Release** |
| Some tests fail | `failure`; Release published |
| All pass | `success`; Release published |
| Release/`result.json` upload fails | grade job fails; latest pointer does not move |
| Extra release asset problem | warning only |
| Reusable workflow cannot load (e.g. public repo) | run fails before any job; collection may list the repo under `detected` |

### 9.5 Group attribution (summary)

Graded once in the shared repo; collection fans the score out. Team (`mode: team`): credited members = live GitHub team members intersected with the roster; failed team read = repo skipped, previous entry kept; deleted team shows **Group team missing**. Legacy group: collaborators on the classroom team (owner always included); owner-only result warns. `submitted_by` records who pushed. See `concepts.md`.

### 9.6 How far to trust a score

- Tests, fixtures, runner come from the config repo each run: students cannot edit them.
- Release not authored by `github-actions[bot]`, or `result.json` uploaded by someone else: still collected, flagged **Unverified**, `provenance_warning` in `scores.json` and CSVs. Teacher-published Releases get flagged too; use `override: true` for manual grades instead.
- Deleting or drafting the newest Release makes an older honest score "latest" with no flag; more Actions runs than Releases is the tell.
- Code executed during grading shares the job's token and could publish a forged Release. Detectable via the Actions tab, not prevented.
- Submission time is the committer date, set by the student's git client.
- Trustworthy final grade: **Close submission** (repos read-only), `gh teacher download`, re-run the same tests on the clones in a context students never touched.
- Spot check one repo: Release author and `result.json` uploader both `github-actions[bot]`, file starts with `"schema": "classroom50/result/v1"`, job summary matches, `.github/workflows/` at the graded commit contains only `autograde.yaml` (plus template-provided workflows).

---

## 10. Feedback pull requests

- On by default (`gh teacher assignment add` and the web form; disable with `--feedback-pr=false`). Stored as `feedback_pr: true` (absent = off).
- One long-lived PR per student repo: base = frozen `feedback` branch at the baseline (the commit that introduced `.classroom50.yaml`; root commit for no-autograder repos), head = default branch. Shows the whole starter-to-latest diff; teachers comment inline next to the scored Release.
- Opened at accept (even with Actions disabled); the runner adopts it by base/head and maintains it, opening it on the first submission if accept could not. Posts `classroom50/feedback-pr` status. Needs baseline != head.
- Labeled **Individual Assignment** / **Group Assignment**. A student closing it gets it reopened; a teacher merge is final.
- Only staff can merge: an org ruleset locks `feedback`, exempting owners and the teacher/HTA/TA teams. Staff write access comes from the collection run, so the merge button appears after the next collection. **Merging is blocked** for staff = re-run `gh teacher init` to update rulesets.
- Body: built-in text, or with `feedback_pr_template: true` (requires template + feedback_pr) the template's first existing `.github/pull_request_template.md`, `pull_request_template.md`, `docs/pull_request_template.md`, verbatim. Fallbacks to built-in on any read problem.
- Prerequisite set by `gh teacher init`: org setting "Allow GitHub Actions to create and approve pull requests".
- Untrusted baseline (marker commit also had other files, or no marker): PR opens against the root commit with a warning; a `feedback` branch at the wrong commit makes the runner refuse until an org admin deletes it.
- Repos accepted before the feature: delete and re-accept.

---

## 11. Managing Actions cost

### 11.1 What a run costs

- The organization pays, never students. Student repos are private by default, so runs consume the org's included minutes (GitHub Team: 3,000 min/month; beyond that billed up to the spending limit).
- Each grading run is two jobs, each rounded up to a whole minute: `setup` (always GitHub-hosted `ubuntu-latest`) + `grade`. Floor is about **2 billed minutes per run**, even a vacuous pass.
- Every run that starts costs at least the setup minute: acceptance-commit runs, suppressed stale-shim pushes, foreign tags.
- `no tests` assignments using the built-in autograder still run (to tag and record), skipping toolchain installs: cheaper, not free.
- Collection: one job in the config repo walking every repo in scope, 30-minute cap. **Collect now** (one assignment) is cheap; **Collect all** walks every assignment (asks for confirmation).
- Regrade: one small job in the config repo plus one grading run per repo.
- Windows and macOS runners bill at higher rates than Linux on GitHub's price list; avoid them unless required.

Estimate: `runs = students x pushes per student` (every-push) or `students x submissions` (tag mode); `minutes ~= runs x (1 + ceil(grade job minutes))`. Example: 120 students x 25 pushes = 3,000 runs x ~2-3 min = 6,000-9,000 minutes, double the Team allowance. Same course in tag mode with 3 submissions each: 360 runs, about 1,000 minutes.

### 11.2 Levers, biggest first

1. **Tag mode** (`--submission-mode tag`, web **A tagged commit**): plain pushes cost nothing. Set at creation; for existing repos retrofit (section 7.4) or stale shims keep starting runs.
2. **No built-in autograder** for hand-graded or own-CI assignments (`no_autograder`): no workflow at all. Affects future accepts only.
3. **Pause autograding**: per assignment, submissions page **Actions** > **Pause autograding** (disables `autograde.yaml` in every student repo via the workflow-disable API; **Resume autograding** re-enables; per-row too). A student with admin on their repo can re-enable it. Org-wide: settings toggle **Pause autograding for all student repositories** narrows the org Actions policy to the `classroom50` repo, which stops **all** workflows in student repos, including course CI.
4. **Self-hosted runners** via `runs-on`: the grade job uses no GitHub minutes, but the setup job still runs GitHub-hosted (about 1 billed minute per run). The wiki's "costs no GitHub Actions minutes" overstates this.
5. **Make runs short**: keep toolchains in the default image (skip `apt` when preinstalled), use a prebuilt `container` with everything baked in, compile once in the Setup command rather than in every test's `setup`, use quiet flags, cut pip installs (commit vendored deps or use a container).
6. **GitHub Education**: verified educators can ask for extra credits.

### 11.3 Spending cap

`gh teacher init` / web setup creates a **$0 Actions spending cap** only when the org has none (a cap you set is never changed). When included minutes run out, runs are blocked until the next billing cycle or until you raise the cap in org billing settings. Blocked pushes are not graded retroactively, so plan a **Regrade all** after raising it. Enterprise-managed orgs may show "Couldn't verify the Actions spending cap" (see `troubleshooting.md`).

### 11.4 Public repositories

Runs in public repos are free on standard hosted runners, but **public student repos are not autograded**: the shim calls a workflow in the private `classroom50` repo and GitHub only lets public repos call public workflows. Every run fails before any job with `Invalid workflow file ... error parsing called workflow ... workflow was not found`. The config repo must stay private (roster). Public visibility (`repo_visibility: public`, `--repo-visibility public`) only saves money for assignments without the built-in autograder; otherwise make repos public only after grading. Fix: make the repo private again (row **Make repository private**, or **Change repository visibility** > **Private** > **Apply to all**) and set the assignment's visibility back to private for future accepts.

---

## 12. Assignment templates

### 12.1 Repository shapes

| Shape | Set with | Student repo gets | Autogrades |
|---|---|---|---|
| Template | `--template OWNER/REPO` | template copy + `.classroom50.yaml` + shim | yes |
| Template, own CI | template + `no_autograder: true` | exact template copy, no Classroom 50 files | no (collection records presence only) |
| No template, README | omit `--template` (README on, CLI default) | README + control files | yes |
| No template, README, no autograder | `no_autograder: true` | README only | no |
| No template, no README | `init_shim: true` | control files only | yes |
| Empty repository | `--empty-repo` | no commits, no files, no feedback PR ever | never |

- Shape changes affect future accepts only. Turning the built-in autograder on later: **Add autograding workflow** on the submissions page or `gh teacher assignment enable-autograder` (adds shim + marker, `[skip ci]`).
- `no_autograder` and `empty_repo` forbid `tests`, `allowed_files`, `release_assets`, `pass_threshold`; `empty_repo` also forbids `template` and feedback PR. `init_shim` forbids `template`.
- Assignment type (individual/group) is locked once set.

### 12.2 Layout

```text
README.md                     student-facing instructions
.gitignore                    optional; re-fetched from template on every gh student submit
.github/                      optional; re-fetched on every submit; non-autograde workflows only
pull_request_template.md      optional; can become the feedback PR body
<starter code + visible tests, requirements.txt, Makefile, Gradle wrapper, Cargo.lock ...>
```

Never include `.github/workflows/autograde.yaml`: accept writes the shim there, and submit's `.github/` re-fetch would overwrite it with the template's copy, double-grading or breaking grading. Other workflow names are untouched. Also avoid committing `result.json` or `release-body.md` (the runner deletes them before grading, but they confuse students).

Put in the template only what students may see and change: starter code, visible tests, build files. Put hidden tests and expected outputs in `CLASSROOM/autograders/ASSIGNMENT/`.

### 12.3 Requirements and gotchas

- Must have at least one commit (else "template ... has no commits"; right after a push GitHub can misreport for a minute, retry).
- Mark it: repo **Settings** > **General** > **Template repository** (`gh repo edit ORG/REPO --template`).
- Visibility: public always works; private works only inside the org (saving the assignment grants the classroom student team read; Enterprise "internal" also works); private outside the org is rejected. Only an org owner can grant: a TA's save succeeds with a warning and needs an owner to re-save. A locked assignment gets no grant until unlocked.
- Private template with forks: GitHub copies the team grant to every private fork, exposing them (dangerous when reusing an old GitHub Classroom starter, whose student repos are forks). Use a fresh fork-free copy. Locking does not undo the exposure.
- Fork of another org's repo: accept can 403 on OAuth App access restrictions of the parent org. Use a fresh non-fork copy.
- Only the default branch is copied unless `include_all_branches: true`. A `@branch` suffix on `--template` is ignored with a warning; change the template's default branch instead.
- Copied: files. Not copied by GitHub: About and topics (Classroom 50 copies them on web accept when **Copy About/topics** are on, not on `gh student accept`), repo features (follow the assignment's feature settings, default inherit).
- Each accept snapshots the template at that moment; late accepters get newer content. Freeze the template or use one per assignment if identical starts matter. `.gitignore`/`.github/` changes propagate to every assignment sharing the template on next submit.
- Starter code and README are never re-fetched after accept.
- The slug passed to `gh student accept` is the assignment slug, not the template name. Repo created: `ORG/<classroom>-<assignment>-<username>` (lowercase, max 100 chars).
- Wiki-vs-template note: upstream `templates/example-assignment/README.md` says submit fetches the autograde workflow from the classroom on every submit. Code and wiki say the shim is written once at accept and never refreshed; submit only re-fetches template `.gitignore` and `.github/`. Trust the code.

---

## 13. Recipes

Conventions: timeouts are per command (default 10 s, max 600); the Setup command starts at 120 s; every command is a fresh `/bin/sh` in the checkout; keep the total under the 15-minute job limit.

### Python

Default runtime has Python 3.14; pin with `{"python": "3.12"}`. Template: starter code, `requirements.txt`, visible `test_*.py`. Setup command (only with deps): `python3 -m pip install -r requirements.txt`.

```json
[ { "name": "pytest suite", "type": "python", "run": "python -m pytest -q", "timeout": 120, "points": 10 } ]
```

Hidden tests from the bundle: `"run": "python3 -m pytest -q \"$CLASSROOM50_BUNDLE_DIR\""` plus a bundled `conftest.py` that puts the checkout on `sys.path`.

Failures: `ModuleNotFoundError` = missing install in Setup command; works locally but not in grading = `src/` layout (`PYTHONPATH=src python -m pytest -q`, or `pythonpath` in `pyproject.toml`/`pytest.ini`); variables vanishing between tests = expected, set inline; exit 127 = old workflow files (re-run `gh teacher init`) or a setup that replaced the environment.

### Java (Gradle)

Runtime `{"java": "21"}`. Commit the Gradle wrapper (`gradlew`, `gradle/wrapper/`), sources in `src/main/java`, tests in `src/test/java`.

```json
[ { "name": "unit tests", "type": "run", "run": "sh ./gradlew test --console=plain", "timeout": 300, "points": 10 } ]
```

Partial credit: one test per class, `sh ./gradlew test --tests "CalculatorTest"`. `Permission denied: ./gradlew` = lost executable bit, run via `sh`. First run downloads Gradle and deps: raise the timeout. Maven: `mvn -q test` similarly (Maven is preinstalled on hosted Ubuntu images).

### C#

Hosted Ubuntu ships recent .NET SDKs; no runtime needed. Pin an SDK with a container that has Python:

```json
{ "container": { "image": "mcr.microsoft.com/dotnet/sdk:8.0" }, "python": "3.14" }
```

(The image must also provide `gh` and `curl`, see section 5; check the **Check runner tools** step.) Setup command `dotnet restore` with a raised timeout.

```json
[ { "name": "unit tests", "type": "run", "run": "dotnet test --nologo", "timeout": 300, "points": 10 } ]
```

Partial credit: `dotnet test --filter "FullyQualifiedName~AddTests"`.

### C and C++

`gcc`, `g++`, `make` preinstalled; extra packages via `{"apt": ["valgrind"]}`. For Catch2 commit the amalgamated header/source.

```json
[
  { "name": "compiles", "type": "run", "run": "make", "timeout": 60, "points": 1 },
  { "name": "unit tests", "type": "run", "setup": "g++ -std=c++17 -o tests tests.cpp student.cpp",
    "run": "./tests", "timeout": 120, "points": 8 },
  { "name": "prints usage", "type": "io", "run": "./student", "input": "\n",
    "expected": "Usage:", "comparison": "included", "points": 1 }
]
```

Partial credit with Catch2 tags: `./tests "[part1]"`, `./tests "[part2]"`. Memory check: `valgrind --error-exitcode=1 --leak-check=full ./student < input.txt` as a `run` test. Compile errors appear as a failed `setup` (output in the Release and log). A crash fails an `io` test with stderr; a hang hits the timeout. Prompting C programs: `fflush(stdout)` or the prompt is lost on timeout.

### Rust

Runtime `{"rust": "stable"}`. Commit `Cargo.lock`.

```json
[
  { "name": "builds", "type": "run", "run": "cargo build", "timeout": 300, "points": 1 },
  { "name": "test suite", "type": "run", "run": "cargo test", "timeout": 120, "points": 9 }
]
```

Partial credit: `cargo test test_add -- --exact` per test. Timeout on `cargo test` = compile happened inside it; keep the separate build test first.

### Node and Go (same pattern)

`{"node": "20"}` + Setup command `npm ci` + `{"type": "run", "run": "npm test --silent", "timeout": 120}`. `{"go": "1.23"}` + `{"type": "run", "run": "go test ./...", "timeout": 180}`; partial credit with `go test -run '^TestAdd$' ./...`.

### Hidden script, any language

```json
{ "name": "adds correctly", "type": "run", "run": "bash \"$CLASSROOM50_BUNDLE_DIR/check.sh\"",
  "failure-details": "actual-only", "points": 5 }
```

### Bring your own CI

- Grade entirely outside Classroom 50: **Do not use the built-in autograder**; the template's own workflows run; collection records who submitted, no scores.
- Keep GitHub Classroom `autograding.json`: custom caller, section 4.7.

---

## 14. Gotchas checklist

- Public student repo = no grading ("workflow was not found").
- `CLASSROOM50_BUNDLE_DIR` or nothing: bundle files are never in the checkout.
- Bundle and `assignments.json` are publicly downloadable from Pages; hidden != secret.
- Unlisted classroom: Pages paths include `CLASSROOM/SECRET/`; bare `CLASSROOM/` URLs 404.
- Committed `tests.json` in the bundle dir breaks grading when the assignment has no tests.
- Per-assignment `autograder.py` silently replaces declarative tests.
- Commands run under `/bin/sh`, not bash; each in a fresh process from the checkout root.
- `io` tests ignore the exit code; `exact` trims only the ends; `included` is case-sensitive; regex needs JSON-escaped backslashes.
- `python` tests append pytest flags to the end of `run`; skipped cases cost points; a venv without `pytest-json-report` means all-or-nothing.
- io test without `input` gets empty stdin.
- Points default 0 when omitted; a failing 0-point test still makes the status red.
- 15-minute grade job ceiling regardless of per-test timeouts.
- `error` outcomes publish no Release, so the student sees only a red status; prefer emitting failing test rows over crashing.
- Pages CDN lag up to about 10 minutes after any config change; test after it.
- Bundle > 10 MB fails.
- Re-running `gh teacher assignment add` drops unspecified fields (`--tests`, `--allowed-files`, `--runtime`).
- `allowed_files` must include manifests, build files, and release-asset sources.
- `submission_mode` / `submission_tags` changes need a shim retrofit and a `git pull` by students.
- Many tags pushed at once trigger nothing; `submit/a/b` does not match `submit/*`.
- Regrade grades the last graded commit, not the newest push; runs older than a month cannot be re-run; always collect afterwards.
- Immutable releases freeze collected scores on regrade.
- Template must not contain `.github/workflows/autograde.yaml`; template `.github/` overwrites student copies on each submit.
- Self-hosted runner or container must provide `bash curl python3 gh` (+ `git`).
- Container images need `user: root` unless they already run as root; images must be public; no `apt` with `container`.
- Org set up before 1.56 (or with old skeleton files): re-run `gh teacher init` and accept the workflow refresh, or features like declarative tests (`materialize_tests.py`), auto pytest install, and `no_autograder` collection misbehave.
- Rapid successive pushes to the same branch share a concurrency group (`classroom50-autograde-<ref>`, no `queue: max`); with GitHub's single pending slot a waiting run can be replaced by a newer one, so not literally every push in a burst gets a Release (inference from the workflow; the wiki says every push gets one).

---

## 15. Wiki vs code notes

| Topic | Wiki says | Code says (followed here) |
|---|---|---|
| `points` | Required | Optional, defaults to 0 (schema, setup validator, runner, CLI `--points` default 0) |
| Self-hosted cost | Self-hosted grading costs no Actions minutes | `setup` job is hard-coded `runs-on: ubuntu-latest`; ~1 hosted minute per run remains |
| Bundle URL example | `.../CLASSROOM/autograders/ASSIGNMENT.tar.gz` | Unlisted classrooms serve under `CLASSROOM/SECRET/...` |
| `result.json` `score` | "Sum of test scores" | Only `score <= max-score` enforced; sum not checked |
| Declarative shell | "shell command" | `/bin/sh -c` (dash on Ubuntu), `cmd.exe` on Windows |
| `python` test | "points split across cases" | `round(points*passed/total)`, capped at `points-1` unless all pass; flags appended to end of `run`; exit-code fallback without a report |
| Bundle size | not mentioned | 10 MB fetch ceiling |
| Regrade | re-runs latest submission | Runs older than ~1 month cannot be re-run; skipped with a warning |
| Every push gets a Release | yes | Concurrency group without `queue: max` can supersede a pending run in a burst (inference) |
| C# container recipe | `mcr.microsoft.com/dotnet/sdk:8.0` + `python` is enough | Grade job also requires `gh` and `curl` in any container ("Check runner tools" fails otherwise); stock SDK images likely lack `gh` |
| Template example README | submit re-fetches the autograde workflow | Shim set once at accept; submit re-fetches only `.gitignore` and `.github/` from the template |
