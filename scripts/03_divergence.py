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
import json, math, os, sys, itertools
import pandas as pd
sys.path.insert(0, "src")
from fda import properties as P

OUT = "data/processed"


def _term(share, delta):
    """share * delta, with 0 * inf defined as 0 rather than nan."""
    if math.isinf(delta):
        return share.map(lambda x: 0.0 if x == 0 else delta)
    return share * delta


def blend(shares, prop, pick="midpoint"):
    """Volume-weighted point estimate, formed from the ASSUMED TYPICAL range.
    Never from the specification envelope: a one-sided specification has no
    midpoint, and pretending otherwise is what produced the defect this
    version corrects."""
    total = 0.0
    for comp, share in shares.items():
        tlo, thi = P.typical(comp, prop)
        v = P.midpoint(comp, prop) if pick == "midpoint" else (
            tlo if pick == "min" else thi)
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
        # The normalising width is the certification specification's own width.
        # The reference is two-sided on both properties, so this is always
        # finite; asserted rather than assumed, because a one-sided reference
        # would make the normalised deviation meaningless.
        rlo, rhi = P.spec(P.REFERENCE, prop)
        if rlo is None or rhi is None:
            raise SystemExit(
                f"The reference component's {prop} specification is one-sided; "
                "normalised deviation is undefined. Stop.")
        width = rhi - rlo
        df[f"{prop}_ref"] = ref
        df[f"{prop}_dev"] = df[f"blend_{prop}"] - ref
        df[f"{prop}_dev_norm"] = df[f"{prop}_dev"] / width
        rep[f"{prop}_reference"] = ref
        rep[f"{prop}_spec_width"] = width

    # An earlier version reported a `divergence_index`: the euclidean magnitude of
    # the normalised (density, cetane) pair. It is retired. Half of it came from a
    # cetane point estimate that rests on an assumed typical range rather than on
    # any specification, so the index let an assumption into a headline number
    # while presenting itself as a summary of the data. `density_dev_norm` carries
    # the comparable, specification-derived magnitude on its own.
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
    # This matters for the headline claim, and the actual intervals are computed
    # below rather than quoted here, because an earlier version of this comment
    # quoted figures that the code had since stopped producing.
    #
    # Only the SPECIFICATION envelope enters this calculation. Where a standard
    # is one-sided - EN 15940 states a cetane minimum of 70 and no maximum,
    # EN 14214 and ASTM D6751 state minima and no maximum - the corresponding
    # side of the deviation interval is unbounded, and is carried as an infinity
    # rather than closed with a number no standard supports. The consequence is
    # asymmetric and deliberate: an unbounded upper side cannot make a sign
    # robust, but it cannot break one either, so a direction established by the
    # lower bound survives while the magnitude honestly does not.
    for prop in ("density", "cetane"):
        pmin, pmax = P.spec_inf(P.REFERENCE, prop)
        lo_terms, hi_terms = [], []
        unbounded_hi = False
        for comp in ("fame", "hvo"):
            cmin, cmax = P.spec_inf(comp, prop)
            d_lo, d_hi = cmin - pmax, cmax - pmin       # extreme differences
            if math.isinf(d_hi):
                unbounded_hi = True
            share = df[f"{comp}_share"]
            # 0 * inf is nan, not 0. A state burning none of a component is not
            # exposed to that component's unbounded specification, so the term
            # is zero there and the guard is load-bearing rather than cosmetic.
            lo_terms.append(_term(share, min(d_lo, d_hi)))
            hi_terms.append(_term(share, max(d_lo, d_hi)))
        df[f"{prop}_dev_low"] = sum(lo_terms)
        df[f"{prop}_dev_high"] = sum(hi_terms)
        df[f"{prop}_dev_band"] = df[f"{prop}_dev_high"] - df[f"{prop}_dev_low"]
        # sign is robust where the whole interval sits one side of zero
        df[f"{prop}_sign_robust"] = (
            (df[f"{prop}_dev_low"] > 0) | (df[f"{prop}_dev_high"] < 0))
        finite = df[f"{prop}_dev_band"].replace([math.inf, -math.inf], pd.NA).dropna()
        rep[f"{prop}_band_median"] = (round(float(finite.median()), 2)
                                      if len(finite) else None)
        rep[f"{prop}_band_unbounded_pct"] = round(float(
            df[f"{prop}_dev_band"].apply(math.isinf).mean() * 100), 1)
        rep[f"{prop}_dev_low_median"] = round(float(df[f"{prop}_dev_low"].median()), 2)
        rep[f"{prop}_upper_bound_exists"] = not unbounded_hi
        rep[f"{prop}_sign_robust_pct"] = round(
            float(df[f"{prop}_sign_robust"].mean() * 100), 1)

    # --- breakdown point: how wrong would the FAME assumption have to be? ---
    #
    # FAME's density bound rests on EN 14214 alone, because ASTM D6751 - the
    # standard the US biodiesel supply is actually made to - sets no density
    # limit at all. Asserting a FAME density therefore puts a European standard
    # on the critical path of a United States result.
    #
    # Reporting a breakdown point removes it from that path. Rather than assume
    # FAME's density and propagate it, we ask how far wrong the assumption would
    # have to be before the sign of the deviation changed. The deviation is
    #
    #     dev = f*(Df - Dp) + h*(Dh - Dp)
    #
    # so holding HVO and petroleum at the admissible values least favourable to
    # a "lighter" conclusion, the sign survives unless
    #
    #     Df > Dp_min - h*(Dh_max - Dp_min)/f
    #
    # A reader can judge that threshold against what a fatty acid methyl ester
    # can physically be, without owning EN 14214.
    plo, phi = P.spec_inf(P.REFERENCE, "density")
    _, hhi = P.spec_inf("hvo", "density")
    hvo_worst = df.hvo_share * (hhi - plo)          # least negative HVO term
    with pd.option_context("mode.use_inf_as_na", False):
        thresh = (-hvo_worst / df.fame_share.where(df.fame_share > 0))
    df["density_breakdown_fame_kg_m3"] = (plo + thresh).where(
        (df.fame_share > 0) & (df.hvo_share > 0))

    bd = df[df.density_breakdown_fame_kg_m3.notna()]
    rep["density_breakdown_defined_rows"] = int(len(bd))
    assumed = P.midpoint("fame", "density")
    rep["fame_density_assumed_midpoint"] = assumed

    # Reported for the latest year and for the whole panel separately, because
    # they say different things. Renewable diesel penetration grew over the
    # window, so a threshold that comfortably clears any plausible FAME density
    # in the latest cross-section does not in the early years, where HVO shares
    # were small relative to FAME. That is the same fact the panel-wide
    # sign-robustness figure reports, seen from the other side.
    latest = bd[bd.year == df.year.max()]
    if len(latest):
        t = latest.loc[latest.density_breakdown_fame_kg_m3.idxmin()]
        rep["density_breakdown_latest_year"] = int(df.year.max())
        rep["density_breakdown_latest_min_kg_m3"] = round(
            float(t.density_breakdown_fame_kg_m3), 0)
        rep["density_breakdown_latest_min_state"] = str(t.State)
        rep["density_breakdown_latest_by_state"] = {
            str(r.State): round(float(r.density_breakdown_fame_kg_m3), 0)
            for _, r in latest.sort_values("density_breakdown_fame_kg_m3").iterrows()}
        rep["density_breakdown_latest_all_clear_assumption"] = bool(
            (latest.density_breakdown_fame_kg_m3 > assumed).all())
    if len(bd):
        t = bd.loc[bd.density_breakdown_fame_kg_m3.idxmin()]
        rep["density_breakdown_panel_min_kg_m3"] = round(
            float(t.density_breakdown_fame_kg_m3), 0)
        rep["density_breakdown_panel_min_state"] = str(t.State)
        rep["density_breakdown_panel_min_year"] = int(t.year)
        rep["density_breakdown_rows_below_assumption"] = int(
            (bd.density_breakdown_fame_kg_m3 <= assumed).sum())

    # component-level difference intervals, reported so the claim is checkable
    rep["component_deltas_vs_petroleum"] = {}
    for prop in ("density", "cetane"):
        pmin, pmax = P.spec_inf(P.REFERENCE, prop)
        for comp in ("fame", "hvo"):
            cmin, cmax = P.spec_inf(comp, prop)
            lo, hi = cmin - pmax, cmax - pmin
            rep["component_deltas_vs_petroleum"][f"{prop}_{comp}"] = {
                "low": None if math.isinf(lo) else lo,
                "high": None if math.isinf(hi) else hi,
                "low_unbounded": bool(math.isinf(lo)),
                "high_unbounded": bool(math.isinf(hi)),
                "excludes_zero": bool(lo > 0 or hi < 0),
                "spec": P.fmt_spec(comp, prop),
            }

    cols = ["State", "year", "pool_total", "units", "petroleum_share", "fame_share",
            "hvo_share",
            "blend_density", "density_ref", "density_dev", "density_dev_norm",
            "density_dev_low", "density_dev_high", "density_dev_band",
            "density_sign_robust",
            # No cetane point estimate is published. Every candidate rests on an
            # assumed typical range rather than a specification, and the bound
            # below says what the specifications actually support.
            "cetane_dev_low", "cetane_dev_high", "cetane_dev_band",
            "cetane_sign_robust",
            "density_breakdown_fame_kg_m3", "direction"]
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
         "density_dev","cetane_dev_low","density_breakdown_fame_kg_m3"]].round(2).to_string(index=False))
    print(latest.nlargest(3, "density_dev")[
        ["State","petroleum_share","fame_share","hvo_share","blend_density",
         "density_dev","cetane_dev_low","density_breakdown_fame_kg_m3"]].round(2).to_string(index=False))
    print("\ndirection counts:", dict(latest.direction.value_counts()))


if __name__ == "__main__":
    main()
