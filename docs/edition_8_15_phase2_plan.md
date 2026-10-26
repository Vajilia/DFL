# Edition 8.15 — Phase 2 implementation lane (working, not released)

Authority: [DFL Design Document Edition 8.15](DFL_Design_Document_Ed8.15.md).
Date: 2026-10-26. Development head: `audit/ed8-15-phase1`, PR #42 (draft).
The human owner authorizes work through Phase 2; this does **not** approve
constitutional defaults or a production deployment.

## Hard boundary

Phase 1 is not complete: consult `ed815_phase1_gates.json`. In particular,
the six §20 pre-founding choices, atomic rule register, versioned NFL baseline,
production route isolation, full SLOW suite, and year-zero rehearsal are not
cleared. A passing legacy test is not evidence of Edition 8.15 compliance.

Historical `engine/phase2_report.py` and `reports/phase2_report.md` were
computed with superseded `engine/rules.py` economics, old calendar and
old exile/standings logic. Do **not** cite their plausible NFL-looking
numbers as an Edition 8.15 calibration result.

## Phase 2 objective

Develop an isolated, deterministically replayable **season transaction
pipeline** that can accept legitimate simulation outcomes for all 40 active
clubs and eight ambassadors without writing, resetting, or publishing the
live league. Rule decisions flow only from the frozen Edition 8.15 document.
Empirical football rates are independently versioned model parameters,
expressed per play, per snap, per player-exposure, or per team-season
rather than forced league totals.

### Modules and acceptance checks

| Deliverable | Required evidence | Status |
|---|---|---|
| Frozen fixtures, 48 stable club identities, eight-year rotation | Founding validator and long-cycle cross-check | Isolated, tested |
| Reversible economy transactions and 48-club snapshot/handoff | SQLite rollback, cap, trade/waiver/draft tests | Isolated, tested |
| Append-only authoritative event history | Hash-chain/restart/anti-mutation checks | Isolated, tested |
| Fixture-bound game-final ingestion | Reject wrong fixture, negative score, duplicate, cross-season event; 360-result replay and restart | New check; CI pending |
| Deterministic full-season engine runner | Independently reproduce game output and event hashes from explicit seeds across restart | Not started |
| People, staff and player creator migration | Preserve IDs, provenance, hidden state and no stored OVR; prohibit narrative from mutating engine | Not started |
| NFL-reference rate calibration | Record fixed reference period, units, denominators, confidence bands and stress/fairness sweep results | Not started |
| Active and Ambassador playoffs / honors | Versioned bracket, Bowl selection, elections, awards and chronology tests | Not started |
| Read-only site bridge | Release-cursor embargo, no privileged controls, no private fields, tested public pages | Isolated preview only |
| Year-zero to year-one rehearsal | Complete simulated league year, crash/restart, handoff and no secrets; complete FAST/SLOW tests | Blocked by upstream gates |

### Promotion criteria

1. Preserve Phase 1's normative-gate failures as failures while decisions remain open.
2. Test the Edition 8.15 kernels under reproducible independent seeds, including adverse inputs.
3. Demonstrate league state, event log, viewer output and handoff reconstruct identically
   after a cold restart. No partly committed result may become public.
4. Publish a report separating **verified**, **untested**, and **proposed** claims,
   including rates with per-exposure denominators and appropriate sample sizes.
5. Obtain the owner's specific release approval and backup/rollback review before
   changing `main`, `step6-rebuild`, the live website or its database.

No test harness result shall be represented as the first official DFL season.
