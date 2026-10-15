# DFL design decision register

This file supplements the existing, detailed historical log at `docs/decisions.md`; it does not replace that log or `engine/rulebook.py`.

## How to use
For each new decision, record date, status (**approved**, **proposed**, **rejected**, **superseded**, or **needs clarification**), scope, rationale, affected files, tests, and who approved it. Do not infer approval merely because code exists.

| Date | Status | Topic | Record |
| --- | --- | --- | --- |
| 2026-10-15 | Approved for preparation | Repository orientation | Prepare a documentation-only branch and PR for fresh AI collaborators. Update 2026-10-15: the owner waived the merge restriction for this PR; **deployment still needs a separate approval.** |
| 2026-10-15 | Approved | Branch consolidation | The owner approved making `step6-rebuild` the new `main` (fast-forward, no history rewritten) and deleting the merged feature branches. `step6-rebuild` is kept as a mirror of `main` because the deploy scripts depend on it. |
| 2026-10-15 | Proposed | Truth/Beta/Alpha pipeline | Separate experimental, acceptance, and production work; define promotion and rollback gates before implementation. |
| 2026-10-15 | Needs verification | Commissioner succession | Owner describes a Commissioner elected from sitting CEOs, with a simulated fan election to replace the departing CEO; audit existing implementation and resolve specifics before coding. |
| 2026-10-15 | Needs verification | Three coordinators | Owner describes three coordinators; existing `README.md` describes offensive and defensive coordinators. Confirm intended third role and implementation. |
| 2026-10-15 | Needs verification | Franchise naming | Owner provided a revised workbook; compare against `data/teams.csv` before making canonical changes. |

## New decision template
```
### YYYY-MM-DD — Topic
Status:
Authority/approver:
Decision:
Why:
Alternatives rejected:
Files/data affected:
Verification:
Follow-up:
```

Do not rewrite historical records to hide contradictions. Mark a superseded decision and link the replacement.
