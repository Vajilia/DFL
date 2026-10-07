# Step 6 handoff

DFL is a 48-team all-female football simulation. Steps 1–5 are recovered and Step 6a supplies earned-service accounting and expiration classification. Step 6b integrates earned service into minimum base pay and DFL practice-squad eligibility. The Commissioner directs design; technical work continues from the recovered Claude engine.

## Decision order

Ask what the NFL would likely do and why, adapted to DFL’s team count, divisions, schedule and exile. Test fair competitiveness. Refer unresolved design choices to the Commissioner-elect. Existing skeleton rules remain fixed; tune model dials rather than widening the 13 fairness bands.

## Recovery and publication

GitHub `Vajilia/DFL`, branch `step6-service`, contains snapshot `13702e1` and documentation follow-up `31eedf0`: Steps 1–5 plus Step 6a. The follow-up tree matches local historical commit `dcf1e7e`. GitHub `main` remains at `02490ab`. Step 6b is local until its next approved push. Snapshot publication compresses the recovered history; the verified bundle preserves full local history.

Restore the published checkpoint with `git clone --branch step6-service https://github.com/Vajilia/DFL.git`. Restore the latest full-history follow-up with `git clone /path/to/dfl_step6b_verified.bundle DFL`. Run `python engine/check_rulebook.py` and read `reports/verification_step6b.md` before changing code.

The inherited handoff requires an explicit yes for each GitHub push. Connector publication works; command-line push lacks credentials. Preserve main and use an expected-current-revision guard when updating the checkpoint branch.

## Built and remaining

`engine/service.py` records qualifying roster/IR games, awards accrued service at six roster/IR games and salary-credited service at three active/inactive roster games (IR is excluded), and classifies expired contracts. Ambassador round-robin games count; byes, practice-squad time, Ambassador Bowl and playoffs do not. A player’s qualifying weeks survive club changes and releases, count once per week, and persist through saves. Annual settlement is idempotent.

Historical roster service is estimated once from calendar years because founding rosters and old saves lack game history. Old partial-year saves also lack a roster/IR split: missing credited-service weeks are estimated once from their existing qualifying weeks. New rookies and founding practice-squad players start at zero. NFI/PUP, suspensions, holdouts and injury settlements need explicit rules before they can count.

Step 6b integrates credited service into minimum base pay and accrued service into DFL practice-squad eligibility. New deals protect base pay before assigning bonuses; continuing deals receive required minimum increases. Newly generated street players start with zero documented service. Next: implement a persistent draft-pick ownership ledger and ERFA/RFA tenders, offer sheets, matching and compensation. Continue with tags, waivers, trades and pick ownership. Re-signing still uses the old probability dial. Classifying an expired contract does not enforce retention rights. `fa.classes` has matching constants and a partial mechanism; Step 6 is unfinished.

Steps 7–9 retain finance/ownership, governance/people and final calibration. Cap and both-engine fairness reports were regenerated for Step 6b. All 13 fairness bands passed on both engines; higher floor top-ups and Equalization Fund surplus remain finance-stage model issues. DFL retains a simpler practice-squad allocation than the actual NFL category quotas, and temporary elevations remain unmodeled. Overtime/injury calibration and retired-player memory growth remain known debt.

## Documents

README maps the code and commands. `docs/decisions.md` records the implementation rationale. `engine/rulebook.py` generates `reports/rulebook_status.md`; matching constants and behavioral completeness are separate. `reports/verification_step6b.md` records exact verification scope. The Drive handoff, README, decision log, rulebook status and synthesis are reconciled with this checkpoint. The original Commissioner reference retains its source content; cap/fairness reports now reflect the Step 6b studies.
