# Fuel Divergence Atlas

**State-level divergence of the in-service diesel pool from the certification fuel**

> **DRAFT — NOT VERIFIED.** Has not passed its verification gate. Do not cite or deposit.

Osariemen Imafidon · [ORCID 0009-0006-3069-4674](https://orcid.org/0009-0006-3069-4674) · Independent Researcher
Part of the [FACET](https://osariemenimafidon.github.io/facet/) research program.

---

## The finding

US diesel pools diverge from the certification fuel **in opposite directions depending on
which policy drives the state.**

Clean-fuel-standard states blend HVO renewable diesel and their pool gets **lighter**.
Biodiesel-mandate states blend FAME and their pool gets **heavier**. An engine calibrated
for the national average is mis-calibrated in California and mis-calibrated the other way
in Minnesota.

Over the full specification envelopes, FAME is always heavier than petroleum diesel and
HVO always lighter, so the **direction** of density divergence is robust to any admissible
choice of property values — only the magnitude is uncertain. Cetane is not robust and
the documentation says so.

## Two things to read before using it

**1. These are estimates, not assays.** Consumption volumes combined with specification
envelopes. Nobody sampled a pump. See `docs/LIMITATIONS.md` §1.

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
