# Architecture and design

## Overview

A conventional Flask layered architecture keeps business rules independent of
the web framework and the database:

```
Browser (Bootstrap 5, mobile-responsive)
        │  HTTP
        ▼
Flask blueprints (app/routes/*)          ← request handling, form validation display
        │
        ▼
Service layer (app/services/*)           ← business rules
  availability.py  scheduling.py
        │
        ▼
Repository layer (app/models.py)         ← validation + SQL
        │
        ▼
SQLite (app/db.py manages connections/schema)
```

The availability rule lives in one place (`services/availability.py`) and is
used by every booking path, including rescheduling, so the rule cannot be
bypassed by a different screen.

## Data model

```
students                 tutors
+ id (PK)                + id (PK)
+ name                   + name
+ year_level             + subjects
+ contact_name           + max_sessions_week (nullable)
+ contact_phone          + status (active|inactive)
+ contact_email
+ subjects               availability_windows
+ status (active|          + id (PK)
  inactive)                + tutor_id (FK)
                           + weekday (1=Mon … 7=Sun)
sessions                   + start_time (HH:MM)
+ id (PK)                  + end_time (HH:MM)
+ student_id (FK)          + note
+ tutor_id (FK)
+ subject                A tutor may have many windows per weekday.
+ session_date (YYYY-MM-DD)
+ start_time (HH:MM)
+ length_minutes (60|90)
+ status (booked|attended|cancelled|missed)
```

Design decisions tied to case-study requirements:

- Deactivated tutors/students are flagged, not deleted, so historical sessions
  remain intact; they disappear from new-booking options.
- Cancelled sessions are retained and stay visible (no hard delete).
- Moving a session updates only that row; other sessions are untouched.
- Room allocation, double-booking detection and billing are absent by design
  (explicitly out of scope; see the product backlog).

## Core domain rule

A proposed slot (weekday, start, length) is valid only when at least one of the
tutor's windows for that weekday satisfies
`window.start <= start` AND `window.end >= start + length`. Otherwise the
service raises `AvailabilityError` with a specific reason:

1. tutor deactivated;
2. no window on that weekday;
3. start is before the earliest window;
4. slot runs past the latest window;
5. slot falls in a gap between two windows.

Boundary behaviour: starting exactly when a window opens, or ending exactly
when it closes, is accepted. These cases are covered by automated tests.

## Validation approach

- Repository functions return `(record, errors)`; invalid form input is never
  saved and the UI names the missing/invalid field.
- Service functions raise typed errors (`AvailabilityError`, `SchedulingError`)
  that routes convert to user-facing messages.
- Database CHECK constraints enforce statuses and 60/90-minute lengths as a
  second line of defence.

## Testing

- Unit tests for the availability rule (positive, boundary, negative).
- Service tests for booking, move, cancel and the status lifecycle.
- Repository tests for required fields, persistence and deactivation.
- Route tests (Flask test client) for page loads and form posts.
- Manual/evidence testing (compatibility matrix, usability script) is tracked
  under RED-12 and the testing workbook.

## Deployment configuration

No production hosting is required for the assessment. Configuration is
environment-driven; `Dockerfile` and `docker-compose.yml` demonstrate a
gunicorn-served deployment with a persistent data volume, and GitHub Actions
runs the test suite on every push and pull request.
