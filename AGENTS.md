# DFL AI collaborator orientation

**Read this before editing anything.** This repository is the Diamond Football League (DFL), a fictional autonomous 48-franchise American football simulation. Its owner/operator is the final authority on project design and deployment. Do not interpret in-world Commissioner authority as permission to modify production infrastructure.

## First five minutes
1. Read `PROJECT_STATUS.md`, `docs/REPOSITORY_MAP.md`, and `docs/GLOSSARY.md`.
2. Read `docs/decisions.md`, `engine/rulebook.py`, and `engine/rules.py` for the existing rulebook and its provenance. `docs/DFL_Reference_Corrected.txt` explicitly warns that it is **not** authoritative.
3. Check the current GitHub branch, its head commit, and the deployment configuration. As of 2026-10-15, `main` and `step6-rebuild` point at the same commit; the deploy scripts still default to `step6-rebuild`, which is kept as a mirror of `main`. **Verify again** before work.
4. Read the relevant source and its `engine/check_*.py` tests. Do not assume a feature is absent because it was absent from an earlier roadmap.
5. Report observations as **verified**, **untested**, or **proposed**. Ask for a decision when project requirements conflict.

## Authority and safety
- The human project owner approves DFL constitutional changes, changes to canonical data, branch promotions, and production deployments.
- Existing code and docs may be incomplete or contradictory. Never silently resolve a constitutional conflict by changing a rule.
- Distinguish immutable scheduling constraints and approved league rules from numerical simulation models, experimental ideas, and prose descriptions.
- The simulation's agents select among legal actions; they must not manufacture outcomes or rewrite game results.
- The media reports events and can influence perception; it must not fabricate events as historical facts.
- Never reset or overwrite live league state. No production deploy, destructive git operation, database migration, service restart, or server change without explicit approval and backup/rollback planning.
- Avoid secrets in prompts, commits, logs, issues, or pull requests.
- Prefer small branches and reviewed PRs. A new assistant's default is **read-only** until a specific task is approved.

## How to validate
- `python engine/run_checks.py --list` shows fast and slow tiers.
- `python engine/run_checks.py` runs fast checks; `python engine/run_checks.py --all` runs both tiers.
- Run focused tests first, then appropriate tiers; document which tests were actually executed and on what revision. Do not claim passing tests without running them.
- Validate scheduling against `data/schedule_2000.csv` and the latest owner-approved founding workbook when available. A fixture comparison is not itself proof of every invariant.
- `engine/golden_fingerprints.json` and fairness checks are regression signals; explain and obtain approval for intentional outcome changes.

## Development lanes (proposed, not yet implemented)
- **Truth:** approved constitutional/specification baseline and separately identified production release.
- **Beta:** isolated experiments, with separate test state.
- **Alpha:** candidate release, acceptance checks, backup/rollback plan.
- Promotion to production requires explicit owner approval. Do not assume branches with these names exist.

## Handoff
Record changed files, decisions, open questions, test commands/results, branch/commit, deployment status, and next safe action in the PR description or an issue. Keep `PROJECT_STATUS.md` current when a milestone is accepted. Preserve rejected alternatives and reasons in `docs/DECISION_LOG.md`. Do not confuse a proposal with an accepted decision.
