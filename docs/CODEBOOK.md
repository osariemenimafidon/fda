# Fuel Divergence Atlas — Codebook


Version 1.0 · built 2026-09-18

Unit of analysis: **(state, year)**. 728 rows,
51 states plus a US total, 2011–2024.

## `fda_state_year.csv`

| Column | Description |
|---|---|
| `State` | USPS state code; `US` is the national total. |
| `year` | Calendar/model year. |
| `pool_total` | Total transportation diesel pool, EIA series `DAACP`. |
| `units` | Volume units for `pool_total` (thousand barrels). |
| `petroleum_share` | Petroleum share of pool = 1 − fame_share − hvo_share. |
| `fame_share` | FAME biodiesel share, `BDACP`/`DAACP`. |
| `hvo_share` | HVO renewable diesel share, `B1ACP`/`DAACP`. |
| `blend_density` | Volume-weighted blend density, kg/m³ at 15 °C. |
| `density_ref` | Reference density (petroleum specification midpoint). |
| `density_dev` | blend_density − density_ref. **Negative = lighter.** |
| `density_dev_norm` | density_dev divided by the petroleum specification width. |
| `density_dev_low` | Lowest deviation across the full specification envelopes. |
| `density_dev_high` | Highest deviation across the full specification envelopes. |
| `density_dev_band` | density_dev_high − density_dev_low. |
| `density_sign_robust` | True when the whole band sits one side of zero. |
| `cetane_dev_low` | Lowest cetane deviation the specifications permit. This is the reported cetane quantity: no cetane point estimate is published, because every candidate rests on an assumed typical range rather than a specification. |
| `cetane_dev_high` | Highest cetane deviation across envelopes. |
| `cetane_dev_band` | Band width. |
| `cetane_sign_robust` | True when the band excludes zero. Only 4.7% of rows. |
| `density_breakdown_fame_kg_m3` | Breakdown point. The FAME density above which the sign of this row's density deviation would no longer be robust, holding HVO and petroleum at the admissible values least favourable to the conclusion. Empty where undefined (no FAME or no HVO). Compare against the assumed FAME density of 880 kg/m3: a threshold far above it means the conclusion does not depend on the FAME assumption. |
| `direction` | `lighter`, `heavier`, or `at_reference`, from the sign of density_dev. |

## `fda_components.csv`

The property envelope table, shipped as data so every assumption is inspectable:
component, specification source, property, min, max, midpoint, note, and a
`verified_by_author` flag that is `False` until the gate is signed.

## `fda_pool.csv`

Raw extracted volumes before any property modelling — `pool_total`, `fame_volume`,
`hvo_volume` per state-year, with `in_usable_window`.
