# Agent Guide

This project is intended for Pi.dev/Codex-style agent development.

## Read First

1. `README.md`
2. `MVP.md`
3. `To-Do.md`
4. `docs/REQUIREMENTS.md`
5. `docs/ARCHITECTURE.md`
6. `docs/DECISIONS.md`

## Rules

- Implement small tasks only.
- Keep deterministic clustering separate from Ollama naming.
- Do not make writes to Immich unless `--no-dry-run` is explicitly used.
- Keep multi-user support intact.
- Preserve idempotency.
- Update Markdown docs when behavior changes.

## Recommended First Prompt

```text
Read all docs. Implement To-Do items 1 and 2 only. Do not implement clustering yet.
```
