---
name: operation-journal-consolidator
description: Decide whether a documentation change should update the latest operation diary entry or create a new operation. Use when working with docs/operacoes/*.md and docs/sphinx/source/operacoes/*.rst, especially when the user wants to avoid diary bloat, merge related steps, or keep operation granularity consistent.
---

# Operation Journal Consolidator

## Overview

Use this skill to choose between consolidating changes into the latest operation or opening a new operation number, then apply the matching documentation workflow.

## Workflow

1. Classify context first: `refatoracao` or `legado`.
2. Inspect the current goal and changed files.
3. Compare with the latest operation scope and latest operation context.
4. Apply the decision rules in `references/relatedness-rules.md`.
5. Execute one mode only: consolidate or create new operation.
6. Report the decision with short, concrete reasons.

## Consolidate Last Operation

Use this mode when changes are clearly incremental to the latest operation.

Precondition:

- Current context must match the latest operation context.

1. Update `docs/operacoes/<last>.md`:
- Add an `## Incremento` section with date and what changed.
- Keep one coherent narrative for the same objective.
- Keep or add explicit line: `Contexto: refatoracao` or `Contexto: legado`.

2. Update `docs/sphinx/source/operacoes/<last>.rst`:
- Adjust `Resumo`, `Efeito principal`, and `Arquivos de interesse`.
- Keep links valid for the same detailed page.

3. Keep `docs/sphinx/source/detalhes/<last>.md` unchanged unless include path changed.

4. Do not create new numbered operation files.

## Create New Operation

Use this mode when scope or intent diverges from the latest operation.

1. Create next numbered files:
- `docs/operacoes/<next>.md`
- `docs/sphinx/source/operacoes/<next>.rst`
- `docs/sphinx/source/detalhes/<next>.md`

2. Add explicit context in the new operation:
- `Contexto: refatoracao` or `Contexto: legado`

3. Update `docs/sphinx/source/operacoes/index.rst`.

4. Preserve previous operation files as historical records.

## Hard Stops

Never consolidate when any of the following is true:

- A new subsystem or domain is introduced (for example: docs-only to runtime/test infra).
- The change introduces a different objective than the latest operation.
- The previous operation is finalized and this step requires separate auditability.
- The context differs from the latest operation (`refatoracao` vs `legado`).

## Output Contract

Always provide:

- Decision: `consolidate-last-operation` or `create-new-operation`.
- Context: `refatoracao` or `legado`.
- 2-3 reasons tied to files/objective.
- Exact files updated.
