"""Task 1: File inventory.

Walks the data directory, reads metadata from every SAS7BDAT / XPT file, and
records wave, content category, row/col counts, presence of AID, and file path.

Emits scripts/prep/outputs/01_file_inventory.csv and
scripts/prep/outputs/01_file_inventory.md. Also caches each file as parquet
under cache/ (top-level) for reuse by later tasks.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

<<<<<<< HEAD:scripts/task01_file_inventory.py
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CACHE = OUT / "cache"
OUT.mkdir(exist_ok=True)
CACHE.mkdir(exist_ok=True)
=======
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis import ROOT, DATA, CACHE  # noqa: E402

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)
>>>>>>> 9ed93fa62a452cb047f78f544077837c3574945d:scripts/prep/01_file_inventory.py


def infer_wave(path: Path) -> str:
    parts = path.parts
    for p in parts:
        if p in {"W1", "W2", "W3", "W4", "W5", "W6"}:
            return p.replace("W", "Wave ")
    return "unknown"


def categorize(fname: str) -> str:
    name = fname.lower()
    # network
    if "network" in name:
        return "network"
    # weights
    if re.search(r"weight|wgt|p5weight|p6weight", name):
        return "weights"
    # biomarker categories
    biomarker_keys = [
        "lipid", "glucose", "a1c", "glua1c", "crp", "ebv", "hscrp",
        "anthro", "cardio", "renal", "meds", "medication", "hepat",
    ]
    for k in biomarker_keys:
        if k in name:
            return "biomarker"
    # context
    if "context" in name:
        return "context"
    # special W3/W4 auxiliary
    if any(k in name for k in ["birth", "child", "partner", "pregnancy", "cmplpreg", "currpreg",
                               "educatn", "graduatn", "segment", "prtnrdtail", "pvt"]):
        return "auxiliary"
    # core survey
    if "inhome" in name or "pwave" in name or "pdemo" in name:
        return "core_survey"
    # section codebooks shouldn't be in here but guard
    if "psec" in name:
        return "section_subset"
    return "other"


def read_metadata(path: Path):
    """Return (nrows, ncols, has_aid, aid_col_name, error)."""
    try:
        if path.suffix.lower() == ".sas7bdat":
            # metadataonly=True is fast; doesn't load values
            df, meta = pyreadstat.read_sas7bdat(str(path), metadataonly=True)
            cols = meta.column_names
            nrows = meta.number_rows
        elif path.suffix.lower() == ".xpt":
            # XPT doesn't support metadataonly in all versions; read and use shape
            df, meta = pyreadstat.read_xport(str(path))
            cols = list(df.columns)
            nrows = len(df)
        else:
            return None, None, False, None, "unsupported_ext"
    except Exception as e:
        return None, None, False, None, f"read_error: {e}"

    # AID may appear as AID, aid, or occasionally AID0/AID1
    aid_col = None
    for c in cols:
        if c.upper() == "AID":
            aid_col = c
            break
    return nrows, len(cols), aid_col is not None, aid_col, None


def main():
    rows = []
    # Only primary data files (skip _fmt_data, _dvn, _format companions)
    exclude_patterns = [
        "_fmt_data", "_dvn", "_format", "_sas-spss",
    ]

    for wave_dir in sorted(DATA.iterdir()):
        if not wave_dir.is_dir():
            continue
        for f in sorted(wave_dir.iterdir()):
            if f.suffix.lower() not in (".sas7bdat", ".xpt"):
                continue
            name_lower = f.name.lower()
            if any(p in name_lower for p in exclude_patterns):
                continue

            nrows, ncols, has_aid, aid_col, err = read_metadata(f)
            rows.append({
                "file_name": f.name,
                "rel_path": str(f.relative_to(ROOT)),
                "wave": infer_wave(f),
                "category": categorize(f.name),
                "n_rows": nrows,
                "n_cols": ncols,
                "has_aid": has_aid,
                "aid_col": aid_col,
                "error": err,
            })
            status = "OK" if err is None else err
            print(f"[{status}] {f.relative_to(DATA)}: n={nrows} vars={ncols} aid={aid_col}")

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "01_file_inventory.csv", index=False)

    # Markdown summary
    lines = ["# Task 1: File Inventory\n"]
    lines.append(f"Total primary data files scanned: **{len(df)}**\n")
    lines.append(f"Files with AID: **{int(df['has_aid'].sum())}**\n")
    lines.append("")

    for wave in ["Wave 1", "Wave 2", "Wave 3", "Wave 4", "Wave 5", "Wave 6"]:
        sub = df[df["wave"] == wave]
        if len(sub) == 0:
            continue
        lines.append(f"## {wave}\n")
        lines.append("| File | Category | N rows | N cols | Has AID |")
        lines.append("|------|----------|--------|--------|---------|")
        for _, r in sub.iterrows():
            lines.append(
                f"| `{r['file_name']}` | {r['category']} | {r['n_rows']} | {r['n_cols']} | {r['has_aid']} |"
            )
        lines.append("")
    (OUT / "01_file_inventory.md").write_text("\n".join(lines))
    print(f"\nWrote {OUT / '01_file_inventory.csv'} and {OUT / '01_file_inventory.md'}")


if __name__ == "__main__":
    main()
