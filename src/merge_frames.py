"""Merge teacher-forcing frames scored in separate runs into one result directory.

Usage: python merge_frames.py <out_tag> <tag_a> <tag_b> [...]
Keeps only files present in every input tag; log.jsonl is taken from the first tag.
"""
from __future__ import annotations

import json
import sys

import numpy as np

from common import RESULTS

out, tags = sys.argv[1], sys.argv[2:]
dirs = [RESULTS / f"conflict_{t}" for t in tags]
od = RESULTS / f"conflict_{out}"
od.mkdir(exist_ok=True)
names = set.intersection(*[{p.name for p in d.glob("*.npz")} for d in dirs])
for n in sorted(names):
    zs = [np.load(d / n) for d in dirs]
    assert all(np.array_equal(zs[0]["offsets"], z["offsets"]) for z in zs[1:]), n
    arrs = {}
    for z in zs:
        arrs.update({k: z[k] for k in z.files})
    np.savez_compressed(od / n, **arrs)
stems = {n[:-4] for n in names}
from run_conflict import key  # noqa: E402

with open(od / "log.jsonl", "w") as f:
    for l in open(dirs[0] / "log.jsonl"):
        r = json.loads(l)
        if "skip" in r or key(r["iid"], r["path"]) in stems:
            f.write(l)
print(f"merged {len(names)} files from {tags} into {od}")
