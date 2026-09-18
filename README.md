# Fuel Divergence Atlas

**State-level divergence of the in-service diesel pool from the certification fuel**

Osariemen Imafidon · [ORCID 0009-0006-3069-4674](https://orcid.org/0009-0006-3069-4674) · Independent Researcher
Part of the [FACET](https://osariemenimafidon.github.io/facet/) research program.

---

## The finding

**States blending HVO renewable diesel have diesel pools that are robustly lighter and
higher-cetane than the fuel EPA certifies engines on.** California's 2024 pool is 54.6%
non-petroleum — 51% renewable diesel — and sits about 34 kg/m³ lighter than the
certification fuel.

That direction holds for **any** admissible property values: HVO's density envelope
(765–800) lies entirely below the certification fuel's (838.9–864.6), and its cetane
minimum (70) sits above the certification fuel's maximum (50). Only the magnitude is
uncertain — and on cetane the magnitude is not merely uncertain but unbounded, because
EN 15940 states a cetane minimum and no maximum.

**For states blending FAME biodiesel, the direction is not established.** FAME's density
envelope (860–900) overlaps the certification fuel's, and its cetane specification is
one-sided (minimum 47), running through and above the certification range. So this dataset
cannot say whether a biodiesel-blending state's pool is heavier or lighter — only that it
differs. Midpoint estimates suggest heavier, and that may be true, but the specifications
do not establish it and the dataset does not claim it.

**A correction, recorded rather than quietly applied.** An earlier version of this pipeline
carried cetane *maxima* of 80 for HVO and 56 for FAME. No standard states either: EN 15940,
EN 14214 and ASTM D6751 all specify cetane minima only. Those invented ceilings closed the
sensitivity interval and understated the uncertainty on every cetane result —
98.6% of state-years have no finite upper bound on their cetane deviation. The density
result is unaffected, because both density specifications are genuinely two-sided, and no
reported density estimate changed. `src/fda/properties.py` now separates what a standard
guarantees from what this study assumes, and two integrity checks fail the build if a
one-sided specification is ever closed again.

**Two assumptions have been taken off the critical path.** ASTM D6751 — the standard US
biodiesel is actually made to — sets no density limit, so FAME's 860–900 kg/m³ bound rests
on EN 14214 alone. Rather than assert it, every state-year with both components carries a
**breakdown point**: the FAME density above which its direction would stop being robust. In
2024 the tightest is
**917 kg/m³**
(US) against a real FAME density near 880, so the
latest cross-section does not depend on EN 14214 at all;
18 early-year rows do, and say so. Separately,
**no cetane point estimate is published** — every candidate rested on an assumed typical
range rather than a specification, so what is reported is `cetane_dev_low`, the least the
pool's cetane can exceed the reference by given only what the standards guarantee. The
`divergence_index` went with it, because half of it was that assumption.

## Two things to read before using it

**1. These are estimates, not assays.** Consumption volumes combined with specification
envelopes. Nobody sampled a pump. See `docs/LIMITATIONS.md` §1.

**1b. The reference is the EPA certification fuel**, 40 CFR 1065.703 (API 32–37, cetane
40–50), not a European standard. An earlier draft used EN 590, which sits ~19 kg/m³
lighter; correcting it changed which conclusions hold.

**2. The intuitive way to compute blend share is wrong.** EIA changed its distillate
accounting in 2021; `DFACP + BDACP + B1ACP` double-counts from then on while being correct
before, which manufactures a fake trend break. Use `DAACP` as the denominator. See
`docs/LIMITATIONS.md` §2.

## Getting the source data

Not redistributed here. Download into `data/raw/`:

- [`use_all_phy.csv`](https://www.eia.gov/state/seds/sep_use/total/csv/use_all_phy.csv) — SEDS consumption, physical units
- [`Codes_and_Descriptions.xlsx`](https://www.eia.gov/state/seds/CDF/Codes_and_Descriptions.xlsx) — MSN dictionary

Hashes are recorded in `logs/provenance.jsonl`.

## Rebuilding

```bash
pip install -r requirements.txt
python3 scripts/01_provenance.py     # hash and log the raw files
python3 scripts/02_extract.py        # SEDS -> state-year pool panel; detects the 2021 break
python3 scripts/03_divergence.py     # shares, blend properties, divergence, sensitivity
python3 scripts/04_qa.py             # integrity checks, stats.json
python3 scripts/05_figures.py        # figures
python3 scripts/06_docs.py           # regenerate this documentation
python3 scripts/07_publish_gate.py   # pre-publication scan
python3 scripts/09_reproduce.py       # clean-clone rebuild, diffed against the committed stats
python3 scripts/10_eia_crosscheck.py  # published shares vs values read straight from EIA
```

Every number in every document is interpolated from `data/processed/stats.json`.

## Output

| File | What |
|---|---|
| `fda_state_year.csv` | Pool shares, blend properties, divergence, sensitivity bands |
| `fda_components.csv` | The property envelope table, as data |
| `fda_pool.csv` | Raw extracted volumes before property modelling |

Built data is not committed; it regenerates in seconds and Zenodo is its citable home.

## Verification

The mechanical half runs as code, not as testimony: `09_reproduce.py` clones this repo into
a clean directory, rebuilds from the raw inputs and diffs the regenerated `stats.json`
against the committed copy; `10_eia_crosscheck.py` compares the published shares against
values read straight from EIA's CSV; and `provenance_hashes_match` recomputes every raw
input's SHA-256 against `logs/provenance.jsonl`. Results live in `qa/`.

What is left for the author is judgement, not arithmetic. See
`docs/VERIFICATION_CHECKLIST.md`.

## Status

**Verified.** The gate is signed and `.gate-signed` is tracked, so a clone rebuilds to this
same verified state rather than reverting to draft. Deleting that file returns every
document and figure to DRAFT on the next build.

The mechanical half of the gate is evidence rather than testimony, and anyone can re-run it:
`qa/09_reproduce.json` records a clean-clone rebuild diffed against the committed
`stats.json` (251 keys, REPRODUCED), `qa/10_eia_crosscheck.json` records the published
shares against values read straight from EIA (AGREES, worst difference 0.000000), and
15 integrity checks run on every build. What the author attested
to is judgement: the four rulings are recorded in `.gate-signed`.

## Licence

Data and docs CC BY 4.0; code MIT. Derived from US EIA SEDS (US Government work).
