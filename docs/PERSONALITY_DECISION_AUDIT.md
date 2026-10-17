# Five-meter personality and decision-contract audit
Date: 2026-10-17
Status: implementation proposal; no gameplay behavior changed
Scope: DFL character models, decision guards, agent inputs, stand-in policies

## Design authority and supersession
The Commissioner's latest five-meter and hidden X-factor decisions supersede contradictory earlier design assumptions. Do **not** preserve archetype-constrained trait selection, fixed soul-based personality limits, or trait-string decision policies merely for backward compatibility. Existing code may be reused as infrastructure, but conflicting behavioral rules must be replaced. Preserve historical design documents as records and mark them superseded instead of silently rewriting the past.

## Confirmed source observations
- `engine/cards.py` defines player and coach cards with `trait`, `wants`, `fears`, `pressure`, and other character properties. Player personality is selected from an archetype-constrained family, with perception and confidence influencing the expressed trait.
- `engine/living.py` describes changing ratings, self-perception, and a core personality bounded by the character's soul.
- `engine/agents.py` explicitly describes `StandIn` as a scripted substitute for real model agents. Several choices maximize perceived utility or follow trait-specific hardcoded policies.
- `engine/decisions.py` defines the legal-option/agent-view boundary. That boundary should remain the authoritative enforcement point.
- These observations do **not** establish a universal five-meter decision policy or a private X-factor implementation. This is a scoped source audit, not a claim that every repository file has been inspected.

## Approved design constraints to implement
1. Every in-world character has exactly five decision-driving personality meters. Other card fields may describe ability, knowledge, state, history, or presentation but must not silently become additional personality meters.
2. Ordinary meter values use a 1–100 scale.
3. At creation, approximately 5% of characters receive one private X-factor: an existing personality dimension amplified to a 1–200 range. It may be harmful as well as beneficial. A value of 100 is normal for the amplified dimension, not automatically exceptional.
4. Neither the X-factor flag nor its numeric value may be exposed to in-world agents, public cards, or narrative viewpoints. Engine-only diagnostics may inspect it. Observers may infer unusual behavior from visible evidence.
5. Character decisions use imperfect information, bounded legal options, and the existing guard/fallback behavior.
6. The currently running season is observational. Durable historical persistence is an Alpha concern, not a prerequisite to this work.

## Decisions that require explicit engineering definitions, not guesses
- Names and semantics of the five meters (not yet specified in the inspected sources; do not invent them). Do not assume the existing `trait` string, ratings, pressure thresholds, or wants/fears are equivalent to the five meters.
- Whether an X-factor is represented by one amplified meter or a separate private multiplier applied to an ordinary meter. Whichever representation is chosen must not introduce a sixth decision-driving meter.
- Whether the 5% assignment is independent per character or sampled to an exact quota per generated population. Test the chosen interpretation statistically.
- Meter initialization distributions, lifecycle changes, and precise influence on different decision types.
- Migration of old card constructors, deterministic seeds, serialized snapshots, and existing fairness checks. Compatibility is an engineering tool, not a reason to keep superseded psychology. The observational season can be regenerated.

## Implementation sequence
### P1: Inventory and contract
- Enumerate all character types and constructors (players, coaches, coordinators, GMs, CEOs, fans/media if treated as individual characters).
- Enumerate all personality-like fields and all agent-facing serializers, especially `DecisionPoint.public()`.
- Enumerate all decision kinds, their current scripted policies, and the available perceived evidence.
- Write a versioned personality schema with exactly five named dimensions, invariant checks, and a private X-factor representation.
- Add a test fixture that instantiates every character category.

### P2: Safe character creation
- Add deterministic, per-character meter initialization without consuming the football engine's random stream.
- Add deterministic 5% X-factor assignment, independent of request order.
- Replace superseded archetype/personality decision rules. Retain APIs only when they serve the new contract and simplify testing.
- Add invariants: five meters exactly, ordinary 1–100 bounds, one amplified dimension at most, X-factor 1–200, no hidden-field serialization.

### P3: Decision integration
- Keep the legal-option guard authoritative and preserve invalid-choice fallback.
- Feed agent policies character-appropriate, **non-secret** descriptions or perceptions. Never expose X-factor values or privileged ground truth.
- Introduce personality influence in a small, measurable decision category before extending to all kinds.
- Compare scripted baseline and personality-aware policy on the same seeds.

### P4: Falsification and balance
- Contrast low/high meters under identical context and measure meaningful decision changes.
- Hold personality fixed, change only perceived information, and measure appropriate responses.
- Test harmful and beneficial X-factor cases, hidden-field leaks, deterministic generation, and character lifecycle continuity.
- Rerun fast and slow suites and the 13 fairness bands after any behavioral change.
- Report effect sizes and failures, not just pass counts.

## Acceptance criteria
- All character categories have the same five-meter contract, or any non-character exception is explicitly documented.
- No in-world API, card, agent payload, narrative input, or public response leaks the X-factor flag or number.
- Tests prove reproducibility and that personality actually influences decisions.
- Existing simulation invariants and fairness bounds still pass.
- A reviewer can trace why a decision was made using privileged **developer-only** diagnostics without confusing that trace with what the character knows.

## Deployment policy
This audit is documentation-only. No live deployment, engine behavior modification, or server restart is part of this change.
