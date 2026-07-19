"""Stage this repo's public tree into `_site/` for the GitHub Pages deploy.

`dashboard/*.html` link to sibling top-level paths with relative `../` hrefs
(`../data/processed/*.csv`, `../figures/*.png`, `../reports/`, `../CITATION.cff`,
`../data_dictionary.md`, `../datapackage.json`) — this mirrors that same
repo-root-relative layout under `_site/` rather than deploying `dashboard/`
alone, which would 404 on every one of those links. `data/raw/` (gitignored
cache, not in git) and internal-only dirs (`.git`, `scripts`,
`indology_archive_research`, `notebooks`) are deliberately left out.
"""

import shutil
from pathlib import Path

PUBLIC_PATHS = [
    "CITATION.cff",
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "data_dictionary.md",
    "datapackage.json",
]

PUBLIC_DIRS = [
    "dashboard",
    "data",
    "figures",
    "reports",
    "feed",
]


def copy_path(src, dest_root):
    source = Path(src)
    if not source.exists():
        return
    destination = dest_root / source
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_dir(src, dest_root):
    source = Path(src)
    if not source.exists():
        return
    destination = dest_root / source
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns("raw"))


def main():
    dest_root = Path("_site")
    if dest_root.exists():
        shutil.rmtree(dest_root)
    dest_root.mkdir()

    for path in PUBLIC_PATHS:
        copy_path(path, dest_root)
    for directory in PUBLIC_DIRS:
        copy_dir(directory, dest_root)

    print(f"Staged Pages artifact at {dest_root}")


if __name__ == "__main__":
    main()
