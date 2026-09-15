"""01 — Hash and log the raw EIA files.

eia.gov is unreachable from the build environment (organisation egress policy),
so raw files are placed in data/raw/ by hand. Provenance is recorded from the
bytes on disk: a rebuilder verifies the hash, not our word.
"""
import hashlib, json, os, datetime

RAW, LOG = "data/raw", "logs/provenance.jsonl"
SOURCES = {
    "use_all_phy.csv": {
        "url": "https://www.eia.gov/state/seds/sep_use/total/csv/use_all_phy.csv",
        "publisher": "US EIA, State Energy Data System",
        "what": "State consumption by energy source, physical units, 1960-2024",
    },
    "Codes_and_Descriptions.xlsx": {
        "url": "https://www.eia.gov/state/seds/CDF/Codes_and_Descriptions.xlsx",
        "publisher": "US EIA, State Energy Data System",
        "what": "MSN series code dictionary with units",
    },
}


def sha256(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for b in iter(lambda: fh.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def main():
    os.makedirs("logs", exist_ok=True)
    recs = []
    for fn, meta in SOURCES.items():
        p = os.path.join(RAW, fn)
        if not os.path.exists(p):
            raise SystemExit(f"MISSING: {p}\nDownload from:\n  {meta['url']}")
        st = os.stat(p)
        r = {"recorded_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
             "file": fn, "bytes": st.st_size, "sha256": sha256(p), **meta}
        recs.append(r)
        print(f"{fn}\n  {r['bytes']:,} bytes  sha256={r['sha256'][:16]}…")
    with open(LOG, "a") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    print(f"\nlogged {len(recs)} files")


if __name__ == "__main__":
    main()
