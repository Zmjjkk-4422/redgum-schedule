# Changelog

All notable changes to this project are documented in this file.
The format is based on Keep a Changelog, and this project adheres to
Semantic Versioning.

## [Unreleased]

### Delivered (Sprint 1)
- Session booking web flow with availability check (Max, RED-07) — merged via PR #6.
- Session move, cancel and attended/missed status web flows (Max, RED-08).

### Planned (Sprint 1, remaining)
- Centre day/week schedule, tutor and student views (Jiao, RED-09/10).
- Seed-data command polish and mobile usability pass (Jiao, RED-11).
- Full test plan, traceability matrix and compatibility evidence (Jiao, RED-12).

## [0.1.0] - 2026-09-19

### Added
- Project scaffold: Flask application factory, environment-based configuration
  (`config.py`, `.env.example`), SQLite schema and repository layer (RED-01/02).
- Tutor availability domain rule service with explanatory rejection messages
  and negative unit tests (RED-03).
- Student record create, list, edit and deactivate flows with required-field
  validation and persistence (RED-04, Han).
- Tutor record create, list, edit and deactivate flows (RED-05, Han).
- Tutor availability window add/remove maintenance screen (RED-06, Han).
- Session scheduling service (book/move/cancel/status) used by later stories.
- pytest suite covering validation, persistence, deactivation and the
  availability rule; GitHub Actions CI workflow; Docker configuration.
