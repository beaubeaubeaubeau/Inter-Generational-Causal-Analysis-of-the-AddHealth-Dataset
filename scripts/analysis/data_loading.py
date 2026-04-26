"""Cached-parquet and SAS/XPT loaders for the W1/W4/W5 frames + survey weights.

``load_outcome`` looks up an outcome code in the cached W4 / W5 parquets and
applies ``clean_var``. The ``load_w*`` helpers wrap the parquet/SAS reads.
"""
from __future__ import annotations

import pandas as pd

from . import CACHE, DATA
from .cleaning import clean_var


def load_outcome(aid: pd.Series, code: str) -> pd.Series:
    """Return a cleaned numeric outcome series aligned to `aid`.

    Looks up `code` in `w4inhome.parquet` (H4*) or `pwave5.parquet` (H5*).
    Applies `clean_var` (strips reserve codes via VALID_RANGES where defined).
    Returns a Series indexed like `aid` with NaN where the respondent has no
    matching row.
    """
    if code.startswith("H4"):
        src = pd.read_parquet(CACHE / "w4inhome.parquet", columns=["AID", code])
    elif code.startswith("H5"):
        src = pd.read_parquet(CACHE / "pwave5.parquet", columns=["AID", code])
    else:
        raise ValueError(f"Unrecognized outcome prefix: {code}")
    src[code] = clean_var(src[code], code)
    m = pd.DataFrame({"AID": aid.values}).merge(src, on="AID", how="left")
    return pd.Series(m[code].values, index=aid.index, name=code)


# ---------------------------------------------------------------------------
# Cache loaders
# ---------------------------------------------------------------------------
def _load_parquet(name: str) -> pd.DataFrame:
    path = CACHE / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing cached parquet: {path}")
    return pd.read_parquet(path)


def load_w1_network() -> pd.DataFrame:
    return _load_parquet("w1network")


def load_w1_inhome() -> pd.DataFrame:
    return _load_parquet("w1inhome")


def load_w4_inhome() -> pd.DataFrame:
    return _load_parquet("w4inhome")


def load_w5() -> pd.DataFrame:
    return _load_parquet("pwave5")


def load_w1_weight() -> pd.DataFrame:
    import pyreadstat
    df, _ = pyreadstat.read_sas7bdat(str(DATA / "W1" / "w1weight.sas7bdat"))
    return df[["AID", "CLUSTER2", "GSWGT1"]]


def load_w4_weight() -> pd.DataFrame:
    import pyreadstat
    df, _ = pyreadstat.read_sas7bdat(str(DATA / "W4" / "w4weight.sas7bdat"))
    return df[["AID", "CLUSTER2", "GSWGT4_2"]]


def load_w5_weight() -> pd.DataFrame:
    import pyreadstat
    df, _ = pyreadstat.read_xport(str(DATA / "W5" / "p5weight.xpt"))
    return df[["AID", "CLUSTER2", "GSW5"]]
