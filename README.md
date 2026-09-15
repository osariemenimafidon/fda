# Fuel Divergence Atlas

**State-level divergence of the in-service diesel pool from the certification fuel**

> **DRAFT — NOT VERIFIED.** Has not passed its verification gate. Do not cite or deposit.

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
envelope entirely above. Only the magnitude is uncertain.

**For states blending FAME biodiesel, the direction is not established.** FAME's density
and cetane envelopes both overlap the certification fuel's, so this dataset cannot say
whether a biodiesel-blending state's pool is heavier or lighter — only that it differs.
Midpoint estimates suggest heavier, and that may be true, but the specifications do not
establish it and the dataset does not claim it.

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
```

Every number in every document is interpolated from `data/processed/stats.json`.

## Output

| File | What |
|---|---|
| `fda_state_year.csv` | Pool shares, blend properties, divergence, sensitivity bands |
| `fda_components.csv` | The property envelope table, as data |
| `fda_pool.csv` | Raw extracted volumes before property modelling |

Built data is not committed; it regenerates in seconds and Zenodo is its citable home.

## Status

Not verified. See `docs/VERIFICATION_CHECKLIST.md`. No DOI minted.

## Licence

Data and docs CC BY 4.0; code MIT. Derived from US EIA SEDS (US Government work).
