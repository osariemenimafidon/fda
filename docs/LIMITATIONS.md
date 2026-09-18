# Fuel Divergence Atlas — Limitations


Version 1.0 · built 2026-09-18

## 1. These are estimates from specification envelopes, not fuel assays

**Nobody sampled a pump.** Every property in this dataset is inferred by combining
EIA consumption volumes with published specification ranges for each fuel component.
A real tank in a real state contains fuel whose actual properties may sit anywhere
inside — or outside — those ranges.

The dataset answers "given what was consumed, what does the specification imply the
pool looked like". It does not answer "what was the density of the fuel at this
station on this day". Any use that treats these as measurements is misuse.

### 1b. It is also not the fuel the certified engines mostly burn

The second limit on scope is easier to miss than the first, and it bounds what this
dataset can say about the rest of the research program.

This analysis covers **transportation-sector** distillate, because that is the sector EIA
publishes by state. The engine population it is meant to speak to lives in CIDEX, and
CIDEX is **91.9% nonroad** (7,925 of 8,627 certified families). Off-road, marine,
rail, heating and industrial distillate are excluded from this pool entirely.

So the pool measured here and the engines certified there are, for the most part,
different populations. What this dataset establishes is a claim about **the market**: that
the diesel sold for transportation in some states has moved a long way from the
certification fuel. It does not establish what fuel any particular certified engine
burned, and it is not evidence that nonroad fuel has moved the same way — nonroad
distillate may differ in blending, in seasonality and in regional distribution, and none
of it is in these numbers.

Closing that gap needs off-road distillate consumption by state, which this analysis does
not use. Until then, a reader joining this dataset to CIDEX should treat the join as
suggestive of a market-wide direction rather than as a property of the certified fleet.

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
cease to be robust. In 2024 the tightest of those thresholds
is **917 kg/m³**
(US), against an assumed FAME density of
880 kg/m³ and a real-world figure near it. No fatty
acid methyl ester approaches those thresholds, so the latest cross-section's direction does
not depend on the assumption. A reader can check that without owning EN 14214.

**Earlier years are a different matter, and the breakdown point says so.** Renewable diesel
penetration grew across the window, so in early years the HVO term was small relative to the
FAME term and the threshold falls: the tightest across the whole panel is
839 kg/m³
(OR, 2017), which
is *below* the assumed FAME density. 18 of
39 defined rows sit below it. Those rows' directions do
depend on the assumption, and that is the same fact the
2.7% panel-wide sign-robustness figure reports from the other
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

The operational detail behind §1b: this analysis uses the `*ACP` series, consumption by the
transportation sector, which is the sector EIA publishes at state level. Off-road, marine,
rail, heating and industrial distillate are excluded. See §1b for what that means for
reading this dataset alongside CIDEX.

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
- PASS — `provenance_hashes_match`
- PASS — `no_cetane_point_estimate_published`
- PASS — `no_divergence_index_published`
- PASS — `breakdown_point_reported_where_defined`
