# Architecture

```text
Immich API users
      ↓
Asset Fetcher
      ↓
Asset Normalizer
      ↓
Merged Timeline
      ↓
Time + GPS Clustering
      ↓
Home-Location Filter
      ↓
Proposal Generator
      ↓
Ollama Naming, optional
      ↓
JSON + Markdown Report
      ↓
Apply to Immich, optional
```

## Modules

- `memory_engine.main`: CLI entrypoint
- `memory_engine.config`: YAML config loading
- `memory_engine.immich_client`: Immich API integration
- `memory_engine.models`: Pydantic data models
- `memory_engine.geoutil`: GPS helpers
- `memory_engine.clustering`: event detection
- `memory_engine.proposals`: proposal generation
- `memory_engine.ollama_client`: LLM naming helper

## Data Flow

1. Fetch assets for each configured user.
2. Normalize each asset with `owner` set.
3. Merge all assets into one timeline.
4. Cluster assets using time + location.
5. Apply home-location rules.
6. Generate album proposals.
7. Optionally improve names via Ollama.
8. Review report.
9. Apply selected proposals to Immich.
