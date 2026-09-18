"""Fuel component property envelopes and the certification-fuel reference.

Every value here is the author's, not EIA's, and they are isolated in one file:
one place to check, one place to correct. Their status at the time of signing is
recorded per value in the notes below and in .gate-signed.

TWO DIFFERENT KINDS OF NUMBER
-----------------------------
An earlier version of this file kept one range per component per property, named
`*_min` / `*_max`, and used it for two incompatible purposes: the point estimate
and the sensitivity interval. That conflation produced a real defect. EN 15940
specifies a cetane *minimum* of 70 and no maximum; EN 14214 and ASTM D6751
specify cetane minima of 51 and 47 and no maximum. The file nonetheless carried
maxima of 80 and 56, which no standard sets. Those invented ceilings closed the
sensitivity interval and so understated the uncertainty on every cetane result.

The two kinds of number are now separate and named for what they are.

  SPEC      What the governing standard actually guarantees. `None` on either
            side means the standard states no limit in that direction. This is
            the only thing the sensitivity analysis may use, because it is the
            only thing a fuel meeting the standard is obliged to satisfy.

  TYPICAL   An assumed range for fuels of that type, used only to form a point
            estimate. It is an assumption of this study, not a specification,
            and every document that reports a point estimate must say so.

Nothing may read SPEC where it means TYPICAL or the reverse; the accessors below
are the only way in, and there are no combined `*_min` / `*_max` keys left to
reach for by mistake.

THE REFERENCE
-------------
Divergence is measured against the fuel engines are actually certified on, which
US regulation specifies: 40 CFR 1065.703, distillate diesel test fuel, ultra-low
sulfur Type 2-D grade.

  API gravity   32-37     (ASTM D4052)
  Cetane number 40-50     (ASTM D613)

API gravity converts to density as SG(60/60F) = 141.5 / (API + 131.5), and
density = SG x 999.016 kg/m3, giving 838.9-864.6 kg/m3. Both of the reference's
envelopes are two-sided, because a test fuel specification reproduces a fuel
rather than merely bounding it.

An earlier draft of this project used the EN 590 range (820-845) as a proxy. That
was wrong: EN 590 is the European automotive diesel standard and sits about
19 kg/m3 lighter than the fuel EPA certifies US engines on. Substituting one for
the other moved the reference point enough to change which conclusions held.

THE PETROLEUM COMPONENT
-----------------------
The petroleum fraction of the in-service pool is assumed to share the
certification fuel's envelope. Both are ASTM D975 No. 2-D ultra-low-sulfur
distillate. The consequence is deliberate: a state burning no biofuel
has exactly zero divergence, so every non-zero value in this dataset is
attributable to biofuel content and nothing else. Real market diesel may sit
elsewhere within D975, which sets no density limit at all; that is stated in
LIMITATIONS rather than modelled.
"""
import math


def api_to_density(api):
    """API gravity to density in kg/m3 at 60 F."""
    return 141.5 / (api + 131.5) * 999.016


# 40 CFR 1065.703, Table 1 - ultra-low-sulfur Type 2-D certification test fuel
CERT_API_MIN, CERT_API_MAX = 32.0, 37.0
CERT_DENSITY_MIN = round(api_to_density(CERT_API_MAX), 1)   # 838.9 (higher API = lighter)
CERT_DENSITY_MAX = round(api_to_density(CERT_API_MIN), 1)   # 864.6
CERT_CETANE_MIN, CERT_CETANE_MAX = 40.0, 50.0

COMPONENTS = {
    "petroleum": {
        "label": "Petroleum diesel (certification envelope)",
        "spec": "40 CFR 1065.703 Type 2-D ULSD test fuel; ASTM D975",
        # spec and typical coincide: the regulation states a two-sided band.
        "density_spec": (CERT_DENSITY_MIN, CERT_DENSITY_MAX),
        "density_typical": (CERT_DENSITY_MIN, CERT_DENSITY_MAX),
        "cetane_spec": (CERT_CETANE_MIN, CERT_CETANE_MAX),
        "cetane_typical": (CERT_CETANE_MIN, CERT_CETANE_MAX),
        "density_note": "Two-sided. Derived from the regulation's API gravity range "
                        "32-37. ASTM D975 sets no density limit.",
        "cetane_note": "Two-sided. 40 CFR 1065.703 cetane 40-50 by ASTM D613. "
                       "ASTM D975 requires a minimum of 40.",
        "density_typical_basis": "Same as the specification; no assumption added.",
        "cetane_typical_basis": "Same as the specification; no assumption added.",
    },
    "fame": {
        "label": "FAME biodiesel (B100)",
        "spec": "ASTM D6751 / EN 14214",
        "density_spec": (860.0, 900.0),
        "density_typical": (860.0, 900.0),
        # No standard sets a cetane maximum for B100. The lower bound is the
        # looser of the two applicable minima, because a fuel meeting D6751 need
        # not meet EN 14214.
        "cetane_spec": (47.0, None),
        "cetane_typical": (47.0, 56.0),
        "density_note": "Two-sided in EN 14214 (860-900). ASTM D6751 sets no density "
                        "limit, so this bound rests on EN 14214 alone. Taken off the critical path by "
                        "the breakdown point rather than confirmed directly; see LIMITATIONS 4.",
        "cetane_note": "One-sided. ASTM D6751 minimum 47; EN 14214 minimum 51. "
                       "Neither standard states a maximum.",
        "density_typical_basis": "Same as the EN 14214 specification range.",
        "cetane_typical_basis": "ASSUMPTION of this study: 47-56 spans the cetane "
                                "numbers commonly reported for the methyl esters in "
                                "the US biodiesel supply. Not a specification bound.",
    },
    "hvo": {
        "label": "HVO renewable diesel",
        "spec": "EN 15940 (paraffinic diesel)",
        "density_spec": (765.0, 800.0),
        "density_typical": (765.0, 800.0),
        # EN 15940 class A states a cetane minimum of 70 and no maximum.
        "cetane_spec": (70.0, None),
        "cetane_typical": (70.0, 90.0),
        "density_note": "Two-sided. EN 15940 specified range, confirmed against the "
                        "standard under FUELDIV's signed verification gate.",
        "cetane_note": "One-sided. EN 15940 class A minimum 70; no maximum stated.",
        "density_typical_basis": "Same as the EN 15940 specification range.",
        "cetane_typical_basis": "ASSUMPTION of this study: 70-90 is the range commonly "
                                "reported for hydrotreated renewable diesel. Not a "
                                "specification bound.",
    },
}

REFERENCE = "petroleum"

# Temperature bases differ: the certification fuel's API gravity is at 60 F
# (15.56 C) while EN 14214 and EN 15940 specify density at 15 C. The offset is
# under 1 kg/m3, far inside the envelope widths, and is not corrected. Ruled on
# by the author at signing: accepted as immaterial at this resolution.
TEMPERATURE_NOTE = ("Certification fuel density derived at 60 F; biofuel "
                    "specifications are at 15 C. Offset <1 kg/m3, not corrected.")


# ------------------------------------------------------------------ accessors
def spec(component, prop):
    """The standard's own bounds. Either element may be None, meaning the
    standard states no limit in that direction. Sensitivity analysis uses this
    and nothing else."""
    return COMPONENTS[component][f"{prop}_spec"]


def spec_inf(component, prop):
    """`spec` with None replaced by an infinity, for arithmetic."""
    lo, hi = spec(component, prop)
    return (-math.inf if lo is None else lo,
            math.inf if hi is None else hi)


def typical(component, prop):
    """The assumed range used to form a point estimate. Always two-sided, and
    always an assumption of this study rather than a specification."""
    return COMPONENTS[component][f"{prop}_typical"]


def is_one_sided(component, prop):
    lo, hi = spec(component, prop)
    return lo is None or hi is None


def midpoint(component, prop):
    """Point-estimate value: the midpoint of the ASSUMED TYPICAL range."""
    lo, hi = typical(component, prop)
    return (lo + hi) / 2.0


def fmt_spec(component, prop):
    lo, hi = spec(component, prop)
    if lo is not None and hi is not None:
        return f"{lo:g}-{hi:g}"
    if lo is not None:
        return f"min. {lo:g}"
    if hi is not None:
        return f"max. {hi:g}"
    return "not specified"


def as_rows():
    rows = []
    for key, c in COMPONENTS.items():
        for prop in ("density", "cetane"):
            slo, shi = spec(key, prop)
            tlo, thi = typical(key, prop)
            rows.append({
                "component": key, "label": c["label"], "spec": c["spec"],
                "property": prop,
                "units": "kg/m3" if prop == "density" else "cetane number",
                "spec_min": slo,
                "spec_max": shi,
                "spec_one_sided": is_one_sided(key, prop),
                "spec_rendered": fmt_spec(key, prop),
                "typical_min": tlo,
                "typical_max": thi,
                "midpoint": midpoint(key, prop),
                "note": c[f"{prop}_note"],
                "typical_basis": c[f"{prop}_typical_basis"],
                "is_reference": key == REFERENCE,
                "verified_by_author": False,
            })
    return rows
