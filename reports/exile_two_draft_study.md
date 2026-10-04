# Exile and the two drafts: variant study

Roster model, fast engine, 6 leagues x 48 seasons (first 8 thrown away). All numbers come from placeholder dials. "Exile effect" is in team-rating points (about 1 point of margin per point; roughly half a win over 18 games).

| Variant | Returner avg finish | Wins division | 5th again | Exile effect (rating pts, +/- 1 se) | Finish 2 yrs on: was 4th / was 5th | Pick in draft 1 / draft 2 | Early in both drafts (top 8 then top 16) | Ambassador stakes (pick gap) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A. Lottery for new exiles; returners mixed into the band by Ambassador record (Phase 1 way), 0.25 premium signings | 3.10 | 18% | 22% | +1.08 (+/- 0.09) | 3.20 / 3.09 | 4.5 / 22.6 | 39% | 25 |
| B. Lottery for new exiles; returners as a block at the end of the band, 0.25 premium signings | 3.14 | 18% | 24% | +0.88 (+/- 0.10) | 3.10 / 3.13 | 4.5 / 30.5 | 0% | 7 |
| C. Lottery for new exiles; returners as a block at the start of the band, 0.25 premium signings | 3.06 | 19% | 21% | +1.24 (+/- 0.09) | 3.26 / 3.06 | 4.5 / 12.5 | 100% | 7 |
| D. Lottery for returners after the exile year; new exiles pick by record, 0.25 premium signings | 3.02 | 20% | 21% | +1.26 (+/- 0.09) | 3.17 / 3.02 | 14.6 / 4.5 | 0% | 7 |
| E. Same as B with no premium signings (the lottery pick is the only help) | 3.20 | 17% | 26% | +0.16 (+/- 0.09) | 3.10 / 3.20 | 4.5 / 30.5 | 0% | 7 |
| F. RECOMMENDED: same as B with 0.05 premium signings | 3.21 | 15% | 24% | +0.37 (+/- 0.09) | 3.07 / 3.21 | 4.5 / 30.5 | 0% | 7 |

## How to read this

- **Exile effect** compares a team that finished 5th with one that finished 4th, both starting year Y with the same rating, and asks how much stronger the exiled team is at the start of year Y+2. Near zero means finishing 5th neither helps nor hurts; a big positive number means teams would rather finish 5th than 4th. Proposed fair band: -0.5 to +0.5 points (`rules.FAIR_COMPETITION_BANDS`).
- **Early in both drafts** is the share of exiled teams that get a top-8 pick in the lottery and then a top-16 pick the next year.
- **Ambassador stakes** is the gap in draft position between the best and worst Ambassador Season finisher. A big gap invites tanking a seven-game season. In variant D it is the spread of the lottery itself, not a block, so it is not comparable.
- The Phase 1 way (A) lets a returning team that happens to have a good Ambassador record also pick early again, which is how about four in ten exiled teams end up with two early picks.
