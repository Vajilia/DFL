# Step 7 design: CEOs, fan cards and the Equalization Fund

Status: BUILT (see docs/decisions.md, "Step 7"); the four open questions were answered with the recommendations below. Written 2026-10-08 for the Commissioner's review. Labels follow the rulebook: Skeleton / NFL / Adapted / Fair / Model.

## What the Commissioner has said (Skeleton)
- Owners become CEOs with a 10 to 20 year tenure.
- A CEO's personal draw is capped at $100M a year; anything above goes to the Equalization Fund.
- Each fanbase card stands for 1,000,000 fans and decides spending.
- Subsidies (to weaker clubs) are paid out of the CEO's draw.

## What the engine has today
- Only the cap economy exists: payroll, banking, dead money, the floor, and the Fund as a cash account (`economy.close_season`). Clubs have no revenue, profit or owner wealth.
- The Fund now runs near break-even (inflow about $439M, outflow $387M a season). Owner cards have a `subsidy` pressure rating but it does nothing yet.
- Fans and media move one number (approval). They never touch a game.

## Proposed model (recommendations, every number a named dial)
1. **Club revenue (Model).** Each club earns revenue from a shared league pool (equal split, NFL-style national TV) plus local revenue that grows with market size and fan card passion and with recent success. Expenses are the payroll plus a fixed operating cost. The remainder is the club's operating surplus.
2. **CEO draw (Skeleton + Model).** The CEO may take up to the surplus as her draw. The draw is capped at $100M a year; the excess goes to the Fund that season. A CEO who takes less leaves money in the club (reserve), which fans read as investment.
3. **Subsidy (Skeleton + Model).** A CEO with high subsidy pressure may send part of her draw to a named weaker club. Subsidy never buys players: it can only fund a club's reserve, which the cap rules already limit (banking to $125M), so competitive balance cannot be bought.
4. **Fan card spending (Skeleton + Model).** A fan card (1M fans) has a budget it wants the club to spend on three things: ticket price relief, stadium experience, and community. Each choice moves approval by a small capped amount, never a game result.
5. **Tenure (Skeleton).** A CEO is seated for 10 to 20 years (drawn at seating). Recalls still work as today (one division a year, plus exile, under 40% approval). A CEO whose tenure ends retires; a successor is drawn.
6. **Fairness guard (Fair).** Money never reaches the field except through the cap, which does not change. All 13 fairness bands are re-tested after the change; dials move, bands do not.

## Open questions for the Commissioner
1. Is the $100M cap on the draw per CEO per year, or per club per year? (Recommendation: per year, per CEO.)
2. Should the draw be taxed when it is large (NFL-style revenue sharing), or is the $100M cap the only limit? (Recommendation: cap only, as you said.)
3. Should a CEO's draw count against fan approval? (Recommendation: yes, mildly. A club that pays its CEO the maximum while losing is unpopular.)
4. Does the Fund still pay the surplus equally to the 40 playing clubs, or should some of it fund the subsidy pool for the weakest clubs? (Recommendation: keep equal payouts and fund subsidies only from CEO draws, as you said.)

## Build order
1. Revenue and surplus ledger per club (new `engine/finance.py`), no behaviour change, with a check script.
2. CEO draw, cap and Fund inflow; tenure.
3. Subsidy transfers.
4. Fan card spending and approval effects.
5. Re-run fairness, cap study and fingerprints; reconcile docs and the rulebook.
