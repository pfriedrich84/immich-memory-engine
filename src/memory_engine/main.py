from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich import print
from pydantic import TypeAdapter

from .config import load_config
from .clustering import cluster_assets
from .models import Asset, EventCluster, AlbumProposal
from .proposals import proposals_from_clusters

app = typer.Typer(help="Immich Memory Engine")


@app.command()
def scan(
    config: str = typer.Option("config.yaml", help="Path to config YAML"),
    from_date: Optional[str] = typer.Option(None, "--from", help="Start date YYYY-MM-DD"),
    to_date: Optional[str] = typer.Option(None, "--to", help="End date YYYY-MM-DD"),
):
    """Scan Immich assets and create initial cluster/proposal outputs.

    Current implementation supports fixture-driven development. Agents should implement real Immich fetching first.
    """
    cfg = load_config(config)
    out_dir = Path(cfg.get("output", {}).get("dir", "output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    assets_path = out_dir / "assets.json"
    if assets_path.exists():
        assets = TypeAdapter(list[Asset]).validate_json(assets_path.read_text(encoding="utf-8"))
        print(f"[green]Loaded existing[/green] {assets_path} with {len(assets)} assets")
    else:
        assets = []
        assets_path.write_text("[]\n", encoding="utf-8")
        print("[yellow]No real Immich scan implemented yet. Wrote empty output/assets.json[/yellow]")

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
    print(f"[green]Wrote[/green] {len(clusters)} clusters and {len(proposals)} proposals")


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

    Placeholder for Milestone 5. Dry-run is the safe default.
    """
    if dry_run:
        print(f"[yellow]DRY RUN[/yellow] Would apply proposal {proposal_id}")
        return
    raise NotImplementedError("Implement Immich album creation in Milestone 5")


if __name__ == "__main__":
    app()
