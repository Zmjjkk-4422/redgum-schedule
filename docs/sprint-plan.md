# Sprint plan — Sprint 1 (RED epics)

- **Sprint goal:** the front desk can maintain students and tutors, record
  tutor availability, and book, move and cancel sessions that always respect
  tutor availability, with day/week and personal views demonstrable on a phone.
- **Duration:** three weeks, planning Friday 25 September 2026, review and
  retrospective Sunday 11 October, presentation Monday 12 October 2026.
- **Capacity:** 12 stories, 44 points, three members; each member also
  completes individual Assessment 2 deliverables by 28 September.

## Story allocation by week

| Week / PM | Han | Max | Jiao |
|---|---|---|---|
| Week 1 (PM Han) 25 Sep–2 Oct | RED-01, RED-04, RED-05, RED-06; RFP & config report (A2) | RED-02, RED-03; A2 reports | CI verification plan; test workbook skeleton; A2 reports |
| Week 2 (PM Max) 3–9 Oct | Support/defix; start report sections | RED-07, RED-08 | RED-09, RED-10 |
| Week 3 (PM Jiao) 10–12 Oct | Final report own sections; demo data | Code freeze support; technical demo | RED-11, RED-12; handover; lessons learned; rehearsal |

## Ceremonies

| Ceremony | When | Output (Confluence) |
|---|---|---|
| Sprint planning | Fri 25 Sep, 60–90 min | Committed backlog, story points, planning memo |
| Daily stand-up | Daily 15 min, [time/channel] | Three-question updates; blockers logged |
| Backlog refinement | Wed 7 Oct | Parking decisions confirmed, acceptance details |
| Sprint review | Sun 11 Oct | Story demonstrations vs acceptance criteria |
| Retrospective | Sun 11 Oct | Lessons learned, process improvements |
| Client presentation | Mon 12 Oct | 10-min presentation + 5-min Q&A; formal acceptance |

## Definition of Ready (planning gate)

- Story follows role–action–benefit format with at least three testable
  acceptance criteria.
- Estimated with a recorded point justification; dependencies identified.
- Owner named; no unresolved scope conflict with the out-of-scope list.

## Definition of Done (fixed by the case study — not amended)

1. Code pushed on a branch named for the story.
2. Every acceptance criterion met and demonstrated.
3. Pull request reviewed by another member; all comments resolved.
4. Automated tests exist and pass, including at least one availability-rule
   test where the story touches it.
5. Runs from a clean checkout following the README alone.
6. No critical defects.
7. Jira and Confluence updated to reflect the true state.

## Velocity and burndown tracking

- 44 points across ~10 working days per person; the rotating PM updates the
  Jira burndown daily and raises slippage at the next stand-up.
- If capacity slips (A2 week is heavy), RED-11 is the first candidate to
  descope because seed data already exists in the repository; RED-01–10 are
  the protected core.
