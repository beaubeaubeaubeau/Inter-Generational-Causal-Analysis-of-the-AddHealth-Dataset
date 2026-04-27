# Scheduled task check-in — 2026-04-27

Autonomous run of the `continue-working-on-inter_generational_causal_analysis` scheduled task. Goal: pick up the "Brainstorm Inter-Generational Causal Analysis approach" thread and report state.

## What I found

The most recent work in this repo was the scaffolding of **9 Phase 6 mechanism experiments** under `experiments/` on 2026-04-27 (TODO §A24). The folders are present but untracked in git:

- `popularity-vs-sociability/` — type-of-tie
- `ego-network-density/` — type-of-tie (Burt structural-holes)
- `friendship-quality-vs-quantity/` — type-of-tie
- `em-compensatory-by-ses/` — effect-modification
- `em-sex-differential/` — effect-modification
- `em-depression-buffering/` — effect-modification
- `popularity-and-substance-use/` — dark-side
- `lonely-at-the-top/` — dark-side
- `cross-sex-friendship/` — cross-sex friendship

Each folder is structurally complete: README field-table, dag.md, run.py (100-200 lines), figures.py, report.md, tables/, figures/, tests/. Field tables are all internally consistent with the entries in `experiments/README.md`. No blocking inconsistencies.

Two new analysis modules ship alongside (also untracked): `scripts/analysis/dr_aipw.py` and `scripts/analysis/matching.py`. The em-* experiments import `match_ate_bias_corrected` from `analysis.matching`; the module file exists.

## Open items the audit surfaced

1. **`popularity-and-substance-use/run.py:125`** carries a docstring TODO asking whether W5 outcomes should attach to the W4 analytic frame (current design) or use a separate W5 frame with `GSW5`. Tagged as "revisit alongside planned IPAW-W5 work" — not a blocker, but should be conclusively settled before the first run. This dovetails with TODO §A3 (IPAW shared utility).

2. **No experiment in the Phase 6 set has been executed yet** — all `tables/` and `figures/` subfolders are empty. These are true scaffolds awaiting first run.

3. **Per-experiment output-directory creation** — none of the 9 run.py files explicitly create their `tables/primary/`, `figures/primary/`, etc. subdirectories. First run may fail on missing-dir writes unless a pre-flight setup step is added (or each run.py uses `Path.mkdir(parents=True, exist_ok=True)` before writes). Worth verifying when smoke-testing.

## Recommended next concrete steps (for next session)

In the order I'd take them:

1. **Smoke-test all 9** via `pytest experiments/*/tests/test_smoke.py`. Confirms the matching/dr_aipw imports resolve and the fixtures wire up. Cheap and high-information.

2. **Execute the three type-of-tie experiments first** (`popularity-vs-sociability`, `ego-network-density`, `friendship-quality-vs-quantity`) — they have no matching dependency, so any failures are isolated to the type-of-tie design rather than the matching utility. Use them as the structural canary.

3. **Settle the W5-frame question in `popularity-and-substance-use/run.py:125`** before its first run. Either document "attach W5 to W4 frame with GSW5 reweighting" per multi-outcome-screening convention, or implement the separate W5 frame.

4. **Then** run the three em-* effect-modification experiments — these exercise the matching module for the first time and will surface any issues there.

## What this run did *not* do

- Did **not execute any pipeline** — the sandbox environment couldn't reliably install pyarrow (45 MB binary kept timing out the install step), so I couldn't run anything that touches the parquet cache.
- Did **not edit any code or reference docs** — only this catch-up note was added.
- Did **not commit anything** — the 9 untracked folders, two new analysis modules, and pending modifications across ~30 tracked files remain as you left them.

Working memory in TODO.md and reference/research-plan.md is current and reflects the 2026-04-26 / 2026-04-27 audit decisions; no drift detected.

## Rough state-of-the-project summary

- **Pipeline:** prep stages 01-09 complete; cognitive-screening + multi-outcome-screening complete with full diagnostic batteries; 7 P0/P1 handoff-style experiments scaffolded (cardiometabolic-handoff, ses-handoff, cognitive-frontdoor, negative-control-battery, saturation-balance, plus dag.md additions across the set on 2026-04-27).
- **Library code:** `scripts/analysis/` has working `cleaning`, `derivation`, `weighted_stats`, `wls`, `plot_style`. Stubs `frontdoor`, `ipw`, `sensitivity` raise `NotImplementedError` with TODO references. New `dr_aipw.py` and `matching.py` are untracked.
- **Tests:** 133 passing + 1 xfail per the last full run (2026-04-26). Some new test files for `matching`, `dr_aipw`, `sensitivity` are also untracked.
- **Open P0 items in TODO:** A2 (NC pre-flight), A3 (IPAW utility implementation), A23 (`L_partner` placeholder, waiting on partner).

---

*Note: this file lives at the repo root because the agent's sandbox could not write to `.claude/scheduled-task-notes/`. Feel free to move it or delete it after reading.*
