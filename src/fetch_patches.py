"""Download public SWE-bench Verified leaderboard patches (patch.diff per instance) + resolved labels.

Source: entries listed in github.com/SWE-bench/experiments (evaluation/verified/*/metadata.yaml),
artifacts in the public bucket s3://swe-bench-submissions (anonymous HTTPS).
Output: data/patches/<submission>.jsonl with {instance_id, patch, resolved}.
"""
import json, sys, re, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "data/swebench_experiments/evaluation/verified"
OUT = ROOT / "data/patches"; OUT.mkdir(exist_ok=True)
IIDS = [json.loads(l)["instance_id"] for l in open(ROOT / "data/swebench_verified.jsonl")]

def get(url):
    for _ in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404): return None
        except Exception:
            pass
    return None

def resolved_set(d: Path):
    p = d / "per_instance_details.json"
    if p.exists():
        j = json.load(open(p)); return {k for k, v in j.items() if v.get("resolved")}
    p = d / "results/results.json"
    if p.exists():
        return set(json.load(open(p)).get("resolved", []))
    return None

def run(sub):
    d = EXP / sub
    out = OUT / f"{sub}.jsonl"
    if out.exists(): return sub, "exists"
    meta = (d / "metadata.yaml").read_text()
    m = re.search(r"logs:\s*s3://swe-bench-submissions/(\S+)", meta)
    res = resolved_set(d)
    if not m or res is None: return sub, "no s3 logs or results"
    base = "https://swe-bench-submissions.s3.amazonaws.com/" + m.group(1).rstrip("/")
    def one(iid):
        return iid, get(f"{base}/{iid}/patch.diff")
    with ThreadPoolExecutor(32) as ex:
        rows = list(ex.map(one, IIDS))
    n = sum(1 for _, p in rows if p)
    if n < 100: return sub, f"only {n} patches"
    with open(out, "w") as f:
        for iid, p in rows:
            f.write(json.dumps({"instance_id": iid, "patch": p, "resolved": iid in res}) + "\n")
    return sub, f"{n} patches, {len(res)} resolved"

if __name__ == "__main__":
    subs = sys.argv[1:] or sorted(p.name for p in EXP.iterdir() if p.is_dir())
    for s in subs:
        try: print(run(s), flush=True)
        except Exception as e: print(s, "ERR", repr(e)[:200], flush=True)
