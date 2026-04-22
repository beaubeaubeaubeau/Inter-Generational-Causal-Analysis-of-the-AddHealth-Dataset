"""Task 6: Empirical attrition profiling of the Add Health public-use sample.

Caveat
------
The public-use subsample is *re-drawn independently* at each wave (W5 public-use
N=4,196 out of restricted-use N~12,300, roughly a 1/3 resample; similar for W6).
We therefore CANNOT cleanly separate true participant dropout from resampling.
This script measures *appearances* per Wave I AID across later files, which is
the right observable in public-use.

Outputs
-------
    outputs/06_attrition_patterns.csv       -- AID-level long table of
        presence indicators and Wave I stratification variables.
    outputs/06_attrition_stacked_bar.png    -- stacked bar chart of public-use
        appearances per wave, stacked by BIO_SEX.
    outputs/06_attrition_summary.md         -- human-readable summary.
"""
from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(
    "/Users/jb/Desktop/Inter-Generational-Causal-Analysis-of-the-AddHealth-Dataset"
)
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CACHE_AIDS = OUT / "cache" / "aids"
CACHE_AIDS.mkdir(parents=True, exist_ok=True)

W1_INHOME = DATA / "W1" / "w1inhome.sas7bdat"


# ---------------------------------------------------------------------------
# AID presence helpers
# ---------------------------------------------------------------------------

def _read_aids(path: Path) -> set[str]:
    """Read AID column from a SAS or XPT file and return a set of string AIDs,
    cached to ``outputs/cache/aids/<fname>.pkl``."""
    cache_path = CACHE_AIDS / f"{path.name}.pkl"
    if cache_path.exists():
        with cache_path.open("rb") as fh:
            return pickle.load(fh)

    suffix = path.suffix.lower()
    if suffix == ".sas7bdat":
        try:
            df, _ = pyreadstat.read_sas7bdat(str(path), usecols=["AID"])
        except Exception:
            df, _ = pyreadstat.read_sas7bdat(str(path))
            df = df[["AID"]]
    elif suffix == ".xpt":
        try:
            df, _ = pyreadstat.read_xport(str(path), usecols=["AID"])
        except Exception:
            df, _ = pyreadstat.read_xport(str(path))
            df = df[["AID"]]
    else:
        raise ValueError(f"Unsupported extension: {suffix}")

    aids = set(df["AID"].dropna().astype(str).str.strip().unique())
    with cache_path.open("wb") as fh:
        pickle.dump(aids, fh)
    return aids


def _union_aids(paths: list[Path]) -> set[str]:
    s: set[str] = set()
    for p in paths:
        s |= _read_aids(p)
    return s


# Files used for each appearance indicator
FILES = {
    "w1_inhome":     [DATA / "W1" / "w1inhome.sas7bdat"],
    "w1_network":    [DATA / "W1" / "w1network.sas7bdat"],
    "w2_inhome":     [DATA / "W2" / "w2inhome.sas7bdat"],
    "w3_inhome":     [DATA / "W3" / "w3inhome.sas7bdat"],
    "w4_inhome":     [DATA / "W4" / "w4inhome.sas7bdat"],
    # biomarker files at W4 are the same 5114 as w4inhome, but we keep the
    # indicator separate so the table is honest.
    "w4_biomarker":  [DATA / "W4" / f for f in
                      ("w4lipid.sas7bdat",
                       "w4glucose.sas7bdat",
                       "w4ebv_hscrp.sas7bdat")],
    "w5_inhome":     [DATA / "W5" / "pwave5.xpt"],
    "w5_biomarker":  [DATA / "W5" / f for f in
                      ("panthro5.xpt",
                       "pcardio5.xpt",
                       "pcrp5.xpt",
                       "pglua1c5.xpt",
                       "plipids5.xpt",
                       "prenal5.xpt")],
    "w5_meds":       [DATA / "W5" / "pmeds5.xpt"],
    "w6_inhome":     [DATA / "W6" / "pwave6.sas7bdat"],
    "w6_biomarker":  [DATA / "W6" / f for f in
                      ("panthro6.sas7bdat",
                       "pbgluaic6.sas7bdat",
                       "pbhepat6.sas7bdat",
                       "pblipids6.sas7bdat",
                       "pcardio6.sas7bdat")],
    "w6_meds":       [DATA / "W6" / "pmeds6.sas7bdat"],
}

PRESENCE_COLS = list(FILES.keys())


# ---------------------------------------------------------------------------
# Wave I stratification variables
# ---------------------------------------------------------------------------

# BIO_SEX: 1=male, 2=female, 6=refused
# H1GI4: Hispanic (0=no, 1=yes, 6/8=refused/dk)
# H1GI6A..E: race components (0/1 each; multiple allowed)
# PA12: parent questionnaire -- A12 level of education (1-10 scale, 96=refused)
STRATA_COLS = ["AID", "BIO_SEX",
               "H1GI4",
               "H1GI6A", "H1GI6B", "H1GI6C", "H1GI6D", "H1GI6E",
               "PA12"]


def _collapse_race(row: pd.Series) -> str:
    """Hispanic -> Black-NH -> White-NH -> Other-NH (multi-race goes to Other)."""
    hisp = row.get("H1GI4")
    if hisp == 1:
        return "Hispanic"
    # race components (0/1). 6/8 treated as missing.
    def _yes(v):
        return v == 1
    black = _yes(row.get("H1GI6B"))
    white = _yes(row.get("H1GI6A"))
    indian = _yes(row.get("H1GI6C"))
    asian = _yes(row.get("H1GI6D"))
    other = _yes(row.get("H1GI6E"))
    n_yes = sum([black, white, indian, asian, other])
    if n_yes == 0:
        return "Unknown"
    if n_yes >= 2:
        return "Other-NH"  # multiracial -> Other-NH bucket
    if black:
        return "Black-NH"
    if white:
        return "White-NH"
    return "Other-NH"


def _parent_ed_tertile(s: pd.Series) -> pd.Series:
    """PA12 is a 1-9 ordinal scale (1=<=8th grade ... 9=prof beyond college);
    10 and 96 are 'never went to school' / refused. Collapse to tertiles
    (low / mid / high) on the valid 1-9 range; everything else -> 'Missing'.
    """
    clean = s.where(s.between(1, 9))
    # Quantile-based tertiles on observed valid distribution
    try:
        q = pd.qcut(clean, 3, labels=["Low", "Mid", "High"], duplicates="drop")
    except ValueError:
        q = pd.cut(clean, bins=[0, 3, 6, 9], labels=["Low", "Mid", "High"])
    out = q.astype("object")
    out[clean.isna()] = "Missing"
    return out


def load_strata() -> pd.DataFrame:
    """Load the W1 stratification variables keyed by AID."""
    df, _ = pyreadstat.read_sas7bdat(str(W1_INHOME), usecols=STRATA_COLS)
    df["AID"] = df["AID"].astype(str).str.strip()
    df["sex"] = df["BIO_SEX"].map({1: "Male", 2: "Female"}).fillna("Unknown")
    df["race"] = df.apply(_collapse_race, axis=1)
    df["parent_ed_tertile"] = _parent_ed_tertile(df["PA12"])
    return df[["AID", "sex", "race", "parent_ed_tertile",
               "BIO_SEX", "H1GI4",
               "H1GI6A", "H1GI6B", "H1GI6C", "H1GI6D", "H1GI6E",
               "PA12"]]


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def build_presence_table() -> pd.DataFrame:
    print("[06] Loading W1 baseline cohort (w1inhome) ...")
    w1_aids = sorted(_read_aids(W1_INHOME))
    print(f"     W1 baseline N = {len(w1_aids)}")

    presence_sets: dict[str, set[str]] = {}
    for col, paths in FILES.items():
        presence_sets[col] = _union_aids(paths)
        print(f"     {col:14s} file-union N = {len(presence_sets[col])}")

    # Build the wide table, restricted to W1 AIDs
    rows = []
    for aid in w1_aids:
        row = {"AID": aid}
        for col in PRESENCE_COLS:
            row[col] = int(aid in presence_sets[col])
        rows.append(row)
    pres = pd.DataFrame(rows)

    print("[06] Loading W1 stratification variables ...")
    strata = load_strata()
    merged = pres.merge(strata, on="AID", how="left")
    return merged


def compute_joint_counts(pres: pd.DataFrame) -> dict[str, int]:
    def _n(expr: pd.Series) -> int:
        return int(expr.sum())

    w1 = pres["w1_inhome"] == 1
    joints = {
        "W1": _n(w1),
        "W1 & W2": _n(w1 & (pres["w2_inhome"] == 1)),
        "W1 & W3": _n(w1 & (pres["w3_inhome"] == 1)),
        "W1 & W4": _n(w1 & (pres["w4_inhome"] == 1)),
        "W1 & W5": _n(w1 & (pres["w5_inhome"] == 1)),
        "W1 & W6": _n(w1 & (pres["w6_inhome"] == 1)),
        "W1 & W4 & W5": _n(w1 & (pres["w4_inhome"] == 1) & (pres["w5_inhome"] == 1)),
        "W1 & W5 & W6": _n(w1 & (pres["w5_inhome"] == 1) & (pres["w6_inhome"] == 1)),
        "W1 & W4 & W5 & W6": _n(
            w1 & (pres["w4_inhome"] == 1) & (pres["w5_inhome"] == 1)
            & (pres["w6_inhome"] == 1)),
        "W1 & W2 & W3 & W4 & W5 (all 5 waves)": _n(
            w1 & (pres["w2_inhome"] == 1) & (pres["w3_inhome"] == 1)
            & (pres["w4_inhome"] == 1) & (pres["w5_inhome"] == 1)),
        "W1 all 6 waves (W1-W6 in-home)": _n(
            w1 & (pres["w2_inhome"] == 1) & (pres["w3_inhome"] == 1)
            & (pres["w4_inhome"] == 1) & (pres["w5_inhome"] == 1)
            & (pres["w6_inhome"] == 1)),
        # biomarker-stacked panels
        "W1 & W4 biomarker": _n(w1 & (pres["w4_biomarker"] == 1)),
        "W1 & W4 bio & W5 bio": _n(
            w1 & (pres["w4_biomarker"] == 1) & (pres["w5_biomarker"] == 1)),
        "W1 & W4 bio & W5 bio & W6 bio": _n(
            w1 & (pres["w4_biomarker"] == 1) & (pres["w5_biomarker"] == 1)
            & (pres["w6_biomarker"] == 1)),
    }
    return joints


def stratified_breakdown(pres: pd.DataFrame, wave_col: str) -> pd.DataFrame:
    """Return a 3-way breakdown (sex x race x parent_ed_tertile) with appearance
    counts and rates at ``wave_col``.
    """
    g = pres.groupby(["sex", "race", "parent_ed_tertile"], dropna=False)
    out = g[wave_col].agg(n_w1="count", n_appear="sum").reset_index()
    out["pct_appear"] = (100 * out["n_appear"] / out["n_w1"]).round(1)
    return out


def stacked_bar(pres: pd.DataFrame, out_path: Path) -> None:
    wave_labels = [
        ("W1 in-home", "w1_inhome"),
        ("W1 network", "w1_network"),
        ("W2 in-home", "w2_inhome"),
        ("W3 in-home", "w3_inhome"),
        ("W4 in-home", "w4_inhome"),
        ("W4 biomarker", "w4_biomarker"),
        ("W5 in-home", "w5_inhome"),
        ("W5 biomarker", "w5_biomarker"),
        ("W5 meds", "w5_meds"),
        ("W6 in-home", "w6_inhome"),
        ("W6 biomarker", "w6_biomarker"),
        ("W6 meds", "w6_meds"),
    ]
    sex_levels = ["Male", "Female", "Unknown"]
    colors = {"Male": "#3b7dd8", "Female": "#d8583b", "Unknown": "#999999"}

    counts = {s: [] for s in sex_levels}
    totals = []
    for _, col in wave_labels:
        sub = pres[pres[col] == 1]
        totals.append(len(sub))
        vc = sub["sex"].value_counts()
        for s in sex_levels:
            counts[s].append(int(vc.get(s, 0)))

    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(wave_labels))
    bottoms = np.zeros(len(wave_labels))
    for s in sex_levels:
        ax.bar(x, counts[s], bottom=bottoms, label=s, color=colors[s])
        bottoms = bottoms + np.asarray(counts[s])
    # annotate totals on top
    for i, t in enumerate(totals):
        ax.text(i, t + 60, str(t), ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([lab for lab, _ in wave_labels], rotation=35, ha="right")
    ax.set_ylabel("W1 AIDs appearing in file (public-use)")
    ax.set_title(
        "Public-use appearances per file, stacked by Wave I biological sex\n"
        "(baseline cohort = 6,504 W1 in-home respondents)"
    )
    ax.legend(title="Sex (W1)")
    ax.set_ylim(0, max(totals) * 1.12)
    fig.tight_layout()
    fig.savefig(out_path, dpi=160)
    plt.close(fig)
    print(f"     wrote {out_path}")


# ---------------------------------------------------------------------------
# Markdown summary
# ---------------------------------------------------------------------------

def _fmt_pct(n: int, d: int) -> str:
    return f"{100*n/d:.1f}%" if d else "-"


def _df_to_md(df: pd.DataFrame) -> str:
    """Render a small DataFrame as a GitHub-flavored markdown table without
    pulling in the `tabulate` dependency."""
    cols = list(df.columns)
    header = "| " + " | ".join(str(c) for c in cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    rows = []
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                # Integers-as-floats -> strip decimals; else keep 1 dp
                if float(v).is_integer():
                    cells.append(str(int(v)))
                else:
                    cells.append(f"{v:.1f}")
            elif pd.isna(v):
                cells.append("")
            else:
                cells.append(str(v))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join([header, sep, *rows])


def write_summary(pres: pd.DataFrame, joints: dict[str, int],
                  summary_path: Path) -> None:
    n_w1 = int((pres["w1_inhome"] == 1).sum())

    lines: list[str] = []
    lines.append("# Task 6 - Public-Use Attrition / Appearance Profile\n")
    lines.append(
        "**Caveat.** The Add Health *public-use* subsample is re-drawn "
        "independently at each wave (W5 public-use N=4,196 of restricted-use "
        "N~12,300 is a ~1/3 resample; W6 public-use N=3,937 is similar). "
        "What looks like 'attrition' from W1 to W5 in this file set is a "
        "mixture of **true dropout** and **independent resampling at the wave "
        "level**. Without restricted-use participation flags we cannot "
        "distinguish the two; this report therefore measures **appearances "
        "per W1 AID**, not dropout.\n"
    )

    # --- wave-by-wave ---
    lines.append("## 1. Wave-by-wave appearance counts (of 6,504 W1 AIDs)\n")
    lines.append("| File | W1 AIDs appearing | Retention % from W1 |")
    lines.append("|------|------------------:|--------------------:|")
    for col in PRESENCE_COLS:
        n = int((pres[col] == 1).sum())
        lines.append(f"| `{col}` | {n:,} | {_fmt_pct(n, n_w1)} |")
    lines.append("")

    # --- joint overlaps ---
    lines.append("## 2. Joint overlaps\n")
    lines.append(f"Of the N={n_w1:,} W1 public-use respondents:\n")
    lines.append("| Pattern | N | % of W1 |")
    lines.append("|---------|--:|--------:|")
    for k, v in joints.items():
        lines.append(f"| {k} | {v:,} | {_fmt_pct(v, n_w1)} |")
    lines.append("")

    # --- W5 stratified breakdown ---
    lines.append("## 3. Stratified breakdown: W5 in-home appearance\n")
    lines.append(
        "Rates are '% of W1 AIDs in that cell that appear in the Wave V "
        "public-use mixed-mode file.'\n"
    )
    tbl = stratified_breakdown(pres, "w5_inhome")
    lines.append(_df_to_md(tbl))
    lines.append("")

    # --- 2-way for robustness ---
    lines.append("### 3b. 2-way (sex x race) for W5 in-home\n")
    sub = pres.groupby(["sex", "race"], dropna=False)["w5_inhome"].agg(
        n_w1="count", n_appear="sum").reset_index()
    sub["pct_appear"] = (100 * sub["n_appear"] / sub["n_w1"]).round(1)
    lines.append(_df_to_md(sub))
    lines.append("")

    # --- W6 stratified breakdown ---
    lines.append("## 4. Stratified breakdown: W6 in-home appearance\n")
    tbl6 = stratified_breakdown(pres, "w6_inhome")
    lines.append(_df_to_md(tbl6))
    lines.append("")

    lines.append("### 4b. 2-way (sex x race) for W6 in-home\n")
    sub6 = pres.groupby(["sex", "race"], dropna=False)["w6_inhome"].agg(
        n_w1="count", n_appear="sum").reset_index()
    sub6["pct_appear"] = (100 * sub6["n_appear"] / sub6["n_w1"]).round(1)
    lines.append(_df_to_md(sub6))
    lines.append("")

    # --- interpretation ---
    lines.append("## 5. Interpretation: resampling vs true dropout\n")
    lines.append(
        "Wave V full-sample N is ~12,300; the public-use release is 4,196 "
        "(~34%). Wave VI full-sample N is ~11,000; public-use is 3,937 (~36%). "
        "That means roughly two-thirds of the W1->W5 'loss' we observe here "
        "is due to the independent public-use draw, not dropout. The 4,196 "
        "W5 public-use respondents are themselves a probability sample that "
        "overlaps only partially with the W4 public-use sample (5,114) and "
        "the W1 public-use sample (6,504). Accordingly, the retention "
        "percentages above **understate true Add Health retention** and "
        "**overstate attrition**. The stratified breakdown is still "
        "informative for detecting *differential* selection on sex / race / "
        "parental-education, because the public-use draw is designed to "
        "approximately preserve those marginals.\n"
    )
    lines.append(
        "**Parental-education note.** Parental education is taken from `PA12` "
        "(Parent Questionnaire item A12, 1=<=8th grade ... 9=professional "
        "training beyond college; 10=never went to school, 96=refused). "
        f"{(pres['PA12'].between(1,9)).sum():,} of {n_w1:,} W1 AIDs have a "
        "valid PA12 response (parent questionnaire was not completed for all "
        "adolescents), so parental-ed tertile is 'Missing' for the rest. "
        "Cells with 'Missing' parental-ed are retained in the breakdown.\n"
    )

    summary_path.write_text("\n".join(lines))
    print(f"     wrote {summary_path}")


def main() -> None:
    pres = build_presence_table()
    pres_out = OUT / "06_attrition_patterns.csv"
    pres.to_csv(pres_out, index=False)
    print(f"     wrote {pres_out}")

    joints = compute_joint_counts(pres)

    stacked_bar(pres, OUT / "06_attrition_stacked_bar.png")
    write_summary(pres, joints, OUT / "06_attrition_summary.md")

    # Console digest
    n_w1 = int((pres["w1_inhome"] == 1).sum())
    print("\n=== CONSOLE DIGEST ===")
    print(f"W1 baseline N = {n_w1}")
    for col in PRESENCE_COLS:
        n = int((pres[col] == 1).sum())
        print(f"  {col:14s} {n:5d}  ({100*n/n_w1:5.1f}%)")
    print()
    for k, v in joints.items():
        print(f"  {k:42s} {v:5d}  ({100*v/n_w1:5.1f}%)")


if __name__ == "__main__":
    main()
