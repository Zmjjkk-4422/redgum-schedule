"""Build docs/testing/test-plan.xlsx for RED-12 (test workbook)."""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = os.path.join(os.path.dirname(__file__), "docs", "testing", "test-plan.xlsx")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

HEADER_FILL = PatternFill("solid", fgColor="D9E1F2")
HEADER_FONT = Font(bold=True)
THIN = Side(style="thin", color="BFBFBF")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")


def style_sheet(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = BORDER
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = WRAP
            cell.border = BORDER
    ws.freeze_panes = "A2"


wb = Workbook()

# ---- Sheet 1: Test Scenarios ----
ws1 = wb.active
ws1.title = "Test Scenarios"
ws1.append(["Scenario ID", "Story", "Scenario description", "Type"])
scenarios = [
    ("TS-01", "RED-03", "Book a session fully inside a tutor availability window", "Positive"),
    ("TS-02", "RED-03", "Book a session that starts before the window opens", "Negative"),
    ("TS-03", "RED-03", "Book a session that runs past the window close", "Negative"),
    ("TS-04", "RED-03", "Book on a weekday with no window", "Negative"),
    ("TS-05", "RED-03", "Session touching a window boundary is accepted", "Positive"),
    ("TS-06", "RED-04", "Create a student with required fields", "Positive"),
    ("TS-07", "RED-04", "Create a student missing required fields", "Negative"),
    ("TS-08", "RED-04", "Edit and deactivate a student", "Positive"),
    ("TS-09", "RED-05", "Create / edit / deactivate a tutor", "Positive"),
    ("TS-10", "RED-05", "Deactivated tutor cannot be newly booked", "Negative"),
    ("TS-11", "RED-06", "Add and remove a tutor availability window", "Positive"),
    ("TS-12", "RED-07", "Book a session via the web form with availability check", "Positive"),
    ("TS-13", "RED-08", "Move a booked session to another valid slot", "Positive"),
    ("TS-14", "RED-08", "Move outside the tutor window is refused", "Negative"),
    ("TS-15", "RED-08", "A cancelled session cannot be moved", "Negative"),
    ("TS-16", "RED-08", "Cancel keeps the record, status cancelled, still visible", "Positive"),
    ("TS-17", "RED-08", "Mark booked attended/missed; cancelled cannot be marked", "Negative"),
    ("TS-18", "RED-09", "Day view lists every session for a chosen day", "Positive"),
    ("TS-19", "RED-09", "Week view covers Mon-Sun with correct bounds", "Positive"),
    ("TS-20", "RED-09", "Empty day/week shows empty state, no error", "Positive"),
    ("TS-21", "RED-09", "Tables responsive, no horizontal scroll at phone width", "Positive"),
    ("TS-22", "RED-10", "Tutor sees only own upcoming sessions, soonest first", "Positive"),
    ("TS-23", "RED-10", "Student detail splits upcoming and past sessions", "Positive"),
    ("TS-24", "RED-10", "Cancelled sessions remain visible and marked", "Positive"),
    ("TS-25", "RED-11", "flask seed loads tutors/windows/students/sessions", "Positive"),
    ("TS-26", "RED-11", "Seeded data matches case-study records", "Positive"),
    ("TS-27", "RED-13", "Booking beyond weekly cap is refused", "Negative"),
    ("TS-28", "RED-13", "Tutor's own max_sessions_week overrides the default", "Positive"),
    ("TS-29", "RED-13", "Cancelled sessions do not count toward the cap", "Negative"),
    ("TS-30", "RED-14", "Overlapping sessions for the same tutor are refused", "Negative"),
    ("TS-31", "RED-15", "Removing a window flags stranded booked sessions", "Positive"),
    ("TS-32", "RED-15", "Stranded sessions are never deleted automatically", "Negative"),
    ("TS-33", "RED-15", "Sessions still covered by another window show all-clear", "Positive"),
]
for s in scenarios:
    ws1.append(list(s))
style_sheet(ws1, [12, 10, 55, 12])

# ---- Sheet 2: Test Cases ----
ws2 = wb.create_sheet("Test Cases")
ws2.append(["Case ID", "Scenario ID", "Preconditions", "Steps", "Test data",
            "Expected result", "Actual result", "Status", "Defect ID", "Automated"])
cases = [
    ("TC-01", "TS-01", "Tomas active, Tue 15:30-19:00 window exists", "Validate a 60-min booking", "Tue 16:00", "Accepted, session booked", "PASS", "Passed", "", "Yes (test_availability.py)"),
    ("TC-02", "TS-02", "Tue window opens 15:30", "Validate booking at 15:00", "Tue 15:00", "Refused: starts before window", "PASS", "Passed", "", "Yes"),
    ("TC-03", "TS-03", "Tue window closes 19:00", "Validate 90-min booking ending 19:30", "Tue 18:00", "Refused: runs past window", "PASS", "Passed", "", "Yes"),
    ("TC-04", "TS-04", "Tomas has no Friday window", "Validate a Friday booking", "Fri 16:00", "Refused: no window that day", "PASS", "Passed", "", "Yes"),
    ("TC-05", "TS-05", "Tue window 15:30-19:00", "Book touching close boundary", "17:30 for 90 min", "Accepted (boundary valid)", "PASS", "Passed", "", "Yes"),
    ("TC-06", "TS-06", "None", "Create student via form with all fields", "Kai Lombardo Y11", "Student created, redirect to detail", "PASS", "Passed", "", "Yes (test_students.py)"),
    ("TC-07", "TS-07", "None", "Create student with missing name", "name blank", "Validation error, not saved", "PASS", "Passed", "", "Yes"),
    ("TC-08", "TS-08", "Student exists", "Edit then deactivate", "", "Fields update; status inactive", "PASS", "Passed", "", "Yes"),
    ("TC-09", "TS-09", "None", "Create/edit/deactivate tutor", "Tomas Ferreira", "CRUD works", "PASS", "Passed", "", "Yes (test_tutors.py)"),
    ("TC-10", "TS-10", "Tutor deactivated", "Attempt to book with deactivated tutor", "", "Refused: tutor inactive", "PASS", "Passed", "", "Yes"),
    ("TC-11", "TS-11", "Tutor exists", "Add then remove a window", "Wed 16:00-18:00", "Window appears then removed", "PASS", "Passed", "", "Yes (test_tutors.py)"),
    ("TC-12", "TS-12", "Tutor/student active, valid slot", "Submit booking form", "valid slot", "Session booked, redirect", "PASS", "Passed", "", "Yes (test_sessions_route.py)"),
    ("TC-13", "TS-13", "Booked session exists", "Move to another valid slot", "new Tue 17:00", "Date/time updated, stays booked", "PASS", "Passed", "", "Yes"),
    ("TC-14", "TS-14", "Booked session exists", "Move outside tutor window", "Fri slot", "Refused with reason, unchanged", "PASS", "Passed", "", "Yes"),
    ("TC-15", "TS-15", "Session cancelled", "Move it", "", "Refused: cancelled cannot move", "PASS", "Passed", "", "Yes (test_scheduling_service.py)"),
    ("TC-16", "TS-16", "Booked session", "Cancel it", "", "Status cancelled, record retained, visible", "PASS", "Passed", "", "Yes"),
    ("TC-17", "TS-17", "Booked & cancelled sessions", "Mark attended/missed", "", "Booked updates; cancelled refused", "PASS", "Passed", "", "Yes"),
    ("TC-18", "TS-18", "Sessions exist on a day", "GET /schedule/?date=...&view=day", "any day", "All that day's sessions listed", "PASS", "Passed", "", "Yes (test_schedule_views.py)"),
    ("TC-19", "TS-19", "Sessions across a week", "view=week", "any week", "Mon-Sun bounds correct", "PASS", "Passed", "", "Yes"),
    ("TC-20", "TS-20", "No sessions", "Open empty day", "", "Empty state text, no error", "PASS", "Passed", "", "Yes"),
    ("TC-21", "TS-21", "Schedule pages", "Resize to phone width (DevTools)", "375px", "No horizontal scroll", "PASS", "Passed", "", "Manual"),
    ("TC-22", "TS-22", "Tutor with future+past sessions", "GET /schedule/tutor/<id>", "", "Only upcoming, soonest first", "PASS", "Passed", "", "Yes (test_red10_views.py)"),
    ("TC-23", "TS-23", "Student with up+past sessions", "Open student detail", "", "Upcoming and Past sections", "PASS", "Passed", "", "Yes"),
    ("TC-24", "TS-24", "Cancelled sessions exist", "Open views", "", "Cancelled visible with red badge", "PASS", "Passed", "", "Yes"),
    ("TC-25", "TS-25", "Fresh DB", "flask --app wsgi seed", "", "Data loads, no error", "PASS", "Passed", "", "Yes (test_seed_data.py)"),
    ("TC-26", "TS-26", "Seeded DB", "Check specific case records", "Tomas/Helen/Kai", "Match case-study paper", "PASS", "Passed", "", "Yes"),
    ("TC-27", "TS-27", "Tutor at weekly cap", "Book one more same ISO week", "cap reached", "Refused: weekly cap", "PASS", "Passed", "", "Yes (test_scheduling_service.py)"),
    ("TC-28", "TS-28", "Tomas max_sessions_week=8", "Book the 9th in a week", "9th session", "Refused at 8 (not 12)", "PASS", "Passed", "", "Yes"),
    ("TC-29", "TS-29", "Tutor near cap", "Cancel one then book", "", "Cancelled not counted", "PASS", "Passed", "", "Yes"),
    ("TC-30", "TS-30", "Tutor has a session at 16:00", "Book another 60 min overlapping", "16:30", "Refused: overlap", "PASS", "Passed", "", "Yes (RED-14 tests)"),
    ("TC-31", "TS-31", "Booked session in a window", "Remove that window", "", "Banner lists stranded session", "PASS", "Passed", "", "Yes (test_red15_change_warning.py)"),
    ("TC-32", "TS-32", "Stranded session", "Remove window", "", "Record remains booked", "PASS", "Passed", "", "Yes"),
    ("TC-33", "TS-33", "Session fits another window", "Remove a different window", "", "Green all-clear, not flagged", "PASS", "Passed", "", "Yes"),
]
for c in cases:
    ws2.append([c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7], c[8], c[9]])
style_sheet(ws2, [9, 11, 28, 30, 18, 32, 10, 9, 9, 24])

# ---- Sheet 3: Requirements Traceability Matrix ----
ws3 = wb.create_sheet("Traceability Matrix")
ws3.append(["Story", "Acceptance criterion", "Scenario IDs", "Case IDs", "Automated test", "Status"])
rtm = [
    ("RED-01/02", "App factory, env config, SQLite schema/repo layer", "-", "-", "CI build + smoke", "Done"),
    ("RED-03", "Session must fall entirely inside a window; boundary valid; plain-language rejection", "TS-01..05", "TC-01..05", "test_availability.py", "Done"),
    ("RED-04", "Student create/list/edit/deactivate, required-field validation", "TS-06..08", "TC-06..08", "test_students.py", "Done"),
    ("RED-05", "Tutor CRUD; deactivated cannot be booked", "TS-09..10", "TC-09..10", "test_tutors.py", "Done"),
    ("RED-06", "Tutor window add/remove screen", "TS-11", "TC-11", "test_tutors.py", "Done"),
    ("RED-07", "Book a session with availability check via web", "TS-12", "TC-12", "test_sessions_route.py", "Done"),
    ("RED-08", "Move/cancel/status flows; cancelled kept", "TS-13..17", "TC-13..17", "test_sessions_route.py, test_scheduling_service.py", "Done"),
    ("RED-09", "Day/week centre view; empty state; phone width", "TS-18..21", "TC-18..21", "test_schedule_views.py", "Done"),
    ("RED-10", "Tutor upcoming; student up/past; cancelled marked", "TS-22..24", "TC-22..24", "test_red10_views.py", "Done"),
    ("RED-11", "Seed command; case-study data; mobile pass", "TS-25..26", "TC-25..26", "test_seed_data.py", "Done"),
    ("RED-13", "Weekly tutor cap; per-tutor override; cancelled excluded", "TS-27..29", "TC-27..29", "test_scheduling_service.py", "Done"),
    ("RED-14", "Overlap guard for same tutor", "TS-30", "TC-30", "RED-14 overlap tests", "Done"),
    ("RED-15", "Availability-change warning; nothing auto-deleted", "TS-31..33", "TC-31..33", "test_red15_change_warning.py", "Done"),
]
for r in rtm:
    ws3.append(list(r))
style_sheet(ws3, [12, 45, 14, 14, 38, 10])

# ---- Sheet 4: Traceability Summary ----
ws4 = wb.create_sheet("Traceability Summary")
rows = [
    ["Redgum Tutoring — Test Workbook Summary (RED-12)", ""],
    ["", ""],
    ["Automated pytest run", "75 passed in ~3s (python -m pytest -q) on main"],
    ["Scenarios", len(scenarios)],
    ["Test cases", len(cases)],
    ["Automated cases", sum(1 for c in cases if c[9].startswith("Yes"))],
    ["Manual cases", sum(1 for c in cases if c[9] == "Manual")],
    ["Passed", sum(1 for c in cases if c[7] == "Passed")],
    ["Failed / open defects", 0],
    ["", ""],
    ["Compatibility matrix", ""],
    ["Chrome desktop", "Pass — booking, schedule, tutor, student flows"],
    ["Edge desktop", "Pass — same flows"],
    ["Phone width (375px)", "Pass — .table-responsive, no horizontal scroll"],
    ["", ""],
    ["Defect log", "None open; no critical defects"],
]
for r in rows:
    ws4.append(r)
ws4.column_dimensions["A"].width = 28
ws4.column_dimensions["B"].width = 60
ws4["A1"].font = Font(bold=True, size=13)
for row in ws4.iter_rows(min_row=2):
    for cell in row:
        cell.alignment = WRAP

wb.save(OUT)
print("saved", OUT)
