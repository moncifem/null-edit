import sys, json, hashlib, subprocess, bisect, re, os
import numpy as np
from unidiff import PatchSet
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
run=sys.argv[1]
inst={}
for l in open(f"{B}/data/swebench_verified.jsonl"):
    d=json.loads(l); inst[d["instance_id"]]=d
def is_test(p):
    parts=p.split("/"); b=parts[-1]
    return any(x in("test","tests","testing") for x in parts[:-1]) or b.startswith("test_") or b.endswith("_test.py") or b=="conftest.py" or b.startswith("tests")
def gold_orig(patch, path):
    """returns (removed set, list of (before, after) anchors) 1-based orig lines"""
    ps=PatchSet(patch); rem=set(); anchors=[]
    for pf in ps:
        sp=pf.source_file[2:] if pf.source_file.startswith("a/") else pf.source_file
        if sp!=path or pf.is_added_file: continue
        for h in pf:
            ptr=h.source_start; block_add=False; block_rem=False
            def close(ptr):
                if block_add and not block_rem: anchors.append((ptr-1,ptr))
            for ln in h:
                if ln.line_type==" ":
                    close(ptr); block_add=block_rem=False; ptr+=1
                elif ln.line_type=="-":
                    rem.add(ptr); block_rem=True; ptr+=1
                elif ln.line_type=="+":
                    block_add=True
            close(ptr)
    return rem, anchors
def assign(offsets, tgt):
    starts=[0]+[i+1 for i,c in enumerate(tgt) if c=="\n"]
    nl=len(tgt.split("\n"))
    out=np.empty(len(offsets),int)
    for t,(s,e) in enumerate(offsets):
        p=s
        for q in range(s,e):
            if tgt[q]!="\n": p=q;break
        p=min(p,len(tgt)-1) if tgt else 0
        out[t]=min(bisect.bisect_right(starts,p)-1,nl-1)
    return out,nl
rows=[json.loads(l) for l in open(f"{run}/log.jsonl")]
rows=[r for r in rows if "skip" not in r]
anom=[]; per=[]; rng=np.random.default_rng(0)
def rank_best(score, has, gold, rng):
    idx=np.where(has)[0]; tb=rng.permutation(len(idx))
    order=idx[np.lexsort((tb,-score[idx]))]
    pos={int(l):i+1 for i,l in enumerate(order)}
    return min(pos[g] for g in gold)
for r in rows:
    iid,path=r["iid"],r["path"]
    f=f"{run}/{iid}__{hashlib.md5(path.encode()).hexdigest()[:8]}.npz"
    if not os.path.exists(f): anom.append(f"missing npz {iid} {path}"); continue
    z=np.load(f); off=z["offsets"]; R=z["lp_R"].astype(float); RX=z["lp_RX"].astype(float)
    if path.endswith(".py")==False or is_test(path): anom.append(f"not eligible {iid} {path}"); continue
    d=inst[iid]
    pr=subprocess.run(["git","-C",f"{B}/data/repos/"+d["repo"].replace("/","_"),"show",f"{d['base_commit']}:{path}"],capture_output=True)
    if pr.returncode: anom.append(f"file not at base {iid} {path}"); continue
    txt=pr.stdout.decode("utf-8","replace"); tgt=txt if txt.endswith("\n") else txt+"\n"
    T=len(off)
    if T!=r["n_tok"] or len(R)!=T or len(RX)!=T: anom.append(f"n_tok mismatch {iid} {path}: log {r['n_tok']} off {T} R {len(R)} RX {len(RX)}")
    if not(np.isfinite(R).all() and np.isfinite(RX).all()): anom.append(f"NaN/inf {iid} {path}")
    if np.mean(R>-1e-3)>0.95 : anom.append(f"lp_R near zero for {np.mean(R>-1e-3):.2f} of tokens {iid} {path}")
    if (R>1e-6).any(): anom.append(f"lp_R positive {iid} {path}")
    if T and (off[0][0]!=0 or off[-1][1]!=len(tgt) or (off[1:,0]<off[:-1,1]).any() or (off[1:,0]!=off[:-1,1]).any()):
        anom.append(f"offsets not contiguous/covering {iid} {path}: first {off[0].tolist()} last {off[-1].tolist()} len {len(tgt)}")
    lineof,nl=assign(off,tgt)
    S=np.zeros(nl); H=np.zeros(nl); L=np.zeros(nl); has=np.zeros(nl,bool)
    np.add.at(S,lineof,-R); np.add.at(H,lineof,np.maximum(0,RX-R)); np.add.at(L,lineof,1); has[lineof]=True
    rem,anc=gold_orig(d["patch"],path)
    gold=set(x-1 for x in rem if 1<=x<=nl)
    for b,a in anc:
        if b>=1:
            i=b-1
            while i>=0 and not has[i]: i-=1
            if i>=0: gold.add(i)
        if a<=nl:
            i=a-1
            while i<nl and not has[i]: i+=1
            if i<nl: gold.add(i)
    gold={g for g in gold if has[g]}
    if not gold: anom.append(f"no gold with tokens {iid} {path}"); continue
    rnd=rng.random(nl)
    per.append(dict(iid=iid,path=path,n_lines=int(has.sum()),n_gold=len(gold),
        S=rank_best(S,has,gold,rng),H=rank_best(H,has,gold,rng),
        L=rank_best(L,has,gold,rng),Rnd=rank_best(rnd,has,gold,rng)))
def summ(k):
    v=np.array([p[k] for p in per]); return [len(v)]+[float((v<=x).mean()) for x in(1,5,10)]+[float(np.median(v))]
out=[f"# Run {run}: {len(rows)} scored rows, {len(per)} files evaluated\n","| score | files | hit@1 | hit@5 | hit@10 | median rank |","|---|---|---|---|---|---|"]
for k in "S H L Rnd".split(): s=summ(k); out.append(f"| {k} | {s[0]} | {s[1]:.3f} | {s[2]:.3f} | {s[3]:.3f} | {s[4]:g} |")
out.append("\n| iid | path | n_lines | n_gold | rank_S | rank_H | rank_len |\n|---|---|---|---|---|---|---|")
for p in per: out.append(f"| {p['iid']} | {p['path']} | {p['n_lines']} | {p['n_gold']} | {p['S']} | {p['H']} | {p['L']} |")
out.append("\nAnomalies:"); out+= ["- "+a for a in anom] or ["- none"]
print("\n".join(out))
