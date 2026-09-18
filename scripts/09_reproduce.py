"""09 - Independent reproduction check: clean clone, rebuild, diff.

The verification checklist used to ask the author to attest that they had run the
pipeline and that stats.json matched. That is a mechanical claim, and testimony
is the wrong instrument for it: a person who runs four commands once produces a
weaker guarantee than a check that runs the whole pipeline in a fresh clone and
diffs the result, every time anyone asks.

So this script does it. It clones the repository at HEAD into a temporary
directory, copies in the raw EIA files (which are deliberately not committed),
runs the pipeline end to end, and compares the regenerated stats.json against the
committed copy key by key. The verdict and any differences are written to
qa/09_reproduce.json.

What this does NOT establish: that the published values are correct, or that they
agree with EIA. It establishes that the shipped numbers come from the shipped
code and the logged inputs, which is the question the checklist was really asking.

Run:  python3 scripts/09_reproduce.py
"""
import json, os, shutil, subprocess, sys, tempfile
from datetime import datetime, timezone

REPO = os.path.abspath(".")
RAW = os.path.join(REPO, "data/raw")
COMMITTED = os.path.join(REPO, "data/processed/stats.json")
QA = os.path.join(REPO, "qa/09_reproduce.json")

# stats.json carries a build date, which is expected to differ between the
# committed copy and a rebuild on another day. Nothing else may.
EXPECTED_TO_DIFFER = {"build_date"}

STEPS = ["02_extract.py", "03_divergence.py", "04_qa.py"]


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def flatten(obj, prefix=""):
    """Compare nested structures leaf by leaf so a diff names the exact key."""
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flatten(v, f"{prefix}[{i}]"))
    else:
        out[prefix] = obj
    return out


def main():
    rep = {"checked_utc": datetime.now(timezone.utc).isoformat(),
           "repo_head": run(["git", "rev-parse", "HEAD"], REPO).stdout.strip()}

    if not os.path.exists(COMMITTED):
        raise SystemExit(f"no committed stats.json at {COMMITTED}")

    tmp = tempfile.mkdtemp(prefix="fda_reproduce_")
    clone = os.path.join(tmp, "fda")
    try:
        r = run(["git", "clone", "--quiet", "--no-local", REPO, clone], tmp)
        if r.returncode:
            raise SystemExit("clone failed:\n" + r.stderr[:500])
        rep["clone_head"] = run(["git", "rev-parse", "HEAD"], clone).stdout.strip()
        rep["clone_is_same_commit"] = rep["clone_head"] == rep["repo_head"]

        # The clone has no raw inputs by design; supply them and record which.
        os.makedirs(os.path.join(clone, "data/raw"), exist_ok=True)
        copied = []
        for fn in sorted(os.listdir(RAW)):
            if fn.startswith("."):
                continue
            shutil.copy2(os.path.join(RAW, fn), os.path.join(clone, "data/raw", fn))
            copied.append(fn)
        rep["raw_files_supplied"] = copied

        # A clone that still held processed outputs would let a stale file answer
        # for a rebuild. Remove them so every value has to be regenerated.
        proc = os.path.join(clone, "data/processed")
        if os.path.isdir(proc):
            shutil.rmtree(proc)
        os.makedirs(proc, exist_ok=True)

        rep["steps"] = []
        for step in STEPS:
            r = run([sys.executable, f"scripts/{step}"], clone)
            rep["steps"].append({"step": step, "returncode": r.returncode,
                                 "stderr_tail": r.stderr[-400:] if r.returncode else ""})
            if r.returncode:
                rep["verdict"] = "FAILED"
                rep["reason"] = f"{step} exited {r.returncode}"
                json.dump(rep, open(QA, "w"), indent=2)
                print(json.dumps(rep, indent=2)[:1500])
                raise SystemExit(f"{step} failed in the clean clone")

        rebuilt_path = os.path.join(clone, "data/processed/stats.json")
        if not os.path.exists(rebuilt_path):
            rep["verdict"] = "FAILED"
            rep["reason"] = "the rebuild produced no stats.json"
            json.dump(rep, open(QA, "w"), indent=2)
            raise SystemExit(rep["reason"])

        a = flatten(json.load(open(COMMITTED)))
        b = flatten(json.load(open(rebuilt_path)))

        diffs = []
        for k in sorted(set(a) | set(b)):
            if k.split(".")[0] in EXPECTED_TO_DIFFER:
                continue
            if a.get(k, "<absent>") != b.get(k, "<absent>"):
                diffs.append({"key": k, "committed": a.get(k, "<absent>"),
                              "rebuilt": b.get(k, "<absent>")})

        rep["keys_compared"] = len([k for k in set(a) | set(b)
                                    if k.split(".")[0] not in EXPECTED_TO_DIFFER])
        rep["keys_ignored"] = sorted(EXPECTED_TO_DIFFER)
        rep["differences"] = diffs
        rep["verdict"] = "REPRODUCED" if not diffs else "DIFFERS"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    os.makedirs(os.path.dirname(QA), exist_ok=True)
    json.dump(rep, open(QA, "w"), indent=2)

    print(f"verdict:        {rep['verdict']}")
    print(f"repo HEAD:      {rep['repo_head'][:12]}")
    print(f"raw supplied:   {', '.join(rep['raw_files_supplied'])}")
    print(f"keys compared:  {rep['keys_compared']} (ignoring {', '.join(rep['keys_ignored'])})")
    if rep["differences"]:
        print("differences:")
        for d in rep["differences"][:20]:
            print(f"  {d['key']}: committed={d['committed']!r} rebuilt={d['rebuilt']!r}")
    print(f"written: {QA}")
    if rep["verdict"] != "REPRODUCED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
