# Requirements

## Functional Requirements

- Scan Immich assets from multiple users.
- Normalize assets into a consistent internal model.
- Cluster photos into events using time and GPS.
- Merge user photos only when time AND location match.
- Avoid huge home-location clusters.
- Generate JSON and Markdown reports.
- Use Ollama for optional naming only.
- Create Immich albums from selected proposals.
- Default to dry-run.
- Avoid duplicate album creation.

## Non-Functional Requirements

- Local-first.
- No direct database access.
- Docker-first.
- Safe by default.
- Debuggable and explainable.
- Works for about 10k photos initially.

## User Setup Assumptions

- Immich runs in LAN.
- Two accounts are used: user and spouse.
- API keys are available for both accounts.
- Ollama is available in LAN with model `gemini4:e4b`.
- Home location is configured manually.
