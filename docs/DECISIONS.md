# Decisions

## Repository Name

Use `immich-memory-engine`.

## Python Package Name

Use `memory_engine`.

## CLI Name

Use `memory-engine`.

## Docker Container Name

Use `immich-memory-engine`.

## Multi-User Support

Minimum MVP uses Option A: separate API keys for each Immich account.

## Merge Rule

Merge requires time AND location match. Time overlap alone is not enough.

## Home Photos

Home photos are not automatically merged into large events. Home-location events need stricter conditions.

## Person Albums

Do not create person-only albums in MVP. Persons may become a future signal for naming/confidence.

## Deduplication

Do not deduplicate in MVP. Keep all photos.

## External Photos

Upload external photos normally into Immich, preferably into an import album such as `Import: Hochzeit Fotograf 2026`. The engine treats them as normal assets.

## Dry-Run

Dry-run is the default for apply operations.

## Idempotency

Repeated runs must not create duplicate albums.
