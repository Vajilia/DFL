# Step 6c/6d verification (rebuild)

This increment was rebuilt on branch `step6-rebuild` from the published Step 6b checkpoint (61d49d6), because the earlier Step 6c/6d work was never published and could not be recovered. Scope: draft-pick ownership, qualifying tenders, funded offers, five-day matching, compensation and format-3 storage. Step 6 is not finished: tags, waivers, full trades, compensatory awards and contract tables remain.

## Results

- Full suite on the rebuilt code: **21 of 21 check scripts passed** (the 20 from Step 6b plus the new `check_movement`).
- Review: an independent read-only review of the new code found one real bug in loading a half-upgraded version-2 file, two smaller ones (unvalidated guarantee years; an unfinishable offer blocking all others) and weak spots in two tests. All were fixed and covered by new tests; a late clean-up lets a lapsed offer release its holds instead of blocking.
- Re-run after those fixes: check_movement (13 cases), check_rulebook, check_rosters, check_store, check_decisions and check_tables all pass; seed 33's 40-season fingerprint still equals the golden.
- Both-engine fairness (`python engine/fairness.py --write`): **all 13 bands inside on the fast engine (12 leagues) and the drive engine (6 leagues)**. The exile effect is the closest to its limit: 0.41 (fast) and 0.38 (drives) against a band of -0.5 to 0.5.
- Four-league cap study refreshed (`reports/cap_report.md`).
- Rulebook: 33 built, 1 differs, 13 missing; `fa.tenders` is now built (mechanism partial) and `draft.trading` is partial.

## What the fairness bands changed

The first version let exiled clubs keep every expiring veteran at a cheap tender; the exile effect reached 1.6 (Step 6b: 0.27) and broke its band. Two model rules fixed it without moving any band: a veteran held only by the exile rule is tendered at market price and only if the club wants her; and players for whom no tender fits are negotiated at the market with the usual re-signing dice. Three new model dials were added (`tender_reach` 1.5, `rfa_offer_prob` 0.10, `exile_veteran_dice` on). No existing dial changed.

## Regression fingerprints (40 seasons, fast engine)

| Seed | Step 6b | Step 6c/6d rebuild |
| --- | --- | --- |
| 33 | `7684454490e55492` | `64cd68524123cb93` |
| 5 | `03c68478cc7241f8` | `90ee43bb0cf4022c` |
| 21 | `c7474fba4bfe3d4c` | `da1bd9214c9d4e96` |

Regenerated for the intended retention, tender and ownership rules; `engine/golden_fingerprints.json` and the GOLD line in `engine/check_tables.py` are updated.

## Check evidence (full suite on the rebuilt code, before the review fixes)

| Check | Exit | Seconds | Log SHA-256 |
| --- | --- | --- | --- |
| `check_rulebook` | 0 | 0 | `f0e613f04dcdac2a0a66dc7da5978b342fcfaa886e067b84a5cfca6cf1ea30c5` |
| `check_agents` | 0 | 78 | `1d660d77af1a6dbac73f6a87ff78cf03f8e880a0fdc0abc890bb2fa43791a702` |
| `check_cards` | 0 | 24 | `388ded528087bd20aefe3bcea6084f9195200f51d0ba110fb4afbd2c9f4e0f2c` |
| `check_contracts` | 0 | 13 | `3caf31f3654a2640c6e11945df969b8ac4e8f31167c727589672c8013bff7db0` |
| `check_decisions` | 0 | 275 | `ffc0a73c782736ce67a06293e29699b2603f3522b9ee437e3572850b90cdbdfa` |
| `check_economy` | 0 | 70 | `de91835da52334ac80e98f652ea3bd1733260533442d1ba19eb3fa566f4e213b` |
| `check_fans` | 0 | 167 | `ec46386ca03ddba53fb1237b7d17f549fad512285e515b66c93ee96293ea9032` |
| `check_interactions` | 0 | 72 | `29f316ab21d3e765f3daf2c2e2e62b90af66c83b18df4fbdb96f639b62830a2d` |
| `check_living` | 0 | 194 | `94a6249e63d2269deca0bd54e4a1c2650ea81817b5bc5a496ccc8e43bc41e96d` |
| `check_movement` | 0 | 10 | `e96d89f0bb530ba3e2c611750e52e8d100815675c270aa3ff9be2245a6b58947` |
| `check_phase0` | 0 | 0 | `5f8917a9fbcb894748c4466d43d4c3e9eaf6079bfc949d19e427b858491089e2` |
| `check_phase1` | 0 | 3 | `86a0ac3cfdd593e6a2ac6ac6292b45c11d029b8d4d6464c0f387864f37af42bd` |
| `check_phase2` | 0 | 552 | `e1b799831a21c5e714d250a5325572d50efb328d3ebc832059651bac64eca41b` |
| `check_rosters` | 0 | 1 | `fb3121cb1d3dee25f244b6d21636e2d4f006d27c386a0920c55c490671ac4468` |
| `check_service` | 0 | 3 | `a1735b5aebaf63855e27c966d42652813d8d0b6e8efbdb905e662551bf0009a5` |
| `check_service_pay` | 0 | 15 | `a3d875ac051063decc674246f7e043aa9db8efa0f36c6ba96a4fc77ca021488a` |
| `check_staff` | 0 | 45 | `aa28d6a6d98e7a1cdb9b6ad99518e0a7a85cabf415e17adefe8fee312535f3fa` |
| `check_store` | 0 | 169 | `30e48e8179c73a9a64188e99cb3da0a5f6dcfcb162d6fed571809e292c0e76e3` |
| `check_tables` | 0 | 184 | `d75b8d37abee8898cc875a3f8dd8bcbb2d7317a67b6239b31a9376243022fa58` |
| `check_tiebreaks` | 0 | 8 | `5b2b0bf1922df0da557ee28374006c843043bbb827d5fd2bf0499830f297eb14` |
| `check_ties` | 0 | 8 | `a575037460d6f1686c99b661f9f96a7955d89c99f02f6f9b0e535ebe3f8be040` |

The JSON receipt `reports/verification_step6cd.json` also holds the hashes of the post-fix re-run.

## Known limits

- Autopilot tender and offer rules are model rules; offer sheets are rare by design (10% of eligible players).
- Not supported: NFL incentives and special clauses, competing offer sheets for one player, unsigned-rights carryover.
- The exile rule's treatment of veterans (market-priced tender, only if wanted) is a DFL adaptation recorded in `docs/decisions.md` for the Commissioner to review.
