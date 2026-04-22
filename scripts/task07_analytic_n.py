"""Task 7 support: compute analytic-sample N for the core design permutations.

Produces outputs/07_analytic_n.csv: each row is a design configuration
(e.g. W1 network observed ∩ W4 cognitive valid) with its N.
"""
from __future__ import annotations

import pandas as pd
import pyreadstat
from pathlib import Path

ROOT = Path("/Users/jb/Desktop/Inter-Generational-Causal-Analysis-of-the-AddHealth-Dataset")
DATA = ROOT / "data"
OUT = ROOT / "outputs"


def reserves(vals, codes):
    return vals.isin(codes)


# Wave I network — use IDGX2 (in-degree) as the indicator of "network observed"
print("Loading W1 network...")
net, _ = pyreadstat.read_sas7bdat(str(DATA / "W1" / "w1network.sas7bdat"),
                                   usecols=["AID", "IDGX2", "ODGX2", "BCENT10X"])
net_obs = net[net["IDGX2"].notna()]["AID"].unique()
print(f"  W1 network rows with IDGX2 observed: {len(net_obs)}")

# W1 inhome — AH_PVT baseline cognition
print("Loading W1 inhome AH_PVT...")
w1, _ = pyreadstat.read_sas7bdat(str(DATA / "W1" / "w1inhome.sas7bdat"),
                                  usecols=["AID", "AH_PVT"])
w1_pvt_valid = w1[w1["AH_PVT"].notna() & (w1["AH_PVT"] < 900)]["AID"].unique()
print(f"  W1 inhome AH_PVT valid: {len(w1_pvt_valid)}")

# Wave IV cognitive
print("Loading W4 cognitive...")
w4, _ = pyreadstat.read_sas7bdat(str(DATA / "W4" / "w4inhome.sas7bdat"),
                                  usecols=["AID", "C4WD90_1", "C4WD60_1", "C4NUMSCR"])
RES4 = {96, 97, 98, 99}
w4_imm = w4[w4["C4WD90_1"].notna() & ~reserves(w4["C4WD90_1"], RES4)]["AID"].unique()
w4_del = w4[w4["C4WD60_1"].notna() & ~reserves(w4["C4WD60_1"], RES4)]["AID"].unique()
w4_bds = w4[w4["C4NUMSCR"].notna() & ~reserves(w4["C4NUMSCR"], RES4)]["AID"].unique()
print(f"  W4 immediate: {len(w4_imm)}; delayed: {len(w4_del)}; BDS: {len(w4_bds)}")

# Wave V cognitive
print("Loading W5 cognitive...")
w5, _ = pyreadstat.read_xport(str(DATA / "W5" / "pwave5.xpt"),
                               usecols=["AID", "C5WD90_1", "C5WD60_1",
                                        "H5MH3A", "H5MH3B", "H5MH4A", "H5MH4B",
                                        "H5MH5A", "H5MH5B", "H5MH6A", "H5MH6B",
                                        "H5MH7A", "H5MH7B", "H5MH8A", "H5MH8B",
                                        "H5MH9A", "H5MH9B", "MODE"])
# For Wave V, reserves include 95/96/97/98 plus 3- and 4-digit equivalents
RES5 = {95, 96, 97, 98, 99, 995, 996, 997, 998, 999}
w5_imm = w5[w5["C5WD90_1"].notna() & ~reserves(w5["C5WD90_1"], RES5)]["AID"].unique()
w5_del = w5[w5["C5WD60_1"].notna() & ~reserves(w5["C5WD60_1"], RES5)]["AID"].unique()

# Derive backward digit span for Wave V
bds_cols = [("H5MH3A", "H5MH3B"), ("H5MH4A", "H5MH4B"),
            ("H5MH5A", "H5MH5B"), ("H5MH6A", "H5MH6B"),
            ("H5MH7A", "H5MH7B"), ("H5MH8A", "H5MH8B"),
            ("H5MH9A", "H5MH9B")]
# A trial is "valid" if value is 0 or 1 (not NA and not reserve)
def clean(x):
    return x.where(~reserves(x, RES5))

any_valid = None
for (a, b) in bds_cols:
    va = clean(w5[a]).notna()
    vb = clean(w5[b]).notna()
    v = va | vb
    any_valid = v if any_valid is None else (any_valid | v)
w5_bds_mask = any_valid
w5_bds = w5[w5_bds_mask]["AID"].unique()
print(f"  W5 immediate: {len(w5_imm)}; delayed: {len(w5_del)}; BDS (any trial): {len(w5_bds)}")

# Intersections
rows = []
def inter(a, b):
    return len(set(a) & set(b))

def inter3(a, b, c):
    return len(set(a) & set(b) & set(c))

def inter4(a, b, c, d):
    return len(set(a) & set(b) & set(c) & set(d))

rows.append(("W1 network observed (IDGX2 non-miss)", "—", len(net_obs)))
rows.append(("W1 AH_PVT valid", "—", len(w1_pvt_valid)))
rows.append(("W4 immediate recall valid", "—", len(w4_imm)))
rows.append(("W4 delayed recall valid", "—", len(w4_del)))
rows.append(("W4 backward digit span valid", "—", len(w4_bds)))
rows.append(("W5 immediate recall valid", "—", len(w5_imm)))
rows.append(("W5 delayed recall valid", "—", len(w5_del)))
rows.append(("W5 BDS any trial valid", "—", len(w5_bds)))

rows.append(("W1 network ∩ W4 immediate", "Primary W4 design", inter(net_obs, w4_imm)))
rows.append(("W1 network ∩ W4 BDS", "Primary W4 design (BDS)", inter(net_obs, w4_bds)))
rows.append(("W1 network ∩ W5 immediate", "Primary W5 design", inter(net_obs, w5_imm)))
rows.append(("W1 network ∩ W5 BDS", "Primary W5 design (BDS)", inter(net_obs, w5_bds)))
rows.append(("W1 network ∩ W4 imm ∩ W5 imm", "Longitudinal change-score", inter3(net_obs, w4_imm, w5_imm)))
rows.append(("W1 network ∩ W4 BDS ∩ W5 BDS", "Longit change (BDS)", inter3(net_obs, w4_bds, w5_bds)))
rows.append(("W1 AH_PVT ∩ W4 immediate", "Friendship(survey)→W4 cog, with baseline", inter(w1_pvt_valid, w4_imm)))
rows.append(("W1 AH_PVT ∩ W5 immediate", "Friendship(survey)→W5 cog, with baseline", inter(w1_pvt_valid, w5_imm)))
rows.append(("W1 network ∩ W1 AH_PVT ∩ W4 imm", "Network + baseline + W4 outcome", inter3(net_obs, w1_pvt_valid, w4_imm)))
rows.append(("W1 network ∩ W1 AH_PVT ∩ W5 imm", "Network + baseline + W5 outcome", inter3(net_obs, w1_pvt_valid, w5_imm)))
rows.append(("W1 network ∩ W1 AH_PVT ∩ W4 imm ∩ W5 imm", "Full longitudinal with baseline", inter4(net_obs, w1_pvt_valid, w4_imm, w5_imm)))

df = pd.DataFrame(rows, columns=["configuration", "design_purpose", "N"])
df.to_csv(OUT / "07_analytic_n.csv", index=False)
print("\n")
print(df.to_string(index=False))
