"""04 — Integrity checks and stats.json.

Every number in every FDA document is read from stats.json. Nothing is typed by hand.
"""
import csv, hashlib, json, math, os, sys
import pandas as pd
sys.path.insert(0, "src")
from fda import properties as P

OUT = "data/processed"
S = {}


def main():
    df = pd.read_csv(f"{OUT}/fda_state_year.csv")
    ext = json.load(open("qa/02_extract.json"))
    dvg = json.load(open("qa/03_divergence.json"))
    states = df[df.State != "US"]
    latest = int(df.year.max())
    L = states[states.year == latest]

    S["build_date"] = pd.Timestamp.utcnow().strftime("%Y-%m-%d")
    S["units"] = "thousand barrels"
    S["year_min"], S["year_max"] = int(df.year.min()), latest
    S["state_count"] = int(states.State.nunique())
    S["rows"] = int(len(df))

    S["accounting_break_year"] = ext["regime_split_years"][0]
    S["identical_regime"] = ext["regime_identical_years"]
    S["naive_overcount_mean_kbbl"] = ext["naive_overcount_mean_kbbl"]
    S["naive_overcount_pct_mean"] = ext["naive_overcount_pct_mean"]
    S["first_nonzero_year"] = ext["first_nonzero_year"]

    S["density_reference"] = dvg["density_reference"]
    S["cetane_reference"] = dvg["cetane_reference"]
    for k in ("density_breakdown_defined_rows", "fame_density_assumed_midpoint",
              "density_breakdown_latest_year", "density_breakdown_latest_min_kg_m3",
              "density_breakdown_latest_min_state", "density_breakdown_latest_by_state",
              "density_breakdown_latest_all_clear_assumption",
              "density_breakdown_panel_min_kg_m3", "density_breakdown_panel_min_state",
              "density_breakdown_panel_min_year",
              "density_breakdown_rows_below_assumption"):
        if k in dvg:
            S[k] = dvg[k]
    S["component_deltas_vs_petroleum"] = dvg["component_deltas_vs_petroleum"]
    S["density_sign_robust_pct"] = dvg["density_sign_robust_pct"]
    S["cetane_sign_robust_pct"] = dvg["cetane_sign_robust_pct"]
    # Band width is only meaningful where both sides are bounded. Where a
    # standard is one-sided the band is unbounded, and the share of rows in that
    # state is reported instead of a median that would describe only the
    # degenerate zero-biofuel rows.
    for prop in ("density", "cetane"):
        for k in ("band_median", "band_unbounded_pct", "dev_low_median",
                  "upper_bound_exists"):
            S[f"{prop}_{k}"] = dvg[f"{prop}_{k}"]

    # headline figures
    S["latest_year"] = latest
    S["spread_kg_m3"] = round(float(L.density_dev.max() - L.density_dev.min()), 1)
    S["n_lighter"] = int((L.direction == "lighter").sum())
    S["n_heavier"] = int((L.direction == "heavier").sum())
    S["n_at_reference"] = int((L.direction == "at_reference").sum())

    def rec(r):
        return {"state": r.State, "petroleum_share": round(float(r.petroleum_share), 4),
                "fame_share": round(float(r.fame_share), 4),
                "hvo_share": round(float(r.hvo_share), 4),
                "blend_density": round(float(r.blend_density), 2),
                "density_dev": round(float(r.density_dev), 2),
                "density_dev_low": round(float(r.density_dev_low), 2),
                "density_dev_high": round(float(r.density_dev_high), 2),
                # Specification-derived, unlike the retired cetane point
                # estimate: the least the pool's cetane can exceed the
                # reference by, given only what the standards guarantee.
                "cetane_dev_low": round(float(r.cetane_dev_low), 2),
                "density_breakdown_fame_kg_m3": (
                    None if (r.density_breakdown_fame_kg_m3 is None
                             or (isinstance(r.density_breakdown_fame_kg_m3, float)
                                 and math.isnan(r.density_breakdown_fame_kg_m3)))
                    else round(float(r.density_breakdown_fame_kg_m3), 0))}

    S["most_lighter"] = [rec(r) for _, r in L.nsmallest(5, "density_dev").iterrows()]
    S["most_heavier"] = [rec(r) for _, r in L.nlargest(5, "density_dev").iterrows()]

    ca = L[L.State == "CA"].iloc[0]
    S["california"] = rec(ca)
    S["california_non_petroleum_pct"] = round(float((1 - ca.petroleum_share) * 100), 1)

    us = df[(df.State == "US")]
    S["us_biofuel_share_by_year"] = {
        str(int(r.year)): round(float((r.fame_share + r.hvo_share) * 100), 2)
        for _, r in us.iterrows()}

    S["components"] = {k: {
        "density_mid": P.midpoint(k, "density"),
        "cetane_mid": P.midpoint(k, "cetane"),
        "density_spec": P.fmt_spec(k, "density"),
        "cetane_spec": P.fmt_spec(k, "cetane"),
        "density_one_sided": P.is_one_sided(k, "density"),
        "cetane_one_sided": P.is_one_sided(k, "cetane"),
        "density_typical": list(P.typical(k, "density")),
        "cetane_typical": list(P.typical(k, "cetane")),
        "spec": P.COMPONENTS[k]["spec"]} for k in P.COMPONENTS}
    S["one_sided_specifications"] = [
        f"{k}.{prop}" for k in P.COMPONENTS for prop in ("density", "cetane")
        if P.is_one_sided(k, prop)]

    checks = {}
    checks["no_negative_petroleum_share"] = bool((df.petroleum_share >= -1e-9).all())
    checks["shares_sum_to_one"] = bool(
        ((df.petroleum_share + df.fame_share + df.hvo_share - 1).abs() < 1e-9).all())
    checks["pool_total_positive"] = bool((df.pool_total > 0).all())
    checks["accounting_break_is_2021"] = S["accounting_break_year"] == 2021
    # An integrity check must test the PIPELINE, not assert the conclusion.
    # An earlier version required density sign-robustness above 90%, which passed
    # only because the reference point was wrong. When the reference was corrected
    # to the EPA certification fuel the figure fell to a few per cent and the check
    # failed - not because the build broke, but because the finding changed. A check
    # that fails when a result changes is a check that pressures you to keep the
    # result. What must be guaranteed is that robustness is MEASURED and CARRIED,
    # whatever it turns out to be.
    checks["sign_robustness_computed"] = bool(
        df.density_sign_robust.notna().all() and df.cetane_sign_robust.notna().all())
    checks["robustness_reported_in_stats"] = all(
        k in S for k in ("density_sign_robust_pct", "cetane_sign_robust_pct"))
    checks["component_deltas_reported"] = len(S["component_deltas_vs_petroleum"]) == 4
    checks["every_row_has_sensitivity_band"] = bool(
        df.density_dev_low.notna().all() and df.density_dev_high.notna().all()
        and df.cetane_dev_low.notna().all() and df.cetane_dev_high.notna().all())
    # Only density has a published point estimate to bracket. Cetane's point
    # estimate was retired, so there is nothing to check against its bound -
    # the bound is the reported quantity.
    checks["deviation_within_band"] = bool(
        ((df.density_dev >= df.density_dev_low - 1e-6) &
         (df.density_dev <= df.density_dev_high + 1e-6)).all())

    # The defect this version corrects: cetane ceilings of 80 and 56 that no
    # standard states, which closed the sensitivity interval and understated the
    # uncertainty on every cetane result. These two checks make its return a
    # build failure rather than something a reader has to notice.
    comp_rows = list(csv.DictReader(open(f"{OUT}/fda_components.csv")))
    checks["one_sided_spec_has_no_upper_bound"] = all(
        r["spec_max"] == "" for r in comp_rows
        if r["spec_one_sided"] in ("True", "true"))
    exposed = df[(df.fame_share + df.hvo_share) > 0]
    checks["unbounded_spec_yields_unbounded_band"] = bool(
        len(exposed) == 0 or exposed.cetane_dev_high.apply(math.isinf).all())
    # Provenance, checked rather than attested. The verification checklist used
    # to ask the author to confirm by hand that the raw files matched their
    # logged digests. That is arithmetic, not judgement, so it runs here and the
    # checklist asks for judgement instead.
    prov, prov_detail = [], []
    for line in open("logs/provenance.jsonl"):
        r = json.loads(line)
        local = os.path.join("data/raw", r["file"])
        if not os.path.exists(local):
            prov.append(False)
            prov_detail.append({"file": r["file"], "status": "missing locally"})
            continue
        h = hashlib.sha256()
        with open(local, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        ok = h.hexdigest() == r["sha256"]
        prov.append(ok)
        prov_detail.append({"file": r["file"], "status": "match" if ok else "DIFFERS",
                            "logged_sha256": r["sha256"], "url": r.get("url")})
    checks["provenance_hashes_match"] = bool(prov and all(prov))
    S["provenance_verification"] = prov_detail

    cols = set(df.columns)
    checks["no_cetane_point_estimate_published"] = not (
        {"blend_cetane", "cetane_dev", "cetane_dev_norm"} & cols)
    checks["no_divergence_index_published"] = "divergence_index" not in cols
    exposed_both = df[(df.fame_share > 0) & (df.hvo_share > 0)]
    checks["breakdown_point_reported_where_defined"] = bool(
        len(exposed_both) == 0
        or exposed_both.density_breakdown_fame_kg_m3.notna().all())
    S["integrity_checks"] = checks
    S["integrity_all_passed"] = all(checks.values())

    json.dump(S, open(f"{OUT}/stats.json", "w"), indent=2, default=str)
    print(json.dumps({k: S[k] for k in
        ["latest_year","spread_kg_m3","n_lighter","n_heavier","n_at_reference",
         "california_non_petroleum_pct","density_sign_robust_pct",
         "cetane_sign_robust_pct","integrity_all_passed"]}, indent=2))
    print("\nintegrity:", json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
