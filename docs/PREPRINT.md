% How far has the diesel pool moved from the certification fuel? A state-level specification-based atlas for the United States, 2011–2024
% Osariemen Imafidon
% 2026-09-18

Independent Researcher. ORCID [0009-0006-3069-4674](https://orcid.org/0009-0006-3069-4674).
Correspondence: odimafid@gmail.com.

**Preprint.** Not peer reviewed. Part of the
[FACET](https://osariemenimafidon.github.io/facet/) research program.

> **DRAFT — NOT VERIFIED.** This manuscript has not passed its verification gate. No value in it has been checked against the primary source by the author. It must not be cited, deposited or submitted.

---

## Abstract

Compression-ignition engines sold in the United States are certified on a test fuel fixed by
40 CFR 1065.703. The fuel they subsequently burn is whatever the market supplies, and the
market has changed: fatty acid methyl ester biodiesel and hydrotreated renewable diesel now
account for a growing share of transportation distillate, and that share is distributed
across states extremely unevenly.

No federal programme publishes measurements of in-service diesel properties. This paper
therefore asks a question that public data can answer: **given what each state consumed, what
do the governing fuel specifications imply about how far its diesel pool sits from the
certification fuel?**

We combine Energy Information Administration state-level consumption volumes for
2011–2024 (728 state-years, 51
jurisdictions) with published specification envelopes for the three pool components, and
propagate the full envelopes rather than only their midpoints, so every estimate carries an
interval that reflects what the specifications actually permit.

The headline results are asymmetric, and the asymmetry is the contribution. For states
blending hydrotreated renewable diesel, the **direction** of divergence is established for
any admissible property values: HVO's density envelope (765–800 kg/m³)
lies entirely below the certification fuel's
(838.9–864.6 kg/m³), and its cetane specification sets a minimum of
70 with no maximum stated, against the certification
fuel's maximum of 50, so it lies wholly above the
certification range on that property too. California's 2024 pool
is **54.6% non-petroleum** —
51% renewable diesel — and sits **34
kg/m³ lighter** than the certification fuel, with a sensitivity interval of
[-50.8, -17.4] that excludes zero.

For states blending only FAME biodiesel, **the direction is not established**. FAME's density
and cetane envelopes both overlap the certification fuel's, so the sign of the deviation
depends on where inside its permitted range the actual fuel sits. Across the panel, the
density deviation is sign-robust in only **2.7%** of state-years
and the cetane deviation in **4.7%** — essentially the
HVO-blending states alone. Midpoint estimates do show biodiesel states heavier, and that may
be true; the specifications do not establish it and this paper does not claim it.

We also document a methodological trap in the source data. EIA changed its distillate
accounting at data year 2021; the intuitive blend-share
construction double-counts from that year forward while being correct before, inflating the
national denominator by about 20,008 thousand
barrels a year (1.726%) and manufacturing a trend break that looks
like a change in the fuel supply. The pipeline detects the break from the data and aborts if
it is not where it is expected.

Every state-year carries its sensitivity interval and two sign-robustness flags, so the
distinction between what this dataset establishes and what it merely suggests is carried by
the data rather than by a limitations section.

**Keywords:** diesel fuel; renewable diesel; biodiesel; engine certification; fuel
specifications; EIA SEDS; uncertainty propagation; open government data

---


## 1 Introduction

### 1.1 The question and why public data can answer only part of it

A compression-ignition engine is certified once, on a test fuel fixed by 40 CFR 1065.703,
and then operated for thousands of hours on fuel drawn from the market. A companion study in
the same research program establishes that the in-market fuel requirement leaves most
injection-relevant fuel properties unconstrained, and that the federal government publishes
measurements of none of them.

That result creates an evidentiary problem rather than solving one. If nobody measures
in-service fuel properties, how far the fuel has actually moved is not a question public data
can answer directly.

It can, however, answer a narrower question. Consumption volumes by component are published;
specification envelopes for each component are published. Combining them yields not a
measurement but an implication: *given what was consumed, what do the specifications imply
the pool looked like?* That is the question this paper answers, and the distinction between
it and a measurement is maintained throughout, because the value of the exercise depends
entirely on not blurring it.

### 1.2 Why the state is the unit

Blending is not uniform across the United States. Renewable diesel adoption is concentrated
where low-carbon fuel policy rewards it; biodiesel blending is concentrated where feedstock
and state mandates favour it; much of the country blends little of either. A national average
therefore describes no actual fuel pool.

The state is the finest geography at which consumption by component is published, and it is
also the geography at which the relevant policies operate. It is a compromise — fuel is
not consumed where it is sold, and a state is not a market — but it is the finest
compromise the public record supports.

### 1.3 Propagating specifications rather than midpoints

The methodological core of this paper is the decision to carry whole envelopes rather than
midpoints.

A specification is a permitted range, not a value. Treating FAME's density as 880 kg/m³
because that is the midpoint of 860–900 kg/m³ produces a point estimate
with no indication that the permitted range overlaps the certification fuel's, and therefore
no indication that the *sign* of the computed deviation is an artefact of the midpoint choice.

Carrying the envelopes makes the difference visible. For HVO the interval excludes zero and
the direction is established. For FAME it does not and the direction is not. Both results are
reported, and the second is reported as prominently as the first, because a paper that
reported only the robust half would leave a reader believing something the data does not
support.

### 1.4 Contributions

1. A state-year panel of estimated diesel pool composition and properties for
   51 jurisdictions over 14 years
   (728 rows), with every property estimate carrying a sensitivity interval
   propagated from the full specification envelopes.
2. An explicit **sign-robustness** determination per state-year and per property, separating
   what the specifications establish from what the midpoints merely suggest.
3. A correction to the reference fuel: divergence is measured against the EPA certification
   fuel rather than a European automotive standard. Section 3.2 records what changed when
   this was corrected, because it changed the headline.
4. Documentation and detection of the EIA 2021 distillate accounting
   break, which the intuitive construction gets wrong in a way that produces a plausible and
   false trend.
5. A reproducible, openly licensed pipeline in which every number in this manuscript is
   interpolated from a machine-written statistics file.

### 1.5 What this paper does not claim

It does not report measurements. Nobody sampled a pump. Any use of these values as assay
results is misuse, and the point is made again in Section 6 because it is the failure mode
most likely to occur.

It does not claim that a divergent pool produces divergent emissions. That would require
in-service emissions data, which do not exist publicly, and an engine model, which this is
not.

It does not claim a direction for FAME-blending states. The specifications do not determine
one.

---

## 2 Data

### 2.1 Source

The Energy Information Administration's State Energy Data System publishes state-level
consumption in physical units by fuel and sector. Three series matter here: distillate
consumed by the transportation sector, biodiesel, and renewable diesel, each identified by an
MSN code.

The panel covers 2011–2024, 51 jurisdictions and
728 state-years, in units of thousand barrels. Source files are not redistributed;
they are downloaded by the pipeline and identified in the provenance log by URL, retrieval
date, byte count and SHA-256 digest.

### 2.2 The 2021 accounting break

This deserves its own section because it is the single defect most likely to be reproduced by
anyone attempting this analysis independently.

For 1960–2020, the transportation distillate
series and the combined distillate-plus-renewables series are **identical in every state and
year**. From 2021, EIA's technical notes state that distillate
includes biodiesel and renewable diesel refinery and blender net inputs but excludes their
product-supplied consumption.

The consequence is that the intuitive construction — summing the distillate series with
the two renewable series to obtain a pool total — is correct before
2021 and double-counts after it. Nationally the overcount averages
about 20,008 thousand barrels a year, or
1.726% of the pool. It is small enough to be plausible and
structured enough to create a step at exactly the year the accounting changed, which a reader
would naturally interpret as a change in the fuel supply.

This pipeline uses the combined series as the denominator and never sums the three. The break
is **detected from the data** rather than assumed: the pipeline locates the first year in
which the two series diverge and aborts if it is not 2021. An
integrity check records the result on every build.

### 2.3 Component property envelopes

Each pool component carries a density and a cetane envelope taken from its governing
specification. These are the paper's central assumptions and are published as data rather
than buried in code.

Table 1. Component property envelopes. The **specification** column is what the governing
standard guarantees, with `min.` meaning the standard states no maximum. The **assumed
typical** range and the point estimate derived from it are assumptions of this study, not
specification bounds; only the specification column enters the sensitivity analysis.

| Component | Property | Specification | Assumed typical | Point est. | Source |
|:--------------------------|:---------|:--------------------|:-----------|-------:|:-----------------|
| Petroleum diesel (certification envelope) | density | 838.9-864.6 kg/m³ | 838.9–864.6 | 851.75 | 40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975 |
| Petroleum diesel (certification envelope) | cetane | 40-50 cetane number | 40–50 | 45 | 40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975 |
| FAME biodiesel (B100) | density | 860-900 kg/m³ | 860–900 | 880 | ASTM D6751 / EN 14214 |
| FAME biodiesel (B100) | cetane | min. 47 cetane number | 47–56 | 51.5 | ASTM D6751 / EN 14214 |
| HVO renewable diesel | density | 765-800 kg/m³ | 765–800 | 782.5 | EN 15940 (paraffinic diesel) |
| HVO renewable diesel | cetane | min. 70 cetane number | 70–90 | 80 | EN 15940 (paraffinic diesel) |

The petroleum row is the reference, and its provenance matters: the density envelope is
derived from the API gravity range that 40 CFR 1065.703 specifies, not from a commercial
diesel standard. ASTM D975 sets no density limit at all, so it cannot serve as a reference
even though it is the standard most United States diesel is produced to.

---


## 3 Method

### 3.1 Pool composition and blend properties

For each state-year, the pool is decomposed into petroleum distillate, FAME and HVO shares
summing to one, and each property is estimated by volume-weighted linear blending:

$$
x_{\mathrm{pool}} = s_{p} x_{p} + s_{f} x_{f} + s_{h} x_{h}
$$

where $s$ denotes volume share and $x$ the property value of each component. The deviation
from the reference is then

$$
\Delta x = x_{\mathrm{pool}} - x_{p}
         = s_{f}\left(x_{f} - x_{p}\right) + s_{h}\left(x_{h} - x_{p}\right)
$$

The second form is the one that matters, and it is worth dwelling on. The deviation depends on
the component *differences* from petroleum, not on the absolute property values. A common-mode
error in the petroleum reference — choosing the wrong point inside its envelope —
cancels. This is why the sensitivity analysis in Section 3.3 is computed on the differences
rather than on the levels, and it is a correction from an earlier version of this pipeline
that computed the band on the absolute value and therefore reported an interval far wider than
the analysis actually warranted.

Density blends close to linearly by volume, so the density estimate is reasonable within its
stated limits. **Cetane does not blend linearly.** The cetane column is a volume-weighted
approximation and is reported as indicative only; it is a further reason not to lean on the
cetane result, and it is stated here rather than only in the limitations.

### 3.2 The reference fuel, and what changed when it was corrected

Divergence is measured against the petroleum component's specification midpoint,
851.75 kg/m³ and cetane 45.0, derived from
40 CFR 1065.703.

An earlier version of this pipeline used EN 590, the European automotive diesel standard, as
the certification-fuel proxy. EN 590 sits roughly 19 kg/m³ lighter than the fuel EPA
actually certifies United States engines on. Correcting the reference moved the density
sign-robustness result from robust in the large majority of state-years to robust in
2.7% of them, because the corrected reference envelope overlaps
FAME's while the European one did not.

We report this because it is the paper's most consequential judgement call and because the
error was of a specific and instructive kind: the wrong reference was not implausible, it was
merely not the one the question was about, and it produced a stronger headline. A result that
strengthens when an assumption is chosen carelessly is the result most in need of the
correction being recorded in public.

### 3.3 Sensitivity: propagating envelopes, not midpoints

For each component and property, the difference from the petroleum reference is evaluated over
the **full** admissible range of both, giving an interval rather than a point.

Table 2. Component differences from the certification fuel over full specification envelopes.

| Property | Component | Difference from certification fuel | Sign |
|:---------|:----------|:-----------------------------------|:-----|
| Density | FAME | -4.6 to +61.1 | **straddles zero** |
| Density | HVO | -99.6 to -38.9 | excludes zero |
| Cetane | FAME | -3.0 or more, no upper bound | **straddles zero** |
| Cetane | HVO | +20.0 or more, no upper bound | excludes zero |

The consequence is the paper's central asymmetry. HVO's density difference is negative across
the entire admissible space and its cetane difference positive across it, so for a state
blending renewable diesel the direction holds for any admissible property values and only the
magnitude is uncertain. FAME's intervals straddle zero in both properties, so for a state
blending only biodiesel the direction is genuinely undetermined by the specifications.

Each state-year's deviation interval is computed by evaluating the deviation expression at the
combination of component values that minimises it and the combination that maximises it. A
state-year is flagged **sign-robust** when that interval excludes zero.

For density, both component specifications are two-sided, so every interval is bounded and
the median band width is 2.02 kg/m³. The bands are narrow in absolute
terms precisely because most states blend little, and narrow bands around small deviations
are still bands that contain zero.

For cetane the situation is different and the difference is the point. Neither EN 15940 nor
EN 14214 nor ASTM D6751 states a cetane maximum, so the upper side of the deviation interval
is **unbounded** for any state blending either component:
98.6% of state-years have no finite upper bound on their cetane
deviation. We carry that as unbounded rather than closing it with a number no standard
supports. The asymmetry is consequential but limited: an unbounded upper side cannot make a
sign robust, and cannot break one either, so a direction established by the lower bound
survives while the magnitude does not.

An earlier version of this pipeline carried cetane maxima of 80 for HVO and 56 for FAME.
Neither is a specification value. Closing the intervals that way understated the uncertainty
on every cetane result, and it is recorded here because it is the same class of error as the
accounting trap in Section 2.2: an assumption that looks like a measurement. No reported
density estimate changed when it was corrected, because density was never affected; the
cetane point estimates did change, because HVO's assumed typical range now matches the basis
its own source note states.

### 3.4 Breakdown points, in place of an assumed FAME density

One assumption in Table 1 is weaker than the rest, and it is weak in a way that matters for
a United States result. ASTM D6751, the standard the domestic biodiesel supply is actually
produced to, sets **no density limit at all**. FAME's density bound therefore rests on
EN 14214, a European standard that does not govern the fuel being described. Asserting it
and propagating it would put that standard on the critical path of every conclusion.

We remove it from that path by reporting a **breakdown point** instead: rather than assume
FAME's density, we compute how far wrong the assumption would have to be before a
conclusion changed. Because the deviation decomposes by component,

$$
\Delta\rho = s_{f}\left(\rho_{f} - \rho_{p}\right)
            + s_{h}\left(\rho_{h} - \rho_{p}\right)
$$

the sign of a "lighter" conclusion survives, with HVO and petroleum held at the admissible
values least favourable to it, unless

$$
\rho_{f} > \rho_{p,\min}
  - \frac{s_{h}\left(\rho_{h,\max} - \rho_{p,\min}\right)}{s_{f}}
$$

That threshold is published for every state-year in which both components are present
(39 rows), and a reader can judge it against what a fatty
acid methyl ester can physically be without consulting EN 14214 at all.

The result is asymmetric across the window, and the asymmetry is informative. In
2024 the tightest threshold is
**917 kg/m³**
(US), far above both the assumed FAME density of
880 kg/m³ and any real methyl ester, so the latest
cross-section's directions do not depend on the assumption. Across the whole panel the
tightest is 839 kg/m³
(OR, 2017), which
is *below* the assumed density: in the early years, when renewable diesel volumes were small
relative to biodiesel, the conclusion does rest on EN 14214.
18 of 39
defined rows are in that position. This is the same fact the
2.7% panel-wide sign-robustness figure reports, seen from the
other side, and reporting it both ways is deliberate.

A breakdown point is a stronger object than a sensitivity interval for a reader who does not
share the author's assumptions. An interval says what follows *given* an envelope; a
breakdown point says how much the envelope would have to be wrong to matter. Where a
specification is unavailable, paywalled, or simply not applicable to the fuel in question,
the second is the honest form.

An earlier version of this paper also reported a `divergence_index`: the euclidean magnitude
of the normalised density and cetane deviations. It is retired. Half of it came from the
cetane point estimate withdrawn in Section 4.3, so the index admitted an assumption into a
headline number while presenting itself as a summary of the data.

### 3.5 Integrity checks

15 checks run on every build. All pass.

Table 3. Integrity checks.

| Check | Result |
|:--------------------------------------|:-------|
| `no_negative_petroleum_share` | pass |
| `shares_sum_to_one` | pass |
| `pool_total_positive` | pass |
| `accounting_break_is_2021` | pass |
| `sign_robustness_computed` | pass |
| `robustness_reported_in_stats` | pass |
| `component_deltas_reported` | pass |
| `every_row_has_sensitivity_band` | pass |
| `deviation_within_band` | pass |
| `one_sided_spec_has_no_upper_bound` | pass |
| `unbounded_spec_yields_unbounded_band` | pass |
| `provenance_hashes_match` | pass |
| `no_cetane_point_estimate_published` | pass |
| `no_divergence_index_published` | pass |
| `breakdown_point_reported_where_defined` | pass |

These test internal consistency — that shares sum to one, that no share is negative, that
the accounting break is where it is expected, that every row carries a sensitivity band and
that every reported deviation lies inside its own band. They do **not** test agreement with
EIA, which is what the verification gate is for.

Note what the checks deliberately do not include. An earlier version asserted that density
direction was robust in more than ninety per cent of state-years, which made the pipeline's
integrity check a test of the conclusion rather than of the data. It has been replaced by
checks that the robustness determination was computed and reported, which is a property of the
pipeline rather than of the answer.

---


## 4 Results

### 4.1 The national picture

Table 4. Estimated non-petroleum share of the United States transportation distillate pool.

| Year | Non-petroleum share |
|-----:|--------------------:|
| 2011 | 2.16% |
| 2012 | 2.32% |
| 2013 | 3.96% |
| 2014 | 3.76% |
| 2015 | 4.01% |
| 2016 | 5.45% |
| 2017 | 5.25% |
| 2018 | 4.71% |
| 2019 | 5.18% |
| 2020 | 5.83% |
| 2021 | 5.91% |
| 2022 | 6.71% |
| 2023 | 9.56% |
| 2024 | 11.28% |

The share rises over the panel, from
2.16% in 2011 to
11.28% in 2024. The national figure
is reported for context only; as Section 1.2 argues, it describes no actual fuel pool.

### 4.2 The state distribution in 2024

In the latest year, 3 states have a pool estimated lighter than the
certification fuel, 40 heavier, and 8 at the reference
because they blend essentially nothing. The spread between the lightest and heaviest state is
**38.3 kg/m³**.

That spread is the finding that does not depend on the reference point. Shifting the reference
moves every state's deviation by a constant and leaves the spread unchanged, so a reader who
disputes the choice of reference in Section 3.2 can still use the spread.

Table 5. The five state pools with the lowest estimated density deviation, 2024. States
blending essentially nothing sit at the reference by construction and appear here with a
deviation of zero.

| State | Petrol. | FAME | HVO | Blend density | Deviation | Sensitivity interval | Cetane, at least | FAME breakdown |
|:------|--------:|-----:|----:|------------:|--------:|:-----------------|---------------:|---------------:|
| CA | 45.4% | 3.8% | 50.8% | 817.6 | -34.1 | [-50.8, -17.4] | +10.0 | 1,360 |
| OR | 63.7% | 9.4% | 27.0% | 835.7 | -16.0 | [-27.3, -4.8] | +5.1 | 951 |
| WA | 78.8% | 2.7% | 18.5% | 839.7 | -12.1 | [-18.6, -5.5] | +3.6 | 1,104 |
| AK | 100.0% | 0.0% | 0.0% | 851.8 | +0.0 | [+0.0, +0.0] | +0.0 | — |
| MT | 100.0% | 0.0% | 0.0% | 851.8 | +0.0 | [-0.0, +0.0] | -0.0 | — |

Table 6. The five state pools with the highest estimated density deviation, 2024.

| State | Petrol. | FAME | HVO | Blend density | Deviation | Sensitivity interval | Cetane, at least | FAME breakdown |
|:------|--------:|-----:|----:|------------:|--------:|:-----------------|---------------:|---------------:|
| MN | 85.0% | 15.0% | 0.0% | 856.0 | +4.2 | [-0.7, +9.2] | -0.5 | — |
| IA | 89.6% | 10.4% | 0.0% | 854.7 | +3.0 | [-0.5, +6.4] | -0.3 | — |
| IL | 92.4% | 7.6% | 0.0% | 853.9 | +2.1 | [-0.3, +4.7] | -0.2 | — |
| HI | 95.2% | 4.8% | 0.0% | 853.1 | +1.4 | [-0.2, +2.9] | -0.1 | — |
| DC | 96.5% | 3.5% | 0.0% | 852.8 | +1.0 | [-0.2, +2.2] | -0.1 | — |

### 4.3 The established result: renewable-diesel states

California is the clearest case and the only one in the panel where the pool is majority
non-petroleum. Its 2024 pool is **54.6% non-petroleum**, of
which **50.8%** is renewable diesel and **3.8%**
biodiesel. The estimated blend density is **817.6 kg/m³**, a
deviation of **-34.1 kg/m³** with a sensitivity interval of
**[-50.8, -17.4]**. The interval excludes zero,
so the direction is established for any admissible property values.

On cetane we report a bound rather than an estimate. Given only what the standards
guarantee, California's pool exceeds the certification fuel's reference cetane by **at least
+10.0** — that is, it sits at or above
55 against a certification envelope of
40–50. The bound is specification-derived and needs no assumption
about what a typical renewable diesel contains; it is also unaffected by the non-linearity
of cetane blending, because a bound does not depend on the blending law the way a
volume-weighted average does. An earlier version published a point estimate here. It has
been withdrawn: every candidate value rested on an assumed typical cetane range rather than
on any specification, and a number nobody can defend from a source adds no information to a
result already established by its bound.

So this is a state whose fuel lies outside the certification specification on two properties
at once — lighter than the whole density envelope, and above the whole cetane
envelope — and both halves of that claim rest on specifications rather than
assumptions.

OR, WA follow the same pattern at smaller renewable shares
and with correspondingly smaller deviations, and their intervals likewise exclude zero.

### 4.4 The unestablished result: biodiesel states

The states furthest above the reference in Table 6 are FAME blenders, and every one of them
has a sensitivity interval that **contains zero**. The largest, MN, has a
midpoint deviation of +4.23 kg/m³ with an interval of
[-0.69, +9.16]; the estimate says
the pool differs from the certification fuel, and does not say in which direction.

This is not a weakness in the data but a property of the specifications. FAME's permitted
density range (860–900 kg/m³) overlaps the certification fuel's
(838.9–864.6 kg/m³), so a biodiesel batch at the bottom of its range
blended into petroleum at the top of its range moves the pool in the opposite direction from a
batch at the top blended into petroleum at the bottom. No amount of consumption data resolves
that; only a measurement would.

Across the whole panel the density deviation is sign-robust in
**2.7%** of state-years and the cetane deviation in
**4.7%**. Those figures are low, and they are the honest figures.
They say that this method establishes a direction only where one component's envelope is
disjoint from the reference's, which is to say only for renewable diesel.

---


## 5 Discussion

### 5.1 What an established direction is worth

For the renewable-diesel states, this paper establishes a directional claim that does not
depend on any choice inside the specification envelopes: the pool is lighter and
higher-cetane than the fuel the engines burning it were certified on. That is a weaker claim
than a measurement and a stronger one than an estimate, and the distinction is worth naming
because it is the kind of claim that specification-based analysis is actually good for.

What it supports is a prioritisation argument. If in-service fuel properties are going to be
measured — and the companion study's finding that nobody measures them is the reason they
should be — the states where the specifications already imply a divergence are where the
first measurements would be most informative.

What it does not support is any statement about emissions. The path from a lighter,
higher-cetane fuel to an emissions difference runs through injection, combustion phasing and
aftertreatment behaviour, and this paper models none of them.

### 5.2 Why the unestablished half matters as much

It would have been easy to report only the California result. The FAME finding is negative,
awkward, and makes the paper's headline smaller.

It is also the more transferable result. It says that specification-based inference can
establish a direction only when one component's envelope is disjoint from the reference's,
and that when envelopes overlap, consumption data cannot substitute for measurement no matter
how much of it there is. That is a general limit on this method, and any future work using
the approach inherits it.

The midpoint estimates for FAME states are not worthless — a midpoint is the expected
value under a uniform prior, and refinery practice may well concentrate real fuels near the
middle of their ranges. But that is an assumption about the fuel supply, not a consequence of
the specifications, and this paper does not make it.

### 5.3 The spread is the robust national finding

Beyond individual states, the panel's most durable result is the spread: a range of
38.3 kg/m³ between the lightest and heaviest estimated state pool in
2024. It is robust to the reference choice, because shifting the reference shifts every
state by the same constant.

A single national certification fuel is a reasonable construct if the fuel supply is
homogeneous. The spread is the quantity that speaks to whether it is, and the national
non-petroleum share rose from 2.16% to
11.28% over the panel while remaining
concentrated in a small number of states. Whether the spread itself is widening is a question
this panel can answer year by year, and we report the 2024 cross-section rather than a trend
because the earlier years' component shares rest on smaller volumes and the sensitivity bands
scale with them.

### 5.4 Relationship to the companion study

The companion specification-divergence register asks what the regulation guarantees; this
paper asks what the market appears to have supplied. They are complementary and neither
substitutes for the other.

The register establishes that density is constrained at certification and not in the market.
This paper estimates that the unconstrained property has in fact moved, by different amounts
in different states. Together they describe a gap that is both legally open and, on the
public evidence, being used — while leaving the question of consequence untouched,
because neither has access to a measurement.

---

## 6 Limitations

These are the paper's binding constraints, not caveats appended to a finished result.

**These are estimates from specification envelopes, not fuel assays.** Nobody sampled a pump.
Every property here is inferred by combining consumption volumes with published specification
ranges. A real tank in a real state contains fuel whose actual properties may sit anywhere
inside, or outside, those ranges. The dataset answers "given what was consumed, what do the
specifications imply"; it does not answer "what was the density of the fuel at this station on
this day". Any use that treats these values as measurements is misuse.

**Component property values are assumptions.** Table 1 is the paper. Every deviation scales
with those envelopes, and they are the author's first verification item.

**Cetane does not blend linearly.** The cetane column is indicative only.

**Transportation sector only.** The analysis uses the transportation consumption series, so
off-road, marine, rail, heating and industrial distillate are excluded. Many of the engines in
the companion certification panel are nonroad, so the fuel pool those engines actually see is
not exactly this one. This is a real mismatch between the two studies and is stated rather
than minimised.

**State of sale, not state of use.** Consumption is attributed to the state of sale;
long-haul freight burns fuel across state lines, so a state's estimated pool is not the fuel
in the tanks of vehicles operating there.

**The reference point is a choice.** Section 3.2 records what changed when it was corrected
once already. The spread in Section 5.3 is the statistic that survives a different choice.

**No in-service emissions claim is supported.** The paper stops at fuel properties.

---

## 7 Reproducibility and verification status

The pipeline is a sequence of numbered scripts. Provenance is logged at every fetch with a
SHA-256 digest. Every number in this manuscript is interpolated from the machine-written
statistics file; none is typed by hand.

**This package has not passed its verification gate.** The verification checklist requires the author to confirm each component property envelope against its governing specification, to reproduce the pipeline from the source files, and to rule on the reference-fuel choice in Section 3.2. Until that attestation exists, the publication gate refuses to remove the draft stamp, and this manuscript must not be cited, deposited or submitted. It is circulated in draft form so that the method can be criticised before the values are relied upon.

---

## Data availability

Processed tables are in the repository under `data/`. The source files are published by the
Energy Information Administration and are not redistributed; the pipeline downloads them and
records URL, retrieval date, byte count and SHA-256 digest in the provenance log. Component
specification envelopes are published as data in `fda_components.csv` with the governing
specification cited on each row.

## Code availability

The complete pipeline is openly licensed and available in the project repository, including
the generator that produced this manuscript.

## Competing interests

The author declares no competing interests.

## Funding

This work received no external funding.

## Use of AI assistance

Pipeline code, table generation and manuscript drafting were produced with AI assistance. The
component property envelopes, the reference-fuel determination and the interpretation of the
results are the author's, and the author is responsible for the content.

## References

1. US Energy Information Administration. *State Energy Data System (SEDS): consumption in
   physical units.*
2. US Energy Information Administration. *State Energy Data System technical notes:
   distillate fuel oil.*
3. United States Code of Federal Regulations, Title 40, Part 1065, Section 1065.703 —
   Distillate diesel fuel.
4. ASTM D975, Standard Specification for Diesel Fuel. ASTM International.
5. ASTM D6751, Standard Specification for Biodiesel Fuel Blend Stock (B100) for Middle
   Distillate Fuels. ASTM International.
6. EN 14214, Liquid petroleum products — Fatty acid methyl esters (FAME) for use in
   diesel engines and heating applications. European Committee for Standardization.
7. EN 15940, Automotive fuels — Paraffinic diesel fuel from synthesis or hydrotreatment.
   European Committee for Standardization.
8. EN 590, Automotive fuels — Diesel — Requirements and test methods. European
   Committee for Standardization.
9. Imafidon, O. *What the fuel regulation guarantees an engine designer: a specification
   divergence register for United States compression-ignition certification.* FACET research
   program.
10. Imafidon, O. *A harmonized panel of United States compression-ignition engine
    certification data, with resolved certification lineage.* FACET research program.

---

## Appendix A: component envelopes with source notes

- **Petroleum diesel (certification envelope)**, density (kg/m³). Specification: 838.9-864.6 [40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975]. Two-sided. Derived from the regulation's API gravity range 32-37. ASTM D975 sets no density limit. Assumed typical range used for the point estimate: 838.9–864.6, midpoint 851.75. Same as the specification; no assumption added.
- **Petroleum diesel (certification envelope)**, cetane (cetane number). Specification: 40-50 [40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975]. Two-sided. 40 CFR 1065.703 cetane 40-50 by ASTM D613. ASTM D975 requires a minimum of 40. Assumed typical range used for the point estimate: 40–50, midpoint 45. Same as the specification; no assumption added.
- **FAME biodiesel (B100)**, density (kg/m³). Specification: 860-900 [ASTM D6751 / EN 14214]. Two-sided in EN 14214 (860-900). ASTM D6751 sets no density limit, so this bound rests on EN 14214 alone. (not yet confirmed against the standard by the author) Assumed typical range used for the point estimate: 860–900, midpoint 880. Same as the EN 14214 specification range.
- **FAME biodiesel (B100)**, cetane (cetane number). Specification: min. 47 [ASTM D6751 / EN 14214]. One-sided. ASTM D6751 minimum 47; EN 14214 minimum 51. Neither standard states a maximum. Assumed typical range used for the point estimate: 47–56, midpoint 51.5. ASSUMPTION of this study: 47-56 spans the cetane numbers commonly reported for the methyl esters in the US biodiesel supply. Not a specification bound.
- **HVO renewable diesel**, density (kg/m³). Specification: 765-800 [EN 15940 (paraffinic diesel)]. Two-sided. EN 15940 specified range. (not yet confirmed against the standard by the author) Assumed typical range used for the point estimate: 765–800, midpoint 782.5. Same as the EN 15940 specification range.
- **HVO renewable diesel**, cetane (cetane number). Specification: min. 70 [EN 15940 (paraffinic diesel)]. One-sided. EN 15940 class A minimum 70; no maximum stated. Assumed typical range used for the point estimate: 70–90, midpoint 80. ASSUMPTION of this study: 70-90 is the range commonly reported for hydrotreated renewable diesel. Not a specification bound.

## Appendix B: panel dimensions

- Years: 2011–2024 (14 years)
- Jurisdictions: 51
- State-years: 728
- Volume units: thousand barrels
- First non-zero year, FAME: 2001
- First non-zero year, HVO: 2011
- Accounting break detected at: 2021
- Identical-regime span: 1960–2020

---

*Preprint generated 2026-09-18. Every quantity is interpolated from the pipeline's own
statistics file; none is transcribed by hand.*
