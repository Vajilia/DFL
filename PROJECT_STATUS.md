# DFL project status

**Orientation snapshot:** 2026-10-15. This is a navigation document, **not** an automatically updated live-status feed.

## Branches and production
- The deployed branch at this snapshot is `step6-rebuild` (head `fd6555f`); `main` is older and must not be assumed canonical.
- `deploy/update.sh` defaults to `step6-rebuild` (overridable with `DFL_BRANCH`), fetches and hard-resets the server checkout, rebuilds the site, and can restart `dfl-live`. **Never run casually.**
- The production site and live feed are separate from this documentation branch. No deployment is authorized by this document.
- The existing rulebook reference is `docs/decisions.md` together with `engine/rulebook.py` and `engine/rules.py`. Resolve conflicts with the project owner.

## Existing capabilities verified by source inspection
- `engine/schedule.py`: tier-slot-based 18-game schedule, 19-week layout.
- `engine/decisions.py`: bounded legal options, agent drivers, guard/fallback, choice logs.
- `engine/ceo_card.py`: CEO spending pledge, boycott response, rapport/standing/legacy.
- `engine/governance.py`: CEO votes, committee, Commissioner ruling constraints; successor vote threshold is 32 of 48.
- `engine/rosters.py`: camp, active roster, practice squad, game-day availability.
- `engine/live.py`: precomputes season play and reveals results on a real-time clock.
- `engine/run_checks.py`: fast/slow test runner.

These are **source-level observations**, not claims that all requirements are implemented or that the entire test suite passes.

## Questions requiring verification or design approval
1. Compare seeded scheduling invariants and founding CSV with the owner's latest spreadsheet, including any revised franchise identities. Do not silently replace the canonical data.
2. Audit authority boundaries: CEO/GM/HC/coordinators, including the requested third coordinator role.
3. Verify Commissioner selection from sitting CEOs, removal by CEOs, and simulated fan election for the vacated CEO seat. Existing vote threshold alone does not establish this workflow.
4. Verify exile recovery balance, fan election behavior, media factual grounding, and agent character-card visibility.
5. Specify and test the proposed Truth → Beta → Alpha → Truth release pipeline before deployment automation.

## Next safe milestone
Documentation-only repository orientation PR; then a read-only source-to-rulebook gap analysis and a schedule regression test proposal. No code move or production changes.
