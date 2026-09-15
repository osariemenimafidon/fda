# Fuel Divergence Atlas — Verification Checklist

> **DRAFT — NOT VERIFIED.** This package has not passed its verification gate. No value in it has been checked against the primary source by the author. Do not cite, deposit, or redistribute.

Author: Imafidon, Osariemen · ORCID 0009-0006-3069-4674

## Part 1 — Reproduce

- [ ] Ran the pipeline from `README.md`; `stats.json` matches the shipped copy
- [ ] All 9 integrity checks PASS
- [ ] SHA-256 hashes in `logs/provenance.jsonl` match my downloaded EIA files

Expected headline figures:

| | |
|---|---|
| Spread across states, 2024 | 38.3 kg/m³ |
| States lighter / heavier / at reference | 3 / 40 / 8 |
| California non-petroleum share | 54.6% |
| Density direction sign-robust | 2.7% of state-years |
| Cetane direction sign-robust | 4.7% of state-years |

## Part 2 — The property values (the load-bearing assumption)

Every number below is mine, not EIA's. **Confirm each against the standard before
anything is published.** They live in `src/fda/properties.py`.

| Component | Specification | Density range | Cetane range |
|---|---|---|---|
| Petroleum diesel | 40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975 | 838.9–864.6 | 40.0–50.0 |
| FAME biodiesel | ASTM D6751 / EN 14214 | 860.0–900.0 | 47.0–56.0 |
| HVO renewable diesel | EN 15940 (paraffinic diesel) | 765.0–800.0 | 70.0–80.0 |

- [ ] Petroleum diesel density range confirmed
- [ ] Petroleum diesel cetane range confirmed
- [ ] FAME density and cetane ranges confirmed
- [ ] HVO density and cetane ranges confirmed
- [ ] Set `verified_by_author` to True in `fda_components.csv` once all four are done

## Part 3 — Spot-checks against EIA

- [ ] California 2024: pool 817 kg/m³ from
      45% petroleum / 4% FAME /
      51% HVO — checked against EIA's own SEDS tables
- [ ] Confirmed EIA's published narrative agrees that renewable diesel consumption is
      overwhelmingly Californian
- [ ] Minnesota 2024 biodiesel share is consistent with its B20 mandate

## Part 4 — Judgement calls

- [ ] **Reference point.** Using the petroleum specification midpoint
      (851.75 kg/m³) as the certification-fuel proxy is defensible, or
      I have substituted EPA's actual certification fuel specification.
- [ ] **Cetane.** I accept that the cetane direction is not robust
      (4.7% of rows) and that LIMITATIONS §3 and §5 say so
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
