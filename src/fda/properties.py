"""Fuel component property envelopes.

EVERY VALUE IN THIS FILE IS [VERIFY]. The divergence index scales directly with
these numbers, so they are isolated here rather than scattered through the
pipeline: one file to check, one file to correct.

Sources are named per value. Midpoints are used for the blend calculation; the
range is carried so the pipeline can report sensitivity rather than implying a
precision the specifications do not support.
"""

COMPONENTS = {
    "petroleum": {
        "label": "Petroleum diesel",
        "spec": "EN 590 (temperate grade) / ASTM D975 No. 2-D",
        "density_min": 820.0, "density_max": 845.0,          # kg/m3 @ 15 C
        "cetane_min": 51.0,   "cetane_max": 55.0,            # EN 590 floor is 51
        "density_note": "EN 590 temperate range. ASTM D975 sets no density limit.",
        "cetane_note": "EN 590 minimum 51; ASTM D975 minimum 40. Upper bound is typical, not a limit.",
    },
    "fame": {
        "label": "FAME biodiesel (B100)",
        "spec": "ASTM D6751 / EN 14214",
        "density_min": 860.0, "density_max": 900.0,
        "cetane_min": 47.0,   "cetane_max": 56.0,
        "density_note": "EN 14214 range 860-900. ASTM D6751 does not specify density.",
        "cetane_note": "ASTM D6751 minimum 47; EN 14214 minimum 51.",
    },
    "hvo": {
        "label": "HVO renewable diesel",
        "spec": "EN 15940 (paraffinic)",
        "density_min": 765.0, "density_max": 800.0,
        "cetane_min": 70.0,   "cetane_max": 80.0,
        "density_note": "EN 15940 specified range.",
        "cetane_note": "EN 15940 minimum 70. Typical HVO is 70-90.",
    },
}

# The reference point divergence is measured against: the fuel an engine is
# certified on. [VERIFY] Choosing the petroleum midpoint is itself a judgement -
# EPA certification fuel has its own specification which may sit elsewhere in
# the range.
REFERENCE = "petroleum"


def midpoint(component, prop):
    c = COMPONENTS[component]
    return (c[f"{prop}_min"] + c[f"{prop}_max"]) / 2.0


def as_rows():
    """The property table as data, so it ships with the dataset."""
    rows = []
    for key, c in COMPONENTS.items():
        for prop in ("density", "cetane"):
            rows.append({
                "component": key, "label": c["label"], "spec": c["spec"],
                "property": prop,
                "units": "kg/m3 at 15 C" if prop == "density" else "cetane number",
                "min": c[f"{prop}_min"], "max": c[f"{prop}_max"],
                "midpoint": midpoint(key, prop),
                "note": c[f"{prop}_note"],
                "verified_by_author": False,
            })
    return rows
