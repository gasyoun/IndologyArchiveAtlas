# Changelog

All notable changes to the standalone INDOLOGY archive atlas appendix are tracked here.

This project follows semantic versioning: `MAJOR.MINOR.PATCH`.

## [Unreleased]

### Added

- Split into its own repo, `gasyoun/IndologyArchiveAtlas` (H460), out of
  `gasyoun/IndologyScholars`'s `Indology/` subtree — full commit history
  preserved via `git filter-repo --subdirectory-filter`.
- `data/raw/` (61MB cached HTML + monthly gzip mbox from
  `list.indology.info`) is now version-controlled, for reproducibility
  independent of the source archive staying reachable.
- `feed/` export (`renou_coverage.csv`, `renou_export_index.csv`,
  `renou_state_summary.csv`, `renou_register_summary.csv`,
  `renou_message_matches.csv`), refreshed each pipeline run — the slice
  `IndologyScholars`'s Renou cross-site comparison now fetches one-way
  instead of reading this tree directly.
- Own standalone GitHub Actions workflow + Pages deploy
  (`prepare_pages_artifact.py`), independent of the former combined
  IndologyScholars build.

### Changed

- `CITATION.cff` / `datapackage.json` `repository-code` repointed from
  `gasyoun/IndologyScholars` to `gasyoun/IndologyArchiveAtlas`.

## 0.1.0 - 2026-06-30

- Start semver tracking for the standalone `Indology/` appendix.
- Add metadata-first INDOLOGY-L archive harvest, analysis, cleaning, reply-network, guided atlas, thread explorer, static search, curation, review-intake, and publication metadata layers.
- Generate public documentation, citation metadata, datapackage metadata, validation reports, dashboard pages, figures, and review queues.
