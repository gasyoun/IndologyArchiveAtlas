"""Refresh the small `feed/` export consumed by the IndologyScholars site.

Kept deliberately narrow: only the tables the Renou cross-site comparison in
`gasyoun/IndologyScholars` (generate_renou_layer.py) actually reads. Everything
else in this dataset stays here; consumers fetch this directory over
raw.githubusercontent.com rather than depending on the full tree.
"""

from __future__ import annotations

import shutil
from pathlib import Path

FEED_FILES = [
    "renou_coverage.csv",
    "renou_export_index.csv",
    "renou_state_summary.csv",
    "renou_register_summary.csv",
    "renou_message_matches.csv",
]


def run_feed_export(output_dir: Path) -> list[Path]:
    processed = output_dir / "data" / "processed"
    feed_dir = output_dir / "feed"
    feed_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name in FEED_FILES:
        source = processed / name
        if not source.exists():
            continue
        destination = feed_dir / name
        shutil.copy2(source, destination)
        written.append(destination)
    return written
