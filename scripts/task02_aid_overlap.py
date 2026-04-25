"""Task 2: AID overlap matrix.

Loads unique AID sets from every file in the inventory (skipping w3schwgt), caches
them as pickles, builds the pairwise overlap matrix, and writes a focused
markdown covering the reference pairwise + multi-way intersections relevant to
the research design.
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CACHE = OUT / "cache" / "aids"
CACHE.mkdir(parents=True, exist_ok=True)

INVENTORY = OUT / "01_file_inventory.csv"

# Files to use for the focused pairwise table
REFERENCE_FILES = {
    "W1 In-Home": "w1inhome.sas7bdat",
    "W1 Network": "w1network.sas7bdat",
    "W2 In-Home": "w2inhome.sas7bdat",
    "W3 In-Home": "w3inhome.sas7bdat",
    "W4 In-Home": "w4inhome.sas7bdat",
    "W5 Mixed-Mode": "pwave5.xpt",
    "W6 Mixed-Mode": "pwave6.sas7bdat",
    "W5 biomarker (panthro5)": "panthro5.xpt",
    "W5 biomarker (pmeds5)": "pmeds5.xpt",
    "W6 biomarker (panthro6)": "panthro6.sas7bdat",
}


def load_aids(rel_path: str, file_name: str) -> set:
    """Load the set of unique AIDs from a file, caching to pickle."""
    cache_path = CACHE / f"{file_name}.pkl"
    if cache_path.exists():
        with cache_path.open("rb") as fh:
            return pickle.load(fh)

    full_path = ROOT / rel_path
    suffix = full_path.suffix.lower()

    try:
        if suffix == ".sas7bdat":
            try:
                df, _ = pyreadstat.read_sas7bdat(str(full_path), usecols=["AID"])
            except Exception:
                # usecols may fail on some SAS files; fall back to full read
                df, _ = pyreadstat.read_sas7bdat(str(full_path))
                df = df[["AID"]]
        elif suffix == ".xpt":
            try:
                df, _ = pyreadstat.read_xport(str(full_path), usecols=["AID"])
            except Exception:
                df, _ = pyreadstat.read_xport(str(full_path))
                df = df[["AID"]]
        else:
            raise ValueError(f"Unsupported extension: {suffix}")
    except Exception as e:
        print(f"  FAILED {file_name}: {e}")
        raise

    aids = set(df["AID"].dropna().astype(str).unique())
    with cache_path.open("wb") as fh:
        pickle.dump(aids, fh)
    return aids


def pct_of_smaller(inter_n: int, a: set, b: set) -> float:
    small = min(len(a), len(b))
    return 100.0 * inter_n / small if small else 0.0


def main():
    inv = pd.read_csv(INVENTORY)
    # Keep only files with AID (drop w3schwgt explicitly; its has_aid is False anyway)
    inv = inv[inv["has_aid"] == True].copy()
    inv = inv[inv["file_name"] != "w3schwgt.sas7bdat"].copy()
    print(f"Loading AID sets for {len(inv)} files...")

    aid_sets: dict[str, set] = {}
    for i, row in enumerate(inv.itertuples(index=False), 1):
        print(f"  [{i}/{len(inv)}] {row.file_name} (n_rows={row.n_rows})")
        aids = load_aids(row.rel_path, row.file_name)
        aid_sets[row.file_name] = aids
        print(f"    unique AIDs = {len(aids)}")

    # Full pairwise overlap matrix
    files = sorted(aid_sets.keys())
    print(f"\nBuilding {len(files)}x{len(files)} overlap matrix...")
    mat = pd.DataFrame(index=files, columns=files, dtype="Int64")
    for a in files:
        sa = aid_sets[a]
        for b in files:
            sb = aid_sets[b]
            if a == b:
                mat.loc[a, b] = len(sa)
            else:
                mat.loc[a, b] = len(sa & sb)
    mat.to_csv(OUT / "02_aid_overlap_full.csv")
    print(f"Wrote {OUT / '02_aid_overlap_full.csv'}")

    # Focused markdown
    md = ["# Task 2: AID Overlap (Focused)\n"]
    md.append("Source: Add Health public-use ICPSR 21600 v26.\n")

    # Unique-N table for reference files
    md.append("## Reference file sizes (unique AIDs)\n")
    md.append("| Label | File | Unique AIDs |")
    md.append("|-------|------|-------------|")
    for label, fn in REFERENCE_FILES.items():
        n = len(aid_sets.get(fn, set()))
        md.append(f"| {label} | `{fn}` | {n} |")
    md.append("")

    # Pairwise table for reference files
    md.append("## Pairwise overlaps (reference files)\n")
    md.append("| Pair | Intersection N | % of smaller file |")
    md.append("|------|----------------|-------------------|")
    labels = list(REFERENCE_FILES.keys())
    pair_results = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            la, lb = labels[i], labels[j]
            fa, fb = REFERENCE_FILES[la], REFERENCE_FILES[lb]
            sa, sb = aid_sets[fa], aid_sets[fb]
            n = len(sa & sb)
            pct = pct_of_smaller(n, sa, sb)
            md.append(f"| {la} x {lb} | {n} | {pct:.1f}% |")
            pair_results.append((la, lb, n, pct))
    md.append("")

    # Multi-way intersections
    md.append("## Critical multi-way intersections\n")
    md.append("| Intersection | N |")
    md.append("|--------------|---|")

    def inter(*names):
        s = aid_sets[names[0]]
        for n in names[1:]:
            s = s & aid_sets[n]
        return s

    multi_specs = [
        ("W1 Network ∩ W4 In-Home ∩ W5 Mixed-Mode",
         ["w1network.sas7bdat", "w4inhome.sas7bdat", "pwave5.xpt"]),
        ("W1 Network ∩ W1 In-Home ∩ W5 Mixed-Mode",
         ["w1network.sas7bdat", "w1inhome.sas7bdat", "pwave5.xpt"]),
        ("W1 In-Home ∩ W4 In-Home ∩ W5 Mixed-Mode",
         ["w1inhome.sas7bdat", "w4inhome.sas7bdat", "pwave5.xpt"]),
        ("W1 Network ∩ W4 In-Home ∩ W5 Mixed-Mode ∩ W6 Mixed-Mode",
         ["w1network.sas7bdat", "w4inhome.sas7bdat", "pwave5.xpt", "pwave6.sas7bdat"]),
        ("W1 In-Home ∩ W2 ∩ W3 ∩ W4 ∩ W5 (full panel)",
         ["w1inhome.sas7bdat", "w2inhome.sas7bdat", "w3inhome.sas7bdat",
          "w4inhome.sas7bdat", "pwave5.xpt"]),
    ]
    multi_results = []
    for label, files_ in multi_specs:
        n = len(inter(*files_))
        md.append(f"| {label} | {n} |")
        multi_results.append((label, files_, n))
    md.append("")

    # Red-line flags
    md.append("## Red-line flags (project-critical N < 500)\n")
    flags = []
    for la, lb, n, pct in pair_results:
        # Flag critical pairs only (W5/W6 cross-wave and core longitudinal)
        critical = ("W5" in la or "W5" in lb or "W6" in la or "W6" in lb
                    or "W1 Network" in (la, lb))
        if critical and n < 500:
            flags.append(f"- **{la} x {lb}** = {n}")
    for label, _, n in multi_results:
        if n < 500:
            flags.append(f"- **{label}** = {n}")
    if not flags:
        md.append("_None of the critical pairs/tuples fall below 500._")
    else:
        md.extend(flags)
    md.append("")
    md.append("Note: the public-use subsample is re-drawn per wave, so any cell <500 "
              "implies the corresponding longitudinal design is effectively impossible "
              "without restricted-use access.")
    md.append("")

    # Sanity checks
    md.append("## Sanity checks\n")
    sc = []

    # 1) W1 In-Home ∩ W1 Network should be 6504
    n_w1h_w1n = len(aid_sets["w1inhome.sas7bdat"] & aid_sets["w1network.sas7bdat"])
    sc.append(f"- W1 In-Home ∩ W1 Network = **{n_w1h_w1n}** (expected 6,504). "
              f"{'PASS' if n_w1h_w1n == 6504 else 'FAIL'}")

    # 2) Each wave's in-home ∩ its own weight file should equal the smaller file
    wave_pairs = [
        ("W1", "w1inhome.sas7bdat", "w1weight.sas7bdat"),
        ("W2", "w2inhome.sas7bdat", "w2weight.sas7bdat"),
        ("W3", "w3inhome.sas7bdat", "w3weight.sas7bdat"),
        ("W4", "w4inhome.sas7bdat", "w4weight.sas7bdat"),
        ("W5", "pwave5.xpt", "p5weight.xpt"),
        ("W6", "pwave6.sas7bdat", "p6weight.sas7bdat"),
    ]
    for tag, ih, wt in wave_pairs:
        if ih in aid_sets and wt in aid_sets:
            a, b = aid_sets[ih], aid_sets[wt]
            n = len(a & b)
            small = min(len(a), len(b))
            sc.append(f"- {tag} core ∩ weight: {n} / smaller={small} "
                      f"({'PASS' if n == small else 'FAIL'})")

    # 3) Biomarker files within a wave should share the same AID subset
    w4_bio = ["w4ebv_hscrp.sas7bdat", "w4glucose.sas7bdat", "w4lipid.sas7bdat"]
    w5_bio_identical = ["panthro5.xpt", "pcardio5.xpt", "pcrp5.xpt",
                        "pglua1c5.xpt", "plipids5.xpt", "prenal5.xpt"]
    w6_bio = ["panthro6.sas7bdat", "pbgluaic6.sas7bdat", "pbhepat6.sas7bdat",
              "pblipids6.sas7bdat", "pcardio6.sas7bdat"]

    def check_biom(tag, files_):
        present = [f for f in files_ if f in aid_sets]
        if len(present) < 2:
            return f"- {tag} biomarker: <2 files available, skipped"
        s0 = aid_sets[present[0]]
        ok = all(aid_sets[f] == s0 for f in present[1:])
        sizes = {f: len(aid_sets[f]) for f in present}
        return f"- {tag} biomarker AID sets identical: {'PASS' if ok else 'FAIL'} ({sizes})"

    sc.append(check_biom("W4", w4_bio))
    sc.append(check_biom("W5 (core 1839 set)", w5_bio_identical))
    sc.append(check_biom("W6", w6_bio))

    md.extend(sc)
    md.append("")

    (OUT / "02_aid_overlap_focused.md").write_text("\n".join(md))
    print(f"Wrote {OUT / '02_aid_overlap_focused.md'}")


if __name__ == "__main__":
    main()
