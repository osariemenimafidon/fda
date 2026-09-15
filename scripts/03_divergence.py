"""03 — Pool composition, blend properties, and divergence from the certification fuel.

Divergence is reported three ways, deliberately:

  signed physical deviation   how much lighter or heavier, in kg/m3 and cetane
                              numbers. The SIGN is the finding - LCFS states go
                              one way, biodiesel-mandate states the other - so a
                              magnitude-only index would destroy the result.

  normalised deviation        each property divided by the certification spec's
                              own width, so density and cetane are comparable
                              without either dominating by unit scale.

  divergence index            euclidean magnitude of the normalised pair. Always
                              positive; use the signed components for direction.

A sensitivity band is computed by re-running the blend at the min and max of every
component's specification envelope, so no reader mistakes the midpoint result for
a precise measurement.
"""
import json, os, sys, itertools
import pandas as pd
sys.path.insert(0, "src")
from fda import properties as P

OUT = "data/processed"


def blend(shares, prop, pick="midpoint"):
    total = 0.0
    for comp, share in shares.items():
        c = P.COMPONENTS[comp]
        v = (P.midpoint(comp, prop) if pick == "midpoint"
             else c[f"{prop}_{pick}"])
        total += share * v
    return total


def main():
    rep = {}
    df = pd.read_csv(f"{OUT}/fda_pool.csv")
    df = df[df.in_usable_window].copy()

    df["fame_share"] = df.fame_volume.fillna(0) / df.pool_total
    df["hvo_share"] = df.hvo_volume.fillna(0) / df.pool_total
    df["petroleum_share"] = 1 - df.fame_share - df.hvo_share

    bad = df[df.petroleum_share < -1e-9]
    rep["negative_petroleum_share_rows"] = len(bad)
    if len(bad):
        raise SystemExit(f"Biofuel volumes exceed the pool total in {len(bad)} "
                         "state-years. The denominator is wrong; stop.")

    sh = lambda r: {"petroleum": r.petroleum_share, "fame": r.fame_share, "hvo": r.hvo_share}

    for prop in ("density", "cetane"):
        df[f"blend_{prop}"] = df.apply(lambda r: blend(sh(r), prop), axis=1)
        ref = P.midpoint(P.REFERENCE, prop)
        width = (P.COMPONENTS[P.REFERENCE][f"{prop}_max"]
                 - P.COMPONENTS[P.REFERENCE][f"{prop}_min"])
        df[f"{prop}_ref"] = ref
        df[f"{prop}_dev"] = df[f"blend_{prop}"] - ref
        df[f"{prop}_dev_norm"] = df[f"{prop}_dev"] / width
        rep[f"{prop}_reference"] = ref
        rep[f"{prop}_spec_width"] = width

    df["divergence_index"] = (df.density_dev_norm**2 + df.cetane_dev_norm**2) ** 0.5
    df["direction"] = pd.cut(df.density_dev, [-1e9, -0.5, 0.5, 1e9],
                             labels=["lighter", "at_reference", "heavier"])

    # --- sensitivity, done on the DEVIATION, not the absolute level ---
    #
    #   deviation = p*Dp + f*Df + h*Dh - Dp        with p = 1 - f - h
    #             = f*(Df - Dp) + h*(Dh - Dp)
    #
    # The deviation depends only on each component's DIFFERENCE from petroleum.
    # A common-mode error in the petroleum reference cancels exactly. Banding the
    # absolute blend density (the obvious approach) therefore overstates the
    # uncertainty enormously - it counts a shift that cancels on both sides.
    #
    # This matters for the headline claim: over the full specification envelopes,
    # FAME is heavier than petroleum by +15 to +80 kg/m3 and HVO lighter by -20 to
    # -80. Both intervals exclude zero, so the DIRECTION of density divergence is
    # robust to any admissible choice of property values. Only the magnitude is
    # uncertain. Cetane is different: FAME's cetane difference spans -8 to +5, so
    # its sign is NOT robust and must not be asserted.
    for prop in ("density", "cetane"):
        pmin = P.COMPONENTS[P.REFERENCE][f"{prop}_min"]
        pmax = P.COMPONENTS[P.REFERENCE][f"{prop}_max"]
        lo_terms, hi_terms = [], []
        for comp in ("fame", "hvo"):
            cmin = P.COMPONENTS[comp][f"{prop}_min"]
            cmax = P.COMPONENTS[comp][f"{prop}_max"]
            d_lo, d_hi = cmin - pmax, cmax - pmin       # extreme differences
            share = df[f"{comp}_share"]
            lo_terms.append(share * min(d_lo, d_hi))
            hi_terms.append(share * max(d_lo, d_hi))
        df[f"{prop}_dev_low"] = sum(lo_terms)
        df[f"{prop}_dev_high"] = sum(hi_terms)
        df[f"{prop}_dev_band"] = df[f"{prop}_dev_high"] - df[f"{prop}_dev_low"]
        # sign is robust where the whole interval sits one side of zero
        df[f"{prop}_sign_robust"] = (
            (df[f"{prop}_dev_low"] > 0) | (df[f"{prop}_dev_high"] < 0))
        rep[f"{prop}_band_median"] = round(float(df[f"{prop}_dev_band"].median()), 2)
        rep[f"{prop}_sign_robust_pct"] = round(
            float(df[f"{prop}_sign_robust"].mean() * 100), 1)

    # component-level difference intervals, reported so the claim is checkable
    rep["component_deltas_vs_petroleum"] = {}
    for prop in ("density", "cetane"):
        pmin = P.COMPONENTS[P.REFERENCE][f"{prop}_min"]
        pmax = P.COMPONENTS[P.REFERENCE][f"{prop}_max"]
        for comp in ("fame", "hvo"):
            cmin = P.COMPONENTS[comp][f"{prop}_min"]
            cmax = P.COMPONENTS[comp][f"{prop}_max"]
            lo, hi = cmin - pmax, cmax - pmin
            rep["component_deltas_vs_petroleum"][f"{prop}_{comp}"] = {
                "low": lo, "high": hi, "excludes_zero": bool(lo > 0 or hi < 0)}

    cols = ["State", "year", "pool_total", "units", "petroleum_share", "fame_share",
            "hvo_share",
            "blend_density", "density_ref", "density_dev", "density_dev_norm",
            "density_dev_low", "density_dev_high", "density_dev_band",
            "density_sign_robust",
            "blend_cetane", "cetane_ref", "cetane_dev", "cetane_dev_norm",
            "cetane_dev_low", "cetane_dev_high", "cetane_dev_band",
            "cetane_sign_robust",
            "divergence_index", "direction"]
    df[cols].to_csv(f"{OUT}/fda_state_year.csv", index=False)
    pd.DataFrame(P.as_rows()).to_csv(f"{OUT}/fda_components.csv", index=False)

    rep["rows"] = len(df)
    rep["years"] = [int(df.year.min()), int(df.year.max())]
    rep["states"] = int(df.State.nunique())
    json.dump(rep, open("qa/03_divergence.json", "w"), indent=2, default=str)
    print(json.dumps(rep, indent=2, default=str))

    latest = df[df.year == df.year.max()]
    latest = latest[latest.State != "US"]
    print("\n--- 2024 extremes ---")
    print(latest.nsmallest(3, "density_dev")[
        ["State","petroleum_share","fame_share","hvo_share","blend_density",
         "density_dev","blend_cetane","divergence_index"]].round(2).to_string(index=False))
    print(latest.nlargest(3, "density_dev")[
        ["State","petroleum_share","fame_share","hvo_share","blend_density",
         "density_dev","blend_cetane","divergence_index"]].round(2).to_string(index=False))
    print("\ndirection counts:", dict(latest.direction.value_counts()))


if __name__ == "__main__":
    main()
