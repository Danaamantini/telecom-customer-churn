"""Shared I/O helpers with project-root-relative path resolution."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from src.data.config import PROJECT_ROOT

PathLike = Union[str, Path]


def _resolve(path: PathLike) -> Path:
    """Resolve a path relative to PROJECT_ROOT when not already absolute."""
    p = Path(path)
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def ensure_dir(path: PathLike) -> Path:
    """Create the directory for ``path`` (and its parents) if missing.

    Returns the resolved directory Path.
    """
    resolved = _resolve(path)
    # If the path already points at a directory (or looks like one), treat it as
    # the directory itself; otherwise create its parent.
    directory = resolved if (resolved.suffix == "" or resolved.is_dir()) else resolved.parent
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def read_csv(path: PathLike, **kwargs) -> pd.DataFrame:
    """Read a CSV, resolving ``path`` relative to PROJECT_ROOT."""
    return pd.read_csv(_resolve(path), **kwargs)


def write_csv(df: pd.DataFrame, path: PathLike, **kwargs) -> Path:
    """Write a DataFrame to CSV, creating parent dirs and resolving relative
    to PROJECT_ROOT. Returns the resolved output path."""
    resolved = _resolve(path)
    ensure_dir(resolved)
    df.to_csv(resolved, index=False, **kwargs)
    return resolved
