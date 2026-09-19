# Product backlog — Redgum Tutoring

Epic 1 **Redgum scheduling core (Sprint 1)** contains the 12 committed
stories (44 story points). Epic 2 **Parked product backlog** records every
request the stakeholders raised but the sprint will not deliver, with a reason
(the case study requires these to stay visible, never be silently dropped).

Story points use the Fibonacci scale (1, 2, 3, 5, 8) and are justified on each
Jira issue. Estimating rule: 2 = trivial form/field change; 3 = one screen or
simple view with tests; 5 = multi-layer feature or core rule; 8 = large,
uncertain feature (split before committing).

## Committed sprint backlog

| ID | Story (as a … I want … so that …) | AC (summary) | Pts | Owner |
|---|---|---|---|---|
| RED-01 | As a developer, I want a runnable, configured project scaffold with CI so the team builds on one baseline | App runs from README on a clean checkout; env-based config; CI installs deps and runs tests; `.env.example`; no secrets in Git | 5 | Han |
| RED-02 | As a developer, I want persistent students, tutors, windows and sessions in SQLite so data survives restarts | Schema + repository CRUD; FK integrity; CHECK constraints; repository tests | 5 | Max |
| RED-03 | As Deb, I want bookings checked against tutor availability so sessions cannot be booked when the tutor is unavailable | Rule service; boundary/gap/no-window/deactivated cases; negative tests; plain-language rejection reasons | 5 | Max (tests: Jiao) |
| RED-04 | As Deb, I want to create, find, edit and deactivate student records so family and subject information is in one place | Name/year/contact/subjects; required-field validation; inactive flag; persists; history retained | 3 | Han |
| RED-05 | As Deb, I want to create, find, edit and deactivate tutor records so the tutor list stays current | Name/subjects required; deactivated tutors hidden from booking options but history retained | 3 | Han |
| RED-06 | As Deb, I want to maintain each tutor's weekly availability windows so bookings match what tutors agreed | Multiple windows per day; add/remove; weekday/start/end validation; end after start | 3 | Han |
| RED-07 | As Deb, I want to book a session (student, tutor, date, start, 60/90 min) so the day is scheduled in seconds | Status booked; appears on the day; availability enforced; only active tutors/students; missing fields named | 5 | Max |
| RED-08 | As Deb, I want to move or cancel a session and mark attendance so changes and no-shows are recorded | Move re-checks availability; cancel keeps record; booked→attended/missed; one move never affects others | 3 | Max |
| RED-09 | As Helen, I want a centre schedule for a chosen day or week so I can see the whole centre at a glance | Day/week selection; student/tutor/subject/time/status; empty-day state; phone usable | 3 | Jiao |
| RED-10 | As a tutor/student, I want my own upcoming or historical sessions so tutors know their week and families get answers | Tutor sees only theirs, soonest first; student past+future; cancelled visible; empty states | 3 | Jiao |
| RED-11 | As the team, I want the paper documents loaded as sample data and a phone-usable interface so demos use real scenarios | `flask seed` loads Documents A–C data; mobile walkthrough fixes; core booking flow under a minute | 2 | Jiao |
| RED-12 | As the tutor/assessor, I want a test plan, cases, traceability and compatibility/usability evidence so quality is verifiable | Four-part testing workbook; every story traced; availability rule tested; browser/device matrix; defect log; CI green | 5 | Jiao |

**Total committed: 44 points.**

## Parked backlog (out of scope for Sprint 1, logged with reasons)

| ID | Request | Source | Reason parked |
|---|---|---|---|
| PARK-01 | Rooms, room-clash checks, 15-minute gaps, Room 3 capacity | Helen/Deb | Rooms excluded from the fixed sprint scope; schedule is tutor-based |
| PARK-02 | Detect overlapping/double bookings across tutors | Deb | Explicitly out of scope; revisit with room model |
| PARK-03 | Invoicing, hourly rates, prepaid ten-session packs | Helen | Billing is out of scope; Kai's pack is noted on his record only |
| PARK-04 | Online payment / parent top-ups | Helen | Out of scope; requires payment vendor and security work |
| PARK-05 | Tutor timesheets, payroll, no-show payment rules | Helen | Out of scope; statuses recorded only |
| PARK-06 | Email/SMS reminders and cancellation notices | Deb/Tomás | Out of scope; needs messaging vendor and consent handling |
| PARK-07 | Parent self-service portal | Helen | Out of scope; privacy and authentication design needed |
| PARK-08 | Video-session links and attendance by link | Tomás | Out of scope; centre is in-person |
| PARK-09 | Blue card expiry tracking and alerts | Case context | Out of scope; compliance workflow of its own |
| PARK-10 | Accountant/Xero export, utilisation and "not booked in 3 weeks" reports | Helen | Out of scope; reporting epic after core scheduling |
| PARK-11 | Tutor post-session notes (what was covered, homework) | Tomás | Future enhancement; sessions stay minimal this sprint |
| PARK-12 | January intensive and NAPLAN workshop scheduling | Helen | Different term pattern; design after weekly schedule proven |
| PARK-13 | User accounts, roles and authentication/security hardening | Implicit (Helen privacy concern) | Sprint assumes a trusted front-desk device; needed before any multi-user release |

## Assumptions carried into the sprint

- Sessions are always 60 or 90 minutes.
- The 24-hour cancellation policy and make-up sessions are recorded as status
  changes; no fees are calculated.
- Helen keeps hand-writing the Saturday whiteboard and the paper diary runs in
  parallel during transition; the system does not replace either by mandate.
- One-off tutor absences (e.g. Tomás's Week 8 placement) are not modelled as
  weekly windows; they become a future exception/cancellation feature.
