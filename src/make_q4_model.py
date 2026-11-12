"""Build a PyTorch checkpoint that carries the *exact* 4-bit weights of an MLX-quantized Gemma 4.

Purpose: the MAC arm (MLX, 4-bit) and the DGX arm (PyTorch, bf16) differ in both backend and
precision. This script de-quantizes the language-model weights of the MLX checkpoint
(affine, group size 64, 4 bits: w = q * scale + bias per group of 64 inputs) and writes them
into a copy of the official checkpoint, so the same quantized weights can be run through the
PyTorch scorer. Everything that MLX left unquantized (norms, scalars, vision/audio towers) is
kept from the official weights.

Usage: python make_q4_model.py <official_dir> <mlx_4bit_dir> <out_dir>
"""
from __future__ import annotations

import glob
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
from safetensors.torch import load_file, save_file

off_dir, mlx_dir, out_dir = map(Path, sys.argv[1:4])
out_dir.mkdir(parents=True, exist_ok=True)
qc = json.load(open(mlx_dir / "config.json"))["quantization"]
bits, gs = qc["bits"], qc["group_size"]
assert qc.get("mode", "affine") == "affine" and 32 % bits == 0

mlx = {}
for f in sorted(glob.glob(str(mlx_dir / "*.safetensors"))):
    mlx.update(load_file(f))
per = 32 // bits
shifts = (np.arange(per, dtype=np.uint32) * bits)[None, None, :]


def dequant(base: str) -> torch.Tensor:
    q = mlx[base + ".weight"].numpy().astype(np.uint32)  # [out, in*bits/32]
    s = mlx[base + ".scales"].float().numpy()  # [out, in/gs]
    b = mlx[base + ".biases"].float().numpy()
    vals = ((q[:, :, None] >> shifts) & ((1 << bits) - 1)).reshape(q.shape[0], -1).astype(np.float32)
    w = vals.reshape(q.shape[0], -1, gs) * s[:, :, None] + b[:, :, None]
    return torch.from_numpy(w.reshape(q.shape[0], -1))


bases = [k[: -len(".scales")] for k in mlx if k.endswith(".scales") and k.startswith("language_model.model.")]
todo = {"model.language_model." + b[len("language_model.model."):] + ".weight": b for b in bases}
print(f"{len(todo)} quantized language-model matrices, {bits} bits, group {gs}")
done, errs = 0, []
for f in sorted(glob.glob(str(off_dir / "*.safetensors"))):
    sd = load_file(f)
    for k in list(sd):
        if k in todo:
            w = dequant(todo[k])
            assert tuple(w.shape) == tuple(sd[k].shape), (k, w.shape, sd[k].shape)
            ref = sd[k].float()
            errs.append(float((w - ref).norm() / ref.norm()))
            sd[k] = w.to(torch.bfloat16)
            done += 1
    save_file(sd, str(out_dir / Path(f).name), metadata={"format": "pt"})
    del sd
assert done == len(todo), (done, len(todo))
errs = np.array(errs)
print(f"replaced {done} matrices; relative Frobenius error vs official bf16: "
      f"median {np.median(errs):.4f}, min {errs.min():.4f}, max {errs.max():.4f}")
for f in off_dir.iterdir():
    if f.is_file() and f.suffix != ".safetensors":
        shutil.copy(f, out_dir / f.name)
json.dump({"source_official": str(off_dir), "source_mlx": str(mlx_dir), "bits": bits, "group_size": gs,
           "n_replaced": done, "rel_err_median": float(np.median(errs)), "rel_err_max": float(errs.max())},
          open(out_dir / "q4_provenance.json", "w"), indent=1)
