Source: Classroom 50 wiki at 4d79ad48 (2026-10-21), pages Troubleshooting and FAQ. Paraphrased; error strings are verbatim.

# Classroom 50 troubleshooting

Search this file for the exact error text, badge, or HTTP status. Each entry has **Symptom**, **Cause**, **Fix**. Placeholders: `ORG` (organization), `CLASSROOM` and `ASSIGNMENT` (slugs), and the example names `cs50-fall-2026` / `cs-principles` / `hello` that the wiki uses.

Background lives in sibling files: `concepts.md` (data model, roles, sync, protection rulesets), `teacher-web.md` (web app UI paths), `teacher-cli.md` (`gh teacher` commands), `student.md` (accept/submit), `autograding.md` (tests, runtime, submission modes, cost).

Contents:
1. First steps (verbose output, GitHub status, stalled network)
2. Sign-in and org access
3. Setup and org policy
4. Service token
5. Roster and invitations
6. Assignments and accept
7. Templates
8. Autograding runs
9. Score collection and downloads
10. Groups
11. GitHub Pages
12. Actions cost and billing
13. CLI install, auth, and build
14. Filing an issue
15. FAQ

---

## 1. First steps

### Seeing what the CLI does
- **Fix:** add `--verbose` / `-v` to any `gh teacher` or `gh student` command. It prints each REST call, its status, raw `git` output and metadata writes. For full request/response headers and bodies, prefix with `GH_DEBUG=api`, e.g. `GH_DEBUG=api gh teacher invite cs50-fall-2026 alice`. `--quiet` / `-q` silences informational output.

### Everything fails at once (accepts erroring, publishing stuck, collection failing)
- **Cause:** Classroom 50 runs entirely on GitHub; a GitHub incident looks like a Classroom 50 bug.
- **Fix:** check https://www.githubstatus.com first. API, Actions and Pages are the relevant components.

### "the network connection appears stalled"
- **Symptom:** a CLI command ends with this instead of hanging.
- **Cause:** both CLIs time-limit each network step: 60 s per GitHub API request; git clone/push/pull fail after about 30 s of zero data transfer (slow but moving transfers continue); 10 min hard limit per repository (backstop, mostly for SSH remotes).
- **Fix:**
  - `gh student submit`: check the connection, run it again. Submit is safe to repeat.
  - `gh teacher download`: the stalled repo is skipped and the rest continue; the summary and final error list failures. Re-run the same command; existing clones are skipped (or fast-forwarded with `--pull`). If one pull keeps failing, delete that clone and re-run.
  - `init`, `roster add`, `assignment add`, `accept`: re-run. They check existing state first and resume.
  - Stalls on a healthy connection: run with `-v` and include the output in an issue.

---

## 2. Sign-in and org access

### classroom50.org won't load / timeout / DNS failure / flagged as phishing
- **Cause:** some ISPs and school filters block the young domain as suspected phishing. Safari may just time out with no warning page. The site is not compromised.
- **Fix:** home users add `classroom50.org` to the ISP security exception list (e.g. AT&T ActiveArmor) or set DNS to `1.1.1.1` / `8.8.8.8`. Schools: ask IT to allow the domains listed on the wiki page GitHub-Integration, section "Network and allowed domains". To get the block lifted, open an issue at github.com/foundation50/classroom50/issues naming the ISP.

### "Couldn't reach the sign-in service. It may be down. Check your connection and try again."
- **Cause:** browser sign-in goes through a small stateless Cloudflare Worker (the GitHub proxy). The browser couldn't reach it: either offline (a separate "You appear to be offline" notice may appear) or a school/corporate filter blocks the proxy.
- **Fix:** restore connectivity, or have IT allow the domains in "Network and allowed domains", or bypass the proxy with a token: sign-in card > **Other sign-in methods** > **Use a personal access token (classic)** or **Use a personal access token (fine-grained)**.

### `redirect_uri is not associated with this application`
- **Cause:** a stale GitHub authorization replayed during sign-in, often after switching GitHub accounts.
- **Fix:** sign out of classroom50.org and sign in again, or use a private browsing window.

### My organization doesn't appear in the list
- **Cause:** GitHub only shows Classroom 50 the orgs you granted it. Owning the org or having GitHub Education doesn't change that.
- **Fix:** work through these in order:
  1. Open https://github.com/settings/connections/applications/Ov23liDFFyDtm0pO5NN5 (also linked from the "Not seeing your organization?" notice on the Classroom 50 home page) and click **Grant** next to the org.
  2. If it shows **Request access** instead, the org restricts third-party apps; an owner approves it at `https://github.com/organizations/ORG/settings/oauth_application_policy`.
  3. SAML SSO org: on the same OAuth page use **Configure SSO** to authorize the org.
  4. Pending invitation: accept it at https://github.com/settings/organizations (unaccepted invites don't count as membership).
  5. Sign out and back in. A token minted before the membership existed can't see the org.
  6. Click **Refresh** in Classroom 50. The org list is cached for 10 minutes.
- **Terminal check** (CLI token is separate from the web token, so a pass here doesn't fix the browser grant):
  ```sh
  gh auth refresh -s read:org,admin:org
  gh api user/memberships/orgs --paginate --jq '.[] | [.organization.login, .state, .role] | @tsv'
  ```
  Expect `active` (and `admin` to run setup).

### 403 / `Resource protected by organization SAML enforcement` (SSO orgs)
- **Symptom:** inviting students returns 403 even though you are an owner; or a student's accept fails with "Couldn't confirm your membership. If your organization uses single sign-on (SSO), authorize it for this org (or open this link from your LMS), then accept again."
- **Cause:** the org requires SAML SSO and the API call had no authorized SSO session.
- **Fix:** sign in to the identity provider, then github.com, and authorize SSO for the org (web app: **Configure SSO** on the Classroom 50 OAuth settings page above). Then retry the invitation or the accept link.

### Sign-in asks for access to all my repositories
- **Cause:** sign-in uses GitHub's `repo` scope, like the `gh` CLI. That scope can't be limited to one org. Classroom 50 only acts on classroom repos.
- **Fix:** nothing required. To grant less, sign in with a fine-grained token scoped to the one org (**Other sign-in methods**). Teachers and students request the same scopes on purpose (one person can hold both roles); permissions come from org/classroom role, not the token.

### Tear down asks for an extra permission and a new sign-in
- **Cause:** normal sign-in never requests repo deletion. Only **Tear down organization** (deletes every repo in the org after typed confirmation) needs it.
- **Fix:** expected. Approve the extra permission and sign in again only if you really want to tear down.

---

## 3. Setup and org policy

### "Couldn't verify the Actions spending cap" (e.g. `Read failed: 400`)
- **Cause:** setup creates a $0 GitHub Actions spending cap only if the org has none (an existing cap is never touched), then tries to read it back. The read fails when billing isn't readable by your token: enterprise-managed billing, a plan without org budgets, or a token lacking Organization Administration read.
- **Fix:** advisory only; nothing is blocked. Confirm the Actions spending limit yourself in the org's billing settings or with the enterprise/billing admin.

### Branch protection / rulesets "Fix it" does nothing; check stays red
- **Cause:** student work is protected by two org rulesets (see `concepts.md`). On an enterprise-managed org an enterprise policy can pin the setting, so the org-level change is silently ignored.
- **Fix:** only an enterprise owner can change it. The check is advisory; Classroom 50 still works.

### Setup wizard loops between steps 1 and 2 after adding the service token
- **Cause:** stale cached browser state.
- **Fix:** sign out, clear the browser cache, sign in again.

### "You have been removed from the team" emails during classroom creation
- **Cause:** teams are created with your token, which auto-adds you to each; Classroom 50 then removes you from the student, `-hta` and `-ta` teams so you keep only `-teacher`.
- **Fix:** expected; ignore.

### Students can't create discussions in a read-only repository / the setting keeps switching off
- **Cause:** older releases disabled **Allow users with read access to create discussions** during the member-privilege lockdown and reported it as drift. Current releases leave it alone. If it keeps reverting, some teacher still runs an old `gh teacher` whose `init` turns it off.
- **Fix:** org settings > **Member privileges** > check **Allow users with read access to create discussions**. Have every teacher run `gh extension upgrade gh-teacher` before anyone re-runs `init`.

### "You need admin access to the organization before adding a repository to it."
- **Symptom:** 403 when a student's repository is being created (accept).
- **Cause:** despite the text, the student does not need admin. The org forbids members from creating repos. Not a template or assignment problem, so re-running assignment setup won't help.
- **Fix:** org settings > **Member privileges** > **Repository creation**: enable it, tick **Private**, leave **Public** unticked. Then have the student accept again. Better: Classroom 50 org settings > **Re-run setup**, which re-applies the whole audited lockdown. If an enterprise policy pins repo creation, the re-run reports success but nothing changes; an enterprise owner must fix it. If creation is already enabled, check that the student accepted their org invitation and is a member, not an outside collaborator.

### `git/trees: HTTP 404` on `gh teacher init`
- **Symptom:** `init` fails with a 404 and `classroom50` ends up with only a README.
- **Cause:** workflow files are committed with the Git Data API, which needs the `workflow` scope. Without it GitHub returns a misleading 404. Whether plain `gh auth login` granted `workflow` depends on prompt choices, so it varies per machine.
- **Fix:** `gh teacher login`, or in place: `gh auth refresh -s admin:org,workflow`. Re-run `init`.

### A team "already exists but wasn't created by Classroom 50"
- **Symptom:** adding staff, creating a classroom, or `gh teacher staff add` stops with this.
- **Cause:** a team already sits at the staff name `classroom50-<classroom>-<role>` but lacks access to the `classroom50` repo (every team Classroom 50 creates has it). Since any member could have created it, Classroom 50 won't trust it.
- **Fix:** open the linked team page. If the members are your staff: team > **Repositories** > give it access to `classroom50`, retry; it is adopted. Otherwise delete the team and retry; a fresh one is created.
- **Special case:** a classroom whose slug ends in `-teacher`, `-hta` or `-ta` collides with another classroom's staff team name. With both `ml` and `ml-ta`, the message says the team "is the student team of classroom ml-ta"; `ml` can't get a TA team while `ml-ta` exists. Leave the role unstaffed or rename one classroom. New classrooms can't take such pair names; existing ones keep working.

### Can I edit files in the `classroom50` repo by hand?
- Not recommended: some state is derived from both the files and live GitHub state, and hand edits create states the tools can't handle. Use the web app or `gh teacher`. The one documented exception is a score override in `scores.json` (see section 9).

---

## 4. Service token

The service token is one fine-grained PAT per org, stored as a secret (`CLASSROOM50_SERVICE_TOKEN`) in the `classroom50` repo. Score collection, regrade and the token-probe workflow use it. Web app and CLI share the same token.

### Required token shape (use when any collection error mentions 401/403/404 or 0 submissions)
- **Repository access:** **All repositories** (not **Only select repositories**: student repos are created on demand and would be out of scope).
- **Repository permissions, Read and write:** **Contents**, **Actions**, **Workflows**, **Administration**.
- **Organization permissions:** **Members**: **Read**.

### Checking or replacing the token
- **Fix:** web app: org **Settings** > **Service token** > **Test token** checks every needed permission. CLI: `gh teacher rotate-service-token cs50-fall-2026` re-scopes and rotates.

### `401` / `403` in the collect-scores log
- **Cause:** bad or expired token, or missing **Members: Read**, unless the log explicitly names a throttle.
- **Fix:** rotate as above. Do not rotate when the log says "collection was throttled by GitHub" or "GitHub is throttling, not refusing" (see section 9).

### Fine-grained PAT returns 404 for student repos
- **Cause:** a repo outside the token's scope returns 404, which looks the same as "no release yet". Produces the "collected 0 submissions" warning.
- **Fix:** set **Repository access** to **All repositories**.

### Setup wizard won't advance after adding the token
- See section 3, "Setup wizard loops between steps 1 and 2".

---

## 5. Roster and invitations

Org membership and classroom enrollment are separate. An invitation only makes someone an org member; enrollment puts them on the roster and classroom team. See `concepts.md`.

### "missing admin:org OAuth scope; run gh teacher login to grant it"
- **Cause:** org invitations need `admin:org`, which plain `gh auth login` doesn't grant.
- **Fix:** `gh teacher login`. The CLI normally widens a `gh`-managed token in place before the request, so this is rare (it does show for under-scoped `GH_TOKEN`; see section 13).

### "you must be an admin of ... to invite members"
- **Cause:** `POST /orgs/{org}/invitations` requires org **Owner**. Admin through a team isn't enough.
- **Fix:** check `https://github.com/orgs/ORG/people`; you must show **Owner**. Have an owner promote you or send the invites.

### "already a member" / "already has a pending invitation" / `already a member of the org`
- **Cause:** the target state already exists. Behavior differs by command:
  - `gh teacher roster add` and `roster import`: report it, exit 0 (safe in scripts).
  - `gh teacher roster invite`: if GitHub already lists the address as member or invited, prints `skipped` and suggests `roster sync` (they may have accepted earlier). If this classroom's roster already has a pending row for the address, exits non-zero to avoid a duplicate row.
  - Repo invitation `gh teacher invite cs50-fall-2026/hello alice`: idempotent, updates permission in place.
  - Org invitation `gh teacher invite cs50-fall-2026 alice`: exits non-zero; GitHub rejects re-inviting a pending or existing member. Use `roster add` for a re-runnable path.

### "Already a member or already invited, so no new invitation was sent." (student already in org, not on roster)
- **Cause:** typically a student from an earlier course. GitHub won't invite an existing member, and inviting doesn't enroll.
- **Fix (web):** org **Members** page (not the classroom **Roster** page) > filter **No classroom** > select rows > **Actions** > **Add to classroom** > pick classroom > **Add** (dialog previews the count).
- **Fix (CLI):** `gh teacher roster add cs50-fall-2026 cs-principles alice` (or `roster import`).
- Uploading a roster CSV or username list on the **Roster** page also enrolls existing members (invite skipped, enrollment done). Rows identified only by email or only by name can't be matched to an existing member and stay as **Unlinked** (next entry).

### Rows stuck as "Unlinked"
- **Cause:** a row with only an email (existing member, address can't be mapped to an account), only a name (SIS export before students have accounts), or an invitation that expired. Sync never deletes rows; only linking or explicit removal ends them.
- **Fix:** roster > **Unlinked** filter, then:
  - click row > **Link account** > **Link to organization member** picker. It suggests classroom members first; tick **Include organization members not in any classroom** to search everyone (e.g. a student who joined the org directly). Linking also enrolls them on the team.
  - click row > **Re-invite** if it has an email and the student isn't in the org yet.
  - select rows > **Actions** > **Remove rows** to delete.
- **Note:** keep `gh teacher` current if you use both tools. Old releases error on name-only rows in `roster list`, and their `roster sync --write` still auto-deletes email rows nothing backs. Deleted rows can be recovered from the `classroom50` repo's commit history.

### "Invitation expired" badge
- **Symptom:** badge next to **Unlinked** (email row) or **Not in organization** (account row) on the **Roster** and **Members** pages.
- **Cause:** GitHub org invitations expire after 7 days and move to the org's failed invitations list. The row stays.
- **Fix:**
  - One student: **Roster** > click row > **Re-invite**. GitHub's failed record is cleared after the send is confirmed.
  - Several: select rows (or filter **Invitation expired** and select all) > **Actions** > **Send invitations (N)**. N is how many of the selection are invitable.
  - Whole class: upload the roster file again. Expired addresses show **Resend invitation (expired)** in the preview and are re-sent; live invitations are skipped.
  - CLI: `gh teacher roster invite ORG CLASSROOM EMAIL` (or `--file LIST`). Re-sends against the same row and dismisses the expired record. An address with a still-open invitation, or accepted but not yet synced, is refused with the reason (with `--file` it's skipped and the rest continue).
  - Drop instead of re-invite: `gh teacher roster remove ORG CLASSROOM EMAIL` (removes only when GitHub confirms nothing backs the row; also clears the leftover metadata team and expired record).

### "failed invitation that isn't on any roster" (Members page)
- **Cause:** the invitation failed and its roster row was already removed.
- **Fix:** it can't be re-invited from there. Add the student to a roster again (upload or **Add to classroom**) and click **Dismiss** on the leftover record.

### **Re-invite** says nothing was sent: GitHub already has a live invitation or member
- **Cause:** the student was invited from another classroom in the same org, or already joined.
- **Fix:** check the org's **People** page on GitHub; link the row to that member once they accept.

### Re-invite / invite hits GitHub's daily invitation limit
- **Cause:** 50 invitations/day for orgs under a month old or on the free plan; otherwise 500/day.
- **Fix:** wait until the next day and retry.

### "Couldn't prepare the invite … so no invite was sent"
- **Cause:** before emailing, Classroom 50 creates a `secret` invite team to hold the address. That step failed, so nothing was sent and nothing written; nothing to cancel.
- **Fix:** if the message mentions a rate limit or server error, wait and invite again. If it repeats, it's a deliberate refusal: a same-named team exists that can't be made `secret`, or one still has a member from an interrupted run. The message names the team; delete it on github.com and invite again. Bulk email uploads report the same failure per address in the **failed** list; `gh teacher roster invite` refuses for the same reasons.

### Student accepted an email invitation but the roster still shows the address
- **Cause:** GitHub doesn't notify Classroom 50 on acceptance and stops listing the invited address, so matching account to pending row needs a sync.
- **Fix:** open the classroom roster in the web app (runs a sync), or:
  ```sh
  gh teacher roster sync cs50-fall-2026 cs-principles          # dry run
  gh teacher roster sync cs50-fall-2026 cs-principles --write  # apply
  ```
  The sync writes username and `github_id` onto the row, keeps name and section, deletes the invite team. Idempotent. Don't use `roster cancel-invite` here; an accepted invitation isn't pending, so it changes nothing.

### `gh teacher roster cancel-invite` refuses and cancels nothing
- **Cause:** org invitations are org-wide, so it first proves the invitation belongs to this classroom. Refusals (non-zero exit, invitation untouched):
  1. No metadata team for the address: another classroom sent it, or the team was deleted by hand.
  2. Metadata team with no invite record: leftover from an interrupted send (the record is written last).
  3. Metadata team naming a different classroom: re-run with that classroom (the message names it).
  4. Invitation carries none of this classroom's teams: two classrooms invited the same address; cancel in the sibling.
- **Fix for 1 and 2:** revoke from the web roster or `https://github.com/orgs/ORG/people/pending_invitations`, then delete any leftover `invite-…` team by hand. `roster sync` won't collect a record-less team either.
- **Not a refusal:** "no pending invitation" exits 0, because an accepted invite looks the same. Run `roster sync … --write`. If it expired, run `roster invite` again; to drop the row, `roster remove`.

### `gh teacher roster sync` exits 1: "sync was incomplete"
- **Cause:** a read degraded (GitHub's pending-invitation list or an invite team). The pass removed nothing, by design: an unreadable invite team can't prove a row dead, and wrong removal loses the only record of the address. stderr warnings name what failed.
- **Fix:** re-run once GitHub is healthy or the rate-limit window resets. In scripts: exit `1` = retry later, exit `2` = dry run found pending changes.

### `invite-…` teams you didn't create
- **Cause:** each email invitation gets a `secret` team `invite-<hash>` holding the address until the person joins. Normal while invitations are outstanding. Removed after accept/cancel; expired ones cleared on a later sync.
- **Fix (clear early):** classroom **Settings** > **Clean up invite data** (saves anything recoverable onto the roster first). CLI `roster sync … --write` deletes a narrower set: older than 24 h, no members, no pending invitation; or whose only member is no longer on any classroom team. `gh teacher teardown` deletes all of them org-wide. A team described `classroom50: preparing invite` is an interrupted send, holds no address, and is safe to delete.
- **Teams sync leaves standing (named on stderr):** stored address no longer hashes to the team name (invitee edited the description); more than one member; description not a readable invite record. Investigate, then delete by hand.
- **Warning:** deleting an invite team while its invitation is still pending permanently breaks the account-to-address link; the student joins but the row stays unlinked and must be linked or deleted manually.

### `line N: row has no username, github_id, or email` (`gh teacher roster import`)
- **Cause:** a row with all three identity cells blank: an empty row, a leftover from another export, or a name-only row (the CLI can't address it; the web **Upload roster** keeps such rows as unlinked).
- **Fix:** fill an identity cell or delete the row and re-run. All bad lines are reported in one pass and nothing is committed.
- **Notes:** columns match by header name in any order or case; unknown columns are ignored; one identity column is enough, so SIS and web-app exports import as-is. A `github_id` cell counts as present even if unusable; such a row is skipped with a notice. Usable id: plain positive digits, at most 9007199254740991; leading zeros are tolerated and stripped; a leading `+` or `-` is unresolved. Only a non-numeric cell fails the line outright. A row identified solely by `github_id` is skipped (import resolves by username); its notice points at the web **Upload roster**. Pending email rows get name/section updates only; the invitation is never sent or cancelled.

### `github_id … is not this account's id` (`gh teacher roster import`)
- **Cause:** the row names a username and an id belonging to a different account. The message shows both ids. Usually Excel mangled the id (`583231` became `5.83231E+05`), columns shifted by one, or a student renamed their account and the username was retyped by hand.
- **Fix:** correct the username, or clear the `github_id` cell (the CLI re-resolves ids from GitHub anyway). Nothing was committed, so re-run freely.

### Web **Upload roster** says a row can't be imported
- **Cause:** the upload validates every row first; any unusable value blocks the whole import, because it usually means a shifted column, a foreign export, or the wrong format chosen above the preview. Each report line names the file line and value.
- **Fix:** fix the listed lines and re-upload. Re-uploading is safe; existing students aren't duplicated.
- **Not blocking:** a row with no `github_id`, username, email or name is reported but skipped; a name-only row is imported as unlinked. A one-column file's first line that is a column name (`username`, `email`, `github_id`, …) is treated as a header; any other bad first line is reported like other rows.

### Upload: a row's `github_id` doesn't match an account
- **Cause:** the upload treats `github_id` as identity (so renamed students are still found). An id matching no account stops the upload; it won't fall back to the username, since a wrong id plus stale username could invite a stranger. Usually Excel number formatting.
- **Fix:** re-export without reformatting the column, or delete the `github_id` column and let `username` identify rows.
- "GitHub couldn't be reached to look up the id": rate limit or transient error; the file is fine, wait and upload again.
- "too many `github_id` values to check at once": retrying won't help. Delete the `github_id` column or split the file. Only happens with large rosters of non-members (members' ids are checked for free).
- Id correct but username stale: not blocked. The preview shows both, asks to confirm, and corrects the stored username.

### `line N: a cell contains a line break, usually from an unmatched quote`
- **Command:** `roster add`, `roster sync --write`, `roster invite` (anything that rewrites `roster.csv`).
- **Cause:** an unclosed `"` on that line (usually a hand edit) would swallow every later line, deleting those students on rewrite.
- **Fix:** close or remove the quote on line N of `roster.csv`, re-run. Nothing was committed.

### `line N: malformed row has X fields, the same as or one short of the rewritten N-column header` / `would be read back as a valid row`
- **Cause:** the row's cell count doesn't match its header; after the rewrite its cells would shift under wrong columns (a name under `email`) and look valid.
- **Fix:** add/remove cells so the row matches the header, or delete the row; re-run.

### A pending row shows a `github_id` that can't be an account
- **Cause:** values `0`, negative, larger than 9007199254740991, or with a leading `+` are not identities; the row still counts as "invited, not yet joined".
- **Fix:** nothing. On accept, sync overwrites the cell with the real id and username. If the invitation is gone with nothing backing it, the row becomes unlinked (link or delete). Web app and `roster sync --write` read the cell identically.

### A student's `role` flipped to `teacher` after `roster add`
- **Cause:** the account is on both a staff team and the student team (often a teacher enrolling themselves). GitHub teams, not the `role` column, decide enrollment; the web app's automatic sync writes the highest role (`teacher > hta > ta > student`), with a commit like `[Classroom 50] Sync roster from teams: <classroom>`. `gh teacher roster sync` doesn't refresh this column.
- **Fix:** nothing breaks; the account is still enrolled and graded as a student and shows both badges. `roster add` prints a note when the target is staff. For a pure student test, use a separate GitHub account.

### TAs don't see students invited by email
- **Cause:** GitHub shows pending invitations to org owners only.
- **Fix:** expected; they appear for TAs once the student accepts and a sync runs.

---

## 6. Assignments and accept

### Quick table: `gh student accept` messages

| Message | Meaning / fix |
| --- | --- |
| "the classroom may not exist yet, or its publish-pages workflow may not have run" | Setup unfinished or Pages not deployed. Wait a few minutes; teacher checks Actions in `ORG/classroom50`. |
| "assignment X is not registered" | Typo, or the teacher hasn't created it. Slug spelling must be exact (case is normalized). |
| "autograder `<name>` not published yet" / "is malformed YAML" | See section 8. |
| "template `<owner>/<repo>` is not accessible to you" | Private template not shared with the student. See section 7. |
| "assignment `<X>` has unsupported mode `<mode>`" | Manifest `mode` isn't `individual`, `group` or `team`; likely hand-edited. Teacher fixes it. |
| "assignment `<X>` is locked by your teacher" | Teacher locked it (e.g. before a timed exam). Wait for unlock. |
| "assignment `<X>` is closed to new submissions" | Teacher used **Close submission**. Ask them to reopen. |
| "the repository name … is over GitHub's 100-character limit" | See below. |
| "Assignment already accepted" | Not an error. See below. |

### "Assignment already accepted"
- **Cause:** the repo `ORG/<classroom>-<assignment>-<username>` already exists. The CLI stops to protect the work, which is untouched.
- **Fix:** clone it (get the URL from `gh repo view ORG/<classroom>-<assignment>-<username>`).

### "the repository name `<name>` is … characters, over GitHub's 100-character limit, so it couldn't be created."
- **Symptom:** CLI accept or web accept page.
- **Cause:** repo name `<classroom>-<assignment>-<username>` exceeds 100 chars. New classrooms/assignments are prevented from this, but older assignments can exceed it for long usernames.
- **Fix:** the student can't fix it. Teacher renames the assignment slug once (web: "Updating an over-budget assignment slug" in the teacher guide; CLI: `gh teacher assignment rename`), then the student accepts again.

### Accept page loads forever, or "…isn't published yet. Ask your teacher to confirm the file exists in the classroom50 repository and that the publish workflow has run."
- **Cause:** assignment data reaches students via GitHub Pages; each change takes at least ~20 s to deploy, longer if Actions is queued.
- **Fix:** (1) wait a minute, reload the link; (2) teacher checks that the publish workflow succeeded under **Actions** in `ORG/classroom50`; (3) student confirms they accepted the org invitation (unaccepted invites also block accept).

### "Couldn't load the classroom's assignments" (accept page, lists URLs tried)
- See section 11 (custom Pages domain or a network filter).

### "You need admin access to the organization before adding a repository to it."
- See section 3 (member repository creation disabled).

### "Couldn't confirm your membership. If your organization uses single sign-on (SSO)…"
- See section 2 (SAML SSO).

### Students can't join with just a link
- **Cause:** GitHub requires an org owner to invite members; there is no self-join.
- **Fix:** add them to the roster (username, email, or CSV), which sends the invitation. Once they've joined the org, accept links work with no further teacher action.

### Due date passed but students can still push
- **Cause:** due dates (date and time, teacher's timezone) only mark later submissions late. There is no cutoff.
- **Fix:** to actually stop work, use **Close submission**: blocks new accepts and makes every student repo read-only.

### Changed the repository shape (README / empty / autograder) but existing repos didn't change
- **Cause:** shape changes apply only to repos accepted afterwards; existing repos aren't retrofitted. The web form warns when students already accepted. **Assignment type** (Individual / Group / Group (legacy)) can't be changed at all after creation.
- **Fix:** expected. For existing repos, change them manually or recreate the assignment. Shapes: template-less with README (initial commit + autograder); empty repository (**Add a README** off and built-in autograder off: no commit, no autograding, no feedback PR ever); README off with autograder on (control files only, grades normally).

### Where students see the assignment description
- The accept page shows it under **Assignment details** (Markdown). Long instructions belong in the template's `README.md`.

---

## 7. Templates

### `template `<owner>/<repo>` has no commits: add at least one commit (a README is enough) so students can generate from it, then re-run`
- **Command:** `gh teacher assignment add`.
- **Cause:** GitHub can't generate a repo from an empty template.
- **Fix:** push at least one commit (a README is enough), re-run. If the template does have commits and the error persists, upgrade the CLI; old releases trusted GitHub's asynchronously computed size field, which reads 0 for freshly pushed repos.

### "Template not found" / 404 / "template `<owner>/<repo>` is not accessible to you" on accept
- **Cause and fix, in order:**
  1. Student can't read the template. Public always works. A private template must be inside the classroom org (registering grants the classroom team read access). A private template outside the org can't be shared; re-add the assignment with an in-org copy or a public template. If one student still 404s, check they're on the roster (hence on the team).
  2. Repo isn't flagged as a template: template repo **Settings** > tick **Template repository**.
  3. The assignment argument doesn't match the registered slug (case is normalized, spelling isn't).
- A private template added to an existing assignment can also 404; see `teacher-web.md` / the wiki "Template visibility".

### `couldn't copy the template `<owner>/<repo>`: it is a fork of a repository in the `<upstream-org>` organization, and copying a fork is governed by that organization's third-party app restrictions`
- **Symptom:** GitHub's raw 403 says the upstream "organization has enabled OAuth App access restrictions"; web shows "Couldn't copy the template".
- **Cause:** the template is a fork; GitHub applies the upstream org's app restrictions when copying a fork. Approving Classroom 50 in your own org can't help.
- **Fix:** preferred: import the repo into your org as a fresh non-fork repo, tick **Template repository**, re-add the assignment. Alternative: an owner of the upstream org approves the Classroom 50 app there.

### Reusing GitHub Classroom starter repos exposes previous students' work
- **Symptom:** warning from the assignment form or `gh teacher assignment add` (also on unlock and reuse) that a private template has forks.
- **Cause:** since 2024 GitHub Classroom creates student repos as forks of the starter, and a private fork inherits its upstream's team permissions. Granting the classroom team read on the starter lets every student read every old fork.
- **Fix:** create a new repo, copy the starter's contents, tick **Template repository**, register the copy. If already registered: first switch the assignment to the fork-free copy, then remove the forks from the classroom team (org **Teams** > team > **Repositories** > select forks > **Remove from team**). Order matters: removing the team from the template leaves grants on the forks (so locking doesn't help), and re-adding the team to the template (unlock, re-save, "Fix template access") re-grants every fork.

### Feedback PR body ignores my `pull_request_template.md`
- **Cause:** GitHub only applies PR templates in the web compare flow, never to the API-created feedback PR.
- **Fix:** web assignment form: enable **Use the template's pull request template as the Feedback PR body** (auto-ticked when a file is detected at `.github/pull_request_template.md`, `pull_request_template.md` or `docs/pull_request_template.md`). Templated assignments only; no `gh teacher` flag. Missing/unreadable file falls back to the built-in body.

---

## 8. Autograding runs

### "push not graded; run gh student submit" (`classroom50/autograde-skipped` status) / push triggers no workflow run
- **Cause:** the assignment is submit-only (`submission_mode: tag`, web **Submission type: A tagged commit**). Plain pushes are deliberately not graded and cost no Actions minutes. Graded commits report under `classroom50/autograde`; a skipped commit never shows green there. No run at all on a push is also normal in tag mode.
- **Fix:** `gh student submit` (pushes a `submit/…` tag), or tag manually: `git tag submit/final && git push origin submit/final`. Any `submit/*` tag grades, plus teacher-named milestone tags (e.g. `git tag phase1 && git push origin phase1`).

### "tag is not a submission trigger"
- **Cause:** the pushed tag matches neither `submit/*` nor a configured milestone tag (milestones are case-sensitive).
- **Fix (student):** confirm milestone names with the teacher, or use `gh student submit` / a `submit/*` tag.
- **Fix (teacher, when you expected push grading):** the repo's workflow is on the wrong trigger for the assignment's mode. Run `gh teacher assignment submission-mode cs50-fall-2026 cs-principles hello --tag` (or `--every-push`), or web submissions page > **Update autograding triggers**. Students then `git pull`.

### `Invalid workflow file` … `error parsing called workflow ... workflow was not found`
- **Symptom:** run fails before any job starts, right after the student repo became public; earlier runs (while private) passed.
- **Cause:** each student repo's `autograde.yaml` calls the grading workflow in the private `classroom50` repo, and GitHub lets public repos call only public workflows. `classroom50` stays private because it holds the roster. Public repos are not autograded.
- **Fix:** web submissions page: one repo: row's manage dialog > **Make repository private**; all repos: **Change repository visibility** > **Private** > **Apply to all**. Then fix future accepts: edit the assignment, set **Repository visibility** to **Private** (CLI: re-run `gh teacher assignment add … --repo-visibility private`). Make repos public only after grading, or combine **Public** with **Do not use the built-in autograder**. On GitHub Free for organizations, making a repo private also takes its Pages site offline.

### `pytest: not found` / exit code 127 in the grading log
- **Cause:** 127 = command not found. The built-in autograder now installs `pytest` and `pytest-json-report`; failures mean old workflow files or a custom setup command that replaced the Python environment.
- **Fix:** refresh workflow files with `gh teacher init cs50-fall-2026` and accept the refresh prompt (or the web update banner). With a custom setup command, install what the tests import there (see `autograding.md`, Python recipe).

### `gh: command not found` / "Check runner tools" fails (self-hosted runner or custom container)
- **Cause:** the grade job needs `curl`, `python3` and `gh` (posts the commit status and the submission Release). GitHub-hosted runners have them; self-hosted runners and custom `container` images have only what you installed. `gh` is the usual gap. Missing `git` only warns: grading runs without `allowed_files` enforcement or a review diff link.
- **Fix:** install the tools the **Check runner tools** step lists (it lists all at once), re-run. Self-hosted runners also skip managed toolchain setup, so provision assignment toolchains in the image. See `autograding.md` (runtime block, `runs-on` labels such as `["self-hosted", "gpu"]`).

### `tests.json is a bare test array` / `tests.json is not a JSON object`
- **Symptom:** every submission ends as an error; **Grade details** complains about the bundled `tests.json`.
- **Cause:** someone committed `tests.json` to `CLASSROOM/autograders/ASSIGNMENT/` in `classroom50` (often copied from the wiki's `--tests` example). That folder is for fixtures and scripts; Publish Pages generates `tests.json` from tests stored on the assignment.
- **Fix:** (1) delete `CLASSROOM/autograders/ASSIGNMENT/tests.json`, push; (2) put the tests on the assignment: web **Autograding tests** section, `gh teacher assignment test add …` for one, or `gh teacher assignment test set ORG CLASSROOM ASSIGNMENT --tests FILE` (accepts bare array or envelope, so the deleted file works); (3) wait for **Publish Pages**, submit as a test student.
- **Related warning:** `replaced by the tests stored on the assignment` in the publish log: grading works, but delete the committed file anyway.

### `bash: check.sh: No such file or directory` (script in `CLASSROOM/autograders/ASSIGNMENT/`)
- **Cause:** test commands run in the student's checkout; bundle files aren't copied there. Only `input-file` and `expected-file` are read from the bundle automatically.
- **Fix:** reference files through `CLASSROOM50_BUNDLE_DIR`:
  ```sh
  gh teacher assignment test add ORG CLASSROOM ASSIGNMENT \
      --name "hidden checks" --type run \
      --run 'bash "$CLASSROOM50_BUNDLE_DIR/check.sh"' --points 5
  ```
  Web: **Run command** = `bash "$CLASSROOM50_BUNDLE_DIR/check.sh"`. Windows runners: `%CLASSROOM50_BUNDLE_DIR%`.

### "autograder `<name>` not published yet" (`gh student accept`)
- **Cause:** (1) for a non-default `--autograder <name>`, `<classroom>/autograders/<name>.yaml` doesn't exist in `classroom50`; (2) `publish-pages.yaml` hasn't run yet for a fresh classroom.
- **Fix:** teacher confirms the file exists; otherwise wait a minute for the first Pages deploy and retry.

### "autograder `<name>` is malformed YAML"
- **Cause:** syntax error in the autograder workflow. `gh student` validates before writing, so nothing broken lands in the student repo.
- **Fix:** teacher fixes the YAML in `classroom50`.

### Submitted but nothing graded / teacher sees no new work
- **Cause/fix:** `submit` pushes to the repo's real default branch (`main` or `master`), which autograding watches. Confirm the push landed on the default branch and that the autograde workflow ran under the repo's **Actions** tab. Also check tag mode (above), paused autograding (section 12), and that the assignment is autograded at all (**Grading: Manual** / **Not graded**, or a template with its own workflow, records no built-in score).

### `.classroom50.yaml not found in this clone, and ...` (`gh student submit`)
- **Cause:** `submit` identifies the assignment from `.classroom50.yaml`; without it, it falls back to the repo name plus the published assignment list. The suffix says why that failed:
  - `doesn't start with any published classroom's short name`: not an assignment clone (wrong directory; `cd` into the folder `git clone` created) or the classroom site isn't published yet.
  - `uses an unlisted URL`: protected classroom; run `gh student submit --key <key>` with the teacher's access key.
  - `has no assignment list under the access key you passed`: wrong key, or the classroom doesn't need one. Check the key or drop `--key`.
  - `matches more than one published assignment`: two classroom+assignment names produce the same prefix; ask the teacher which applies.
  - `doesn't match any assignment published for classroom`: repo made by hand or assignment unpublished. Commit and `git push` directly, or ask the teacher.
- Empty-repository assignments and those without the built-in autograder never have the marker; the fallback exists for them, and `submit` leaves their `.gitignore` and `.github/` alone.

### `this repository was updated by your teacher (it now carries .classroom50.yaml)` (`gh student submit`)
- **Cause:** the teacher enabled the built-in autograder after the student cloned; GitHub has the new files, the clone doesn't, and submitting would delete them.
- **Fix:** `git pull`, then `gh student submit`.

### "Merging is blocked" on a feedback pull request
- **Cause:** the `feedback` branch is locked by ruleset `classroom50-feedback-base-lock` so students can't merge or move it. Org owners and the classroom's teacher, head TA and TA teams are exempt.
- **Fix by what you see:**
  - Owner sees a "Merge without waiting for requirements to be met" checkbox: ruleset from an older release. Re-run `gh teacher init` or web org settings > rulesets check > **Fix it** (the checkbox works meanwhile). If it returns, a co-teacher's old `gh teacher` reinstalled it; everyone runs `gh extension upgrade gh-teacher`.
  - TA/head TA sees no merge button: staff get write on student repos from the score-collection workflow, not at accept. Click **Collect now** (or wait for the scheduled run), reload the PR.
  - TA/head TA sees merging blocked: their staff team isn't on the exemption list (classroom predates the feature). Teacher clicks **Fix it** on the rulesets check or re-runs `gh teacher init`. A hand-made team at a staff name is never added (section 3).

### Students see why tests failed?
- Yes by default: each submission's Release and the Actions run summary show per-test details (expected vs actual for `io`, captured output for `run`/`python`), unless the assignment's failure-details setting limits it. A custom `autograder.py` can add messages to `result.json`.

---

## 9. Score collection and downloads

### `collect-scores` warns "collected 0 submissions"
- **Cause:** almost always the service token can't read student repos (fine-grained PAT 404s look like "no release"). Less often there really is nothing: autograding paused, or a tag-mode assignment nobody submitted to.
- **Fix:** verify the token shape (section 4), **Test token**, or `gh teacher rotate-service-token cs50-fall-2026`. The warning is suppressed when the run saw pushes not yet graded (token clearly works; the autograder is behind; see "The collection run failed.").

### "collection was throttled by GitHub (HTTP `<code>`, `<reason>`)"
- **Cause:** GitHub's rate limiter, reported as such, not a token fault. Fatal so incomplete scores never report success.
- **Fix:** don't rotate the token. Wait for the rate-limit window, run collection again.

### "GitHub is throttling, not refusing" … deferred repositories "are granted by the next run"
- **Cause:** a staff-access grant was throttled. The run doesn't fail.
- **Fix:** nothing; the next run grants the rest.

### "The collection run failed."
- **Symptom:** banner on the submissions page.
- **Cause:** the latest `collect-scores.yaml` run failed outright. Most often an expired or under-scoped service token.
- **Fix:** open the failed run under **Actions** in `ORG/classroom50`; the log names the cause. Token: section 4. Throttle: wait and rerun.

### `collect-scores` says "no staff access was granted"
- **Cause by level:**
  - **notice:** no staff team exists at all. Solo teachers ignore it; it stops after adding a TA (roster page or `gh teacher staff add cs50-fall-2026 cs-principles carol --role ta`).
  - **warning:** a staff team exists but is empty, or a team named in `classroom.json` is missing/unreadable. Check TA roles on the roster page, collect again.
  - **warning that `classroom.json` records another team:** `teams.<role>` names a team Classroom 50 didn't create. Collection still grants `classroom50-<classroom>-<role>`. Fix the record with `gh teacher staff add ORG CLASSROOM <any-current-member> --role <role>`.
  - **warning that a team "was not created by Classroom 50":** a team at the staff name lacks access to `classroom50` (hand-made, or the student team of a classroom whose slug ends in that role). It gets nothing. If it's yours, team page > **Repositories** > grant `classroom50` access; otherwise delete it and let Classroom 50 recreate it when you next add staff.

### Student submitted but no score shows
- **Cause and fix:**
  - Not collected yet: submissions page > **Collect now** (scoped to the viewed assignment, so fast).
  - Pages still deploying after a config change: wait a few minutes.
  - Tag-mode assignment: the student must `gh student submit` or push a `submit/*` tag.
  - Not autograded: **Grading** is **Manual** / **Not graded**, or the template ships its own grading workflow.
  - Token or collection failure: entries above.

### Score marked **Unverified**
- **Cause:** a Release the student created, or a replaced `result.json`, is collected but flagged (with the publisher's name) in the submissions page and exports, and collection warns. Note the limit: code running inside the grading job (the workflow, an extra workflow the student adds, or student code during tests) can publish a forged score under the trusted identity; that leaves an Actions run, so it's detectable, not prevented.
- **Fix:** inspect the student repo's **Actions** history. For a final score students can't influence: close the assignment, download repos, run the tests yourself.

### Manually override a score
- Submissions page > row score cell > **Add score** / **Edit score** / **Override score**. Manual assignments: score out of **Max points**. Autograded: override is kept separately, shows a **Manual** badge, autograding won't change it; **Clear override** restores the autograded score. If not yet autograded, the dialog asks for max points. Owners only. Stored in `scores.json` as an entry with `"override": true`, which collection leaves alone (the one sanctioned hand edit).

### `gh teacher download` clones nothing
- **Cause:** download is team-driven by default.
- **Fix:** confirm `ORG/classroom50` exists and the classroom team has members (`gh teacher roster add` / `import`); confirm the assignment is registered (`gh teacher assignment list`); check repos exist at `https://github.com/orgs/ORG/repositories?q=CLASSROOM-ASSIGNMENT`; re-run with `-v` to see probed members. If `classroom50` isn't bootstrapped, or to grab every matching repo regardless of roster, add `--by-pattern`.

### Exporting scores / bulk download
- Submissions page **Actions** menu: **Download scores (CSV)**; **Download all submissions** (zip of latest submissions, built in the browser). Real clones: `gh teacher download` (also writes `scores.csv` at the destination; **Clone all submissions** gives the ready command). Raw data: `scores.json` in `classroom50`.

### Students can't see scores in the web app
- **Cause:** not supported yet (no server; browsers can't read Release assets cross-origin; issue #567).
- **Fix:** students open their repo's **Releases** page (the **View score** link) or the feedback PR.

---

## 10. Groups

### Student can't accept a group assignment ("Teacher assigns groups")
- **Cause:** with teacher-assigned groups, a student not placed in a group can't accept.
- **Fix:** add them on the assignment's **Manage groups** page or with `gh teacher team`.

### "assignment `<X>` has unsupported mode `<mode>`"
- **Cause:** manifest `mode` isn't `individual`, `group` or `team`; usually a hand edit of `classroom50`.
- **Fix:** teacher corrects it through the web app or CLI rather than by hand.

### Renamed a group but the repo name didn't change
- **Cause:** group repos are `<classroom>-<assignment>-group-<n>`; the display name is independent.
- **Fix:** expected. Legacy groups (**Group (legacy)**) have no names, their repo is named after the first accepter's username, and renaming a legacy group repo isn't recommended.

### Group members' scores
- Current groups: every rostered member of the group team gets the same score. Legacy: every rostered collaborator gets the same score. A member not on the roster gets no score.

### Need to switch an assignment between Individual and Group
- **Cause:** **Assignment type** is locked after creation (changing it would invalidate submissions).
- **Fix:** create a new assignment.

---

## 11. GitHub Pages

Assignment metadata and autograder bundles reach students through the org's Pages site, built by `publish-pages.yaml` in `classroom50`. Every publish deploys the whole site, so the next successful one includes all earlier changes.

### "Publishing … to the student site: failed" with `due to in progress deployment`
- **Symptom:** red banner after creating/editing a classroom or assignment; build passed, deploy step logged `Failed to create deployment (status: 400) … Deployment request failed for <sha> due to in progress deployment. Please cancel <other sha> first or wait for it to complete.`
- **Cause:** Pages deploys one version at a time and still considers an earlier publish in progress (slow deploy or cancelled run). Your change is saved in `classroom50`; nothing is misconfigured. Clears by itself within ~10 minutes.
- **Fix (web banner):** **Wait, then Retry** (row changes to "the earlier publish has finished"; **Retry** re-runs only the failed deploy step), or **Cancel the stuck publish and retry** (needs Pages write, which the standard teacher sign-in has).
- **Fix (CLI):**
  ```sh
  gh api -X POST repos/ORG/classroom50/pages/deployments/OTHER-SHA/cancel
  gh run rerun RUN-ID --failed -R ORG/classroom50
  ```
- Creating a new classroom doesn't help; the lock is on the shared `classroom50` repo.

### Publish shows "included in a newer publish"
- **Cause:** GitHub cancelled it in favor of a newer run that published the same change.
- **Fix:** none needed. Updating the org's workflow files (the update banner) makes publishes queue instead of cancel.

### "Couldn't load the classroom's assignments" (accept page error card)
- **Cause:** the student's browser couldn't fetch published assignment data. (1) The org's Pages site uses a custom domain, so `github.io` requests redirect and the browser rejects it. (2) A network filter on the student side blocks the Pages host.
- **Fix:** (1) classroom **Settings** > **Custom Pages domain** (see `teacher-web.md`). (2) Have the student screenshot the card (it lists exact URLs) and check them against the allowed-domains list.

### "Couldn't reach the classroom's custom Pages domain"
- **Cause:** the custom domain set in classroom settings is mistyped or offline. Students aren't locked out; the app falls back to the `github.io` address.
- **Fix:** verify the domain in classroom **Settings**.

### Accept page "isn't published yet" / freshly changed data not visible
- See section 6. Pages needs at least ~20 s per change, more if Actions is queued.

### Student repo's own Pages site went offline
- **Cause:** on GitHub Free for organizations, making a repo private disables its Pages site.
- **Fix:** expected trade-off when making repos private for grading.

### Hidden test files readable by students
- **Cause:** files in `CLASSROOM/autograders/ASSIGNMENT/` are served by the org's public Pages site. They're fetched fresh each run so students can't edit them, but a determined student can read them.
- **Fix:** accept the limit or grade sensitive tests yourself after closing (see `autograding.md`).

---

## 12. Actions cost and billing

### Need a paid plan? / free org can't host a classroom
- **Cause:** Classroom 50 needs an org on **Team** or **Enterprise** (notably for Pages from a private repo).
- **Fix:** verified educators get GitHub Team free via GitHub Education (github.com/education/teachers).

### "Couldn't verify the Actions spending cap"
- See section 3. Advisory; check limits in org billing settings.

### Reducing Actions minutes / turning autograding off
- **Fix:** **Submission type: A tagged commit** (grade only on submit); **Do not use the built-in autograder** for assignments graded elsewhere; pause autograding per assignment or org-wide; self-hosted runners. Trade-offs in `autograding.md`. Remember pausing also means collection finds nothing ("collected 0 submissions").

### Pushes not producing runs
- See section 8, tag mode: expected and costs nothing.

---

## 13. CLI install, auth, and build

### Under-scoped `GH_TOKEN` / `GITHUB_TOKEN`: error naming missing scopes
- **Cause:** required scopes are `admin:org`, `read:org`, `repo`, `workflow`. A `gh`-managed token (config file or keyring) is widened in place with `gh auth refresh`; a token from an env var can't be.
- **Fix:** re-issue the token with those scopes, or unset the variable and sign in.

### `Proceed and let gh auth login replace it? [y/N]` (`gh teacher login`)
- **Cause:** `gh teacher login` wraps `gh auth login`, which mints a new token and replaces your stored github.com auth. It is the only command that does that; others reuse a sufficient token untouched, widen an under-scoped one in place, or start sign-in if none exists.
- **Fix:** usually answer No (the default; nothing changes) and just run the command you need. Alternatives printed on decline: `gh auth refresh -h github.com -s admin:org,read:org,repo,workflow`, or export `GH_TOKEN` with a PAT carrying those scopes.

### Wrong GitHub account used
- **Cause:** with multiple `gh` accounts the CLIs use the active github.com account.
- **Fix:** `gh auth status`, then `gh auth switch`. Read-only health probe: `gh teacher audit cs50-fall-2026`.

### Old behavior keeps coming back (discussions setting, feedback ruleset, roster cleanup)
- **Cause:** a co-teacher runs an outdated `gh teacher`; its `init` re-applies old settings and its `audit` flags new ones as drift.
- **Fix:** everyone runs `gh extension upgrade gh-teacher` before re-running `init`.

### Build fails after `git pull` (from-source install)
- **Cause:** `gh extension install .` registers the binary only once; pulled changes aren't rebuilt.
- **Fix:**
  ```sh
  (cd cli/gh-teacher && go build .)
  (cd cli/gh-student && go build .)
  ```
  If `go build` fails, run `go mod tidy` first.

---

## 14. Filing an issue

Open https://github.com/foundation50/classroom50/issues with: the exact command, full output (with `-v` and/or `GH_DEBUG=api`), `gh --version`, `go version` (if built from source), OS and shell. Feature requests and use cases go to the project's Discussions.

---

## 15. FAQ

Questions already answered above are omitted (plan requirement, students self-joining, due dates, shapes, group basics, overrides, exports, score visibility, scopes, service token, hidden tests, self-hosted runners).

**How does Classroom 50 differ from GitHub Classroom?**
Same teaching flow (assignments, per-student repos, autograding), but no server or database: settings, roster, assignments and scores live in a private `classroom50` repo in your org, and grading runs in GitHub Actions. See `concepts.md`.

**Web app or CLI?**
Either, as full alternatives. Teachers can do everything on classroom50.org or with `gh teacher`; students accept and submit from the web or `gh student`.

**Can I self-host?**
There is no server. The web app is a static open-source site you may host yourself. GitHub only; no self-hosted Git platforms.

**Multiple classrooms per org? One org per course?**
A classroom is a directory in `classroom50`; an org holds any number (**Create classroom** or `gh teacher classroom add`). A stable teaching team usually keeps one org with a classroom per term or section; separate orgs suit school-wide adoption or huge courses.

**Roles?**
teacher (org owner, full control), head TA (write on `classroom50`, not owner), TA (read on `classroom50`), student. Manage in classroom **Settings** > **Staff and roles**, or `gh teacher staff add`. Only the web app can invite staff by email.

**Bulk or email enrollment?**
Web **Upload roster** takes a CSV or plain list; rows may use `github_id`, username or email, mixed. Email rows are pending until accepted. CLI: `gh teacher roster invite ORG CLASSROOM ada@example.edu` or `--file` (one address per line; always a student invite). `gh teacher roster import` invites username rows from a stored `roster.csv` but never sends email invitations.

**See students who haven't accepted?**
Yes, the submissions view lists every rostered student with status. Email invitees appear by address, to org owners only.

**Unenroll vs remove?**
Unenroll removes from roster and team, keeps org membership and repos. Removing from the org revokes access to all repos, deletes nothing. Deleting repos is always a separate manual step. Both actions are on the org **Members** page, per member or in bulk.

**Grade without writing test code?**
Yes, declarative tests (input/output, run-command, pytest) on the assignment; `autograder.py` for more control. See `autograding.md`.

**Can students change their recorded score?**
Not invisibly: student-made Releases or replaced `result.json` show as **Unverified**. Code running inside the grading job can forge a score, but leaves an Actions run. See section 9.

**Codespaces?**
Works if enabled for the org, like any repo. Classroom 50 doesn't manage it; education benefits are GitHub's side.

**Test an assignment as a student?**
Add yourself to the roster while staying on a staff team (dual role, graded as student), or accept as staff without enrolling (repo shows with a role badge; counted when **Include teaching staff** next to **Collect all** is on). As an org owner you keep `admin` on your own repo, unlike students' `write`; for an exact replica use a separate GitHub account.

**Will my GitHub Classroom scripts work?**
Mostly: student repos are ordinary repos named `<classroom>-<assignment>-<username>`. Reuse old starter repos only as non-fork copies (section 7).

**Is it FERPA compliant? Where does data go?**
No Classroom 50 server holds student data; everything sits in your GitHub org and your browser/machine talks to GitHub directly, except browser sign-in and repo downloads, which pass through a stateless proxy storing nothing. Compliance rests on your institution's GitHub agreement and what identifying data you put there.

**Accessibility / VPAT?**
Targets WCAG 2.2 A and AA. A VPAT 2.5Rev (WCAG edition) report, accessibility statement and contrast audit are at classroom50.org/accessibility, no sign-in needed, downloadable as Markdown or printable to PDF.

**Missing features?**
No LTI/LMS grade passback, no in-app student score view, no roster self-selection. Reasons are on the wiki page Known Limitations; request via the project's Discussions.
