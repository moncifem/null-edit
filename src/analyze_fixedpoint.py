"""E2 analysis: does residual null-edit hazard of the PATCHED file separate resolved from unresolved patches?

Within-instance pairwise AUROC (resolved vs unresolved candidates of the same task), instance-level
bootstrap CI, top-1 selection rate, baselines (diff size, consensus count, similarity to gold) and a
logistic regression with instance fixed effects removed (within-instance centring).
"""
import json, sys
import numpy as np

import argparse
from common import RESULTS
ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--keep-equals-gold", action="store_true")
args = ap.parse_args(); tag = args.tag
rows = [json.loads(l) for l in open(RESULTS / f"fixedpoint_{tag}" / "scores.jsonl")]
if not args.keep_equals_gold:  # candidates textually identical to the human fix are removed (they are trivially "resolved")
    for r in rows:
        r["cands"] = [c for c in r["cands"] if c["h"] in ("orig", "gold") or not c.get("equals_gold")]
# score definitions: higher = "more likely resolved"
def feats(c, orig):
    f = {
        "-S_total (residual hazard)": -c["S_total"],
        "S_orig - S_total (hazard removed by the patch)": orig["S_total"] - c["S_total"],
        "-S_top5 lines": -c["S_top5"],
        "-S_line_max": -c["S_line_max"],
        "-S per token": -c["S_total"] / c["n_tok"],
        "-S_changed (hazard on patched lines)": -c["S_changed"],
        "-S_unchanged": -c["S_unchanged"],
        "consensus (#submissions with same patch)": c["n_subs"],
        "-n_changed_lines (smaller diff)": -c["n_changed_lines"],
        "+n_changed_lines (larger diff)": c["n_changed_lines"],
        "similarity to gold (oracle covariate)": c["sim_gold"],
    }
    if "H_total" in c:
        f["-H_total (issue-specific residual)"] = -c["H_total"]
        f["-H_line_max"] = -c["H_line_max"]
        f["-(S - S_wrong) total"] = -(c["S_total"] - c["SX_total"])
    return f

per_inst = []
for r in rows:
    orig = next(c for c in r["cands"] if c["h"] == "orig")
    gold = next(c for c in r["cands"] if c["h"] == "gold")
    cs = [c for c in r["cands"] if c["h"] not in ("orig", "gold")]
    pos = [c for c in cs if c["resolved"]]
    neg = [c for c in cs if not c["resolved"]]
    if not pos or not neg:
        continue
    per_inst.append((r["iid"], orig, gold, pos, neg))
print(f"instances: {len(per_inst)}; candidates: {sum(len(p)+len(n) for _,_,_,p,n in per_inst)} "
      f"({sum(len(p) for _,_,_,p,n in per_inst)} resolved / {sum(len(n) for _,_,_,p,n in per_inst)} unresolved)")
names = list(feats(per_inst[0][3][0], per_inst[0][1]))
rng = np.random.default_rng(0)
print(f"\n{'score (higher = predicted resolved)':44s} {'pairwise AUROC [95% CI]':>26s} {'top-1 resolved %':>18s}")
exp_random = np.mean([len(p) / (len(p) + len(n)) for _, _, _, p, n in per_inst])
for name in names:
    aucs, top1 = [], []
    for iid, orig, gold, pos, neg in per_inst:
        sp = [feats(c, orig)[name] for c in pos]
        sn = [feats(c, orig)[name] for c in neg]
        a = np.mean([(x > y) + 0.5 * (x == y) for x in sp for y in sn])
        aucs.append(a)
        allc = [(s, 1) for s in sp] + [(s, 0) for s in sn]
        m = max(s for s, _ in allc)
        top1.append(np.mean([l for s, l in allc if s == m]))
    aucs, top1 = np.array(aucs), np.array(top1)
    idx = rng.integers(0, len(aucs), (5000, len(aucs)))
    bs = aucs[idx].mean(1)
    print(f"{name:44s} {aucs.mean():.3f} [{np.percentile(bs,2.5):.3f}, {np.percentile(bs,97.5):.3f}] {100*top1.mean():14.1f}")
print(f"{'random pick (expected)':44s} {'0.500':>26s} {100*exp_random:14.1f}")
# descriptive: orig vs gold vs resolved vs unresolved
def m(xs): return float(np.mean(xs))
print("\nmean S_total: original %.2f | gold-patched %.2f | resolved cands %.2f | unresolved cands %.2f" % (
    m([o["S_total"] for _, o, _, _, _ in per_inst]), m([g["S_total"] for _, _, g, _, _ in per_inst]),
    m([np.mean([c["S_total"] for c in p]) for _, _, _, p, _ in per_inst]), m([np.mean([c["S_total"] for c in n]) for _, _, _, _, n in per_inst])))
print("fraction of instances where gold-patched file has lower S_total than original: %.3f" % m([g["S_total"] < o["S_total"] for _, o, g, _, _ in per_inst]))
print("mean P(no edit)=exp(-S): original %.4f | gold-patched %.4f" % (m([np.exp(-o["S_total"]) for _, o, _, _, _ in per_inst]), m([np.exp(-g["S_total"]) for _, _, g, _, _ in per_inst])))

# --- does residual hazard add anything beyond similarity to the (possibly memorised) human fix and diff size? ---
# within-instance centred logistic regression; instance-level bootstrap on the coefficient of -S_total
from sklearn.linear_model import LogisticRegression
X, y, g = [], [], []
for gi, (iid, orig, gold, pos, neg) in enumerate(per_inst):
    cs = [(c, 1) for c in pos] + [(c, 0) for c in neg]
    A = np.array([[-c["S_total"], c["sim_gold"], -c["n_changed_lines"]] for c, _ in cs], float)
    X.append(A - A.mean(0)); y += [l for _, l in cs]; g += [gi] * len(cs)
X, y, g = np.vstack(X), np.array(y), np.array(g)
X = X / (X.std(0) + 1e-9)
def fit(idx):
    return LogisticRegression(C=10.0, max_iter=500).fit(X[idx], y[idx]).coef_[0]
coef = fit(np.arange(len(y)))
bs = []
for _ in range(1000):
    pick = rng.integers(0, len(per_inst), len(per_inst))
    idx = np.concatenate([np.where(g == i)[0] for i in pick])
    if len(set(y[idx])) == 2:
        bs.append(fit(idx))
bs = np.array(bs)
print("\nwithin-instance logistic regression (standardised coefficients, instance bootstrap 95% CI):")
for j, nm in enumerate(["-S_total (residual hazard)", "similarity to gold", "-n_changed_lines"]):
    print(f"  {nm:30s} {coef[j]:+.2f} [{np.percentile(bs[:, j], 2.5):+.2f}, {np.percentile(bs[:, j], 97.5):+.2f}]")
