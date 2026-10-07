# Step 6a verification (historical checkpoint)

## Scope and outcome

All 18 recovered Step-5 baseline check scripts passed at `fcada34`. All seven selected changed-branch scripts passed against the Step 6a accounting code from `744678d`: service, rulebook, phase0, phase1, rosters, store and living. This is a full baseline suite plus targeted Step 6a verification, not a claim that all 19 scripts were rerun on the modified branch. Subsequent changes are documentation and rule-description corrections only; the rulebook check was rerun after those corrections. Compilation and whitespace checks pass.

The five service test cases cover accrued/credited boundaries, IR and inactive rosters, practice-squad exclusion and promotions, releases and club changes, duplicate weeks, Ambassador and postseason distinctions, expired-contract classes and exile, rookie initialization, both game engines and partial-year save/resume. The store check compares every serialized card/body/list/counter through a 20-to-40-season resume, and also tests snapshots, agents and return to autopilot. The living check exercises 60-season honors/Hall behavior and deterministic replay.

## Regression and fairness

| Seed | Seasons | Expected and observed fingerprint |
| --- | --- | --- |
| 33 | 40 | `c66f3a3cf3773dc8` |
| 5 | 40 | `e17ae5e4aa110fcd` |
| 21 | 40 | `48636918634fa008` |

These Step 6a runs match the existing golden values exactly. No fingerprints were regenerated, and no model dials or fairness bands changed. The recovered baseline Phase 2 check passed all 13 fast-engine fairness bands and both-engine talent/parity/tier stability checks. The historical cap and both-engine fairness reports remain Step-5 studies; they were not regenerated or relabeled as new Step 6a studies.

## Per-script evidence

| Checkout | Check | Exit | Runtime (seconds) | Log SHA-256 |
| --- | --- | --- | --- | --- |
| Step-5 baseline | `check_agents` | 0 | 47.5 | `e09e550edd256f65c0960bc1aa9ba7ff62e20505ddea3cb0cf8382fb47076682` |
| Step-5 baseline | `check_cards` | 0 | 15.7 | `90a5b413cffdc8e30d6488da7598f0467b9b84a65cef8a2f6bbee892e79ec4f4` |
| Step-5 baseline | `check_contracts` | 0 | 8.3 | `30fdbbd801d2d0e0ed9bf11ad12f1992dec01f9df845aca1b2fb00fe61ab1507` |
| Step-5 baseline | `check_decisions` | 0 | 168.1 | `dda724aaef92ca204ddcdceebfa1f82e3054f5cd4c21f8f9cddacd68ce8fa738` |
| Step-5 baseline | `check_economy` | 0 | 89.3 | `a5ab53cccb42029fb4d72dd55905cfdef2f6d9d2a131760ba2dc1b45aa448aaf` |
| Step-5 baseline | `check_fans` | 0 | 101.9 | `ee7181adb343469534db2645fc6e4e42890b507beea30e8e706a49c92a25ffcb` |
| Step-5 baseline | `check_interactions` | 0 | 45.3 | `c5fdceb8e7b181fa68b4928e4b7e237c54f58cc17c11139b1a675f9a167a9471` |
| Step-5 baseline | `check_living` | 0 | 246.9 | `928b8609315717a33759cc927fe2646832bde169552ed615b5b25a5d4b6c0377` |
| Step-5 baseline | `check_phase0` | 0 | 0.0 | `5f8917a9fbcb894748c4466d43d4c3e9eaf6079bfc949d19e427b858491089e2` |
| Step-5 baseline | `check_phase1` | 0 | 2.3 | `86a0ac3cfdd593e6a2ac6ac6292b45c11d029b8d4d6464c0f387864f37af42bd` |
| Step-5 baseline | `check_phase2` | 0 | 367.1 | `35ce7eb74b955e920817ed8f3aeddc6113ed7bf95596562db1889618b37862d4` |
| Step-5 baseline | `check_rosters` | 0 | 0.9 | `5d9030fef42b10111198bd43acffb88524a94457c2411f73ac16690b588a1526` |
| Step-5 baseline | `check_rulebook` | 0 | 0.0 | `d6d52ae6f78e31332ada71612b029022c8a397acfef3b0781456f1c8f097e4fc` |
| Step-5 baseline | `check_staff` | 0 | 26.4 | `108b2d92c04c77571495fcffe9cb2c9fdc558a5e36364ec30554dc05b246902d` |
| Step-5 baseline | `check_store` | 0 | 486.9 | `0d6ef90afd69b30d6a4e8b8ac90d51857684a9dd8cd15bb2cf4ee95b79f85cd4` |
| Step-5 baseline | `check_tables` | 0 | 132.7 | `feb196bb27b3238a4061681dd8f6c3d7888c403b2ebcce901228d6de0e3a90bd` |
| Step-5 baseline | `check_tiebreaks` | 0 | 5.6 | `32156ba95604f6d06a74a8777689ecd4e8fa6efa1df217776c623e5b01ba90b1` |
| Step-5 baseline | `check_ties` | 0 | 4.9 | `a575037460d6f1686c99b661f9f96a7955d89c99f02f6f9b0e535ebe3f8be040` |
| Step 6a | `check_service` | 0 | 1.8 | `cf46826d0229af2cf660a41dc3d16b6147ee707fd199ed5612d0fb7baecd4857` |
| Step 6a | `check_rulebook` | 0 | 0.0 | `c8562512fe4a2d5f1290af2eafe54511645f9fe6d2b6d4612ea6e990b2bbe713` |
| Step 6a | `check_phase0` | 0 | 0.0 | `5f8917a9fbcb894748c4466d43d4c3e9eaf6079bfc949d19e427b858491089e2` |
| Step 6a | `check_phase1` | 0 | 2.3 | `86a0ac3cfdd593e6a2ac6ac6292b45c11d029b8d4d6464c0f387864f37af42bd` |
| Step 6a | `check_rosters` | 0 | 0.9 | `5d9030fef42b10111198bd43acffb88524a94457c2411f73ac16690b588a1526` |
| Step 6a | `check_store` | 0 | 581.7 | `2acb62e52600d70aa0b6bf0d9fa84f903efb997f4fa621a658328e0527d5b699` |
| Step 6a | `check_living` | 0 | 296.3 | `84b1967d87386c1b8a9561af22f9936dec5de020c4503af68ab0e942213123cd` |

## Implementation boundary and publication

The rulebook reports 32 matching constant rows, 1 differs and 14 missing. `fa.classes` is a partial mechanism: service and expiration classification are built, while tenders and rights enforcement, minimum-pay integration and practice-squad eligibility integration remain pending. Historical service uses a one-time founding/old-save estimate. NFI/PUP, suspensions, holdouts and injury settlements are not modeled. These limitations are recorded in the README, decision log, handoff and Drive synthesis/status copies.

At this historical checkpoint, GitHub `step6-service` was at snapshot `13702e1`, whose tree `919676c7271ec18e4cb730a09c085f0178471ad9` matches local `744678d`. GitHub main is unchanged at `02490ab`. This verification/documentation follow-up is committed locally and retained in the verified bundle; a further GitHub push requires explicit approval under the project handoff rule.

The Drive handoff, README, decision log, rulebook status and synthesis were updated. Existing heading/list/table topology was preserved and checked on readback. The original Commissioner reference and historical cap/fairness studies retain their source content. The separate historical Claude artifact was not edited.

The Step 6a documentation follow-up was subsequently published as `31eedf0`, matching local `dcf1e7e`. For the newer salary/eligibility increment, see `verification_step6b.md`.

Primary-source correction in Step 6b: the CBA excludes IR from salary-credited service. Step 6a used a shared roster/IR counter for both clocks; that historical implementation was corrected before Step 6b final verification.
