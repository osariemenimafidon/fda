"""Fuel component property envelopes and the certification-fuel reference.

EVERY VALUE HERE IS [VERIFY]. The whole dataset scales with them, so they are
isolated in one file: one place to check, one place to correct.

THE REFERENCE
-------------
Divergence is measured against the fuel engines are actually certified on, which
US regulation specifies: 40 CFR 1065.703, distillate diesel test fuel, ultra-low
sulfur Type 2-D grade.

  API gravity   32-37     (ASTM D4052)
  Cetane number 40-50     (ASTM D613)

API gravity converts to density as SG(60/60F) = 141.5 / (API + 131.5), and
density = SG x 999.016 kg/m3, giving 838.9-864.6 kg/m3.

An earlier draft of this project used the EN 590 range (820-845) as a proxy. That
was wrong: EN 590 is the European automotive diesel standard and sits about
19 kg/m3 lighter than the fuel EPA certifies US engines on. Substituting one for
the other moved the reference point enough to change which conclusions held.

THE PETROLEUM COMPONENT
-----------------------
The petroleum fraction of the in-service pool is assumed to share the
certification fuel's envelope. Both are ASTM D975 No. 2-D ultra-low-sulfur
distillate. [VERIFY] The consequence is deliberate: a state burning no biofuel
has exactly zero divergence, so every non-zero value in this dataset is
attributable to biofuel content and nothing else. Real market diesel may sit
elsewhere within D975, which sets no density limit at all; that is stated in
LIMITATIONS rather than modelled.
"""

def api_to_density(api):
    """API gravity to density in kg/m3 at 60 F."""
    return 141.5 / (api + 131.5) * 999.016


# 40 CFR 1065.703, Table 1 — ultra-low-sulfur Type 2-D certification test fuel
CERT_API_MIN, CERT_API_MAX = 32.0, 37.0
CERT_DENSITY_MIN = round(api_to_density(CERT_API_MAX), 1)   # 838.9 (higher API = lighter)
CERT_DENSITY_MAX = round(api_to_density(CERT_API_MIN), 1)   # 864.6
CERT_CETANE_MIN, CERT_CETANE_MAX = 40.0, 50.0

COMPONENTS = {
    "petroleum": {
        "label": "Petroleum diesel (certification envelope)",
        "spec": "40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975",
        "density_min": CERT_DENSITY_MIN, "density_max": CERT_DENSITY_MAX,
        "cetane_min": CERT_CETANE_MIN, "cetane_max": CERT_CETANE_MAX,
        "density_note": "Derived from the regulation's API gravity range 32-37. "
                        "ASTM D975 sets no density limit.",
        "cetane_note": "40 CFR 1065.703 cetane 40-50 by ASTM D613. "
                       "ASTM D975 requires a minimum of 40.",
    },
    "fame": {
        "label": "FAME biodiesel (B100)",
        "spec": "ASTM D6751 / EN 14214",
        "density_min": 860.0, "density_max": 900.0,
        "cetane_min": 47.0, "cetane_max": 56.0,
        "density_note": "EN 14214 range 860-900. ASTM D6751 sets no density limit.",
        "cetane_note": "ASTM D6751 minimum 47; EN 14214 minimum 51.",
    },
    "hvo": {
        "label": "HVO renewable diesel",
        "spec": "EN 15940 (paraffinic diesel)",
        "density_min": 765.0, "density_max": 800.0,
        "cetane_min": 70.0, "cetane_max": 80.0,
        "density_note": "EN 15940 specified range.",
        "cetane_note": "EN 15940 minimum 70; typical HVO 70-90.",
    },
}

REFERENCE = "petroleum"

# Temperature bases differ: the certification fuel's API gravity is at 60 F
# (15.56 C) while EN 14214 and EN 15940 specify density at 15 C. The offset is
# under 1 kg/m3, far inside the envelope widths, and is not corrected. [VERIFY]
TEMPERATURE_NOTE = ("Certification fuel density derived at 60 F; biofuel "
                    "specifications are at 15 C. Offset <1 kg/m3, not corrected.")


def midpoint(component, prop):
    c = COMPONENTS[component]
    return (c[f"{prop}_min"] + c[f"{prop}_max"]) / 2.0


def as_rows():
    rows = []
    for key, c in COMPONENTS.items():
        for prop in ("density", "cetane"):
            rows.append({
                "component": key, "label": c["label"], "spec": c["spec"],
                "property": prop,
                "units": "kg/m3" if prop == "density" else "cetane number",
                "min": c[f"{prop}_min"], "max": c[f"{prop}_max"],
                "midpoint": midpoint(key, prop),
                "note": c[f"{prop}_note"],
                "is_reference": key == REFERENCE,
                "verified_by_author": False,
            })
    return rows
