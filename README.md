# Redgum Tutoring Scheduling System

A small web application that replaces Redgum Tutoring's magnetic whiteboard,
pencil desk diary and corkboard tutor-availability cards with one shared,
persistent schedule for students, tutors and sessions.

Built for **ISYS3001 Managing Software Development (T4 2026)** Assessments 2
and 3 (case study 3, Redgum Tutoring). The team uses Scrum with Jira and
Confluence; this repository is the configuration-management artefact.

> The data in `app/seed_data.json` is fictional case-study data only. Never put
> real personal data, passwords or tokens in this repository.

## Tech stack

- Python 3.11+ and Flask 3
- SQLite (no external database server needed)
- Jinja2 templates with Bootstrap 5 (mobile-responsive)
- pytest for automated tests
- GitHub Actions for continuous integration
- Optional Docker / docker-compose for deployment configuration

## Run from a clean checkout

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (optional) load the fictional sample data
flask --app wsgi seed

# 4. Run the application
python wsgi.py
# then open http://127.0.0.1:5000
```

The SQLite database is created automatically at `instance/redgum.db`.

## Run the tests

```bash
python -m pytest -q
```

The suite includes positive and **negative tests for the tutor availability
rule** (a session must fall entirely inside one of the tutor's availability
windows for that weekday, including when moved).

## Configuration

Settings are environment-based (see `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `FLASK_CONFIG` | `dev` | Configuration profile: `dev`, `test`, `production` |
| `SECRET_KEY` | dev placeholder | Flask session secret; set a real value outside development |
| `DATABASE` | `instance/redgum.db` | SQLite database path |

Copy `.env.example` to `.env` for local overrides. The real `.env` is
git-ignored and must never be committed.

## Run with Docker (optional deployment evidence)

```bash
docker compose up --build
# application on http://127.0.0.1:5000, data persisted in the redgum-data volume
```

## Project structure

```
redgum-schedule/
├── app/
│   ├── __init__.py            # Flask application factory
│   ├── config.py (root)       # environment-based configuration
│   ├── db.py                  # SQLite connection + schema
│   ├── models.py              # repository layer + validation
│   ├── seed.py / seed_data.json
│   ├── services/
│   │   ├── availability.py    # core availability domain rule
│   │   └── scheduling.py      # book / move / cancel / status
│   ├── routes/                # Flask blueprints (students, tutors, sessions, schedule)
│   ├── templates/             # Jinja2 + Bootstrap 5 pages
│   └── static/
├── tests/                     # pytest suite
├── docs/                      # architecture, backlog, sprint plan, Jira import
├── .github/workflows/ci.yml   # CI: install + pytest on every push/PR
├── Dockerfile, docker-compose.yml
└── wsgi.py                    # entry point
```

## Branching and contribution model

- `main` is protected; never push directly.
- One branch per Jira story: `feature/RED-04-student-records`.
- Every change merges through a pull request reviewed by another team member;
  CI must be green and all review comments resolved.
- Conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `chore:`.
- See [docs/branching-strategy.md](docs/branching-strategy.md).

## Sprint status

| Jira | Feature | Owner | Status |
|---|---|---|---|
| RED-01/02/03 | Scaffold, data model, availability rule | Han | In repository (foundation) |
| RED-04/05/06 | Students, tutors, availability windows | Han | In repository |
| RED-07/08/13/14 | Session booking, move/cancel, weekly cap, overlap guard | Max | Service ready; web UI on feature branches |
| RED-09/10/11 | Schedule views, seed polish, mobile pass | Jiao | Planned |
| RED-12/15 | Test plan, traceability, evidence, change-impact warning | Jiao | Planned |

See [docs/product-backlog.md](docs/product-backlog.md) and the Jira board.

## Team

Han (Zmjjkk-4422), Max (Max-25259298), Jiao (Jiao-25258826) — ISYS3001 Team
[Team No.]. Each member pushes only from their own GitHub account; Assessment
2 reports are written individually. No student numbers or personal contact
details are stored in this repository.
