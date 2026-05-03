# Immich Memory Engine

Docker-only MVP tooling for turning an Immich photo library into structured memory/album proposal artifacts.

## Current status and safety

- **Supported runtime/setup:** Docker Compose only. Local Python/Poetry is not a required user workflow.
- **Immich API assumption:** tested/designed for Immich **2.7.5**, using `x-api-key` auth and the metadata search API.
- **Read-only scan:** `scan` only reads from Immich and writes local files under `output/`.
- **No Immich writes yet:** album creation is not implemented. Future writes must require an explicit `apply --no-dry-run`.
- **Trust boundary:** until Milestones 2-4 are implemented, only `output/assets.json` should be treated as trustworthy. `clusters.json` and `proposals.json` are placeholder artifacts.

## Operator quick start

```bash
cp .env.example .env
cp config.example.yaml config.yaml
```

Edit `.env`:

- `IMMICH_URL` points to your Immich server, for example `http://immich-server:2283`.
- Set one API key per configured user, for example `IMMICH_API_KEY_PAUL` and `IMMICH_API_KEY_WIFE`.

Edit `config.yaml` if you want different user names/env var names. Do **not** duplicate the Immich URL in YAML; keep `url: "${IMMICH_URL}"` so Docker Compose's env file drives the target.

Run a scan:

```bash
docker compose run --rm memory-engine scan --config /app/config.yaml --from 2025-01-01 --to 2025-12-31
```

Outputs are written to `./output` on the host. Keep `MEMORY_ENGINE_OUTPUT_DIR=output` unless you also update the Compose volume mapping.

## Docker-only commands

```bash
# Build the image
docker compose build

# CLI smoke test
docker compose run --rm memory-engine --help

# Run the test suite inside Docker
docker compose run --rm memory-engine test

# Default compose command is a scan using /app/config.yaml
docker compose run --rm memory-engine
```

`.env` is required by Compose and is intentionally ignored by git. Never commit `.env` or API keys.

## For OSS contributors and coding agents

Use Docker/Compose as the source of truth:

```bash
cp .env.example .env
cp config.example.yaml config.yaml
docker compose build
docker compose run --rm memory-engine test
```

A quick local fallback can be useful in constrained environments, but it is not the supported setup contract:

```bash
PYTHONPATH=src python3 -m pytest -q
```

Keep changes milestone-scoped. Do not implement real clustering, Ollama naming, or Immich write/apply behavior as part of foundation or scan hardening.

## Configuration

`config.example.yaml` uses Docker-friendly environment interpolation:

- `${NAME}` means `NAME` must be set in `.env`/environment.
- `${NAME:-default}` uses a default when `NAME` is missing or empty.

Minimal scan validation checks:

- `immich.url` is present after env interpolation.
- At least one `immich.users` entry exists.
- Each user has `name` and `api_key_env`.
- Every referenced API key env var is present.
- `output.dir` defaults to `output`.

## Troubleshooting

- **Compose says `.env` is missing:** run `cp .env.example .env` and edit it.
- **Missing `IMMICH_URL` or API key env var:** set it in `.env`, then rerun the Compose command.
- **HTTP 401/403 from Immich:** verify the user API key and its permissions.
- **HTTP 404 from Immich search:** this project assumes Immich 2.7.5 metadata search behavior; check your server version.
- **Cannot reach Immich from Docker:** use a URL reachable from inside the container, not only from the host browser.
- **Unexpected clusters/proposals:** expected for now. Use `output/assets.json` for validation until clustering/proposal milestones land.

## CI and images

GitHub Actions builds and tests the Docker image on PRs. Pushes to `main` publish maintainer-testing images to GHCR tagged `latest` and `sha-*`; PRs do not publish images.
