# Fuel Divergence Atlas — Verification Checklist


Author: Imafidon, Osariemen · ORCID 0009-0006-3069-4674

## How this checklist is organised

An attestation should carry **judgements**, not arithmetic. Anything a machine can check,
a machine checks, and the result is recorded as evidence in `qa/` where a reader can see
it. What remains for the author is the set of decisions only a person can make.

This is a change from an earlier version, which asked the author to attest that they had
run the pipeline, matched the hashes and confirmed each property value. Those are
mechanical claims, and testimony is a weaker instrument for them than a check that runs
every time anyone asks.

## Part 1 — Reproduction and provenance: checked mechanically, nothing to sign

- `scripts/09_reproduce.py` clones this repository at HEAD into a clean directory, supplies
  the raw EIA files, runs the pipeline end to end and diffs the regenerated `stats.json`
  against the committed copy, key by key. Verdict in `qa/09_reproduce.json`. This
  establishes that the shipped numbers come from the shipped code and the logged inputs.
- The integrity check `provenance_hashes_match` recomputes the SHA-256 of every raw input
  and compares it against `logs/provenance.jsonl`. Detail in `stats.json` under
  `provenance_verification`.
- All 15 integrity checks run on every build and are reported in
  `stats.json`.

Neither check establishes that the values are *correct*, or that they agree with EIA. They
establish reproducibility and provenance, which is what this part was really asking.

Headline figures a rebuild should reproduce:

| | |
|---|---|
| Spread across states, 2024 | 38.3 kg/m³ |
| States lighter / heavier / at reference | 3 / 40 / 8 |
| California non-petroleum share | 54.6% |
| Density direction sign-robust | 2.7% of state-years |
| Cetane direction sign-robust | 4.7% of state-years |

## Part 2 — The property values

Every number below is mine, not EIA's, and they live in `src/fda/properties.py`.

| Component | Specification | Density (spec) | Cetane (spec) | Cetane (assumed typical) |
|---|---|---|---|---|
| Petroleum diesel | 40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975 | 838.9-864.6 | 40-50 | 40–50 |
| FAME biodiesel | ASTM D6751 / EN 14214 | 860-900 | min. 47 | 47–56 |
| HVO renewable diesel | EN 15940 (paraffinic diesel) | 765-800 | min. 70 | 70–90 |

The **spec** columns are what the standard guarantees; `min.` means the standard states no
maximum. The **assumed typical** column is an assumption of this study, used only to form a
point estimate.

**This part used to be the load-bearing one. It is not any more.** Four of the six values
below are the same figures FUELDIV confirmed against the primary sources under its own
signed gate — the certification fuel's density and cetane envelopes from 40 CFR 1065.703,
and EN 15940's density range and cetane minimum. The fifth, FAME's density, has been taken
off the critical path by the breakdown point in LIMITATIONS §4. The sixth, the assumed
typical cetane ranges, no longer feeds any published number, because no cetane point
estimate is published.

- [ ] The four values carried over from FUELDIV are the ones I confirmed there:
      certification density 838.9-864.6 kg/m³, certification cetane
      40-50, EN 15940 density 765-800
      kg/m³, EN 15940 cetane min. 70
- [ ] I accept the breakdown-point treatment of FAME density: the
      2024 cross-section's direction holds unless FAME
      density exceeds 917 kg/m³, which it cannot,
      **and** 18 earlier rows do depend on the
      EN 14214 figure and are reported as such
- [ ] Set `verified_by_author` to True in `fda_components.csv`

Optional, and no longer blocking: confirm EN 14214's density range of
860-900 kg/m³ directly. It would tighten the early years; it changes
nothing in the latest cross-section.

## Part 3 — Agreement with EIA: checked mechanically, nothing to sign

`scripts/10_eia_crosscheck.py` recomputes the pool shares from values read directly out of
EIA's published CSV and compares them against what this pipeline published. The captured
values, with the source URL, HTTP status, byte count and capture date, are in
`qa/eia_capture_*.json`; the comparison is in `qa/10_eia_crosscheck.json`.

Result at the last run: **AGREES**, with a worst share difference of
0.000000 across
3 jurisdictions
(California, Minnesota and the national total) for 2024.

Two further things fall out of the same captured data rather than needing separate checks:

- **The accounting break is witnessed, not asserted.** In 2024 the naive sum of the
  three series exceeds the combined total by
  19,273 thousand barrels
  (1.662%). A pipeline built that way would
  inflate the national pool by that much; this one uses `DAACP`.
- **Renewable diesel really is overwhelmingly Californian.**
  88.8% of the national transportation volume is
  consumed in California, computed from the captured figures.

One caveat, recorded rather than smoothed over: eia.gov is refused by the build
environment's egress proxy, so the capture was made in a browser on the author's machine
rather than fetched by the pipeline. That is a weaker guarantee than a live fetch. The byte
count is recorded so the capture can be tied to a specific version of EIA's file, and
re-running the capture is the way to refresh it.

## Part 4 — Judgement calls

- [ ] **Reference point.** Using the midpoint of EPA's own certification fuel envelope
      (851.75 kg/m³, the centre of the API 32-37 range in
      40 CFR 1065.703) as the reference is defensible. I have read §7, and I accept that
      shifting the reference moves every state's deviation by a constant and leaves the
      38.3 kg/m³ spread between states unchanged.
- [ ] **Cetane.** I accept that the cetane direction is not robust
      (4.7% of rows) and that LIMITATIONS §3 and §5 say so
      plainly enough that no reader will quote a cetane direction for a FAME state.
- [ ] **Framing.** LIMITATIONS §1 makes it unmissable that these are specification-based
      estimates, not fuel assays.
- [ ] **Sector.** Transportation-sector-only coverage is stated, and its mismatch with
      CIDEX's nonroad engines is acknowledged.

## Part 5 — Before deposit

- [ ] The abstract reads in my own voice
- [ ] `scripts/09_reproduce.py` reports REPRODUCED
- [ ] `scripts/07_publish_gate.py` passes and no DRAFT stamp remains

## Sign-off

This attestation covers judgement, not arithmetic. The mechanical claims — that the
published numbers regenerate from the published code and the logged inputs, and that the
raw inputs match their recorded digests — are established by the checks in `qa/` rather
than by this signature, and a reader should verify them there rather than take my word.

What I attest to is this:

> I have read the limitations and the judgement calls recorded in this package, and I
> accept them. The certification-fuel and EN 15940 values carried over from FUELDIV are
> the ones I confirmed against their sources under that project's gate. I have read the
> results of the reproduction, provenance and EIA cross-checks, and the spot-checks against
> EIA's published tables agree with this dataset. I accept the breakdown-point treatment of
> FAME density, including that 18 early-year
> rows do depend on the EN 14214 figure and are reported as doing so. No number in this
> package is described as measured, and no direction is asserted that the specifications do
> not establish.

Signed: ____________________  Date: ____________
