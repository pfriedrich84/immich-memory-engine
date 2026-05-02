# Immich Memory Engine

Turn your Immich photo library into structured memories.

Immich Memory Engine is a local-first MVP for automatic event detection, album suggestions, and timeline-style memory generation using time, location, multi-user signals, and optional Ollama-generated titles/descriptions.

## MVP Goal

Create useful Immich album proposals from roughly 10k photos across two Immich accounts, while avoiding bad mega-clusters such as months of home photos.

## Core Features Planned

- Multi-user Immich scan via separate API keys
- Time + GPS clustering
- Home-location special handling
- JSON and Markdown proposal reports
- Optional Ollama naming
- Dry-run by default
- Idempotent album creation with prefix, e.g. `Vorschlag: ...`
- External photos workflow via normal Immich upload

## Quick Start

```bash
cp .env.example .env
cp config.example.yaml config.yaml
# edit both files

docker compose run --rm memory-engine scan --config /app/config.yaml --from 2025-01-01 --to 2025-12-31
```

## Example Commands

```bash
# Scan assets and generate proposals
memory-engine scan --config config.yaml --from 2025-01-01 --to 2025-12-31

# Review generated proposals
memory-engine review --input output/proposals.json

# Dry-run album creation, default behavior
memory-engine apply proposal_123 --dry-run

# Actually create album in Immich
memory-engine apply proposal_123 --no-dry-run
```

## Important Status

This repository is an agent-ready MVP starter. It contains the structure, docs, initial CLI and implementation stubs. The first real development target is Milestone 1: a working Immich API scan with pagination and normalized asset export.

## Recommended Agent Workflow

Use Pi.dev/Codex with small prompts. Start with:

```text
Read README.md, MVP.md, docs/REQUIREMENTS.md, docs/ARCHITECTURE.md, docs/MILESTONES.md, docs/DECISIONS.md and To-Do.md.

Implement To-Do item 1 and 2 only:
- Immich API client with pagination
- date range filtering
- multi-user API key support from config/env
- normalize assets into the Asset model
- write output/assets.json

Do not implement clustering yet.
Add or update tests where useful.
Keep Docker workflow working.
```
