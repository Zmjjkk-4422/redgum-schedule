# Configuration management report — starter outline (Assessment 2, individual)

> This file is a shared starter outline only. Assessment 2 is an **individual**
> submission: every member writes their own Configuration Management report
> (and Procurement Plan) in their own words, with their own screenshots from
> their own GitHub account. Do not submit identical text.

File name: `[StudentID]_ISYS3001_Configuration_Management.pdf`
Format: Arial 12 pt, 1.5 line spacing, APA 7 references, GenAI declaration.

## Suggested structure

1. **Introduction** — the Redgum project, why configuration/version management
   matters for a small team replacing paper records (lost whiteboard incident,
   tutor turnover, parallel changes).
2. **Repository and tooling** — GitHub public repository, branch protection,
   GitHub Actions CI; include your own screenshots (repo home, Actions runs,
   branch/network graph, a pull request you authored and one you reviewed).
3. **Branching model** — GitHub Flow, story-named branches, PR review rules;
   reference `docs/branching-strategy.md`; show the branch list and a merged PR.
4. **Commit and change management** — conventional commits, CHANGELOG, tags;
   show your commit history; explain how Jira statuses track code state.
5. **Environment configuration** — dev/test/production profiles in `config.py`,
   `.env.example`, why `.env` is ignored, secrets handling; SQLite locations
   per environment; Dockerfile/docker-compose as deployment configuration.
6. **Build, test and CI** — clean-checkout steps, pytest suite (highlight the
   availability-rule tests), CI matrix; include a green Actions screenshot.
7. **Defects and rollback** — how issues are logged in Jira, how reverts work
   with protected main and tagged releases.
8. **Reflection** — what configuration problems were avoided, what you would
   improve (e.g. adding release notes automation, Dependabot).
9. **References (APA 7)** — Git SCM docs, GitHub Actions docs, Flask
   configuration docs, Twelve-Factor App, IEEE/PMI config-management sources
   your tutor recommended.

## Evidence checklist (collect as you work)

- [ ] Repository created/joined under your own GitHub account
- [ ] At least one feature branch and merged PR authored by you
- [ ] At least one PR review with comments resolved
- [ ] Green CI run on a PR of yours
- [ ] Clean-clone run recorded (commands + output/screenshots)
- [ ] `.env.example` shown; proof `.env`/`*.db` are ignored
- [ ] CHANGELOG/tag evidence
