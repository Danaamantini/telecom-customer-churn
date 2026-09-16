"""Unit tests for ``src.utils.io`` — CSV round-trip and directory creation."""

from __future__ import annotations

import pandas as pd

from src.utils import io


def test_write_read_csv_roundtrip(tmp_path):
    df = pd.DataFrame(
        {
            "customer_id": ["0002-ORFBO", "0003-TJLSM"],
            "age": [42, 29],
            "monthly_charge": [63.25, 74.5],
            "married": [True, False],
        }
    )
    out = tmp_path / "nested" / "out.csv"
    resolved = io.write_csv(df, out)

    # write_csv resolves (absolute paths are untouched) and returns the path.
    assert resolved == out
    assert out.is_file()

    back = io.read_csv(out)
    pd.testing.assert_frame_equal(back, df, check_dtype=True)


def test_ensure_dir_creates_and_is_idempotent(tmp_path):
    target = tmp_path / "a" / "b" / "c"
    assert not target.exists()

    first = io.ensure_dir(target)
    assert first.is_dir()
    assert target.is_dir()

    # A second call must succeed without raising (idempotent).
    second = io.ensure_dir(target)
    assert second.is_dir()
    assert second == target


def test_ensure_dir_creates_parent_for_file_path(tmp_path):
    target = tmp_path / "x" / "y" / "file.csv"
    io.ensure_dir(target)
    # For a file-like path, only the parent directory is created.
    assert target.parent.is_dir()
    assert not target.is_dir()
