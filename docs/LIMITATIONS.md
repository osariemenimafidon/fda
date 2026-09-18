# Fuel Divergence Atlas — Limitations

> **DRAFT — NOT VERIFIED.** This package has not passed its verification gate. No value in it has been checked against the primary source by the author. Do not cite, deposit, or redistribute.

Version 1.0 · built 2026-09-18

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

## 3. Only the HVO direction is established; the FAME direction is not

Over the **full** specification envelopes, each component's difference from petroleum
diesel is:

| Property | Component | Specification | Difference from certification fuel | Sign |
|---|---|---|---|---|
| Density | FAME | 860-900 | -5 to +61 kg/m³ | **not determined** |
| Density | HVO | 765-800 | -100 to -39 kg/m³ | always lighter |
| Cetane | FAME | min. 47 | -3 or more, no upper bound | **not determined** |
| Cetane | HVO | min. 70 | +20 or more, no upper bound | always higher |

Because the deviation equals `fame_share × (FAME − petroleum) + hvo_share × (HVO −
petroleum)`, a common-mode error in the petroleum reference cancels. So:

**HVO is robustly lighter and robustly higher-cetane than the certification fuel.** Both
its intervals exclude zero, so for states blending renewable diesel the direction of
divergence holds for any admissible property values.

**FAME's direction is not determined.** Its density envelope
(860-900) overlaps the certification fuel's
(838.9-864.6), and its cetane specification
(min. 47) is one-sided and runs through and above the
certification fuel's (40-50). Both intervals
straddle zero. For a state blending only biodiesel, **this dataset cannot say whether its
pool is heavier or lighter than the certification fuel**, only that it differs.

**One-sided specifications are carried as unbounded, not closed with a number.** Neither
EN 15940 nor EN 14214 nor ASTM D6751 states a cetane maximum, so the upper side of every
cetane deviation interval is unbounded: 98.6% of state-years
have no finite upper bound on their cetane deviation. An earlier version of this pipeline
carried invented cetane ceilings of 80 and 56, which closed those intervals and understated
the uncertainty on every cetane result. The density result is unaffected, because both
density specifications are genuinely two-sided.

Consequently density direction is sign-robust in just
2.7% of state-years and cetane direction in
4.7% - essentially only the HVO-blending states. The midpoint
estimates do show biodiesel states heavier, and that may well be true, but the
specifications do not establish it and this dataset does not claim it.

An earlier draft of this project reported density direction as robust in 95.3% of
state-years. That figure came from using EN 590 - the European automotive diesel
standard - as the certification-fuel proxy. EN 590 sits about 19 kg/m3 lighter than the
fuel EPA actually certifies US engines on. Correcting the reference to 40 CFR 1065.703
moved the result from "robust" to "not established" for every FAME-blending state.

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
(851.75 kg/m³, cetane 45.0). EPA's certification
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
- PASS — `sign_robustness_computed`
- PASS — `robustness_reported_in_stats`
- PASS — `component_deltas_reported`
- PASS — `every_row_has_sensitivity_band`
- PASS — `deviation_within_band`
- PASS — `one_sided_spec_has_no_upper_bound`
- PASS — `unbounded_spec_yields_unbounded_band`
