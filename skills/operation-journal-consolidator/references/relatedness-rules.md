# Relatedness Rules

## Purpose

Classify whether the current change belongs to the latest operation or to a new one.

## Scoring

Start at `0` and sum:

- `+30` same context as latest operation (`refatoracao` or `legado`).
- `+40` same primary objective as latest operation.
- `+20` at least 60% of changed files overlap latest operation files.
- `+15` same component/path family (for example both in `docs/sphinx/source/api/`).
- `+10` same execution window/session with no context switch.
- `-50` context differs from latest operation.
- `-30` introduces a new objective or a second independent deliverable.
- `-40` mixes unrelated domains in one commit.

Decision:

- score `>= 50`: consolidate in latest operation.
- score `< 50`: create a new operation.

## Hard Rule Override

Always create a new operation when a hard stop from SKILL.md is triggered, even if score is high.

Context mismatch is a hard stop.

## File-Based Heuristics

Prefer consolidation when all changes are within these families and the latest operation already covers them:

- `docs/sphinx/source/api/generated/`
- `docs/sphinx/source/api/index.rst`
- `docs/sphinx/source/conf.py`
- `docs/operacoes/` and related `docs/sphinx/source/operacoes/` mirrors
- `.specs/project/` when latest operation context is `refatoracao`
- `.specs/codebase/` when latest operation context is `legado`

Prefer new operation when changes cross into independent workstreams, such as:

- runtime pipeline scripts
- environment bootstrap behavior
- CI workflow policy changes unrelated to the same doc objective
- mixes `refatoracao` and `legado` context in one commit
