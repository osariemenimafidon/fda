# Fuel Divergence Atlas — Limitations

> **DRAFT — NOT VERIFIED.** This package has not passed its verification gate. No value in it has been checked against the primary source by the author. Do not cite, deposit, or redistribute.

Version 1.0 · built 2026-09-15

## 1. These are estimates from specification envelopes, not fuel assays

**Nobody sampled a pump.** Every property in this dataset is inferred by combining
EIA consumption volumes with published specification ranges for each fuel component.
A real tank in a real state contains fuel whose actual properties may sit anywhere
inside — or outside — those ranges.

The dataset answers "given what was consumed, what does the specification imply the
pool looked like". It does not answer "what was the density of the fuel at this
station on this day". Any use that treats these as measurements is misuse.

## 2. The obvious way to compute blend share is wrong

EIA changed its distillate accounting at data year **2021**.
For 1960–2020, `DFACP` (distillate consumed
by transportation) and `DAACP` (distillate + biodiesel + renewable diesel) are identical
in every state and year. From 2021, EIA's technical notes state
distillate "includes all biodiesel and renewable diesel refinery and blender net inputs
volumes, but excludes biodiesel and renewable diesel product supplied consumption".

Consequently **`DFACP + BDACP + B1ACP` double-counts** from 2021
forward — nationally by about 20,008 thousand barrels a
year, roughly 1.726% — while being correct before. A pipeline
built that way manufactures a trend break at 2021 that looks like
a real change in fuel supply.

**This dataset uses `DAACP` as the denominator and never sums the three series.** The
pipeline detects the break from the data and aborts if it is not at
2021.

## 3. Density direction is robust; cetane direction is not

Over the **full** specification envelopes, each component's difference from petroleum
diesel is:

| Property | Component | Difference from petroleum | Sign |
|---|---|---|---|
| Density | FAME | +15 to +80 kg/m³ | **always heavier** |
| Density | HVO | -80 to -20 kg/m³ | **always lighter** |
| Cetane | FAME | -8 to +5 | **sign can flip** |
| Cetane | HVO | +15 to +29 | always higher |

Because the deviation equals `fame_share × (FAME − petroleum) + hvo_share × (HVO −
petroleum)`, a common-mode error in the petroleum reference cancels. So:

- **Density direction holds in 95.3% of state-years** whatever
  admissible property values are chosen. The *magnitude* remains uncertain.
- **Cetane direction holds in only 3.2% of state-years.** FAME's
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
(832.5 kg/m³, cetane 53.0). EPA's certification
fuel has its own specification which may sit elsewhere in that range. Shifting the
reference shifts every deviation by a constant; it does not change the spread between
states, which is the finding.

## 8. State of consumption, not state of use

EIA attributes consumption to the state of sale. Long-haul freight burns fuel across
state lines.

## Integrity checks

All pass in this build. They test internal consistency, **not** agreement with EIA.

- PASS — `no_negative_petroleum_share`
- PASS — `shares_sum_to_one`
- PASS — `pool_total_positive`
- PASS — `accounting_break_is_2021`
- PASS — `density_direction_mostly_robust`
- PASS — `cetane_robustness_disclosed`
- PASS — `every_row_has_sensitivity_band`
- PASS — `deviation_within_band`
