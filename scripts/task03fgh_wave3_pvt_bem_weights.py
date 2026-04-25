"""Task 3 (f, g, h): Wave III AHPVT repeat, Wave III BEM Sex-Role Inventory,
and weight-variable names across all waves.

Deliverable: outputs/03fgh_wave3_pvt_bem_weights.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

MD_PATH = OUT / "03fgh_wave3_pvt_bem_weights.md"

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def read_any(path: Path, metadataonly: bool = False):
    suffix = path.suffix.lower()
    if suffix == ".sas7bdat":
        return pyreadstat.read_sas7bdat(str(path), metadataonly=metadataonly)
    if suffix == ".xpt":
        return pyreadstat.read_xport(str(path), metadataonly=metadataonly)
    raise ValueError(f"Unsupported suffix: {suffix}")


def describe_column(series: pd.Series) -> dict:
    s = series.dropna()
    info = {"n_nonmiss": int(s.shape[0]), "dtype": str(series.dtype)}
    is_numeric = pd.api.types.is_numeric_dtype(series)
    if is_numeric and not s.empty:
        info.update(
            {
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": float(s.mean()),
                "std": float(s.std(ddof=1)) if s.shape[0] > 1 else float("nan"),
            }
        )
    elif not s.empty:
        # category / string: show up to 5 unique values
        uniques = s.unique()[:5]
        info["sample_values"] = [str(v) for v in uniques]
    return info


# --------------------------------------------------------------------------- #
# Task 3f: Wave III AHPVT repeat
# --------------------------------------------------------------------------- #


def task_3f() -> tuple[str, dict]:
    lines: list[str] = ["## Task 3f — Wave III AHPVT repeat (`w3pvt.sas7bdat`)", ""]
    path = DATA / "W3" / "w3pvt.sas7bdat"
    df, meta = read_any(path)
    lines.append(f"- File: `{path.relative_to(ROOT)}`")
    lines.append(f"- Shape: {df.shape[0]:,} rows x {df.shape[1]} cols")
    lines.append("")
    lines.append("### All variables")
    lines.append("")
    lines.append("| var | label | dtype | n_nonmiss | min | max | mean | std |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |")

    col_info = {}
    for col in df.columns:
        label = (meta.column_names_to_labels or {}).get(col, "") or ""
        info = describe_column(df[col])
        col_info[col] = {"label": label, **info}
        mn = f"{info['min']:.3f}" if "min" in info else ""
        mx = f"{info['max']:.3f}" if "max" in info else ""
        mean = f"{info['mean']:.3f}" if "mean" in info else ""
        std = f"{info['std']:.3f}" if "std" in info else ""
        lines.append(
            f"| `{col}` | {label} | {info['dtype']} | {info['n_nonmiss']} | {mn} | {mx} | {mean} | {std} |"
        )

    # Identify candidates
    # Standardized PVT: mean ~100, sd ~15, range roughly 35-150
    # Raw PVT: integer counts (0-87 typical for PPVT)
    std_candidates = []
    raw_candidates = []
    for col, info in col_info.items():
        if col == "AID":
            continue
        if "mean" not in info:
            continue
        mn, mx, mean, sd = info["min"], info["max"], info["mean"], info.get("std", 0)
        label_lower = (info["label"] or "").lower()
        if 80 <= mean <= 120 and 8 <= sd <= 25 and mx <= 200:
            std_candidates.append((col, info))
        if (mean < 80 and mx <= 120) or "raw" in label_lower:
            raw_candidates.append((col, info))

    lines.append("")
    lines.append("### Candidates")
    lines.append("")
    if std_candidates:
        lines.append("**Standardized AHPVT (analog of W1 `AH_PVT`):**")
        for col, info in std_candidates:
            lines.append(
                f"- `{col}` (label: {info['label']!r}) — mean={info['mean']:.2f}, "
                f"sd={info.get('std', float('nan')):.2f}, range=[{info['min']:.1f}, {info['max']:.1f}], "
                f"n={info['n_nonmiss']}"
            )
    else:
        lines.append("**Standardized AHPVT:** no clear candidate (mean~100, sd~15).")
    lines.append("")
    if raw_candidates:
        lines.append("**Raw AHPVT (analog of W1 `AH_RAW`):**")
        for col, info in raw_candidates:
            lines.append(
                f"- `{col}` (label: {info['label']!r}) — mean={info['mean']:.2f}, "
                f"sd={info.get('std', float('nan')):.2f}, range=[{info['min']:.1f}, {info['max']:.1f}], "
                f"n={info['n_nonmiss']}"
            )
    else:
        lines.append("**Raw AHPVT:** no clear candidate.")

    # Compare to Wave I AH_PVT / AH_RAW
    lines.append("")
    lines.append("### Comparison to Wave I baseline")
    w1_path = DATA / "W1" / "w1inhome.sas7bdat"
    w1_df, w1_meta = pyreadstat.read_sas7bdat(
        str(w1_path), usecols=["AID", "AH_PVT", "AH_RAW"]
    )
    lines.append("")
    lines.append("| var | n_nonmiss | min | max | mean | std |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for col in ("AH_PVT", "AH_RAW"):
        info = describe_column(w1_df[col])
        lines.append(
            f"| `{col}` | {info['n_nonmiss']} | {info.get('min', float('nan')):.3f} | "
            f"{info.get('max', float('nan')):.3f} | {info.get('mean', float('nan')):.3f} | "
            f"{info.get('std', float('nan')):.3f} |"
        )
    lines.append("")

    return "\n".join(lines), {
        "columns": col_info,
        "std_candidates": [c for c, _ in std_candidates],
        "raw_candidates": [c for c, _ in raw_candidates],
    }


# --------------------------------------------------------------------------- #
# Task 3g: Wave III BEM items
# --------------------------------------------------------------------------- #

BEM_KEYWORDS = [
    "bem",
    "masculin",
    "feminin",
    "gender role",
    "sex role",
    "assertive",
    "nurtur",
    "affection",
    "ambitio",
    "tender",
    "yielding",
    "compassion",
    "sympath",
    "sensitive",
    "warm",
    "soft",
    "loyal",
    "loves children",
    "aggressive",
    "forceful",
    "independent",
    "athletic",
    "analytical",
    "leadership",
    "competitive",
    "dominant",
    "self-reliant",
    "self reliant",
    "willing to take a stand",
    "willing to take risk",
    "defend",
    "strong personality",
    "personality",
]


def task_3g() -> tuple[str, dict]:
    lines: list[str] = ["## Task 3g — Wave III BEM Sex-Role Inventory (`w3inhome.sas7bdat`)", ""]
    path = DATA / "W3" / "w3inhome.sas7bdat"
    _, meta = read_any(path, metadataonly=True)
    n2l = meta.column_names_to_labels or {}
    lines.append(f"- File: `{path.relative_to(ROOT)}` ({len(meta.column_names)} variables)")

    # Collect hits
    hits = []
    for name in meta.column_names:
        label = n2l.get(name, "") or ""
        blob = f"{name} {label}".lower()
        for kw in BEM_KEYWORDS:
            if kw in blob:
                hits.append((name, label, kw))
                break

    # Also look for H3BE* / H3SE* / H3PR* prefixes that are common BEM section names
    prefix_hits = [n for n in meta.column_names if n.upper().startswith(("H3BE", "H3SE", "H3PR"))]
    lines.append(f"- Keyword hits: {len(hits)}")
    lines.append(f"- Prefix hits (H3BE*/H3SE*/H3PR*): {len(prefix_hits)}")
    lines.append("")

    lines.append("### Keyword-hit variables (first 80)")
    lines.append("")
    lines.append("| var | label | matched_kw |")
    lines.append("| --- | --- | --- |")
    for name, label, kw in hits[:80]:
        lines.append(f"| `{name}` | {label} | {kw} |")

    # Try to detect BEM block by contiguous prefix family in label space
    # If we see something like "You are affectionate" / "You are aggressive" together
    you_are = [
        (n, n2l.get(n, "") or "")
        for n in meta.column_names
        if (n2l.get(n, "") or "").lower().startswith(("you are ", "how much do you", "how well"))
    ]
    lines.append("")
    lines.append(f"### Variables with label starting 'You are ...' / 'How much do you ...' (n={len(you_are)})")
    lines.append("")
    if you_are:
        lines.append("| var | label |")
        lines.append("| --- | --- |")
        for n, lbl in you_are[:40]:
            lines.append(f"| `{n}` | {lbl} |")

    # Pull a sample of prefix-hit vars with labels
    lines.append("")
    lines.append("### Sample H3BE*/H3SE*/H3PR* variables")
    lines.append("")
    if prefix_hits:
        lines.append("| var | label |")
        lines.append("| --- | --- |")
        for n in prefix_hits[:40]:
            lines.append(f"| `{n}` | {n2l.get(n, '')} |")
    else:
        lines.append("_No H3BE*/H3SE*/H3PR* prefix variables present._")

    # Present / absent verdict
    lines.append("")
    lines.append("### Verdict")
    bem_item_count = len(
        [
            h
            for h in hits
            if h[2] in {"masculin", "feminin", "bem", "gender role", "sex role"}
        ]
    )
    lines.append(
        f"- Variables with explicit BEM/masculine/feminine/gender-role label tokens: {bem_item_count}"
    )
    # The 30 BEM adjective items
    adjective_kws = {
        "assertive",
        "nurtur",
        "affection",
        "ambitio",
        "tender",
        "yielding",
        "compassion",
        "sympath",
        "sensitive",
        "warm",
        "soft",
        "loyal",
        "loves children",
        "aggressive",
        "forceful",
        "independent",
        "athletic",
        "analytical",
        "leadership",
        "competitive",
        "dominant",
        "self-reliant",
        "self reliant",
        "willing to take a stand",
        "willing to take risk",
        "defend",
        "strong personality",
    }
    adjective_hits = [h for h in hits if h[2] in adjective_kws]
    lines.append(f"- Variables matching BEM adjective keywords: {len(adjective_hits)}")
    lines.append("")

    return "\n".join(lines), {
        "hits": hits,
        "prefix_hits": prefix_hits,
        "adjective_hits": adjective_hits,
        "bem_item_count": bem_item_count,
    }


# --------------------------------------------------------------------------- #
# Task 3h: Weights across all waves
# --------------------------------------------------------------------------- #

WEIGHT_FILES = [
    ("Wave I", DATA / "W1" / "w1weight.sas7bdat"),
    ("Wave II", DATA / "W2" / "w2weight.sas7bdat"),
    ("Wave III (main)", DATA / "W3" / "w3weight.sas7bdat"),
    ("Wave III (edu subsample)", DATA / "W3" / "w3eduwgt.sas7bdat"),
    ("Wave IV", DATA / "W4" / "w4weight.sas7bdat"),
    ("Wave V", DATA / "W5" / "p5weight.xpt"),
    ("Wave VI", DATA / "W6" / "p6weight.sas7bdat"),
]

# Names flagged in the companion report
FLAGGED = {"CORE1", "CORE2", "HIEDBLK", "GSW5", "GSW145", "GSW1345", "GSW12345"}


def task_3h() -> tuple[str, dict]:
    lines: list[str] = ["## Task 3h — Weight variable names across all waves", ""]
    all_vars = {}  # wave -> list of dicts
    consolidated_rows = []

    for wave, path in WEIGHT_FILES:
        if not path.exists():
            lines.append(f"### {wave}: `{path.relative_to(ROOT)}` — **MISSING**")
            continue
        df, meta = read_any(path)
        n2l = meta.column_names_to_labels or {}
        lines.append(f"### {wave} — `{path.relative_to(ROOT)}`  ({df.shape[0]:,} x {df.shape[1]})")
        lines.append("")
        lines.append("| var | label | dtype | n_nonmiss | min | max | mean |")
        lines.append("| --- | --- | --- | ---: | ---: | ---: | ---: |")
        wave_cols = []
        for col in df.columns:
            info = describe_column(df[col])
            label = n2l.get(col, "") or ""
            wave_cols.append({"name": col, "label": label, **info})
            mn = f"{info['min']:.3f}" if "min" in info else ""
            mx = f"{info['max']:.3f}" if "max" in info else ""
            mean = f"{info['mean']:.3f}" if "mean" in info else ""
            lines.append(
                f"| `{col}` | {label} | {info['dtype']} | {info['n_nonmiss']} | {mn} | {mx} | {mean} |"
            )
            if col.upper() != "AID":
                consolidated_rows.append(
                    {
                        "wave": wave,
                        "file": path.name,
                        "var": col,
                        "label": label,
                        "n_nonmiss": info["n_nonmiss"],
                        "mean": info.get("mean"),
                        "min": info.get("min"),
                        "max": info.get("max"),
                    }
                )
        all_vars[wave] = wave_cols
        lines.append("")

    # Consolidated mapping table
    lines.append("### Consolidated weight mapping")
    lines.append("")
    lines.append("| wave | file | var | label | n | mean |")
    lines.append("| --- | --- | --- | --- | ---: | ---: |")
    for row in consolidated_rows:
        mean = f"{row['mean']:.2f}" if row["mean"] is not None else ""
        lines.append(
            f"| {row['wave']} | {row['file']} | `{row['var']}` | {row['label']} | "
            f"{row['n_nonmiss']} | {mean} |"
        )
    lines.append("")

    # Flagged-name check
    lines.append("### Presence check for names referenced in the companion report")
    lines.append("")
    lines.append("| flagged_name | present? | in_wave/file |")
    lines.append("| --- | --- | --- |")
    all_names = {(r["var"].upper(), r["wave"], r["file"]) for r in consolidated_rows}
    for flag in sorted(FLAGGED):
        matches = [
            (wave, fname) for (name, wave, fname) in all_names if name == flag
        ]
        if matches:
            loc = "; ".join(f"{w} ({f})" for w, f in matches)
            lines.append(f"| `{flag}` | YES | {loc} |")
        else:
            lines.append(f"| `{flag}` | NO | — |")
    lines.append("")

    return "\n".join(lines), {"all_vars": all_vars, "rows": consolidated_rows}


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main() -> None:
    sections = []
    sections.append("# Task 3 (f, g, h): Wave III PVT, BEM items, and weights\n")

    md_f, info_f = task_3f()
    sections.append(md_f)
    md_g, info_g = task_3g()
    sections.append(md_g)
    md_h, info_h = task_3h()
    sections.append(md_h)

    MD_PATH.write_text("\n".join(sections))
    print(f"Wrote {MD_PATH}")

    # Short stdout summary for convenience
    print("\n--- Summary ---")
    print(
        "3f std candidates:",
        info_f["std_candidates"],
        "| raw candidates:",
        info_f["raw_candidates"],
    )
    print(
        "3g BEM hits:",
        len(info_g["hits"]),
        "| adjective hits:",
        len(info_g["adjective_hits"]),
        "| prefix hits:",
        len(info_g["prefix_hits"]),
    )
    print("3h weight waves:", list(info_h["all_vars"].keys()))


if __name__ == "__main__":
    main()
