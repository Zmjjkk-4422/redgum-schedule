# Branching and configuration management strategy

## Branch model (GitHub Flow)

- `main` is always deployable and protected: no direct pushes, required pull
  request review, required CI checks.
- Every Jira story gets one branch named `feature/RED-ID-short-name`,
  e.g. `feature/RED-07-book-session`.
- Bug fixes use `fix/RED-ID-or-bug-id-short-name`; documentation-only changes
  use `docs/...`; chores use `chore/...`.
- Branch from the latest `main`, keep branches short-lived (one story), rebase
  or merge main in if the branch ages.

## Pull requests

- Title begins with the Jira ID, e.g. `RED-07: book a session with availability check`.
- Description links the Jira issue and lists the acceptance criteria with
  evidence (screenshots/test names).
- At least one **other** team member reviews; every review comment is resolved
  (fixed or discussed) before merge.
- CI must be green; the author merges with a merge commit (preserves the branch
  history for assessment evidence).

## Commit conventions

`<type>: <summary>` where type is `feat`, `fix`, `docs`, `test`, `refactor`,
`chore`. Summaries are imperative and under ~72 characters; explain the why in
the body when needed. Example:

```
feat: refuse bookings outside tutor availability windows
```

## Identity and access

- Each member pushes only from their own GitHub account with their own
  credentials. Account sharing or pushing on a teammate's behalf is academic
  misconduct.
- The repository is public; it must contain **no** student IDs, real personal
  data, `.env` files, tokens or passwords.
- Secrets are managed outside Git; `.env.example` documents required variables
  with illustrative values only.

## Environments and configuration

| Environment | FLASK_CONFIG | Database | How it is created |
|---|---|---|---|
| Local development | `dev` | `instance/redgum.db` | auto-created; `flask --app wsgi seed` for sample data |
| Automated tests / CI | `test` | temporary database | pytest fixtures / GitHub Actions |
| Demonstration / deployment | `production` | volume-mounted SQLite | Docker image, env vars supplied at run time |

## Releases and change tracking

- Notable changes are recorded in `CHANGELOG.md` (Keep a Changelog).
- Sprint milestones are tagged, e.g. `v0.1.0` (foundation), `v1.0.0` (sprint close).
- Jira status moves with the work: To Do → In Progress (branch pushed) →
  In Review (PR open) → Done (merged, AC demonstrated, docs updated).

## Backup and recovery

- SQLite database files and the data volume are the only stateful artefacts;
  source history is the backup for code and configuration.
- Confluence/Jira content is exported at sprint milestones; the fictional seed
  data can always rebuild a demo database with one command.
