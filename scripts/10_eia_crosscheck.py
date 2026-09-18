"""10 - Cross-check the published shares against values read from EIA directly.

The integrity checks in 04 establish internal consistency. They cannot establish
agreement with EIA, and the verification checklist used to close that gap by
asking the author to look up two figures by hand and attest to them.

This script closes it with evidence instead. qa/eia_capture_<date>.json holds
values read straight from EIA's published CSV, with the URL, HTTP status, byte
count and capture date recorded. This script recomputes the pool shares from
those captured values and compares them against what the pipeline published.

Why a captured file rather than a live fetch: eia.gov is refused by this
environment's egress proxy at CONNECT, before TLS. The capture was therefore made
in a browser on the author's own machine. That is a weaker guarantee than a live
fetch would be and is recorded as such; the byte count is included so the capture
can be tied to a specific version of EIA's file.

Run:  python3 scripts/10_eia_crosscheck.py
"""
import csv, glob, json, os

OUT, QA = "data/processed", "qa"
TOL = 0.001            # shares agree to a tenth of a percentage point

caps = sorted(glob.glob(f"{QA}/eia_capture_*.json"))
if not caps:
    raise SystemExit("no EIA capture file in qa/; nothing to cross-check against")
cap = json.load(open(caps[-1]))
year = str(cap["year"])

rows = {(r["State"], r["year"]): r
        for r in csv.DictReader(open(f"{OUT}/fda_state_year.csv"))}

rep = {"capture_file": os.path.basename(caps[-1]),
       "captured_utc": cap["captured_utc"],
       "source_url": cap["source_url"],
       "source_bytes": cap["bytes"],
       "year": cap["year"], "tolerance": TOL, "comparisons": []}

for state, v in cap["values"].items():
    key = (state, year)
    if key not in rows:
        rep["comparisons"].append({"state": state, "status": "not in panel"})
        continue
    pub = rows[key]
    total = float(v["DAACP"])
    eia = {"fame_share": v["BDACP"] / total,
           "hvo_share": v["B1ACP"] / total}
    eia["petroleum_share"] = 1.0 - eia["fame_share"] - eia["hvo_share"]
    cmp_ = {"state": state}
    worst = 0.0
    for k, expected in eia.items():
        got = float(pub[k])
        cmp_[k] = {"eia_derived": round(expected, 5), "published": round(got, 5),
                   "abs_diff": round(abs(got - expected), 6)}
        worst = max(worst, abs(got - expected))
    cmp_["max_abs_diff"] = round(worst, 6)
    cmp_["status"] = "agrees" if worst <= TOL else "DISAGREES"
    rep["comparisons"].append(cmp_)

# The accounting break, re-derived from the captured values rather than asserted:
# after 2021 the naive sum of the three series exceeds the combined total.
us = cap["values"].get("US")
if us:
    naive = us["DFACP"] + us["BDACP"] + us["B1ACP"]
    rep["accounting_break_witness"] = {
        "year": cap["year"],
        "combined_total_DAACP": us["DAACP"],
        "naive_sum_DFACP_plus_BDACP_plus_B1ACP": naive,
        "overcount": naive - us["DAACP"],
        "overcount_pct": round((naive - us["DAACP"]) / us["DAACP"] * 100, 3),
        "note": "A pipeline summing the three series would inflate the national "
                "pool by this much in this year. DAACP is used instead."}
    rep["renewable_diesel_california_share_of_us"] = round(
        cap["values"]["CA"]["B1ACP"] / us["B1ACP"] * 100, 1)

rep["verdict"] = ("AGREES" if all(c.get("status") == "agrees"
                                  for c in rep["comparisons"]) else "DISAGREES")

json.dump(rep, open(f"{QA}/10_eia_crosscheck.json", "w"), indent=2)

print(f"verdict: {rep['verdict']}   (source {rep['source_bytes']:,} bytes, "
      f"captured {rep['captured_utc'][:10]})")
for c in rep["comparisons"]:
    if "max_abs_diff" in c:
        print(f"  {c['state']}: {c['status']}, worst share difference "
              f"{c['max_abs_diff']:.6f}")
        for k in ("petroleum_share", "fame_share", "hvo_share"):
            d = c[k]
            print(f"      {k:16} EIA {d['eia_derived']:.4f}  published {d['published']:.4f}")
if "accounting_break_witness" in rep:
    w = rep["accounting_break_witness"]
    print(f"  accounting break witnessed in {w['year']}: naive sum overcounts by "
          f"{w['overcount']:,} ({w['overcount_pct']}%)")
    print(f"  renewable diesel: {rep['renewable_diesel_california_share_of_us']}% "
          "of US transportation volume is Californian")
print(f"written: {QA}/10_eia_crosscheck.json")
if rep["verdict"] != "AGREES":
    raise SystemExit(1)
