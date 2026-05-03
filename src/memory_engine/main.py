from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
import httpx
import typer
from pydantic import TypeAdapter
from rich import print

from .clustering import cluster_assets
from .config import ConfigError, load_config, validate_scan_config
from .immich_client import ImmichClient
from .models import AlbumProposal, Asset, EventCluster
from .proposals import proposals_from_clusters

app = typer.Typer(help="Immich Memory Engine")


@app.command()
def scan(
    config: str = typer.Option("config.yaml", help="Path to config YAML"),
    from_date: Optional[str] = typer.Option(None, "--from", help="Start date YYYY-MM-DD"),
    to_date: Optional[str] = typer.Option(None, "--to", help="End date YYYY-MM-DD"),
):
    """Scan Immich assets and create initial cluster/proposal outputs.

    The scan is read-only against Immich. In the current MVP stage only
    output/assets.json should be treated as trustworthy; clusters/proposals are
    placeholder artifacts until later milestones.
    """
    try:
        cfg = load_config(config)
        base_url, users, out_dir = validate_scan_config(cfg)
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
    out_dir.mkdir(parents=True, exist_ok=True)

    assets: list[Asset] = []
    for user in users:
        owner = user["name"]
        api_key_env = user["api_key_env"]
        api_key = os.environ[api_key_env]
        try:
            fetched = ImmichClient(base_url, api_key, owner).fetch_assets(from_date, to_date)
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = exc.response.text[:500]
            raise click.ClickException(
                f"Immich API request failed for user {owner}: HTTP {status}. "
                f"Check IMMICH_URL, API key permissions, and Immich 2.7.5 compatibility. Response: {body}"
            ) from exc
        except httpx.RequestError as exc:
            raise click.ClickException(
                f"Could not reach Immich for user {owner} at {base_url}: {exc}. "
                "Check IMMICH_URL and Docker network access."
            ) from exc
        except ValueError as exc:
            raise click.ClickException(f"Could not normalize Immich asset for user {owner}: {exc}") from exc

        assets.extend(fetched)
        print(f"[green]Fetched[/green] {len(fetched)} assets for {owner}")

    assets.sort(key=lambda asset: asset.taken_at)
    assets_path = out_dir / "assets.json"
    assets_path.write_text(
        TypeAdapter(list[Asset]).dump_json(assets, indent=2).decode(),
        encoding="utf-8",
    )
    print(f"[green]Wrote[/green] {assets_path} with {len(assets)} assets")

    clusters = cluster_assets(assets, cfg)
    (out_dir / "clusters.json").write_text(
        TypeAdapter(list[EventCluster]).dump_json(clusters, indent=2).decode(),
        encoding="utf-8",
    )

    album_prefix = cfg.get("output", {}).get("album_prefix", "Vorschlag: ")
    proposals = proposals_from_clusters(clusters, album_prefix)
    (out_dir / "proposals.json").write_text(
        TypeAdapter(list[AlbumProposal]).dump_json(proposals, indent=2).decode(),
        encoding="utf-8",
    )
    print(f"[green]Wrote[/green] {len(clusters)} placeholder clusters and {len(proposals)} placeholder proposals")


@app.command()
def review(input: str = "output/proposals.json"):
    path = Path(input)
    if not path.exists():
        raise typer.BadParameter(f"Missing file: {input}")
    proposals = json.loads(path.read_text(encoding="utf-8"))
    for p in proposals:
        print(f"[bold]{p['title']}[/bold] — confidence {p['confidence']}")
        for reason in p.get("reasons", []):
            print(f"  - {reason}")


@app.command()
def apply(
    proposal_id: str,
    config: str = "config.yaml",
    dry_run: bool = typer.Option(True, help="Dry-run by default; use --no-dry-run to write to Immich"),
):
    """Create an Immich album from a proposal.

    Placeholder for Milestone 6. Dry-run is the safe default.
    """
    if dry_run:
        print(f"[yellow]DRY RUN[/yellow] Would apply proposal {proposal_id}")
        return
    raise NotImplementedError("Implement Immich album creation in Milestone 6")


@app.command("test")
def run_tests():
    """Run the project's pytest suite inside the Docker image."""
    result = subprocess.run([sys.executable, "-m", "pytest", "-q"], check=False)
    raise typer.Exit(result.returncode)


if __name__ == "__main__":
    app()
