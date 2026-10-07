# Step 6b verification

All 20 check scripts passed on the corrected Step 6b code, including six service test cases and four salary/eligibility test cases. Both fast and drive simulations and save/resume are covered. Compilation, whitespace and rulebook checks pass. The initial Step 6b run was stopped when primary-source review exposed the IR salary-credit exclusion; its interim fingerprints, fairness and cap results are superseded by the corrected run below.

## Regression check corrections

The first full corrected-code run passed 18 scripts and failed two legacy assertions. check_cards inspected cached coach references after staff turnover rather than the next-season refresh boundary; it now refreshes the current-staff reference before checking centering. check_fans correlated accuracy with final-year credibility (a short moving average): the sampled correlation was 0.03 against a 0.05 threshold. It now keeps the same threshold while comparing career mean forecast scores, and adds a controlled same-result grading check. Both scripts were rerun after their corrections. These edits change test measurements, not simulation behavior, model dials or fairness limits. The refreshed studies and all other passing scripts remain applicable because engine behavior did not change.

## Corrected behavior

Earned credited service controls minimum BASE salary, including continuing contracts and promotions. Bonus allocation cannot consume the base floor. Earned accrued service controls the frozen DFL practice-squad eligibility allocation. New street players start at zero documented service. Separate game lists implement CBA Article 26 Section 2: roster/inactive games earn both kinds of service, IR games only accrued service. The DFL Ambassador inclusion remains; practice-squad time, byes and postseason games earn neither.

Founding and closed legacy service remain one-time estimates. An older partial-year save missing salary-credit weeks copies its existing qualifying weeks once as an estimate because no past IR/roster split exists. Future seasons use both correct lists. Exact NFL practice-squad category quotas and temporary elevations remain unmodeled. Re-signing is still a probability policy; tender, matching, tag, waiver, trade and draft ownership enforcement remain unfinished. Step 6 is NOT complete.

## Regression fingerprints

| Seed | Seasons | Corrected Step 6b | Step 5/6a |
| --- | --- | --- | --- |
| 33 | 40 | `7684454490e55492` | `c66f3a3cf3773dc8` |
| 5 | 40 | `03c68478cc7241f8` | `e17ae5e4aa110fcd` |
| 21 | 40 | `c7474fba4bfe3d4c` | `48636918634fa008` |

Goldens were regenerated for intended service, salary-floor and bonus-allocation changes, including the IR distinction. These affect roster choices and outcomes. No model dial or fairness band was changed. The full suite independently verifies the corrected goldens via decision and table checks.

## Fairness and cap

The corrected study ran 12 fast-engine leagues and 6 drive-engine leagues, each for 48 seasons with the first eight discarded. All 13 fairness bands passed on both engines. The cap study ran four additional 48-season fast leagues. Current numerical results are in fairness_report.md and cap_report.md. Those reports are new studies, not relabeled Step-5 results. Model spending gaps, floor top-ups and Fund surplus remain finance-stage issues; a passed fairness study does not make the finance model complete.

## Check evidence

| Check | Exit | Seconds | Log SHA-256 |
| --- | --- | --- | --- |
| `check_agents` | 0 | 51.8 | `d57092aad22ea1a87a5199f3e6df097157c7e37b8c26c2ab5b693c87a8f1e0f7` |
| `check_cards` | 0 | 17.3 | `683aa2fac88e15da8c8008d1339afaf7053d81359e62ba8a942ca1f801042084` |
| `check_contracts` | 0 | 9.0 | `ba1966a4171edb62d6ad4594e21fb51a2c7b889ee1aae982ed4cc60f89603f14` |
| `check_decisions` | 0 | 186.7 | `27f892f8511635dbd0a8a64ed110fb35317c4d848973ec5259bd180f8f74a621` |
| `check_economy` | 0 | 103.6 | `cddc62c49754c94b68c1dd1afe86fce65269a922d0fbf90f85b48fdecf3cb703` |
| `check_fans` | 0 | 111.0 | `f02313edd04c6055da5c0575e9ac7ca6149ce01f94c37db10999b1af74d34f08` |
| `check_interactions` | 0 | 50.1 | `1a4a6e22ced60773db7ff401f064e13b6ec2a3f99962914bc9c6fe64ef901293` |
| `check_living` | 0 | 296.7 | `7269e35ad5c3a861c78212e21282a311e8e28dadfbd2bbff2ecbf022bef37f41` |
| `check_phase0` | 0 | 0.0 | `5f8917a9fbcb894748c4466d43d4c3e9eaf6079bfc949d19e427b858491089e2` |
| `check_phase1` | 0 | 2.4 | `86a0ac3cfdd593e6a2ac6ac6292b45c11d029b8d4d6464c0f387864f37af42bd` |
| `check_phase2` | 0 | 399.7 | `ed40f46687514ec9d66d468cb2c7c2544cf99088e822d2497a71c4ba957b11e8` |
| `check_rosters` | 0 | 1.0 | `5e544eaaa91255eecfcdc847ebcfdb4cb607742797e4feab5bd8404017ea6bef` |
| `check_rulebook` | 0 | 0.0 | `fc0c8f188e126700789dedd00e36031a37ceca9adddb315a2219e4672fcb8e18` |
| `check_service` | 0 | 1.9 | `c432af132e0cadbaf802137f8492814f07ccd82dfc81c7f2645eb491fde74b63` |
| `check_service_pay` | 0 | 30.6 | `3d6b637c5ae99ab00e4c8be92dd719f3088c3efadf31737f5ce6a86a2548905e` |
| `check_staff` | 0 | 28.4 | `799f9539f21ac519f7a322425aef777ab37007cda113f2440e7a7143f3d006de` |
| `check_store` | 0 | 586.2 | `5be3409dd59bdd683c9aa09123847cbfa2bf516711d15e6b57e5b845a6789a6b` |
| `check_tables` | 0 | 141.3 | `12a0e46453462695ae4691b93b79180448822a90f2e940fee7656bd8b35e5ee5` |
| `check_tiebreaks` | 0 | 5.8 | `486fb44316815cf5abca32820dc9a4fe59eb1c16d969c2ca73b0c220112881b6` |
| `check_ties` | 0 | 5.0 | `a575037460d6f1686c99b661f9f96a7955d89c99f02f6f9b0e535ebe3f8be040` |

## Publication and documents

Step 6b is committed locally and retained in dfl_step6b_verified.bundle. GitHub step6-service remains at 31eedf0 (Step 6a plus documentation) pending an explicitly approved push; main remains unchanged. README, the decision log, handoff, rulebook status, current cap/fairness studies and seven relevant Drive documents were reconciled. The historical Step 6a report records its earlier scope and the later IR correction. The synthesis introductory source link was repaired and verified.
