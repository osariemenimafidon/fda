# Fuel Divergence Atlas — Build Spec v1.0

**FDA — state-level divergence of in-service diesel fuel properties from the
certification fuel**

Author: Osariemen Imafidon (ORCID 0009-0006-3069-4674), Independent Researcher
Part of [FACET](https://osariemenimafidon.github.io/facet/)
Drafted 2026-09-15 · **DRAFT — awaiting approval before any pipeline code**

---

## 1. The question

FACET's premise is that an engine is certified on one fuel and then runs on whatever
the market supplies. CIDEX establishes what was certified. **This project establishes
what is actually supplied, and how far it has drifted.**

Concretely: *for each US state and year, how far do the bulk properties of the
in-service diesel pool sit from the properties of the certification fuel the engines
burning it were approved on?*

## 2. What the source check already changed

Two findings from profiling, before any pipeline code. Both change the project.

### 2.1 The thesis is bidirectional divergence, not "California is different"

The original scope assumed diffuse divergence; the concern after the first source check
was that renewable diesel is almost entirely Californian and the map would be one dark
state. Profiling the actual state-year data shows something better than either:

**The US diesel pool diverges from the certification fuel in *opposite directions*
depending on which policy drives the state.**

| 2024 | Petroleum | FAME | HVO | Blend density | Deviation | Blend cetane |
|---|---|---|---|---|---|---|
| California | 45% | 4% | **51%** | 808.9 | **−23.6** | 63.2 |
| Oregon | 64% | 9% | 27% | 823.5 | −9.0 | 57.5 |
| Washington | 79% | 3% | 19% | 824.5 | −8.0 | 55.5 |
| Minnesota | 85% | **15%** | 0% | 839.6 | **+7.1** | 51.1 |
| Iowa | 90% | 10% | 0% | 837.5 | +5.0 | 51.1 |

*(Provisional midpoints — every property value is [VERIFY].)*

**LCFS states blend HVO and their pool gets lighter and higher-cetane. Biodiesel-mandate
states blend FAME and their pool gets heavier.** An engine calibrated for the national
average is mis-calibrated in California and mis-calibrated in the opposite sense in
Minnesota. Total spread across states: **30.7 kg/m³**. 3 states lighter than reference,
47 heavier, 1 exactly at it.

California's diesel pool is **over half non-petroleum**. That is the headline number.

### 2.2 EIA changed its own accounting in 2021, and the obvious method is wrong

`DFACP` (distillate consumed by transportation) and `DAACP` (distillate + biodiesel +
renewable diesel) are **identical for all 52 states in every year 2005–2020**, then
diverge for 51 of 52 states from 2021. EIA's technical notes give the reason:

> "For 2021 forward, EIA assumes that distillate fuel oil consumption includes all
> biodiesel and renewable diesel refinery and blender net inputs volumes, but excludes
> biodiesel and renewable diesel product supplied consumption."

Consequences, both load-bearing:

1. **`DFACP + BDACP + B1ACP` double-counts** the blender-net-inputs portion from 2021 on.
   The sum exceeds `DAACP` by a stable ~40 million barrels a year. Anyone computing blend
   shares that way gets silently wrong answers from 2021 forward, and correct ones before.
2. **`DAACP` is the only consistently defined denominator.** Using it, the national
   biofuel share moves across the 2021 break with no discontinuity (2020 → 2021 is
   +0.08 pp, well inside normal year-to-year variation), and `BDACP + B1ACP` never
   exceeds `DAACP` in any of the state-years checked.

**Method: pool = `DAACP`. Shares = `BDACP`/`DAACP` and `B1ACP`/`DAACP`. Never sum the
three series.** This is documented in LIMITATIONS as a trap for reusers, since the
intuitive approach is the wrong one.

## 3. Sources

| Source | What it gives | Status |
|---|---|---|
| EIA SEDS `use_all_phy.csv` | State × year × energy source consumption, **physical units**, 1960–2024 | Confirmed; manual download (eia.gov blocked by egress policy) |
| EIA SEDS `Codes_and_Descriptions.xlsx` | MSN code dictionary | Confirmed; manual download |
| EN 590 / EN 15940 / ASTM D975 / ASTM D6751 | Property envelopes per fuel type | Specification values, cited not downloaded |

Provenance is hash-logged exactly as in CIDEX.

## 4. Unit of analysis

One row per **(state, year)**. 50 states + DC, and the usable window is set by when EIA
first publishes renewable diesel separately — expected 2011 onward, **to be confirmed
from the data, not assumed**.

## 5. The computation

**Step 1 — pool composition.** For each state-year, take physical-unit consumption of
petroleum distillate, FAME biodiesel and HVO renewable diesel, and compute each as a
volume share of the total diesel pool.

**Step 2 — component properties.** Each fuel type carries a specification property
envelope (midpoint and range):

| Component | Density @15 °C | Cetane |
|---|---|---|
| Petroleum diesel (EN 590 / ASTM D975) | 820–845 kg/m³ | ≥ 51 |
| FAME biodiesel (ASTM D6751) | ~880 kg/m³ | ~47–56 |
| HVO renewable diesel (EN 15940) | 765–800 kg/m³ | ~70–80 |

**[VERIFY] Every figure in this table is a specification value the author must confirm
before publication.** They are the load-bearing assumption of the whole index.

**Step 3 — blend properties.** Volume-weighted mean of the component midpoints. Density
blends near-linearly by volume; cetane does not blend strictly linearly, which is a
**stated limitation**, not a hidden one.

**Step 4 — divergence.** Distance from the certification-fuel reference point, reported
per property and as a composite index. The composite normalises each property by its
certification-spec width before combining, so the index is dimensionless and neither
property dominates by unit scale.

**[VERIFY] The weighting of the composite is a judgement.** v1.0 weights density and
cetane equally and ships both components separately so any reader can reweight.

## 6. What this is not

- **Not measured fuel.** These are specification-envelope estimates driven by consumption
  volumes, not assays of fuel at the pump. The dataset must say so in its title field,
  its abstract, and its first figure caption.
- **Not a claim about any individual fuelling event.** State-year averages say nothing
  about what one truck received on one day.
- **Not a compliance instrument.**

## 7. Outputs

- `fda_state_year.csv` — pool shares, blend properties, divergence components, composite
- `fda_components.csv` — the property envelope table, with its citations, as data
- `stats.json` — every number any document cites
- Figures: divergence choropleth for the latest complete year; divergence over time for
  the top states; pool composition stacked area for California vs national; sensitivity
  of the index to the weighting choice
- Documentation set matching CIDEX: README, CODEBOOK, LIMITATIONS, VERIFICATION_CHECKLIST,
  CITATION.cff, LICENCE

## 8. Venues

Dataset on Zenodo (CC BY 4.0). Data descriptor or short analysis paper. The interactive
map is a **later, separate** layer on this dataset, not part of v1.0.

## 9. Verification points

1. Reproduce the pipeline; `stats.json` matches
2. Confirm every specification value in §5 Step 2 against the standards
3. Rule on the composite weighting
4. Confirm the "estimates, not assays" framing is prominent enough to be unmissable
5. Spot-check California's pool shares against EIA's own published narrative

## 10. Licence

Data and docs CC BY 4.0; code MIT.
