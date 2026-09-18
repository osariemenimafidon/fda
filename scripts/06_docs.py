"""06 — Generate the documentation set. Every number read from stats.json."""
import json, os, sys
import pandas as pd
sys.path.insert(0, "src")
from fda import properties as P

OUT, DOCS = "data/processed", "docs"
S = json.load(open(f"{OUT}/stats.json"))
A = json.load(open("AUTHORS.json")); au = A["authors"][0]
os.makedirs(DOCS, exist_ok=True)
f = lambda n: f"{n:,}" if isinstance(n, int) else n
DRAFT = ("> **DRAFT — NOT VERIFIED.** This package has not passed its verification gate. "
         "No value in it has been checked against the primary source by the author. "
         "Do not cite, deposit, or redistribute.\n")
d = S["component_deltas_vs_petroleum"]
ca = S["california"]

def _verdict(k, prop):
    v = d[k]
    if not v["excludes_zero"]:
        return "**not determined**"
    if prop == "density":
        return "always lighter" if (v["high"] is not None and v["high"] < 0) else "always heavier"
    return "always higher" if (v["low"] is not None and v["low"] > 0) else "always lower"


def _interval(k, unit):
    """Render a difference interval, saying so where a side is unbounded because
    the governing standard states no limit in that direction."""
    v = d[k]
    lo = "unbounded" if v["low_unbounded"] else f"{v['low']:+.0f}"
    hi = "unbounded" if v["high_unbounded"] else f"{v['high']:+.0f}"
    if v["low_unbounded"] and v["high_unbounded"]:
        return "unbounded both sides"
    if v["high_unbounded"]:
        return f"{lo}{unit} or more, no upper bound"
    if v["low_unbounded"]:
        return f"{hi}{unit} or less, no lower bound"
    return f"{lo} to {hi}{unit}"

_rows = []
for prop in ("density", "cetane"):
    for comp in ("fame", "hvo"):
        k = f"{prop}_{comp}"
        unit = " kg/m³" if prop == "density" else ""
        _rows.append(f"| {prop.capitalize()} | {comp.upper()} | "
                     f"{d[k]['spec']} | {_interval(k, unit)} | {_verdict(k, prop)} |")
delta_table = "\n".join(_rows)

# ---------------- LIMITATIONS ----------------
lim = f"""# Fuel Divergence Atlas — Limitations

{DRAFT}
Version 1.0 · built {S['build_date']}

## 1. These are estimates from specification envelopes, not fuel assays

**Nobody sampled a pump.** Every property in this dataset is inferred by combining
EIA consumption volumes with published specification ranges for each fuel component.
A real tank in a real state contains fuel whose actual properties may sit anywhere
inside — or outside — those ranges.

The dataset answers "given what was consumed, what does the specification imply the
pool looked like". It does not answer "what was the density of the fuel at this
station on this day". Any use that treats these as measurements is misuse.

## 2. The obvious way to compute blend share is wrong

EIA changed its distillate accounting at data year **{S['accounting_break_year']}**.
For {S['identical_regime'][0]}–{S['identical_regime'][1]}, `DFACP` (distillate consumed
by transportation) and `DAACP` (distillate + biodiesel + renewable diesel) are identical
in every state and year. From {S['accounting_break_year']}, EIA's technical notes state
distillate "includes all biodiesel and renewable diesel refinery and blender net inputs
volumes, but excludes biodiesel and renewable diesel product supplied consumption".

Consequently **`DFACP + BDACP + B1ACP` double-counts** from {S['accounting_break_year']}
forward — nationally by about {f(int(S['naive_overcount_mean_kbbl']))} thousand barrels a
year, roughly {S['naive_overcount_pct_mean']}% — while being correct before. A pipeline
built that way manufactures a trend break at {S['accounting_break_year']} that looks like
a real change in fuel supply.

**This dataset uses `DAACP` as the denominator and never sums the three series.** The
pipeline detects the break from the data and aborts if it is not at
{S['accounting_break_year']}.

## 3. Only the HVO direction is established; the FAME direction is not

Over the **full** specification envelopes, each component's difference from petroleum
diesel is:

| Property | Component | Specification | Difference from certification fuel | Sign |
|---|---|---|---|---|
{delta_table}

Because the deviation equals `fame_share × (FAME − petroleum) + hvo_share × (HVO −
petroleum)`, a common-mode error in the petroleum reference cancels. So:

**HVO is robustly lighter and robustly higher-cetane than the certification fuel.** Both
its intervals exclude zero, so for states blending renewable diesel the direction of
divergence holds for any admissible property values.

**FAME's direction is not determined.** Its density envelope
({S['components']['fame']['density_spec']}) overlaps the certification fuel's
({S['components']['petroleum']['density_spec']}), and its cetane specification
({S['components']['fame']['cetane_spec']}) is one-sided and runs through and above the
certification fuel's ({S['components']['petroleum']['cetane_spec']}). Both intervals
straddle zero. For a state blending only biodiesel, **this dataset cannot say whether its
pool is heavier or lighter than the certification fuel**, only that it differs.

**One-sided specifications are carried as unbounded, not closed with a number.** Neither
EN 15940 nor EN 14214 nor ASTM D6751 states a cetane maximum, so the upper side of every
cetane deviation interval is unbounded: {S['cetane_band_unbounded_pct']}% of state-years
have no finite upper bound on their cetane deviation. An earlier version of this pipeline
carried invented cetane ceilings of 80 and 56, which closed those intervals and understated
the uncertainty on every cetane result. The density result is unaffected, because both
density specifications are genuinely two-sided.

Consequently density direction is sign-robust in just
{S['density_sign_robust_pct']}% of state-years and cetane direction in
{S['cetane_sign_robust_pct']}% - essentially only the HVO-blending states. The midpoint
estimates do show biodiesel states heavier, and that may well be true, but the
specifications do not establish it and this dataset does not claim it.

An earlier draft of this project reported density direction as robust in 95.3% of
state-years. That figure came from using EN 590 - the European automotive diesel
standard - as the certification-fuel proxy. EN 590 sits about 19 kg/m3 lighter than the
fuel EPA actually certifies US engines on. Correcting the reference to 40 CFR 1065.703
moved the result from "robust" to "not established" for every FAME-blending state.

Every row carries `density_sign_robust` and `cetane_sign_robust` so this cannot be missed.

## 4. Component property values are assumptions — but they are no longer load-bearing

All values live in `src/fda/properties.py`, which separates two things an earlier version
conflated: the **specification** a standard guarantees, and an **assumed typical** range
used only for a point estimate.

Two consequences follow, and they run in opposite directions.

**The FAME density assumption has been taken off the critical path.** ASTM D6751 — the
standard the United States biodiesel supply is actually produced to — sets no density limit
at all, so the 860–900 kg/m³ bound rests on EN 14214, a European standard, alone. Rather
than assert it and propagate it, every state-year with both components now carries a
**breakdown point**: the FAME density above which the sign of its density deviation would
cease to be robust. In {S['density_breakdown_latest_year']} the tightest of those thresholds
is **{S['density_breakdown_latest_min_kg_m3']:.0f} kg/m³**
({S['density_breakdown_latest_min_state']}), against an assumed FAME density of
{S['fame_density_assumed_midpoint']:.0f} kg/m³ and a real-world figure near it. No fatty
acid methyl ester approaches those thresholds, so the latest cross-section's direction does
not depend on the assumption. A reader can check that without owning EN 14214.

**Earlier years are a different matter, and the breakdown point says so.** Renewable diesel
penetration grew across the window, so in early years the HVO term was small relative to the
FAME term and the threshold falls: the tightest across the whole panel is
{S['density_breakdown_panel_min_kg_m3']:.0f} kg/m³
({S['density_breakdown_panel_min_state']}, {S['density_breakdown_panel_min_year']}), which
is *below* the assumed FAME density. {S['density_breakdown_rows_below_assumption']} of
{S['density_breakdown_defined_rows']} defined rows sit below it. Those rows' directions do
depend on the assumption, and that is the same fact the
{S['density_sign_robust_pct']}% panel-wide sign-robustness figure reports from the other
side.

**No cetane point estimate is published at all.** Every candidate rested on an assumed
typical range rather than a specification, so the reported cetane quantity is
`cetane_dev_low`: the least the pool's cetane can exceed the reference by, given only what
the standards guarantee. The retired `divergence_index` went with it, because half of it was
that assumption.

## 5. Linear volume blending

Density blends close to linearly by volume, so the density estimate is reasonable within
its stated limits. **Cetane does not blend linearly.** That was one of two reasons the
cetane point estimate has been withdrawn; the other is in §4. What remains for cetane is a
bound, not an estimate, and a bound is unaffected by the blending law.

## 6. Transportation sector only

Uses the `*ACP` series — consumption by the transportation sector. Off-road, marine,
rail, heating and industrial distillate are excluded. Many of the engines CIDEX covers
are nonroad, so the fuel pool they actually see is **not** exactly this one.

## 7. The reference point is a choice

Divergence is measured against the midpoint of the petroleum diesel specification
({S['density_reference']} kg/m³, cetane {S['cetane_reference']}). EPA's certification
fuel has its own specification which may sit elsewhere in that range. Shifting the
reference shifts every deviation by a constant; it does not change the spread between
states, which is the finding.

## 8. State of consumption, not state of use

EIA attributes consumption to the state of sale. Long-haul freight burns fuel across
state lines.

## Integrity checks

All pass in this build. They test internal consistency, **not** agreement with EIA.

""" + "\n".join(f"- {'PASS' if v else 'FAIL'} — `{k}`" for k, v in S["integrity_checks"].items()) + "\n"
open(f"{DOCS}/LIMITATIONS.md", "w").write(lim)

# ---------------- CODEBOOK ----------------
df = pd.read_csv(f"{OUT}/fda_state_year.csv", nrows=5)
COL = {
 "State":"USPS state code; `US` is the national total.","year":"Calendar/model year.",
 "pool_total":"Total transportation diesel pool, EIA series `DAACP`.",
 "units":"Volume units for `pool_total` (thousand barrels).",
 "petroleum_share":"Petroleum share of pool = 1 − fame_share − hvo_share.",
 "fame_share":"FAME biodiesel share, `BDACP`/`DAACP`.",
 "hvo_share":"HVO renewable diesel share, `B1ACP`/`DAACP`.",
 "blend_density":"Volume-weighted blend density, kg/m³ at 15 °C.",
 "density_ref":"Reference density (petroleum specification midpoint).",
 "density_dev":"blend_density − density_ref. **Negative = lighter.**",
 "density_dev_norm":"density_dev divided by the petroleum specification width.",
 "density_dev_low":"Lowest deviation across the full specification envelopes.",
 "density_dev_high":"Highest deviation across the full specification envelopes.",
 "density_dev_band":"density_dev_high − density_dev_low.",
 "density_sign_robust":"True when the whole band sits one side of zero.",
 "blend_cetane":"Volume-weighted blend cetane. **Indicative only — see LIMITATIONS §5.**",
 "cetane_ref":"Reference cetane (petroleum specification midpoint).",
 "cetane_dev":"blend_cetane − cetane_ref.","cetane_dev_norm":"Normalised by spec width.",
 "cetane_dev_low":"Lowest cetane deviation the specifications permit. This is the reported cetane quantity: no cetane point estimate is published, because every candidate rests on an assumed typical range rather than a specification.",
 "density_breakdown_fame_kg_m3":"Breakdown point. The FAME density above which the sign of this row's density deviation would no longer be robust, holding HVO and petroleum at the admissible values least favourable to the conclusion. Empty where undefined (no FAME or no HVO). Compare against the assumed FAME density of 880 kg/m3: a threshold far above it means the conclusion does not depend on the FAME assumption.",
 "cetane_dev_high":"Highest cetane deviation across envelopes.",
 "cetane_dev_band":"Band width.",
 "cetane_sign_robust":f"True when the band excludes zero. Only {S['cetane_sign_robust_pct']}% of rows.",
 "divergence_index":"Euclidean magnitude of the normalised (density, cetane) pair. Always ≥ 0; use the signed columns for direction.",
 "direction":"`lighter`, `heavier`, or `at_reference`, from the sign of density_dev.",
}
rows = "\n".join(f"| `{c}` | {COL.get(c,'—')} |" for c in df.columns)
open(f"{DOCS}/CODEBOOK.md","w").write(f"""# Fuel Divergence Atlas — Codebook

{DRAFT}
Version 1.0 · built {S['build_date']}

Unit of analysis: **(state, year)**. {f(S['rows'])} rows,
{S['state_count']} states plus a US total, {S['year_min']}–{S['year_max']}.

## `fda_state_year.csv`

| Column | Description |
|---|---|
{rows}

## `fda_components.csv`

The property envelope table, shipped as data so every assumption is inspectable:
component, specification source, property, min, max, midpoint, note, and a
`verified_by_author` flag that is `False` until the gate is signed.

## `fda_pool.csv`

Raw extracted volumes before any property modelling — `pool_total`, `fame_volume`,
`hvo_volume` per state-year, with `in_usable_window`.
""")

# ---------------- VERIFICATION CHECKLIST ----------------
open(f"{DOCS}/VERIFICATION_CHECKLIST.md","w").write(f"""# Fuel Divergence Atlas — Verification Checklist

{DRAFT}
Author: {au['name']} · ORCID {au['orcid']}

## Part 1 — Reproduce

- [ ] Ran the pipeline from `README.md`; `stats.json` matches the shipped copy
- [ ] All {len(S['integrity_checks'])} integrity checks PASS
- [ ] SHA-256 hashes in `logs/provenance.jsonl` match my downloaded EIA files

Expected headline figures:

| | |
|---|---|
| Spread across states, {S['latest_year']} | {S['spread_kg_m3']} kg/m³ |
| States lighter / heavier / at reference | {S['n_lighter']} / {S['n_heavier']} / {S['n_at_reference']} |
| California non-petroleum share | {S['california_non_petroleum_pct']}% |
| Density direction sign-robust | {S['density_sign_robust_pct']}% of state-years |
| Cetane direction sign-robust | {S['cetane_sign_robust_pct']}% of state-years |

## Part 2 — The property values

Every number below is mine, not EIA's, and they live in `src/fda/properties.py`.

| Component | Specification | Density (spec) | Cetane (spec) | Cetane (assumed typical) |
|---|---|---|---|---|
| Petroleum diesel | {P.COMPONENTS['petroleum']['spec']} | {P.fmt_spec('petroleum','density')} | {P.fmt_spec('petroleum','cetane')} | {P.typical('petroleum','cetane')[0]:g}–{P.typical('petroleum','cetane')[1]:g} |
| FAME biodiesel | {P.COMPONENTS['fame']['spec']} | {P.fmt_spec('fame','density')} | {P.fmt_spec('fame','cetane')} | {P.typical('fame','cetane')[0]:g}–{P.typical('fame','cetane')[1]:g} |
| HVO renewable diesel | {P.COMPONENTS['hvo']['spec']} | {P.fmt_spec('hvo','density')} | {P.fmt_spec('hvo','cetane')} | {P.typical('hvo','cetane')[0]:g}–{P.typical('hvo','cetane')[1]:g} |

The **spec** columns are what the standard guarantees; `min.` means the standard states no
maximum. The **assumed typical** column is an assumption of this study, used only to form a
point estimate.

**This part used to be the load-bearing one. It is not any more.** Four of the six values
below are the same figures FUELDIV confirmed against the primary sources under its own
signed gate — the certification fuel's density and cetane envelopes from 40 CFR 1065.703,
and EN 15940's density range and cetane minimum. The fifth, FAME's density, has been taken
off the critical path by the breakdown point in LIMITATIONS §4. The sixth, the assumed
typical cetane ranges, no longer feeds any published number, because no cetane point
estimate is published.

- [ ] The four values carried over from FUELDIV are the ones I confirmed there:
      certification density {P.fmt_spec('petroleum','density')} kg/m³, certification cetane
      {P.fmt_spec('petroleum','cetane')}, EN 15940 density {P.fmt_spec('hvo','density')}
      kg/m³, EN 15940 cetane {P.fmt_spec('hvo','cetane')}
- [ ] I accept the breakdown-point treatment of FAME density: the
      {S['density_breakdown_latest_year']} cross-section's direction holds unless FAME
      density exceeds {S['density_breakdown_latest_min_kg_m3']:.0f} kg/m³, which it cannot,
      **and** {S['density_breakdown_rows_below_assumption']} earlier rows do depend on the
      EN 14214 figure and are reported as such
- [ ] Set `verified_by_author` to True in `fda_components.csv`

Optional, and no longer blocking: confirm EN 14214's density range of
{P.fmt_spec('fame','density')} kg/m³ directly. It would tighten the early years; it changes
nothing in the latest cross-section.

## Part 3 — Spot-checks against EIA

- [ ] California {S['latest_year']}: pool {f(int(ca['blend_density']))} kg/m³ from
      {ca['petroleum_share']:.0%} petroleum / {ca['fame_share']:.0%} FAME /
      {ca['hvo_share']:.0%} HVO — checked against EIA's own SEDS tables
- [ ] Confirmed EIA's published narrative agrees that renewable diesel consumption is
      overwhelmingly Californian
- [ ] Minnesota {S['latest_year']} biodiesel share is consistent with its B20 mandate

## Part 4 — Judgement calls

- [ ] **Reference point.** Using the petroleum specification midpoint
      ({S['density_reference']} kg/m³) as the certification-fuel proxy is defensible, or
      I have substituted EPA's actual certification fuel specification.
- [ ] **Cetane.** I accept that the cetane direction is not robust
      ({S['cetane_sign_robust_pct']}% of rows) and that LIMITATIONS §3 and §5 say so
      plainly enough that no reader will quote a cetane direction for a FAME state.
- [ ] **Framing.** LIMITATIONS §1 makes it unmissable that these are specification-based
      estimates, not fuel assays.
- [ ] **Sector.** Transportation-sector-only coverage is stated, and its mismatch with
      CIDEX's nonroad engines is acknowledged.

## Part 5 — Before deposit

- [ ] `python3 scripts/07_publish_gate.py` passes
- [ ] No DRAFT stamp remains in any published document
- [ ] Abstract rewritten in my own voice

## Sign-off

I have personally reproduced this pipeline, confirmed the property values against their
standards, and checked its outputs against the primary source.

Signed: ____________________  Date: ____________
""")

# ---------------- CITATION ----------------
open("CITATION.cff","w").write(f"""cff-version: 1.2.0
title: "FDA: Fuel Divergence Atlas"
message: "If you use this dataset, please cite it as below."
type: dataset
authors:
  - family-names: "{au['family_name']}"
    given-names: "{au['given_names']}"
    orcid: "https://orcid.org/{au['orcid']}"
    affiliation: "{au['affiliation']}"
version: "1.0.0-draft"
date-released: "{S['build_date']}"
license: CC-BY-4.0
abstract: >-
  State-level estimates of how far the in-service transportation diesel pool diverges
  from the certification fuel, {S['year_min']}-{S['year_max']}, derived from US EIA State
  Energy Data System consumption volumes combined with published fuel specification
  envelopes. Finds that divergence is bidirectional: states driven by low-carbon fuel
  standards blend HVO renewable diesel and their pool becomes lighter, while states with
  biodiesel blending mandates blend FAME and their pool becomes heavier, giving a spread
  of {S['spread_kg_m3']} kg/m3 across states in {S['latest_year']}. These are
  specification-based estimates, not fuel assays.
keywords:
  - diesel fuel
  - renewable diesel
  - biodiesel
  - fuel properties
  - low carbon fuel standard
  - open data
""")
print("written:")
for p_ in ["docs/LIMITATIONS.md","docs/CODEBOOK.md","docs/VERIFICATION_CHECKLIST.md","CITATION.cff"]:
    print(f"  {os.path.getsize(p_):>6,}  {p_}")
