"""Console script for SHOWROOM Podcast."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from showroompodcast.showroom_podcast import ShowroomPodcast


@click.command()
@click.option(
    "-f",
    "--file",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    default=Path("config.yml"),
)
def showroom_podcast(file: Path | None) -> None:
    """Console script for SHOWROOM Podcast."""
    podcast = ShowroomPodcast(path_to_configuration=file)
    try:
        podcast.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        sys.exit(130)
