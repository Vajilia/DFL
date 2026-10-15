# DFL repository map

Use this map to locate code; verify filenames on the current branch. Do not move modules just to match an ideal folder hierarchy.

| Area | Where to start | Purpose |
| --- | --- | --- |
| Project orientation | `README.md`, `AGENTS.md`, `PROJECT_STATUS.md` | Overview, safety, status |
| Rules and provenance | `docs/decisions.md`, `engine/rulebook.py`, `engine/rules.py` | Current rulebook and rule constants |
| Founding data | `data/teams.csv`, `data/schedule_2000.csv`, `engine/identity.py`, `engine/founding.py`, `engine/import_workbook.py` | Franchise identity and founding schedule |
| Schedule and standings | `engine/schedule.py`, `engine/standings.py`, `engine/tiebreak.py`, `engine/calendar_dfl.py` | Matchups, tier slots, timing, rankings |
| Season and football | `engine/season.py`, `engine/sim.py`, `engine/game_engine.py`, `engine/playoffs.py` | Competition |
| Players and personnel | `engine/players.py`, `engine/rosters.py`, `engine/gm_roster.py`, `engine/staff_cards.py`, `engine/coordinators.py` | Rosters and staff |
| Agents and character cards | `engine/decisions.py`, `engine/agents.py`, `engine/cards.py`, `engine/living.py`, `engine/roles.py` | Character state and legal decisions |
| Governance and society | `engine/governance.py`, `engine/ceo_card.py`, `engine/fan_media_cards.py`, `engine/interactions.py`, `engine/relations.py` | Institutional accountability |
| Economics | `engine/economy.py`, `engine/finance.py`, `engine/contracts.py`, `engine/transactions.py` | Money and transactions |
| Persistence | `engine/store.py` | Save/load |
| Site and live feed | `engine/build_site.py`, `engine/site_export.py`, `engine/live.py`, `engine/control_server.py` | Dashboard and runtime |
| Deployment | `deploy/` | Server configuration and deployment scripts |
| Verification | `engine/run_checks.py`, `engine/check_*.py`, `engine/golden_fingerprints.json` | Fast/slow checks and regression baselines |
| Historical plans | `docs/step*.md`, `docs/decisions_pre_rebase.md`, `docs/DFL_Reference_Corrected.txt` | Historical context, not automatically current authority |

## Proposed future organization
A possible eventual hierarchy includes `constitution/`, `tests/`, and `assets/`. **None is being created or adopted by this orientation milestone.** Code imports, existing test paths, deploy scripts, and live-state compatibility must be assessed before moving anything.

## Documentation precedence
A dated historical note or README summary does not supersede a current, owner-approved rule. Existing `docs/decisions.md` describes the rulebook precedence and identifies an external living document; that external document has not been independently inspected in this milestone. Any new constitutional rule or contradiction must be presented to the owner for explicit resolution.
