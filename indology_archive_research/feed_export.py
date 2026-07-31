"""Refresh the small `feed/` export consumed by the IndologyScholars site.

Kept deliberately narrow: only the tables the community-lenses comparison in
`gasyoun/IndologyScholars` actually reads (the legacy Renou cross-site
comparison in `generate_renou_layer.py`, plus the H1894 community-lenses
`indology_l` adapter). Everything else in this dataset stays here; consumers
fetch this directory over raw.githubusercontent.com rather than depending on
the full tree.

H1894 adds a schema-versioned, hash-pinned `manifest.json` so a downstream
fetcher can validate a snapshot is complete and unmixed before promoting it
(see `IndologyScholars/tools/fetch_indology_feed.py`), plus three existing
atlas summary tables and one new privacy-safe per-message metadata table
(`atlas_records_public.csv`) sufficient for denominators and adapter joins.
`atlas_records_public.csv` deliberately excludes every author/from-header
column: nothing here should carry a raw email address or contact string.
"""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Feed contract version. Bump only on a breaking change to file names, column
# sets, or the manifest shape itself -- consumers pin this and refuse a
# mismatch (see IndologyScholars community_lenses/schema.py SCHEMA_VERSION,
# which this deliberately does NOT have to track: this is the *feed*
# contract, not the shared five-lens schema).
FEED_SCHEMA_VERSION = "1.0.0"

# Legacy files: copied byte-identical from data/processed/. Preserved so the
# existing generate_renou_layer.py consumer keeps working unmodified even
# once the manifest-first fetcher lands downstream.
LEGACY_FEED_FILES = [
    "renou_coverage.csv",
    "renou_export_index.csv",
    "renou_state_summary.csv",
    "renou_register_summary.csv",
    "renou_message_matches.csv",
]

# New Wave-1B community-lenses exports: three existing atlas summary tables,
# copied as-is, plus one new privacy-safe per-message feed built below.
NEW_FEED_FILES = [
    "atlas_timeline.csv",
    "atlas_topic_profiles.csv",
    "atlas_list_functions.csv",
    "atlas_records_public.csv",
]

FEED_FILES = LEGACY_FEED_FILES + NEW_FEED_FILES

MANIFEST_FILE = "manifest.json"

# Columns copied from data/processed/messages.csv into atlas_records_public.csv.
# Every column here is public archive/topic metadata; none carries an author
# name, email header, or contact string (from_header/author/author_html/
# author_display are deliberately excluded).
PUBLIC_RECORD_COLUMNS = [
    "message_id",
    "archive_id",
    "archive_url",
    "archive_year",
    "archive_month",
    "date",
    "year",
    "month",
    "decade",
    "in_reply_to",
    "thread_root_id",
    "thread_depth",
    "thread_length",
    "primary_topic",
    "topic_tags",
    "is_noisy_subject",
]


def build_records_public(processed_dir: Path, feed_dir: Path) -> Path | None:
    """Write the privacy-safe per-message metadata feed.

    Returns None (writing nothing) if the source messages table is absent,
    matching the existing fault-tolerant "safe to skip" posture of this
    module -- a missing upstream table must never crash the export.
    """
    source = processed_dir / "messages.csv"
    if not source.exists():
        return None
    destination = feed_dir / "atlas_records_public.csv"
    with source.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        available = [c for c in PUBLIC_RECORD_COLUMNS if c in (reader.fieldnames or [])]
        with destination.open("w", encoding="utf-8", newline="") as out_handle:
            writer = csv.DictWriter(out_handle, fieldnames=available)
            writer.writeheader()
            for row in reader:
                writer.writerow({col: row.get(col, "") for col in available})
    return destination


def _pipeline_commit(output_dir: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=output_dir,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            check=True,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def _sha256_and_rows(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    rows = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 16), b""):
            digest.update(chunk)
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = max(sum(1 for _ in handle) - 1, 0)
    return digest.hexdigest(), rows


def write_feed_manifest(output_dir: Path, written: list[Path]) -> Path:
    """Write feed/manifest.json: the atomic-fetch contract for downstream.

    Every listed file carries its own sha256 + row count so a consumer can
    verify a staged download matches this exact snapshot before promoting it
    -- no file may be silently substituted or partially updated.
    """
    feed_dir = output_dir / "feed"
    files = []
    for path in sorted(written, key=lambda p: p.name):
        sha256, rows = _sha256_and_rows(path)
        files.append(
            {
                "name": path.name,
                "sha256": sha256,
                "bytes": path.stat().st_size,
                "rows": rows,
            }
        )
    manifest = {
        "schema_version": FEED_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pipeline_commit": _pipeline_commit(output_dir),
        "source_repository": "https://github.com/gasyoun/IndologyArchiveAtlas",
        "files": files,
    }
    manifest_path = feed_dir / MANIFEST_FILE
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest_path


def run_feed_export(output_dir: Path) -> list[Path]:
    processed = output_dir / "data" / "processed"
    feed_dir = output_dir / "feed"
    feed_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for name in FEED_FILES:
        source = processed / name
        if not source.exists():
            continue
        destination = feed_dir / name
        shutil.copy2(source, destination)
        written.append(destination)

    records_public = build_records_public(processed, feed_dir)
    if records_public is not None and records_public not in written:
        written.append(records_public)

    write_feed_manifest(output_dir, written)
    return written
