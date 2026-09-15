"""02 — Extract the diesel pool series from SEDS into a state-year panel.

THE CRITICAL METHOD NOTE
------------------------
EIA changed its distillate accounting at data year 2021. Before 2021, DFACP
(distillate consumed by transportation) already INCLUDED blended biofuels, and
DAACP equals it exactly in every state and year. From 2021, EIA's technical
notes state that distillate "includes all biodiesel and renewable diesel
refinery and blender net inputs volumes, but excludes biodiesel and renewable
diesel product supplied consumption" - so DFACP becomes petroleum-plus-some and
DAACP adds the remainder.

Consequence: DFACP + BDACP + B1ACP DOUBLE-COUNTS from 2021 forward, by a stable
~40 million barrels a year nationally, while being correct before. A pipeline
built that way manufactures a trend break in 2021 that nobody would spot.

DAACP is the only consistently defined total. This script uses it as the
denominator and never sums the three series. The regime break is detected from
the data and asserted, not assumed.
"""
import json, os, sys
import pandas as pd

RAW, OUT = "data/raw", "data/processed"
SERIES = {"DAACP": "pool_total", "BDACP": "fame_volume", "B1ACP": "hvo_volume",
          "DFACP": "distillate_series"}   # DFACP carried for the regime check only
UNITS = "thousand barrels"


def main():
    os.makedirs(OUT, exist_ok=True); os.makedirs("qa", exist_ok=True)
    rep = {}
    df = pd.read_csv(f"{RAW}/use_all_phy.csv")
    years = [c for c in df.columns if c.isdigit()]
    rep["source_rows"] = len(df)
    rep["source_year_range"] = [int(years[0]), int(years[-1])]

    sub = df[df.MSN.isin(SERIES)]
    long = sub.melt(id_vars=["State", "MSN"], value_vars=years,
                    var_name="year", value_name="v")
    long["year"] = long.year.astype(int)
    long["v"] = pd.to_numeric(long.v, errors="coerce")
    w = long.pivot_table(index=["State", "year"], columns="MSN",
                         values="v").reset_index()

    # --- detect the accounting regime break from the data ---
    g = w.dropna(subset=["DAACP", "DFACP"]).copy()
    g["same"] = (g.DAACP - g.DFACP).abs() < 1e-6
    by_year = g.groupby("year").same.mean()
    pre = sorted(int(y) for y, v in by_year.items() if v == 1.0)
    post = sorted(int(y) for y, v in by_year.items() if v < 1.0)
    rep["regime_identical_years"] = [min(pre), max(pre)] if pre else None
    rep["regime_split_years"] = [min(post), max(post)] if post else None
    if post and min(post) != 2021:
        raise SystemExit(f"Accounting break detected at {min(post)}, not 2021. "
                         "EIA has changed something; re-read the technical notes "
                         "before trusting this pipeline.")

    # --- the trap, quantified, so LIMITATIONS can cite a real number ---
    us = w[(w.State == "US") & (w.year.isin(post))].copy()
    us["naive_sum"] = us[["DFACP", "BDACP", "B1ACP"]].fillna(0).sum(axis=1)
    us["overcount"] = us.naive_sum - us.DAACP
    rep["naive_overcount_mean_kbbl"] = round(float(us.overcount.mean()), 1)
    rep["naive_overcount_pct_mean"] = round(float((us.overcount / us.DAACP * 100).mean()), 3)

    w = w.rename(columns=SERIES)
    w = w[["State", "year", "pool_total", "fame_volume", "hvo_volume"]]
    w = w[w.pool_total.notna() & (w.pool_total > 0)].copy()

    # --- usable window: all three series populated ---
    fy = {}
    for col in ("fame_volume", "hvo_volume"):
        nz = w[w[col].fillna(0) != 0]
        fy[col] = int(nz.year.min()) if len(nz) else None
    rep["first_nonzero_year"] = fy
    start = max(v for v in fy.values() if v)
    rep["usable_year_start"] = start
    rep["usable_year_end"] = int(w.year.max())

    w["in_usable_window"] = w.year >= start
    w["units"] = UNITS
    w.to_csv(f"{OUT}/fda_pool.csv", index=False)
    rep["panel_rows"] = len(w)
    rep["states"] = int(w.State.nunique())

    json.dump(rep, open("qa/02_extract.json", "w"), indent=2)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
