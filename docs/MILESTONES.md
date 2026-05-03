# Milestones

This repository is currently an MVP starter: core module boundaries exist, but most behavior is still thin or placeholder-level. The goal is to grow it in small, reviewable increments while keeping Immich writes safe and clustering deterministic.

## Current State Summary

Implemented / present:

- Python package and Typer CLI (`memory-engine`).
- YAML config loader and example config.
- Basic Pydantic models for assets, clusters, and proposals.
- Read-only Immich scan path started: multi-user API keys, metadata search pagination, asset normalization, `output/assets.json`.
- Simple time-only clustering stub.
- Basic proposal JSON generation.
- Ollama client wrapper exists but is not integrated.
- Docker and docker-compose workflow with `.env.example` and config env interpolation.
- Small pytest suite for geoutil, config validation, clustering, and Immich normalization/client behavior.
- GitHub Actions Docker build/test workflow with GHCR publish on `main` only.

Important gaps:

- Clustering does not yet enforce the MVP decision that time and location must match for normal merges.
- Home-location rules are mostly not implemented beyond a simple majority flag.
- Proposal IDs and confidence are still simplistic.
- Markdown report generation is missing.
- Apply/idempotency workflow is missing.
- Debug output and raw-sample capture are minimal.

## Milestone 0 — Foundation Hardening

Goal: make the starter reliable enough for iterative development.

Scope/status:

- [x] Add `.env.example` matching `config.example.yaml`.
- [x] Document Docker-only setup, test, scan, and troubleshooting commands.
- [x] Add CI Docker build/test workflow and GHCR publish for maintainer testing.
- [x] Document supported Immich API version / endpoint assumptions: Immich 2.7.5 metadata search with `x-api-key`.
- [x] Add stronger scan-start config validation for required fields/env vars.
- [x] Ensure Docker image builds and `memory-engine --help` is a documented smoke test.

Definition of done:

```bash
PYTHONPATH=src python3 -m pytest -q
docker compose build
```

passes, and a new user can configure the read-only scan from docs without guessing env var names.

Status: implemented as Docker-only foundation hardening. `.env` is required, ignored, and documented as never-to-commit.

## Milestone 1 — Read-only Immich Scan

Goal: produce normalized assets from all configured Immich users without writing to Immich.

Scope:

- Verify Immich metadata search endpoint against the target server version.
- Keep `x-api-key` authentication only.
- Support all configured users and preserve owner names.
- Fetch all pages safely for ~10k assets.
- Filter by CLI date range.
- Normalize image/video assets into `Asset`.
- Handle missing GPS/exif safely.
- Write deterministic, sorted `output/assets.json`.
- Add useful error messages for missing config/env/API failures.

Definition of done:

```bash
memory-engine scan --config config.yaml --from 2025-01-01 --to 2025-12-31
```

writes assets with `id`, `owner`, `taken_at`, optional `latitude`/`longitude`, `type`, and no Immich writes occur.

Status: mostly implemented; needs live Immich verification and hardening.

## Milestone 2 — Deterministic Event Clustering

Goal: turn normalized assets into explainable event clusters.

Scope:

- Sort merged assets by timestamp.
- Implement merge decisions using time gap AND GPS distance when GPS is available.
- Use GPS-less fallback as time-only with lower confidence / explicit reason.
- Enforce `min_assets_per_event` and `max_event_duration_days`.
- Merge assets from all users before clustering.
- Count participants per cluster.
- Save `output/clusters.json`.
- Add tests for edge cases: far-apart same-time photos, close-location multi-user event, GPS-less fallback, event duration limit.

Definition of done:

Clusters do not combine separate locations just because timestamps are close, and every cluster has participant counts plus enough metadata to explain why it exists.

## Milestone 3 — Home-Location Rules

Goal: avoid bad mega-clusters such as months of home photos.

Scope:

- Detect home assets using configured home lat/lon/radius.
- Outside home: use normal time + location merge.
- Inside home: do not create long-running automatic clusters.
- Only create home events if `inside_home_min_assets` is reached.
- Only create home events if duration is below `inside_home_max_duration_hours`.
- Record home-specific reasons/debug decisions.
- Add tests for large home mega-cluster prevention and valid short home event creation.

Definition of done:

A dense month of home photos does not become a proposal, while a short, photo-heavy home event can still be proposed.

## Milestone 4 — Proposal Generation + Markdown Review

Goal: create reviewable album suggestions from clusters.

Scope:

- Generate stable proposal IDs from deterministic cluster content.
- Calculate confidence from asset count, GPS strength, participants, duration, and home/GPS-less penalties.
- Generate human-readable reasons.
- Write `output/proposals.json`.
- Write `output/proposals.md` with title, period, participants, location info, confidence, reasons, and apply commands.
- Keep proposal generation separate from Ollama.
- Add tests for ID stability and confidence/reason behavior.

Definition of done:

A user can review `output/proposals.md` and understand why each album was suggested before applying anything.

## Milestone 5 — Optional Ollama Naming

Goal: improve titles/descriptions without affecting grouping.

Scope:

- Add optional Ollama naming pass behind config flag.
- Prompt for short title candidates and one description based only on cluster metadata.
- Validate output shape and length.
- Fall back to deterministic title on errors/invalid output.
- Never let LLM output change cluster membership or asset IDs.
- Add mocked tests for success, timeout/error, and invalid response fallback.

Definition of done:

With Ollama disabled or unavailable, proposals are still deterministic and complete. With Ollama enabled, only title/description improve.

## Milestone 6 — Apply to Immich + Idempotency

Goal: safely create albums from reviewed proposals.

Scope:

- Keep `apply` dry-run by default.
- Load proposal by stable ID from `output/proposals.json`.
- Show exactly which album/assets would be written in dry-run.
- Implement `--no-dry-run` album creation.
- Add assets to created album.
- Store local created-album mapping, e.g. `output/state/created_albums.json`.
- Detect existing created mappings and avoid duplicates.
- Prefer idempotent title prefix from config, e.g. `Vorschlag: `.
- Add tests with mocked Immich API.

Definition of done:

Repeated apply runs for the same proposal do not create duplicate albums, and no writes happen unless `--no-dry-run` is explicit.

## Milestone 7 — Debuggability + Operational Polish

Goal: make real-library runs understandable and safe.

Scope:

- Add `--debug` flag.
- Optionally save raw sample responses with secrets excluded.
- Log clustering decisions and rejected cluster reasons.
- Add summary stats: assets scanned, GPS coverage, clusters created/rejected, proposals generated.
- Handle partial user/API failures clearly.
- Add performance sanity checks for ~10k assets.
- Add README troubleshooting section.

Definition of done:

When a proposal is surprising or missing, the user can inspect output/debug files to understand why.

## Future / Post-MVP

- Recurring events such as birthdays, Christmas, annual trips.
- Highlight/best-photo selection.
- Import-source detection for photographer/friend uploads.
- Person/faces as naming/confidence signal, not person-only albums.
- Timeline UI or integration with a review frontend.
- More advanced geocoding / place naming.
