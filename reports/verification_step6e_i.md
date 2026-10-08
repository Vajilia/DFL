# Step 6e to 6i verification: waivers, tags, trades, compensatory picks, contract tables

Branch `step6-rebuild`, local commit on top of the 6c/6d rebuild (not pushed).

## Results on the final code
- **Check suite:** all 22 scripts exit 0 (`check_transactions.py` is new: 58 tests; `check_movement.py` 13; every older script unchanged and passing).
- **Fairness (both engines):** 12 fast-engine leagues x 48 seasons and 6 drive-engine leagues x 48 seasons, **all 13 bands inside their ranges**, no band touched. The exile effect (extra rating two years after finishing 5th versus 4th) reads -0.36 (fast) and -0.31 (drives) against a band of -0.5 to 0.5: inside, but toward the lower edge, so a Step 9 calibration item.
- **Cap study** (4 leagues x 48 seasons): mean payroll 98.4M (91.6M before), 15.8% of club-seasons below the 90% floor (44.1% before), 4.7% at their limit, 16.4 cap cut-downs a season (5.3 before), floor top-ups 16.9M a season (91.8M before), Equalization Fund in 439M and out 387M a season (721M in before), average levy 7M, average payout 56M.
- **Rulebook:** 39 built, 0 differ, 8 missing (33 / 1 / 13 before). Rows moved to built (partial): `draft.compensatory`, `draft.trading`, `fa.tags`, `fa.waivers`, `trade.deadline`, `resign`.
- **Golden fingerprints regenerated** (seeds 33, 5, 21; 40 seasons) because outcomes legitimately changed: `d84eff9cd0dd9ea5`, `608a7a6af9529ddd`, `9ee065a72afa9a42`.

## What each piece does under the autopilot
- Waivers: about 40 releases a year go on the wire; claims are rare (a club needs an open place and a need).
- Tags: about 12 a year.
- Compensatory picks: about 15 a year (the maximum is 48).
- Contract tables: about 100 to 150 a year for players rated 70+; with the autopilot they settle at the market price in two turns.
- Trades: none by the autopilot; the API is tested directly.

## Tuning forced by the fairness bands and the economy checks
1. Using the new value rule for every expiring player let exiled clubs (payroll counted at half) keep every wanted veteran: exile effect 0.77, band 0.5. Fixed by keeping the old dice as an additional gate for veterans held only by the exile rule (-0.07 in a 6-league trial).
2. Payrolls reached 102M, outside the economy check's 92 to 100M. Fixed with the market-price dial `economy.PAY_SCALE` 12.5 to 11.5 and a new model dial `cap_headroom` 3.0 (98.9M).

## Independent review
A fresh agent reviewed the new code. Four findings, all fixed with tests: a fourth consecutive franchise tag was possible once old rights were pruned; table walkers were left out of the `expired_roster` tally; a practice-squad player could reach a table; the trade checker crashed on list-shaped pick keys. No cap, dead-money or determinism problems found.

## Known gaps (also in the rulebook rows)
- Extensions are made only when a contract expires; the table has no guarantee or bonus terms.
- The DFLPA representative is a guard in the table, not a character with a card; there is no trade table.
- Waivers do not cover the cutdown or offseason releases.
- Compensatory pick slot equals the last slot of the round, so two rookies in a round share a draft-pick number.
- Waiver priority uses the draft order for the wire run at the end of Week 3 (a low-confidence reading of "through Week 3").
- The exile effect now sits near the lower edge of its band.
