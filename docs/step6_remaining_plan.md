# Remaining Step 6 implementation order

Decision standard: NFL reasoning adapted to the DFL structure, fair competitiveness, then the Commissioner-elect for unresolved design choices. Existing skeleton rules remain fixed. A rule is complete only when legal actions execute in the season loop, illegal actions are rejected, state survives saves and the corresponding behavior is tested.

## Next: transaction clock and pick ownership

Give every pick a stable identity: draft year, round, original club, and kind (ordinary or compensatory). Track current owner separately from the club whose draft position determines the slot. Resolve the existing lottery/bands before evaluating pick order. Preserve the original slot and rookie scale when ownership changes. A pick may have one owner, one reservation and one eventual selection; spending or trading it twice must fail without changing state. Persist the ledger through `League` and the explicit `store` allowlist, with a migration for old saves. Track the current draft and the frozen three-drafts-ahead horizon.

Use a simulation transaction clock, rather than wall-clock waiting, for the free-agency opening, five-day match window, 24-hour waivers and Tuesday-after-Week-9 trade deadline. The clock and pending transactions must survive a mid-window save. A repeated resume or transaction submission must not apply a transfer twice.

## Tenders, offers and tags

Integrate eligibility into actual expiration handling: a class label alone creates no club rights. ERFA rights require the qualifying one-year minimum offer; an untendered player is free. Preserve prior base salary before contract rundown/clearing so RFA tender prices use the right 110% comparison. A withdrawn tender removes the corresponding retention rights.

Validate and reserve the bidder's cap room and required draft compensation before accepting an offer sheet. Match principal terms, not just one annual salary number. A match releases the bidder's reservation; non-match commits the player, contract and compensation together. The NFL CBA permits the bidder's own or better available selections in the required rounds. Original-round compensation for undrafted players and upgraded-tender interactions require explicit tests. Practice-squad expiration and poaching must not accidentally manufacture exclusive rights at the practice-squad wage.

Tags share the one-designation-per-team-year limit. Use the frozen DFL positional top-seven/top-fifteen adaptations and prior-pay/consecutive-tag floors. Snapshot the salary reference pool so designation order cannot change tag prices. Non-exclusive franchise compensation uses the same pick reservation path. Distinguish unsigned rights, a signed one-year tag, and an agreed longer deal.

## Waivers and trades

Audit every release/cutdown path. A waived player must retain claimable contract terms until clearance; today's `economy.release` clears those terms immediately and cannot be reused unchanged for claims. Resolve claims by the applicable frozen priority and cap/roster legality, not loop order. Practice-squad signings require clearance where applicable, and a rival's roster signing must enforce the frozen three-week stay.

Trades must be atomic: validate player/list ownership, pick ownership, deadline and both final cap states before mutation. Preserve the receiving club's salary/guarantee obligations; accelerate the sending club's remaining signing bonus under the applicable timing rule. A trade is not a release: charging the sending club the receiving club's guaranteed base pay would double-count obligations. Record a receipt for every committed transfer and every rejected proposal.

The frozen waiver paragraph omits post-deadline treatment for vested veterans and uses accrued seasons; the NFL CBA uses retirement-plan credited service. Those are different from the Article 26 salary-credit definition. Resolve this source mismatch explicitly before implementing the waiver test. Do not silently reuse a salary-service counter for every purpose.

## Draft and contract integration

Build compensatory selections from a saved qualifying-UFA acquisition/loss ledger, with cancellation and the frozen league/team limits. Append them in rounds 3–7 and keep ordinary slot bands intact. State the valuation model and timing exclusions explicitly; do not mistake additional compensatory picks for the 336 ordinary picks.

Replace probabilistic re-signing with contract decision tables and representative review. Respect drafted-rookie extension timing, real principal terms and the existing cap limits. Keep policy formulas labeled as model dials; legality must come from rule enforcement, not a policy that happens to choose legal actions.

## Completion gate

Boundary and atomicity checks must cover unfunded offers, unavailable picks, duplicated reservations, tender withdrawal, drafted/undrafted compensation, tag reuse, deadline edges, competing waiver claims, failed two-team cap checks and mid-window save/resume. Include attempts to bypass movement rules through camp cuts, practice-squad transitions and unsigned-player signings. Then run the full check suite, explain any intended fingerprint changes, re-run both-engine fairness and cap studies, reconcile the rulebook/documentation and save a recovery checkpoint. GitHub publication remains subject to the handoff's explicit approval rule.

Primary reference for tender matching and available compensation picks: NFL/NFLPA CBA, Article 9, Sections 2–3. Waiver definitions: Article 29, Section 1. Salary-credit IR exclusion: Article 26, Section 2. Source: https://nflpaweb.blob.core.windows.net/website/PDFs/CBA/March-15-2020-NFL-NFLPA-Collective-Bargaining-Agreement-Final-Executed-Copy.pdf
