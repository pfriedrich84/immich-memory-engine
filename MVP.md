# MVP Plan

## Product Vision

Immich Memory Engine proposes meaningful memories from an Immich library: events, album suggestions, and eventually timelines/highlights. The MVP focuses on reliable event detection from time and location, with family/multi-user support.

## MVP Scope

- Read assets from two Immich users via separate API keys
- Merge assets before clustering when time and location match
- Treat home-location differently to avoid huge home clusters
- Generate JSON + Markdown reports
- Optionally use Ollama for better titles/descriptions
- Apply selected proposals to Immich as albums with prefix `Vorschlag: `
- Dry-run by default
- Avoid duplicate albums across repeated runs

## Out of Scope for MVP

- Deduplication or best-photo selection
- Full UI
- Direct Immich DB access
- Person-only albums
- Automatic deletion or modification of original photos

## Important Principle

Clustering must be deterministic and explainable. Ollama may improve names/descriptions, but it must not be the source of truth for grouping.
