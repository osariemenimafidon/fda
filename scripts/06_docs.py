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

## 3. Density direction is robust; cetane direction is not

Over the **full** specification envelopes, each component's difference from petroleum
diesel is:

| Property | Component | Difference from petroleum | Sign |
|---|---|---|---|
| Density | FAME | {d['density_fame']['low']:+.0f} to {d['density_fame']['high']:+.0f} kg/m³ | **always heavier** |
| Density | HVO | {d['density_hvo']['low']:+.0f} to {d['density_hvo']['high']:+.0f} kg/m³ | **always lighter** |
| Cetane | FAME | {d['cetane_fame']['low']:+.0f} to {d['cetane_fame']['high']:+.0f} | **sign can flip** |
| Cetane | HVO | {d['cetane_hvo']['low']:+.0f} to {d['cetane_hvo']['high']:+.0f} | always higher |

Because the deviation equals `fame_share × (FAME − petroleum) + hvo_share × (HVO −
petroleum)`, a common-mode error in the petroleum reference cancels. So:

- **Density direction holds in {S['density_sign_robust_pct']}% of state-years** whatever
  admissible property values are chosen. The *magnitude* remains uncertain.
- **Cetane direction holds in only {S['cetane_sign_robust_pct']}% of state-years.** FAME's
  cetane number straddles petroleum's, so for biodiesel-blending states the sign of the
  cetane deviation is **not determined**. Do not assert a cetane direction for those states.

Every row carries `density_sign_robust` and `cetane_sign_robust` so this cannot be missed.

## 4. Component property values are assumptions, not measurements

All midpoints live in `src/fda/properties.py` with their specification source. The whole
index scales with them. They are the author's first verification item.

## 5. Linear volume blending

Density blends close to linearly by volume. **Cetane does not.** The cetane column is a
volume-weighted approximation and should be treated as indicative only — a further reason
not to lean on the cetane result.

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
 "cetane_dev_low":"Lowest cetane deviation across envelopes.",
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

## Part 2 — The property values (the load-bearing assumption)

Every number below is mine, not EIA's. **Confirm each against the standard before
anything is published.** They live in `src/fda/properties.py`.

| Component | Specification | Density range | Cetane range |
|---|---|---|---|
| Petroleum diesel | {P.COMPONENTS['petroleum']['spec']} | {P.COMPONENTS['petroleum']['density_min']}–{P.COMPONENTS['petroleum']['density_max']} | {P.COMPONENTS['petroleum']['cetane_min']}–{P.COMPONENTS['petroleum']['cetane_max']} |
| FAME biodiesel | {P.COMPONENTS['fame']['spec']} | {P.COMPONENTS['fame']['density_min']}–{P.COMPONENTS['fame']['density_max']} | {P.COMPONENTS['fame']['cetane_min']}–{P.COMPONENTS['fame']['cetane_max']} |
| HVO renewable diesel | {P.COMPONENTS['hvo']['spec']} | {P.COMPONENTS['hvo']['density_min']}–{P.COMPONENTS['hvo']['density_max']} | {P.COMPONENTS['hvo']['cetane_min']}–{P.COMPONENTS['hvo']['cetane_max']} |

- [ ] Petroleum diesel density range confirmed
- [ ] Petroleum diesel cetane range confirmed
- [ ] FAME density and cetane ranges confirmed
- [ ] HVO density and cetane ranges confirmed
- [ ] Set `verified_by_author` to True in `fda_components.csv` once all four are done

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
