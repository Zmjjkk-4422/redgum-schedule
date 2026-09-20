# -*- coding: utf-8 -*-
"""Generate docs/jira-import/redgum-backlog.csv for Jira Scrum import."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "redgum-backlog.csv")

EPIC_CORE = "Redgum scheduling core (Sprint 1)"
EPIC_PARKED = "Parked product backlog"

HEADER = ["Issue Type", "Summary", "Epic Name", "Description",
          "Story Points", "Priority", "Labels"]


def story(summary, epic, role, want, benefit, ac, points, priority, labels):
    desc = (
        f"As {role}, I want {want}, so that {benefit}.\n\n"
        "Acceptance criteria:\n" + "\n".join(f"- {c}" for c in ac)
        + f"\n\nStory point justification: {points} = "
        + ("small single-screen change" if points <= 3
           else "multi-layer feature touching routes, services and tests" if points == 5
           else "large/uncertain; must be split")
    )
    return ["Story", summary, epic, desc, points, priority, labels]


rows = [
    ["Epic", EPIC_CORE, EPIC_CORE,
     "Committed Sprint 1 epic: student/tutor records, tutor availability, "
     "session booking with the availability rule, and schedule views.",
     "", "High", "committed-sprint-1"],
    ["Epic", EPIC_PARKED, EPIC_PARKED,
     "Stakeholder requests explicitly parked out of Sprint 1 with reasons; "
     "kept visible for future planning per the case study.",
     "", "Low", "parked"],

    story("RED-01 Project scaffold, configuration and CI", EPIC_CORE,
          "a developer", "a runnable, configured project scaffold with CI",
          "the whole team builds on one working baseline",
          ["Application starts from a clean checkout following the README alone",
           "Environment-based configuration (dev/test/production) with .env.example",
           "GitHub Actions installs dependencies and runs pytest on push and pull requests",
           "No secrets, tokens, student IDs or real personal data in the repository"],
          5, "High", "committed-sprint-1 owner-han"),
    story("RED-02 Data model and SQLite persistence", EPIC_CORE,
          "a developer", "students, tutors, availability windows and sessions persisted in SQLite",
          "data survives application restarts",
          ["Schema for students, tutors, availability_windows and sessions with foreign keys",
           "Repository create/read/update functions with required-field validation",
           "CHECK constraints for statuses and 60/90 minute session lengths",
           "Repository tests demonstrate persistence across a new connection"],
          3, "High", "committed-sprint-1 owner-han"),
    story("RED-03 Tutor availability domain rule with negative tests", EPIC_CORE,
          "Deb (front desk)", "every proposed booking checked against the tutor's availability windows",
          "sessions can never be booked when the tutor is unavailable",
          ["A slot is accepted only when it falls entirely inside one window for that weekday",
           "Starting exactly at window open or ending exactly at window close is accepted",
           "Bookings before open, after close, across a gap, on an unavailable day, or with a deactivated tutor are refused with a clear reason",
           "Automated positive and negative tests cover every case, including moved sessions"],
          3, "High", "committed-sprint-1 owner-han"),
    story("RED-04 Student records: create, find, edit, deactivate", EPIC_CORE,
          "Deb", "to maintain student records with name, year, family contact and subjects",
          "student information is correct and available in one place",
          ["Create a student with name, year level, family contact and subjects",
           "Missing required fields are named and the record is not saved",
           "Find and edit existing students; deactivate a student without deleting history",
           "Records persist after restart"],
          3, "High", "committed-sprint-1 owner-han"),
    story("RED-05 Tutor records: create, find, edit, deactivate", EPIC_CORE,
          "Deb", "to maintain tutor records and deactivate tutors who leave",
          "the tutor list stays current after tutor turnover",
          ["Create a tutor with name and subjects taught",
           "Find and edit tutors; deactivate a tutor",
           "Deactivated tutors keep historical sessions but disappear from new-booking options",
           "Required fields are validated and nothing invalid is saved"],
          3, "High", "committed-sprint-1 owner-han"),
    story("RED-06 Maintain tutor availability windows", EPIC_CORE,
          "Deb", "to add, change and remove each tutor's weekly availability windows",
          "bookings match what tutors agreed, including mid-term amendments",
          ["Add multiple windows per weekday with start and end times",
           "Windows can be removed (change = remove then re-add)",
           "Weekday 1-7 and HH:MM times validated; end must be after start",
           "Windows are shown with the tutor and used by booking validation"],
          3, "High", "committed-sprint-1 owner-han"),
    story("RED-07 Book a session with availability check", EPIC_CORE,
          "Deb", "to book a session choosing student, tutor, date, start time and 60/90 minute length",
          "a correct booking takes under a minute while a parent waits",
          ["Session saves with status booked and appears on that day's schedule",
           "Only active students and tutors can be selected; lengths limited to 60 or 90 minutes",
           "Bookings outside an availability window are refused with a plain-language reason",
           "Missing required fields are named and nothing is saved"],
          5, "High", "committed-sprint-1 owner-max"),
    story("RED-08 Move, cancel and mark session status", EPIC_CORE,
          "Deb", "to reschedule or cancel a session and mark attendance",
          "changes, cancellations and no-shows are reliably recorded",
          ["Moving a session re-checks the availability rule on the new slot",
           "Cancelling keeps the record visible with status cancelled",
           "Booked sessions can be marked attended or missed; cancelled sessions cannot",
           "Moving or cancelling one session never changes another session"],
          3, "High", "committed-sprint-1 owner-max"),
    story("RED-13 Enforce each tutor's weekly session cap", EPIC_CORE,
          "Helen", "a booking refused when it would exceed a tutor's maximum sessions per week",
          "tutors such as Tomas (max 8 per week) are never overbooked",
          ["Booked and attended sessions in the booking's ISO week count toward the tutor's max_sessions_week; cancelled and missed do not",
           "A booking that would reach cap + 1 is refused with a plain-language reason showing the current count and cap",
           "A booking at exactly the cap is refused and cap minus one accepted; moving a session out frees the capacity",
           "Automated positive and negative tests cover create, move and status-change paths"],
          3, "High", "committed-sprint-1 owner-max"),
    story("RED-14 Prevent overlapping bookings for the same tutor or student", EPIC_CORE,
          "Deb", "the system to refuse a session that overlaps another active session for the same tutor or student",
          "nobody is double-booked while paper and system run in parallel",
          ["On create and move, overlapping booked or attended sessions on the same date for the same tutor are refused, naming the conflict",
           "The same check applies to the student; cancelled and missed sessions are ignored",
           "Sessions that merely touch (one ends exactly when the next starts) are accepted",
           "Automated positive and negative tests cover tutor overlap, student overlap, touching boundary and move paths"],
          3, "High", "committed-sprint-1 owner-max"),
    story("RED-09 Centre day and week schedule view", EPIC_CORE,
          "Helen", "to see the whole centre's sessions for a chosen day or week",
          "she can judge tutor utilisation and the day at a glance",
          ["Choose a day or a week and list every session with student, tutor, subject, time, length and status",
           "Days with no sessions show an empty state, not an error",
           "View is usable at phone width without horizontal scrolling"],
          3, "Medium", "committed-sprint-1 owner-jiao"),
    story("RED-10 Tutor upcoming and student history views", EPIC_CORE,
          "a tutor and a parent", "tutors see their own upcoming sessions and a student's past/future sessions are visible",
          "tutors know their week and Deb answers parent questions immediately",
          ["Tutor view lists only that tutor's upcoming sessions, soonest first, with an empty state",
           "Student view lists past and future sessions in date order",
           "Cancelled sessions remain visible and are clearly marked"],
          3, "Medium", "committed-sprint-1 owner-jiao"),
    story("RED-11 Load case-study seed data and complete mobile usability pass", EPIC_CORE,
          "the team", "the paper documents loaded as sample data and a phone-usable interface",
          "demonstrations use realistic scenarios and tutors can use their phones",
          ["A single command loads tutors, windows, students and Week 5 sessions from Documents A-C",
           "Seeded data matches the case study (Tomas card, diary moves, Kai enrolment)",
           "Mobile walkthrough of the core booking flow completes within one minute; defects fixed or logged"],
          2, "Medium", "committed-sprint-1 owner-jiao"),
    story("RED-12 Test plan, cases, traceability and compatibility/usability evidence", EPIC_CORE,
          "the assessor", "a complete test workbook and quality evidence",
          "delivery quality is independently verifiable",
          ["Test scenarios, test cases, requirements traceability matrix and summary following the provided workbook example",
           "Every committed story traced to at least one positive and negative case",
           "Browser/device compatibility matrix and usability walkthrough evidence with screenshots",
           "Defect log with retesting; CI green; no critical defects open"],
          5, "High", "committed-sprint-1 owner-jiao"),
    story("RED-15 Warn when availability changes affect existing bookings", EPIC_CORE,
          "Deb", "a warning listing booked sessions that no longer fit after a tutor's window is removed or shortened",
          "mid-term amendments such as Tomas's Thursday change never silently strand a booking",
          ["Removing (or shortening, via remove-then-re-add) an availability window checks existing booked sessions against the windows that remain",
           "Affected sessions are listed with date, time and student on the tutor's availability page and a warning banner; sessions are never deleted automatically",
           "Sessions still inside another window are not flagged; an all-clear state is shown",
           "Automated tests cover affected, unaffected and re-added-window cases"],
          2, "Medium", "committed-sprint-1 owner-jiao"),
]

parked = [
    ("PARK-01 Room allocation, clash checks, 15-minute gaps and Room 3 capacity",
     "rooms, room-clash detection, the 15-minute turnaround and Room 3 capacity rules",
     "the centre schedule respects physical rooms",
     ["Rooms selectable per session", "Clashes, gaps and capacity rules enforced", "Rooms shown on schedule views"],
     "Rooms excluded from the fixed sprint scope; schedule is tutor-based this sprint."),
    ("PARK-02 Room-based clash checks across tutors (rooms, 15-minute gaps, Room 3 capacity)",
     "room allocation and warnings when sessions in different rooms overlap or breach room rules",
     "the June Room 2 double-booking incident cannot recur once rooms are modelled",
     ["Room selectable per session", "Cross-tutor clash, gap and capacity rules enforced", "Rooms shown on schedule views"],
     "Rooms are excluded from the fixed sprint scope; same-tutor and same-student overlap is delivered as RED-14."),
    ("PARK-03 Invoicing, rates and prepaid ten-session packs",
     "fees, hourly rates and prepaid pack balances such as Kai's ten-pack",
     "billing matches what families owe",
     ["Pack purchase and balance tracking", "Rate tables", "Invoice records"],
     "Billing is explicitly out of scope; payment noted on paper for now."),
    ("PARK-04 Online payment and parent top-ups",
     "online card payment for sessions and packs",
     "families can self-serve payment",
     ["Payment vendor integration", "Receipts and reconciliation"],
     "Out of scope; requires vendor selection, security and compliance work."),
    ("PARK-05 Tutor timesheets, payroll and no-show payment rules",
     "worked-hour and payroll reports for casual tutors",
     "Helen can pay tutors accurately",
     ["Timesheet export", "No-show payment policy applied"],
     "Out of scope; session statuses are recorded only."),
    ("PARK-06 Email and SMS reminders and cancellation notices",
     "automatic reminders and cancellation notifications",
     "tutors stop arriving for cancelled sessions",
     ["Reminder templates and opt-in", "Cancellation notices on status change"],
     "Out of scope; needs messaging vendor and consent handling."),
    ("PARK-07 Parent self-service portal",
     "parents to view bookings and request changes themselves",
     "front-desk call volume drops",
     ["Authenticated parent access", "Booking request workflow"],
     "Out of scope; needs accounts, roles and privacy design (PARK-13)."),
    ("PARK-08 Video-session links and attendance",
     "video links recorded for any online sessions",
     "online sessions are supported if introduced",
     ["Link field and attendance by link"],
     "Out of scope; the centre is in-person."),
    ("PARK-09 Blue card expiry tracking and alerts",
     "tutor blue-card numbers and expiry dates with alerts",
     "the centre never schedules an unverified tutor",
     ["Compliance fields", "Expiry dashboard and alerts"],
     "Out of scope; standalone compliance workflow."),
    ("PARK-10 Accountant export, utilisation and inactive-student reports",
     "Xero/accountant exports, utilisation and three-week-inactivity reports",
     "Helen gets the commercial visibility she asked for",
     ["Scheduled exports", "Utilisation and inactivity reports"],
     "Out of scope; reporting epic after core scheduling stabilises."),
    ("PARK-11 Tutor post-session notes",
     "tutors to record what was covered and homework set",
     "next sessions pick up where the last one ended",
     ["Notes per session, visible to tutors", "History on student view"],
     "Future enhancement requested by Tomas; sessions stay minimal this sprint."),
    ("PARK-12 January intensive and NAPLAN workshop scheduling",
     "different day patterns for the January intensive and workshops",
     "term and holiday patterns coexist",
     ["Term-pattern calendar", "Workshop enrolment blocks"],
     "Different scheduling model; design after weekly scheduling is proven."),
    ("PARK-13 User accounts, roles, authentication and security hardening",
     "individual logins with role-based access",
     "children's and families' personal data is protected",
     ["Login, roles (owner/desk/tutor)", "Tutor data scoping enforced server-side", "Audit log"],
     "Sprint assumes a trusted front-desk device; required before any multi-user release."),
]
for summary, want, benefit, ac, reason in parked:
    desc = (
        f"As a stakeholder, I want {want}, so that {benefit}.\n\n"
        "Acceptance criteria (future):\n" + "\n".join(f"- {c}" for c in ac)
        + f"\n\nParked reason: {reason}"
    )
    rows.append(["Story", summary, EPIC_PARKED, desc, "", "Low", "parked out-of-scope-sprint-1"])

with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(HEADER)
    writer.writerows(rows)

print(f"Wrote {OUT} with {len(rows)} issues")
