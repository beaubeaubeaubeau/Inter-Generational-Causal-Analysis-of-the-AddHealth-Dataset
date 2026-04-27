"""Shared E-value / Cornfield-grid / η-tilt sensitivity-panel scaffolding.

This module bundles the boilerplate that every Phase-6 experiment runs after
its primary fit:

  - ``build_evalue_table(primary, ...)``
        Compute VanderWeele-Ding E-values per primary cell. For continuous
        outcomes, the standardised effect ``d = β · SD_X / SD_Y`` is mapped
        to a pseudo risk-ratio ``RR ≈ exp(0.91 · d)`` (Chinn 2000) before
        applying the E-value formula (`scripts/analysis/sensitivity.py:evalue`).

  - ``build_cornfield_grid(primary, rr_au_grid, rr_uy_grid)``
        For each significant cell (``p < 0.05``) tabulate the bias-factor
        ``B = (RR_AU · RR_UY) / (RR_AU + RR_UY − 1)`` from
        `scripts/analysis/sensitivity.py:cornfield_bound` for every pair on a
        small ``RR_AU × RR_UY`` grid. Useful as a robustness curve sweep —
        the contour ``B = observed_RR`` traces the (RR_AU, RR_UY) pairs that
        would just explain the observed signal away.

  - ``build_eta_tilt_table(rows, eta_grid)``
        For each (binary-A) row supplied, sweep ``η_1, η_0`` over a 5×5 grid
        and record the perturbed ATE estimate from
        `scripts/analysis/sensitivity.py:eta_tilt`. Continuous-A experiments
        either binarise via the top-vs-bottom-quintile contrast or document
        the limitation in their report.

  - ``plot_sensitivity_panel(...)``
        Three-panel figure: (a) E-value bar chart per primary cell;
        (b) Cornfield bias-factor heatmap on the (RR_AU, RR_UY) grid for the
        most-significant cell; (c) η-tilt ATE-shift curve (or an "N/A —
        continuous exposure" annotation when applicable).

All helpers are pure-pandas / pure-matplotlib; they never touch the parquet
cache and do not depend on per-experiment registries. Every experiment's
``run.py`` calls these from a small adaptor that reshapes its own primary
results into the expected schema and supplies any (μ_1, μ_0, A) inputs the
η-tilt sweep needs.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import math

import numpy as np
import pandas as pd

from analysis.sensitivity import cornfield_bound, eta_tilt, evalue

__all__ = [
    "DEFAULT_RR_GRID",
    "DEFAULT_ETA_GRID",
    "rr_from_beta",
    "build_evalue_table",
    "build_cornfield_grid",
    "build_eta_tilt_table",
    "build_eta_cell_from_quintile_contrast",
    "plot_sensitivity_panel",
]

# Default sensitivity sweeps (locked here so every panel looks comparable).
DEFAULT_RR_GRID: Tuple[float, ...] = (1.5, 2.0, 3.0, 5.0)
DEFAULT_ETA_GRID: Tuple[float, ...] = (0.8, 0.9, 1.0, 1.1, 1.2)


# ---------------------------------------------------------------------------
# β → pseudo risk-ratio (Chinn 2000) for continuous outcomes.
# ---------------------------------------------------------------------------
def rr_from_beta(
    beta: float,
    sd_x: Optional[float] = None,
    sd_y: Optional[float] = None,
) -> float:
    """Continuous-outcome β to pseudo-RR via Chinn-2000 (``RR ≈ exp(0.91·d)``).

    ``d = β · SD_X / SD_Y`` is the standardised effect size of a unit-SD-X
    increase on the outcome's SD scale. When ``sd_x`` / ``sd_y`` are missing,
    we fall back to ``RR = exp(|β|)`` — the unit-exposure proxy used by the
    earlier inline sensitivity blocks. The returned RR is always ``≥ 1``;
    protective effects are mapped through ``1 / RR`` upstream by ``evalue``.
    """
    if not np.isfinite(beta):
        return float("nan")
    if sd_x is not None and sd_y is not None and sd_y > 0 and np.isfinite(sd_x):
        d = beta * float(sd_x) / float(sd_y)
        rr = math.exp(0.91 * d)
    else:
        rr = math.exp(abs(beta))
    if rr <= 0:
        return float("nan")
    return rr


# ---------------------------------------------------------------------------
# E-value table.
# ---------------------------------------------------------------------------
def build_evalue_table(
    primary: pd.DataFrame,
    *,
    beta_col: str = "beta",
    sd_x_col: Optional[str] = None,
    sd_y_col: Optional[str] = None,
    keep_cols: Sequence[str] = (),
    only_significant: bool = False,
    p_col: str = "p",
    p_thresh: float = 0.05,
) -> pd.DataFrame:
    """Per-row E-value via the Chinn-2000 → VanderWeele transform.

    Parameters
    ----------
    primary
        Primary-fit dataframe; must include ``beta_col`` and (if
        ``only_significant``) ``p_col``.
    beta_col
        Name of the β column.
    sd_x_col, sd_y_col
        Names of the per-row exposure / outcome SD columns. If either is
        ``None`` the function falls back to the unit-exposure proxy
        ``RR = exp(|β|)`` and notes that in the ``rr_basis`` column.
    keep_cols
        Identifying columns to copy through (e.g. ``("exposure",
        "outcome")``).
    only_significant
        If True, drop rows with ``p ≥ p_thresh`` before computing E-values.
    """
    rows: List[dict] = []
    for _, r in primary.iterrows():
        if only_significant and (
            pd.isna(r.get(p_col)) or float(r[p_col]) >= p_thresh
        ):
            continue
        beta = r.get(beta_col, np.nan)
        sd_x = float(r[sd_x_col]) if sd_x_col and sd_x_col in r else None
        sd_y = float(r[sd_y_col]) if sd_y_col and sd_y_col in r else None
        rr = rr_from_beta(float(beta) if pd.notna(beta) else np.nan, sd_x, sd_y)
        try:
            ev = evalue(rr) if (np.isfinite(rr) and rr > 0) else float("nan")
        except (ValueError, OverflowError):
            ev = float("nan")
        out: Dict[str, object] = {c: r[c] for c in keep_cols if c in r}
        out.update({
            "beta": float(beta) if pd.notna(beta) else np.nan,
            "p": float(r[p_col]) if (p_col in r and pd.notna(r[p_col])) else np.nan,
            "sd_x": sd_x if sd_x is not None else np.nan,
            "sd_y": sd_y if sd_y is not None else np.nan,
            "rr_basis": "chinn-2000" if (sd_x is not None and sd_y is not None) else "unit-exposure",
            "rr": rr,
            "evalue": ev,
        })
        rows.append(out)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Cornfield grid.
# ---------------------------------------------------------------------------
def build_cornfield_grid(
    primary: pd.DataFrame,
    *,
    rr_au_grid: Sequence[float] = DEFAULT_RR_GRID,
    rr_uy_grid: Sequence[float] = DEFAULT_RR_GRID,
    beta_col: str = "beta",
    p_col: str = "p",
    p_thresh: float = 0.05,
    sd_x_col: Optional[str] = None,
    sd_y_col: Optional[str] = None,
    keep_cols: Sequence[str] = (),
) -> pd.DataFrame:
    """Tabulate Cornfield ``B`` over an ``RR_AU × RR_UY`` grid per significant β.

    Long-form output (one row per (cell, RR_AU, RR_UY) triple) so the same
    table is easy to pivot for the heatmap panel and easy to filter by cell
    for the ``B = observed_RR`` "explained-away" curve.
    """
    rows: List[dict] = []
    for _, r in primary.iterrows():
        if pd.isna(r.get(p_col)) or float(r[p_col]) >= p_thresh:
            continue
        beta = r.get(beta_col, np.nan)
        if pd.isna(beta):
            continue
        sd_x = float(r[sd_x_col]) if sd_x_col and sd_x_col in r else None
        sd_y = float(r[sd_y_col]) if sd_y_col and sd_y_col in r else None
        rr_obs = rr_from_beta(float(beta), sd_x, sd_y)
        if not np.isfinite(rr_obs) or rr_obs <= 0:
            continue
        rr_obs_geq1 = 1.0 / rr_obs if rr_obs < 1.0 else rr_obs
        identity = {c: r[c] for c in keep_cols if c in r}
        for rr_au in rr_au_grid:
            for rr_uy in rr_uy_grid:
                try:
                    B = cornfield_bound(float(rr_au), float(rr_uy))
                except ValueError:
                    B = float("nan")
                row = dict(identity)
                row.update({
                    "rr_au": float(rr_au),
                    "rr_uy": float(rr_uy),
                    "B": B,
                    "rr_observed": rr_obs_geq1,
                    "explains_away": bool(np.isfinite(B) and B >= rr_obs_geq1),
                })
                rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# η-tilt table.
# ---------------------------------------------------------------------------
def build_eta_tilt_table(
    cells: Iterable[dict],
    *,
    eta_grid: Sequence[float] = DEFAULT_ETA_GRID,
) -> pd.DataFrame:
    """For each binary-A cell, sweep (η_1, η_0) over the 5×5 grid.

    Each ``cells`` entry must look like::

        {
            "label": "<identifying str>",          # e.g. "IDGX2 -> H4BMI"
            "exposure": "...",                     # optional pass-through
            "outcome":  "...",                     # optional pass-through
            "binarisation": "raw" | "top-quintile" | "...",
            "A":   <0/1 array>,
            "mu_1": <array>,
            "mu_0": <array>,
            # plus any extra identifying keys; all are copied through.
        }

    A baseline ATE row (``η_1 = η_0 = 1``) is included so downstream prose can
    quote "perturbed ATE − baseline ATE" deltas directly.
    """
    rows: List[dict] = []
    for cell in cells:
        A = np.asarray(cell["A"], dtype=float)
        mu_1 = np.asarray(cell["mu_1"], dtype=float)
        mu_0 = np.asarray(cell["mu_0"], dtype=float)
        baseline = eta_tilt(np.ones_like(mu_1), np.ones_like(mu_0), mu_1, mu_0, A)
        identity = {
            k: v for k, v in cell.items()
            if k not in {"A", "mu_1", "mu_0"}
        }
        identity.setdefault("binarisation", "raw")
        for e1 in eta_grid:
            for e0 in eta_grid:
                ate = eta_tilt(
                    np.full_like(mu_1, float(e1)),
                    np.full_like(mu_0, float(e0)),
                    mu_1, mu_0, A,
                )
                row = dict(identity)
                row.update({
                    "eta_1": float(e1),
                    "eta_0": float(e0),
                    "ate_perturbed": float(ate),
                    "ate_baseline": float(baseline),
                    "ate_shift": float(ate - baseline),
                })
                rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Helper: build an η-tilt input cell from a continuous exposure via a
# top-quintile-vs-bottom-quintile contrast.
# ---------------------------------------------------------------------------
def build_eta_cell_from_quintile_contrast(
    *,
    label: str,
    df,
    exposure_col: str,
    outcome_col: str,
    weight_col: str,
    cluster_col: str,
    adj_builder,
    extra_keys: Optional[Dict[str, object]] = None,
    force_binary: bool = False,
):
    """Construct the (μ_1, μ_0, A) inputs for η-tilt from a continuous-A column.

    Strategy (documented at the call site in each experiment): cut ``exposure_col``
    into quintiles, restrict the analytic frame to Q1 ∪ Q5, code A = 1 for Q5
    and A = 0 for Q1, fit two separate WLS — one on the A=1 subset, one on the
    A=0 subset — then evaluate both fitted models on the pooled (Q1 ∪ Q5) frame
    to get μ_1 and μ_0 vectors. This converts the continuous-A awkwardness
    flagged in the task spec into a tractable binary-A η-tilt input. Any rows
    with NaN exposure / outcome / weight / adjustment-set covariates are
    dropped before fitting.

    Returns either a dict shaped for ``build_eta_tilt_table`` (``label``,
    ``binarisation`` = ``"top-quintile-vs-bottom"``, ``A``, ``mu_1``, ``mu_0``,
    plus any ``extra_keys``) or ``None`` if either tail is too thin (< 30 rows
    after the adjustment-set NaN drop).
    """
    import pandas as _pd
    import numpy as _np

    from analysis.cleaning import clean_var
    from analysis.wls import quintile_dummies, weighted_ols

    if exposure_col not in df.columns or outcome_col not in df.columns:
        return None
    exp_clean = clean_var(df[exposure_col], exposure_col)
    # If the exposure is already binary (only {0,1} after cleaning), or the
    # caller forces binary treatment, use the raw 0/1 contrast — which lets
    # the η-tilt sweep operate on the *primary* exposure scale rather than a
    # binarised proxy.
    unique_nonnull = _pd.unique(exp_clean.dropna())
    if force_binary or (
        set(unique_nonnull.astype(float).tolist()) <= {0.0, 1.0}
    ):
        A = exp_clean.astype(float)
        binarisation = "raw-binary"
    else:
        _, trend = quintile_dummies(exp_clean, n=5)
        A = _pd.Series(_np.nan, index=df.index)
        A[trend == 1] = 0.0
        A[trend == 5] = 1.0
        binarisation = "top-quintile-vs-bottom"
    mask = A.notna() & df[outcome_col].notna() & df[weight_col].notna()
    if mask.sum() < 60:
        return None
    sub = df.loc[mask].copy()
    A_sub = A.loc[mask].astype(float)
    adj = adj_builder(sub)
    # Drop rows where any adjustment covariate is NaN.
    keep = adj.notna().all(axis=1)
    sub = sub.loc[keep]
    A_sub = A_sub.loc[keep]
    adj = adj.loc[keep]
    if (A_sub == 1).sum() < 30 or (A_sub == 0).sum() < 30:
        return None
    y = sub[outcome_col].astype(float).values
    w = sub[weight_col].astype(float).values
    psu = sub[cluster_col].values
    X_full = _pd.concat([adj.reset_index(drop=True)], axis=1)
    X_full.insert(0, "const", 1.0)
    # Fit on A=1 subset, then predict on full (A1 + A0) sample.
    X1 = X_full.loc[A_sub.values == 1.0]
    X0 = X_full.loc[A_sub.values == 0.0]
    res1 = weighted_ols(
        y[A_sub.values == 1.0], X1.values,
        w[A_sub.values == 1.0], psu[A_sub.values == 1.0],
        column_names=list(X_full.columns),
    )
    res0 = weighted_ols(
        y[A_sub.values == 0.0], X0.values,
        w[A_sub.values == 0.0], psu[A_sub.values == 0.0],
        column_names=list(X_full.columns),
    )
    if res1 is None or res0 is None:
        return None
    beta1 = res1["beta"].reindex(X_full.columns).fillna(0.0).values
    beta0 = res0["beta"].reindex(X_full.columns).fillna(0.0).values
    mu_1 = X_full.values @ beta1
    mu_0 = X_full.values @ beta0
    cell = {
        "label": label,
        "exposure": exposure_col,
        "outcome": outcome_col,
        "binarisation": binarisation,
        "A": A_sub.values,
        "mu_1": mu_1,
        "mu_0": mu_0,
    }
    if extra_keys:
        for k, v in extra_keys.items():
            if k not in cell:
                cell[k] = v
    return cell


# ---------------------------------------------------------------------------
# Three-panel figure.
# ---------------------------------------------------------------------------
def plot_sensitivity_panel(
    out_path: Path,
    *,
    title: str,
    evalue_table: pd.DataFrame,
    cornfield_table: pd.DataFrame,
    eta_tilt_table: pd.DataFrame,
    label_col: str = "label",
    cornfield_cell_label: Optional[str] = None,
    eta_cell_label: Optional[str] = None,
    eta_continuous_note: Optional[str] = None,
) -> Path:
    """Render the standard three-panel sensitivity figure.

    Panel (a) — bar chart of E-values per row of ``evalue_table``. The
    threshold line at ``E = 2`` separates fragile (E < 2) from moderately
    robust (E ≥ 2) cells.

    Panel (b) — Cornfield bias-factor heatmap for the cell named in
    ``cornfield_cell_label`` (defaults to the first cell in
    ``cornfield_table``). Cells where ``B ≥ observed RR`` are annotated with
    a check, marking the "could explain away" region.

    Panel (c) — η-tilt ATE surface for the ``eta_cell_label`` cell. If
    ``eta_continuous_note`` is provided (and ``eta_tilt_table`` is empty), the
    panel renders that string as an annotation instead.

    Returns the output path (also saved).
    """
    # Local imports so pure-data callers don't pay matplotlib's import cost.
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # ---- Panel (a): E-value bars ----
    ax_a = axes[0]
    if evalue_table.empty or "evalue" not in evalue_table.columns:
        ax_a.text(0.5, 0.5, "No E-values\n(no rows in input)",
                  ha="center", va="center", transform=ax_a.transAxes)
        ax_a.set_axis_off()
    else:
        ev = evalue_table.dropna(subset=["evalue"]).copy()
        if ev.empty:
            ax_a.text(0.5, 0.5, "No finite E-values",
                      ha="center", va="center", transform=ax_a.transAxes)
            ax_a.set_axis_off()
        else:
            if label_col not in ev.columns:
                ev[label_col] = [
                    f"row {i}" for i in range(len(ev))
                ]
            ev = ev.sort_values("evalue", ascending=True)
            y = np.arange(len(ev))
            colors = ["#1f77b4" if v >= 2.0 else "#d62728" for v in ev["evalue"]]
            ax_a.barh(y, ev["evalue"].values, color=colors, edgecolor="black", linewidth=0.4)
            ax_a.axvline(2.0, color="grey", linestyle="--", linewidth=1.0,
                         label="E = 2 (moderately robust)")
            ax_a.set_yticks(y)
            ax_a.set_yticklabels(ev[label_col].astype(str).values, fontsize=8)
            ax_a.set_xlabel("E-value")
            ax_a.set_title("(a) E-value per primary cell")
            ax_a.legend(loc="lower right", fontsize=8)

    # ---- Panel (b): Cornfield heatmap ----
    ax_b = axes[1]
    if cornfield_table.empty:
        ax_b.text(0.5, 0.5, "No significant cells\nfor Cornfield grid",
                  ha="center", va="center", transform=ax_b.transAxes)
        ax_b.set_axis_off()
    else:
        if cornfield_cell_label is None:
            if (
                label_col in cornfield_table.columns
                and "rr_observed" in cornfield_table.columns
            ):
                # Pick the cell whose observed RR sits furthest from 1 — i.e.
                # the most-significant primary cell — so the panel showcases the
                # signal that matters most.
                rr_obs = cornfield_table.groupby(label_col)["rr_observed"].first()
                cell_id = rr_obs.sub(1.0).abs().idxmax()
            elif label_col in cornfield_table.columns:
                cell_id = cornfield_table[label_col].iloc[0]
            else:
                cell_id = None
        else:
            cell_id = cornfield_cell_label
        sub = (
            cornfield_table[cornfield_table[label_col] == cell_id]
            if (label_col in cornfield_table.columns and cell_id is not None)
            else cornfield_table
        )
        if sub.empty:
            sub = cornfield_table
        pivot = sub.pivot_table(index="rr_uy", columns="rr_au", values="B")
        pivot = pivot.sort_index().sort_index(axis=1)
        im = ax_b.imshow(
            pivot.values, origin="lower", cmap="viridis",
            aspect="auto",
        )
        ax_b.set_xticks(range(pivot.shape[1]))
        ax_b.set_xticklabels([f"{v:g}" for v in pivot.columns])
        ax_b.set_yticks(range(pivot.shape[0]))
        ax_b.set_yticklabels([f"{v:g}" for v in pivot.index])
        ax_b.set_xlabel("RR_AU")
        ax_b.set_ylabel("RR_UY")
        rr_obs = sub["rr_observed"].iloc[0] if "rr_observed" in sub.columns else None
        title_b = "(b) Cornfield bias-factor B"
        if rr_obs is not None and np.isfinite(rr_obs):
            title_b += f"\ncell: {cell_id} (observed RR ≈ {rr_obs:.2f})"
        ax_b.set_title(title_b)
        # Annotate cells with B; mark explained-away with bold + white.
        for i, rr_uy in enumerate(pivot.index):
            for j, rr_au in enumerate(pivot.columns):
                B = pivot.values[i, j]
                if not np.isfinite(B):
                    continue
                explains = (
                    rr_obs is not None and np.isfinite(rr_obs) and B >= rr_obs
                )
                ax_b.text(
                    j, i, f"{B:.2f}",
                    ha="center", va="center",
                    color="white" if explains else "black",
                    fontsize=8,
                    fontweight="bold" if explains else "normal",
                )
        fig.colorbar(im, ax=ax_b, fraction=0.046, pad=0.04, label="B")

    # ---- Panel (c): η-tilt surface ----
    ax_c = axes[2]
    if eta_tilt_table is None or eta_tilt_table.empty:
        msg = eta_continuous_note or "No η-tilt cells supplied"
        ax_c.text(0.5, 0.5, msg, ha="center", va="center",
                  transform=ax_c.transAxes, wrap=True, fontsize=10)
        ax_c.set_title("(c) η-tilt sensitivity")
        ax_c.set_axis_off()
    else:
        if eta_cell_label is None:
            cell_id_c = eta_tilt_table[label_col].iloc[0] if label_col in eta_tilt_table.columns else None
        else:
            cell_id_c = eta_cell_label
        sub_c = (
            eta_tilt_table[eta_tilt_table[label_col] == cell_id_c]
            if (label_col in eta_tilt_table.columns and cell_id_c is not None)
            else eta_tilt_table
        )
        if sub_c.empty:
            sub_c = eta_tilt_table
        pivot_c = sub_c.pivot_table(
            index="eta_0", columns="eta_1", values="ate_perturbed"
        ).sort_index().sort_index(axis=1)
        im_c = ax_c.imshow(
            pivot_c.values, origin="lower", cmap="coolwarm", aspect="auto",
        )
        ax_c.set_xticks(range(pivot_c.shape[1]))
        ax_c.set_xticklabels([f"{v:g}" for v in pivot_c.columns])
        ax_c.set_yticks(range(pivot_c.shape[0]))
        ax_c.set_yticklabels([f"{v:g}" for v in pivot_c.index])
        ax_c.set_xlabel("η₁")
        ax_c.set_ylabel("η₀")
        title_c = "(c) η-tilt ATE perturbation"
        if cell_id_c is not None:
            title_c += f"\ncell: {cell_id_c}"
        if "binarisation" in sub_c.columns and len(sub_c) > 0:
            biner = sub_c["binarisation"].iloc[0]
            if isinstance(biner, str) and biner != "raw":
                title_c += f" [{biner}]"
        ax_c.set_title(title_c)
        for i, e0 in enumerate(pivot_c.index):
            for j, e1 in enumerate(pivot_c.columns):
                v = pivot_c.values[i, j]
                if not np.isfinite(v):
                    continue
                ax_c.text(
                    j, i, f"{v:.2f}",
                    ha="center", va="center",
                    color="black", fontsize=7,
                )
        fig.colorbar(im_c, ax=ax_c, fraction=0.046, pad=0.04, label="perturbed ATE")
        if eta_continuous_note:
            ax_c.text(
                0.02, -0.18, eta_continuous_note,
                transform=ax_c.transAxes, ha="left", va="top",
                fontsize=8, style="italic", color="dimgrey",
            )

    fig.suptitle(title, fontsize=12, y=1.02)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return out_path
