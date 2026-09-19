# Jira and Confluence set-up guide (Sprint 1)

## 1. Create the Jira project (Han, Week-1 PM)

1. Log in to Jira (free plan) with the SCU email `y.wu.80@student.scu.edu.au`;
   Max and Jiao create accounts with their own SCU emails.
2. Create project → **Scrum** template → team-managed or company-managed
   (either works; team-managed is fastest on the free plan). Name:
   **Redgum Tutoring Scheduling**, key e.g. `RED`.
3. Project settings → add Max and Jiao as members.
4. Create the linked Confluence space (one click from the project sidebar)
   and share it with the team.

## 2. Import the backlog CSV

1. Open **Filters → Advanced issue search → ⋯ → Import issues from CSV**
   (or Settings → System → External system import → CSV).
2. Choose `docs/jira-import/redgum-backlog.csv` (UTF-8 with BOM).
3. Map columns:
   - `Issue Type` → Issue Type (map **Epic** and **Story**; create Story if missing)
   - `Summary` → Summary
   - `Epic Name` → Epic Name (required so stories attach to the two epics)
   - `Description` → Description
   - `Story Points` → Story Points (create/select the story-point estimate field)
   - `Priority` → Priority
   - `Labels` → Labels
4. Run the import; verify 2 epics, 12 committed stories and 13 parked stories.
5. Open the **Redgum scheduling core (Sprint 1)** epic → bulk-select its 12
   stories → add to the new sprint **Sprint 1 (25 Sep – 12 Oct)**.
6. Assign stories per the labels/owner column (Han: RED-01/04/05/06;
   Max: RED-02/03/07/08; Jiao: RED-09/10/11/12). Assignees must be set by each
   member from their own account where possible.

## 3. Board and workflow conventions

- Workflow: To Do → In Progress → In Review → Done.
- Move to **In Progress** when the story-named branch is pushed.
- Move to **In Review** when the pull request is open.
- **Done** only when every Definition-of-Done item is true (see
  `docs/sprint-plan.md`).
- Parked stories stay in the backlog under the parked epic, never deleted.

## 4. Confluence structure

Create these pages (memos follow the same template: date, attendees, decisions,
actions with owners):

1. Project Charter and Team Rules (attach the signed PDFs)
2. Product backlog and sprint plan (link Jira)
3. Meeting memos (planning, stand-ups, refinement, review, retrospective)
4. Decisions and assumptions log
5. Test plan and results (link the workbook)
6. Handover document (the fixed six parts from the case study)

## 5. Evidence to collect for Assessment 3

- Screenshot of the populated backlog with epics, points and priorities.
- Sprint burndown at review; board showing all stories Done.
- Each story's branch, PR and review linked in its Jira description/comments.
- Memo timestamps for every ceremony.
