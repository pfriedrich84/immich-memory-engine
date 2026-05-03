# To-Do.md

## Goal

Build an MVP for automatic Immich album suggestions using multi-user asset scans, time/GPS clustering, home-location rules, optional Ollama naming, and safe album creation.

# HIGH Priority — MVP Core

## 1. Immich API Client

- [x] Implement httpx client
- [x] Authenticate via `x-api-key`
- [x] Support multiple configured users/API keys
- [x] Implement asset pagination
- [x] Filter by date range
- [x] Save `output/assets.json`

Definition of done:

```bash
memory-engine scan --from 2025-01-01 --to 2025-12-31
```

produces normalized assets with `id`, `owner`, `taken_at`, optional GPS fields.

## 2. Data Normalization

- [x] Map Immich asset JSON to `Asset`
- [x] Handle missing GPS safely
- [x] Handle image/video type
- [x] Preserve owner name
- [x] Add tests for field mapping

## 3. Time + GPS Clustering

- [ ] Sort by timestamp
- [ ] Implement Haversine distance
- [ ] Merge only when time AND location match
- [ ] Support GPS-less assets using time-only fallback with lower confidence
- [ ] Save `output/clusters.json`

## 4. Multi-User Merge

- [ ] Merge assets from all users before clustering
- [ ] Count participants per cluster
- [ ] Add confidence bonus for multi-user events

Example:

```json
"participants": {
  "paul": 23,
  "wife": 19
}
```

## 5. Home-Location Logic

Outside home:

- [ ] Normal time + location merge

Inside home:

- [ ] Do not automatically merge long-running home photos
- [ ] Only create home event if `inside_home_min_assets` is reached
- [ ] Only create home event if duration is below `inside_home_max_duration_hours`

Goal: avoid albums like `Vorschlag: Zuhause März 2025`.

## 6. Proposal Generator

- [ ] Convert cluster to proposal
- [ ] Generate stable proposal ID
- [ ] Calculate confidence
- [ ] Generate reasons
- [ ] Save `output/proposals.json`

## 7. Markdown Report

- [ ] Generate `output/proposals.md`
- [ ] Include title, period, location, participants, reasons, command examples

## 8. Ollama Naming

- [ ] Add Ollama client usage
- [ ] Prompt for 3 short titles + one description
- [ ] Validate/fallback on invalid output
- [ ] Keep clustering deterministic

## 9. Apply to Immich

- [ ] Load proposal by ID
- [ ] Create Immich album with configured prefix
- [ ] Add assets to album
- [ ] Dry-run default
- [ ] `--no-dry-run` actually writes

## 10. Idempotency

- [ ] Generate stable proposal IDs
- [ ] Store created album mapping
- [ ] Do not create duplicate albums on repeated runs

# MEDIUM Priority

## 11. Debugging

- [ ] Add `--debug`
- [ ] Save raw sample data
- [ ] Log clustering decisions

## 12. Performance

- [ ] Page/chunk 10k+ assets safely
- [ ] Avoid holding large thumbnails/images in memory

# LOW Priority / Future

## 13. Recurring Events

- [ ] Detect recurring memories such as birthdays, Christmas, annual trips

## 14. Highlight Selection

- [ ] Select best 10-30 photos from large clusters
- [ ] Prefer favorites and high-quality source photos

## 15. External Imports

- [ ] Treat photos uploaded from photographers/friends as normal Immich assets
- [ ] Later infer `source: external` from import albums or paths

# Agent Working Rules

- One task group per prompt
- Add tests for logic-heavy changes
- Keep docs updated
- Do not remove safety defaults
- Dry-run remains default
