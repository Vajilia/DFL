# Step 6a handoff

DFL is a 48-team all-female football simulation. Steps 1–5 are recovered and Step 6a supplies earned-service accounting and expiration classification. The Commissioner directs design; technical work continues from the recovered Claude engine.

## Decision order

Ask what the NFL would likely do and why, adapted to DFL’s team count, divisions, schedule and exile. Test fair competitiveness. Refer unresolved design choices to the Commissioner-elect. Existing skeleton rules remain fixed; tune model dials rather than widening the 13 fairness bands.

## Recovery and publication

GitHub `Vajilia/DFL`, branch `step6-service`, contains snapshot `13702e1`: Steps 1–5 plus Step 6a. Its tree matches local historical commit `744678d`. GitHub `main` remains at `02490ab`. The verification/documentation follow-up is a local commit until the next approved push. Snapshot publication compresses the recovered history; the verified bundle preserves full local history.

Restore the published checkpoint with `git clone --branch step6-service https://github.com/Vajilia/DFL.git`. Restore the latest full-history follow-up with `git clone /path/to/dfl_step6a_verified.bundle DFL`. Run `python engine/check_rulebook.py` and read `reports/verification_step6a.md` before changing code.

The inherited handoff requires an explicit yes for each GitHub push. Connector publication works; command-line push lacks credentials. Preserve main and use an expected-current-revision guard when updating the checkpoint branch.

## Built and remaining

`engine/service.py` records qualifying roster/IR games, awards accrued service at six games and credited service at three, and classifies expired contracts. Ambassador round-robin games count; byes, practice-squad time, Ambassador Bowl and playoffs do not. A player’s qualifying weeks survive club changes and releases, count once per week, and persist through saves. Annual settlement is idempotent.

Historical roster service is estimated once from calendar years because founding rosters and old saves lack game history. New rookies and founding practice-squad players start at zero. NFI/PUP, suspensions, holdouts and injury settlements need explicit rules before they can count.

Next: integrate credited service into minimum pay and accrued service into practice-squad eligibility, then implement ERFA/RFA tenders, offer sheets, matching and compensation. Continue with tags, waivers, trades and pick ownership. Re-signing still uses the old probability dial. Classifying an expired contract does not enforce retention rights. `fa.classes` has matching constants and a partial mechanism; Step 6 is unfinished.

Steps 7–9 retain finance/ownership, governance/people and final calibration. Existing cap and fairness reports remain historical Step-5 studies; no changed outcome or new study should be implied by this accounting checkpoint. Overtime/injury calibration and retired-player memory growth remain known debt.

## Documents

README maps the code and commands. `docs/decisions.md` records the implementation rationale. `engine/rulebook.py` generates `reports/rulebook_status.md`; matching constants and behavioral completeness are separate. `reports/verification_step6a.md` records exact verification scope. The Drive handoff, README, decision log, rulebook status and synthesis are reconciled with this checkpoint. The original Commissioner reference and historical cap/fairness studies retain their source content.
