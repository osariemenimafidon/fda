# Fuel Divergence Atlas — Codebook

> **DRAFT — NOT VERIFIED.** This package has not passed its verification gate. No value in it has been checked against the primary source by the author. Do not cite, deposit, or redistribute.

Version 1.0 · built 2026-09-15

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
| `blend_cetane` | Volume-weighted blend cetane. **Indicative only — see LIMITATIONS §5.** |
| `cetane_ref` | Reference cetane (petroleum specification midpoint). |
| `cetane_dev` | blend_cetane − cetane_ref. |
| `cetane_dev_norm` | Normalised by spec width. |
| `cetane_dev_low` | Lowest cetane deviation across envelopes. |
| `cetane_dev_high` | Highest cetane deviation across envelopes. |
| `cetane_dev_band` | Band width. |
| `cetane_sign_robust` | True when the band excludes zero. Only 3.2% of rows. |
| `divergence_index` | Euclidean magnitude of the normalised (density, cetane) pair. Always ≥ 0; use the signed columns for direction. |
| `direction` | `lighter`, `heavier`, or `at_reference`, from the sign of density_dev. |

## `fda_components.csv`

The property envelope table, shipped as data so every assumption is inspectable:
component, specification source, property, min, max, midpoint, note, and a
`verified_by_author` flag that is `False` until the gate is signed.

## `fda_pool.csv`

Raw extracted volumes before any property modelling — `pool_total`, `fame_volume`,
`hvo_volume` per state-year, with `in_usable_window`.
