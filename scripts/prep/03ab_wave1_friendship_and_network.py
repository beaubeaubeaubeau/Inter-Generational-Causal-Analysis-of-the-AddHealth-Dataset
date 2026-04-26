"""Task 3a + 3b: Wave I friendship items (Section 20) and Network file catalog.

3a) Empirically identify the two-letter prefix used for Section 20 "Friends"
    items in w1inhome.sas7bdat, list all friendship-related variables with
    labels, value ranges, and frequency tables. Also confirm H1DA7 (hang out
    with friends, Sect 2) and H1ED19-H1ED24 (school belonging).

3b) Full variable catalog for w1network.sas7bdat: 439 variables with labels
    and dtype, categorized (centrality / local_structure / isolation /
    school_level / id / other). Explicitly confirm presence of Bonacich
    centrality and clustering-coefficient variables.

Outputs:
    scripts/prep/outputs/03a_wave1_friendship_items.md
    scripts/prep/outputs/03b_network_variable_catalog.csv
    scripts/prep/outputs/03b_network_variable_catalog.md
    cache/w1inhome_meta.parquet
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import pyreadstat

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis import ROOT, CACHE  # noqa: E402

DATA = ROOT / "data" / "W1"
OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)

W1_INHOME = DATA / "w1inhome.sas7bdat"
W1_NETWORK = DATA / "w1network.sas7bdat"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

FRIEND_KEYWORDS = [
    "friend",
    "best friend",
    "problem",
    "hang out",
    "talk",
    "closeness",
    "close",
    "nominate",
]

SCHOOL_BELONGING_VARS = [f"H1ED{n}" for n in range(19, 25)]


def two_letter_prefix(name: str) -> str | None:
    """Return the two letters after an initial 'H1' prefix, else None."""
    m = re.match(r"^H1([A-Za-z]{2})", name)
    return m.group(1).upper() if m else None


def label_contains_any(label: str | None, keys) -> bool:
    if not label:
        return False
    lab = label.lower()
    return any(k in lab for k in keys)


def get_value_labels(meta, var):
    """Return dict of {raw_value: label} for var, or None."""
    fmt = meta.variable_to_label.get(var)
    if fmt and fmt in meta.value_labels:
        return meta.value_labels[fmt]
    return None


def describe_var(df_col, meta, var) -> dict:
    s = df_col
    non_missing = s.dropna()
    n = int(non_missing.shape[0])
    vmin = non_missing.min() if n else None
    vmax = non_missing.max() if n else None
    vl = get_value_labels(meta, var)
    if vl is not None:
        # categorical: frequency of every raw value (non-missing), then label
        vc = s.value_counts(dropna=True).sort_index()
        freq = [(float(k) if pd.api.types.is_number(k) else k,
                 int(v), vl.get(k, vl.get(float(k), vl.get(int(k), ""))))
                for k, v in vc.items()]
    else:
        freq = None
    sample = s.head(5).tolist()
    return dict(
        var=var,
        label=meta.column_names_to_labels.get(var, ""),
        n_non_missing=n,
        min=vmin,
        max=vmax,
        value_labels=vl,
        freq=freq,
        sample=sample,
    )


# ---------------------------------------------------------------------------
# 3a: Wave I In-Home friendship items
# ---------------------------------------------------------------------------

def task_3a():
    print("[3a] reading w1inhome metadata...")
    _, meta = pyreadstat.read_sas7bdat(str(W1_INHOME), metadataonly=True)
    cols = list(meta.column_names)
    labels = meta.column_names_to_labels
    print(f"     {len(cols)} columns")

    # cache name + label
    meta_df = pd.DataFrame(
        {"var_name": cols, "label": [labels.get(c, "") for c in cols]}
    )
    meta_df.to_parquet(CACHE / "w1inhome_meta.parquet", index=False)
    print(f"     cached -> {CACHE / 'w1inhome_meta.parquet'}")

    # prefix frequencies across H1 variables
    prefix_counts: Counter = Counter()
    for c in cols:
        p = two_letter_prefix(c)
        if p is not None:
            prefix_counts[p] += 1

    # candidate prefixes: label-match friendship keywords
    per_prefix_friendship_hits: dict[str, list[tuple[str, str]]] = {}
    for c in cols:
        p = two_letter_prefix(c)
        if p is None:
            continue
        lab = labels.get(c, "") or ""
        if label_contains_any(lab, ["friend", "hang out", "nominate", "closeness"]):
            per_prefix_friendship_hits.setdefault(p, []).append((c, lab))

    # Candidate set: H1FR, H1WP, H1MF, H1FF  (empirical scan - task listed
    # MF/WP/FR, but the actual file also uses FF for Female-Friend items.)
    candidate_prefixes = ["FR", "WP", "MF", "FF"]
    candidate_summary = {
        p: {
            "total_vars": prefix_counts.get(p, 0),
            "friendship_label_matches": len(per_prefix_friendship_hits.get(p, [])),
            "examples": per_prefix_friendship_hits.get(p, [])[:10],
        }
        for p in candidate_prefixes
    }

    # Section 20 empirically splits into MALE-friend (H1MF*) + FEMALE-friend
    # (H1FF*) blocks.  Any prefix whose variable labels carry an S20Q* tag is
    # Section 20.
    sec20_prefixes_detected: list[str] = []
    for p in candidate_prefixes:
        for v, lab in per_prefix_friendship_hits.get(p, []):
            if "S20Q" in (lab or ""):
                sec20_prefixes_detected.append(p)
                break
    sec20_prefixes_detected = sorted(set(sec20_prefixes_detected))
    section20_prefix = " + ".join(
        "H1" + p for p in sec20_prefixes_detected
    )

    # Collect all variables with those prefixes
    sec20_vars = [
        c for c in cols
        if two_letter_prefix(c) in sec20_prefixes_detected
    ]
    sec20_vars_with_labels = [(v, labels.get(v, "")) for v in sec20_vars]

    # All friendship-keyword hits anywhere (broad scan)
    all_friendship_hits = []
    for c in cols:
        lab = labels.get(c, "") or ""
        if label_contains_any(lab, FRIEND_KEYWORDS):
            all_friendship_hits.append((c, lab))

    # Now load just the needed columns to characterize values
    friend_cols = sec20_vars + ["H1DA7"] + SCHOOL_BELONGING_VARS
    friend_cols = [c for c in friend_cols if c in cols]  # safety

    print(f"[3a] loading {len(friend_cols)} columns (values)...")
    df_vals, meta2 = pyreadstat.read_sas7bdat(
        str(W1_INHOME), usecols=friend_cols
    )

    descriptions = {v: describe_var(df_vals[v], meta2, v) for v in friend_cols}

    # -------------------- render markdown --------------------
    lines: list[str] = []
    lines.append("# Task 3a: Wave I Section 20 Friendship Items (empirical)\n")
    lines.append(f"Source: `{W1_INHOME.relative_to(ROOT)}` "
                 f"({len(cols)} variables)\n")

    lines.append("## Two-letter H1 prefix frequencies\n")
    lines.append("| Prefix | N vars |")
    lines.append("|--------|--------|")
    for p, n in prefix_counts.most_common():
        lines.append(f"| H1{p} | {n} |")
    lines.append("")

    lines.append("## Candidate-prefix friendship-label scan\n")
    lines.append("| Prefix | Total H1xx vars | Friendship-label hits | Examples |")
    lines.append("|--------|----------------|----------------------|----------|")
    for p in candidate_prefixes:
        s = candidate_summary[p]
        ex = "; ".join(f"`{v}`: {lab}" for v, lab in s["examples"][:3]) or "-"
        lines.append(f"| H1{p} | {s['total_vars']} | {s['friendship_label_matches']} | {ex} |")
    lines.append("")

    lines.append(f"### Empirically identified Section 20 prefix(es): **{section20_prefix}**\n")
    lines.append("(Section 20 splits into two parallel blocks: male-friend nominations "
                 "under `H1MF*` and female-friend nominations under `H1FF*`.)\n")
    lines.append(f"All Section-20 variables ({len(sec20_vars)}):\n")
    lines.append("| Variable | Label |")
    lines.append("|----------|-------|")
    for v, lab in sec20_vars_with_labels:
        lines.append(f"| `{v}` | {lab} |")
    lines.append("")

    lines.append("## H1DA7 (Section 2 Daily Activities - hang out with friends)\n")
    if "H1DA7" in descriptions:
        d = descriptions["H1DA7"]
        lines.append(f"- Label: **{d['label']}**")
        lines.append(f"- N non-missing: {d['n_non_missing']}")
        lines.append(f"- Min/Max: {d['min']} / {d['max']}")
        if d["freq"]:
            lines.append("\n| Value | Count | Label |")
            lines.append("|-------|-------|-------|")
            for val, cnt, vlab in d["freq"]:
                lines.append(f"| {val} | {cnt} | {vlab} |")
        lines.append(f"\nSample: {d['sample']}\n")
    else:
        lines.append("**H1DA7 NOT FOUND in file.**\n")

    lines.append("## H1ED19-H1ED24 (School Belonging)\n")
    lines.append("| Variable | Label | N | Min | Max | Value labels |")
    lines.append("|----------|-------|---|-----|-----|--------------|")
    for v in SCHOOL_BELONGING_VARS:
        if v not in descriptions:
            lines.append(f"| `{v}` | NOT FOUND | - | - | - | - |")
            continue
        d = descriptions[v]
        vl = d["value_labels"]
        vl_str = "; ".join(f"{k}={lbl}" for k, lbl in (vl.items() if vl else []))
        lines.append(
            f"| `{v}` | {d['label']} | {d['n_non_missing']} | {d['min']} | {d['max']} | {vl_str} |"
        )
    lines.append("")

    lines.append(f"## Detailed value summaries for each Section-20 variable ({section20_prefix})\n")
    for v in sec20_vars:
        d = descriptions[v]
        lines.append(f"### `{v}` - {d['label']}")
        lines.append(f"- N non-missing: {d['n_non_missing']}")
        lines.append(f"- Min/Max: {d['min']} / {d['max']}")
        if d["freq"]:
            lines.append("\n| Value | Count | Label |")
            lines.append("|-------|-------|-------|")
            for val, cnt, vlab in d["freq"]:
                lines.append(f"| {val} | {cnt} | {vlab} |")
        lines.append(f"\nFirst-5 sample: {d['sample']}\n")

    lines.append("## Broad scan: all variables whose label matches friendship keywords\n")
    lines.append(f"N hits: {len(all_friendship_hits)}\n")
    lines.append("| Variable | Label |")
    lines.append("|----------|-------|")
    for v, lab in all_friendship_hits:
        lines.append(f"| `{v}` | {lab} |")
    lines.append("")

    (OUT / "03a_wave1_friendship_items.md").write_text("\n".join(lines))
    print(f"     wrote {OUT / '03a_wave1_friendship_items.md'}")

    return {
        "section20_prefix": section20_prefix,
        "sec20_vars": sec20_vars,
        "descriptions": descriptions,
    }


# ---------------------------------------------------------------------------
# 3b: Network file catalog
# ---------------------------------------------------------------------------

def categorize_network(label: str, name: str) -> str:
    lab = (label or "").lower()
    nm = name.upper()

    # id
    if nm in {"AID", "SCID", "SQID", "SSCID", "COMMID"} or "_ID" in nm:
        return "id"

    # centrality keywords (degree, bonacich, betweenness, closeness centrality,
    # eigenvector, prestige, influence domain, reach-based)
    centrality_tokens = [
        "degree", "indegree", "outdegree", "in-degree", "out-degree",
        "bonacich", "betweenness", "closeness centrality", "eigenvector",
        "centrality", "prestige", "influence domain", "reachable",
        "reach",
    ]
    if any(t in lab for t in centrality_tokens):
        return "centrality"
    # catch by name when label is sparse
    if re.search(r"^BON|^BCENT|IDGX|ODGX|INDEG|OUTDEG|_CENT|BETW|EIGEN|"
                 r"^REACH|PRXPREST|INFLDMN|IGDMEAN", nm):
        return "centrality"

    # local_structure: clustering coef, reciprocity, transitivity,
    # ego-net density, ego-net heterogeneity/diversity
    if any(t in lab for t in ["cluster", "reciproc", "transitiv", "density",
                              "heterogeneity", "prop. "]):
        return "local_structure"
    if re.search(r"CLUS|^CC[0-9_]?|RECIP|TRANS|DENS|^EH[SRA-Z]|^ER[SRA-Z]",
                 nm):
        return "local_structure"

    # isolation
    if any(t in lab for t in ["isolat", "no friends", "no nominations",
                              "no nomination", "has a best", "has no"]):
        return "isolation"
    if re.search(r"ISOL|^HAVEB", nm):
        return "isolation"

    # school-level (alter-mean aggregates, school totals)
    if any(t in lab for t in ["school", "grade-level", "overall density",
                              "school-level", "alter mean", "send alter",
                              "recv alter", "questionnaires"]):
        return "school_level"
    if re.search(r"^AX[SR]|^SIZE$|^NOUTNOM$|^TAB", nm):
        return "school_level"

    return "other"


def task_3b():
    print("[3b] reading w1network metadata...")
    _, meta = pyreadstat.read_sas7bdat(str(W1_NETWORK), metadataonly=True)
    cols = list(meta.column_names)
    labels = meta.column_names_to_labels
    dtypes = meta.readstat_variable_types  # dict var -> type
    print(f"     {len(cols)} columns")

    rows = []
    for c in cols:
        lab = labels.get(c, "") or ""
        dt = dtypes.get(c, "")
        cat = categorize_network(lab, c)
        rows.append({"var_name": c, "label": lab, "dtype": dt, "category": cat})

    catalog = pd.DataFrame(rows)
    catalog.to_csv(OUT / "03b_network_variable_catalog.csv", index=False)

    # Summary
    per_cat = catalog["category"].value_counts().to_dict()

    # Bonacich + clustering explicit search
    bon_mask = catalog["var_name"].str.contains("BON", case=False, regex=False) | \
               catalog["label"].str.contains("bonacich", case=False, regex=False, na=False)
    clus_mask = catalog["var_name"].str.contains("CLUS", case=False, regex=False) | \
                catalog["var_name"].str.fullmatch(r"CC[0-9_A-Z]*", case=False, na=False) | \
                catalog["label"].str.contains("cluster", case=False, regex=False, na=False)

    bon_hits = catalog[bon_mask]
    clus_hits = catalog[clus_mask]

    # Nomination variants (best-friend-only vs all, directed)
    nom_mask = catalog["label"].str.contains(
        "nomin|best friend|friend", case=False, regex=True, na=False
    ) | catalog["var_name"].str.contains(
        "NOM|BF|FR", case=False, regex=True, na=False
    )
    nom_hits = catalog[nom_mask]

    # school-level hint
    school_agg_mask = catalog["label"].str.contains(
        "school|mean|average|grade-level|overall", case=False, regex=True, na=False
    )
    school_agg_hits = catalog[school_agg_mask]

    # ---- markdown
    lines = ["# Task 3b: Wave I Public-Use Network File Catalog\n"]
    lines.append(f"Source: `{W1_NETWORK.relative_to(ROOT)}` (N rows = "
                 f"{meta.number_rows}, N vars = {len(cols)})\n")

    lines.append("## Totals per category\n")
    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat in ["centrality", "local_structure", "isolation", "school_level", "id", "other"]:
        lines.append(f"| {cat} | {per_cat.get(cat, 0)} |")
    lines.append("")

    lines.append("## Examples per category (up to 10)\n")
    for cat in ["centrality", "local_structure", "isolation", "school_level", "id", "other"]:
        sub = catalog[catalog["category"] == cat].head(10)
        lines.append(f"### {cat} ({per_cat.get(cat, 0)})\n")
        if sub.empty:
            lines.append("_(none)_\n")
            continue
        lines.append("| Variable | Label |")
        lines.append("|----------|-------|")
        for _, r in sub.iterrows():
            lines.append(f"| `{r['var_name']}` | {r['label']} |")
        lines.append("")

    lines.append("## Bonacich centrality (explicit search)\n")
    lines.append(f"Hits: **{len(bon_hits)}** variables with 'BON' in name or 'bonacich' in label.\n")
    if len(bon_hits):
        lines.append("| Variable | Label |")
        lines.append("|----------|-------|")
        for _, r in bon_hits.iterrows():
            lines.append(f"| `{r['var_name']}` | {r['label']} |")
        lines.append("")
        lines.append("**Answer: YES, Bonacich centrality variables appear by name.**\n")
    else:
        lines.append("**Answer: NO, no Bonacich centrality variables found by name.**\n")

    lines.append("## Clustering coefficient (explicit search)\n")
    lines.append(f"Hits: **{len(clus_hits)}** variables.\n")
    if len(clus_hits):
        lines.append("| Variable | Label |")
        lines.append("|----------|-------|")
        for _, r in clus_hits.iterrows():
            lines.append(f"| `{r['var_name']}` | {r['label']} |")
        lines.append("")
        lines.append("**Answer: YES, clustering-coefficient variables appear by name.**\n")
    else:
        lines.append("**Answer: NO, no clustering-coefficient variables found by name.**\n")

    lines.append("## Nomination-variant scan\n")
    lines.append(f"Variables whose label or name suggest friend/nomination: **{len(nom_hits)}**.\n")
    if len(nom_hits):
        lines.append("| Variable | Label |")
        lines.append("|----------|-------|")
        for _, r in nom_hits.iterrows():
            lines.append(f"| `{r['var_name']}` | {r['label']} |")
        lines.append("")

    lines.append("## Possible school-level aggregates\n")
    lines.append(f"Variables whose label mentions school / mean / grade-level / overall: "
                 f"**{len(school_agg_hits)}**.\n")
    if len(school_agg_hits):
        lines.append("| Variable | Label |")
        lines.append("|----------|-------|")
        for _, r in school_agg_hits.iterrows():
            lines.append(f"| `{r['var_name']}` | {r['label']} |")
        lines.append("")

    (OUT / "03b_network_variable_catalog.md").write_text("\n".join(lines))
    print(f"     wrote {OUT / '03b_network_variable_catalog.csv'}")
    print(f"     wrote {OUT / '03b_network_variable_catalog.md'}")

    return {
        "per_cat": per_cat,
        "bon_hits": bon_hits,
        "clus_hits": clus_hits,
    }


def main():
    a = task_3a()
    b = task_3b()
    print("\n=== SUMMARY ===")
    print("Section 20 prefix:", a["section20_prefix"])
    print("Sec 20 vars:", a["sec20_vars"])
    print("Per-category counts:", b["per_cat"])
    print("Bonacich hits:", len(b["bon_hits"]))
    print("Clustering hits:", len(b["clus_hits"]))


if __name__ == "__main__":
    main()
