"""Teacher-forced token scoring with a local Gemma 4 model (PyTorch / transformers, CUDA).

Same interface as scorer_mlx.Scorer. Full-precision (bf16) official checkpoints.
"""
from __future__ import annotations

import os
import time

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from scorer_common import Scored, line_scores  # noqa: F401


class Scorer:
    def __init__(self, model_path: str, chunk: int = 1024):
        self.hf = AutoTokenizer.from_pretrained(model_path)
        self.tok = self.hf
        # Hard cap on this process's GPU memory (the DGX Spark shares one 121 GB pool between CPU and GPU: without
        # a cap an oversized job stalls the whole machine instead of failing). Callers catch the OOM per file.
        frac = float(os.environ.get("SCORER_MEM_FRACTION", "0"))
        if frac:
            torch.cuda.set_per_process_memory_fraction(frac)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path, dtype=getattr(torch, os.environ.get("SCORER_DTYPE", "bfloat16")), device_map="cuda")
        self.model.eval()
        self.chunk = chunk
        self.model_path = model_path
        self.dev = next(self.model.parameters()).device
        self.throttle = float(os.environ.get("THROTTLE", "0"))
        eos = self.model.generation_config.eos_token_id
        self.eos = set(eos if isinstance(eos, (list, tuple)) else [eos])

    # -- prompt helpers -------------------------------------------------------
    def chat_prefix(self, user: str, assistant_start: str = "") -> str:
        msgs = [{"role": "user", "content": user}]
        s = self.hf.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return s + assistant_start

    def encode(self, text: str, offsets: bool = False):
        enc = self.hf(text, add_special_tokens=False, return_offsets_mapping=offsets)
        if offsets:
            return enc["input_ids"], enc["offset_mapping"]
        return enc["input_ids"]

    def vocab_ids_startswith(self, chars: str) -> list[int]:
        toks = self.hf.convert_ids_to_tokens(list(range(len(self.hf))))
        return [i for i, t in enumerate(toks) if t and t[0] in chars]

    def _with_bos(self, prefix: str) -> list[int]:
        p_ids = self.encode(prefix)
        if (not p_ids or p_ids[0] != self.hf.bos_token_id) and self.hf.bos_token_id is not None:
            p_ids = [self.hf.bos_token_id] + p_ids
        return p_ids

    # -- scoring --------------------------------------------------------------
    @torch.inference_mode()
    def score(self, prefix: str, target: str, want_rank1: bool = False, masks: dict | None = None) -> Scored:
        t0 = time.time()
        p_ids = self._with_bos(prefix)
        t_ids, offs = self.encode(target, offsets=True)
        ids = p_ids + t_ids
        n_p, n = len(p_ids), len(ids)
        out = np.empty(len(t_ids), dtype=np.float32)
        r1 = np.empty(len(t_ids), dtype=bool) if want_rank1 else None
        extra = {k: np.empty(len(t_ids), dtype=np.float32) for k in (masks or {})}
        mask_ids = {k: torch.tensor(v, device=self.dev) for k, v in (masks or {}).items()}
        pkv = None
        pos = 0
        while pos < n - 1:
            end = min(pos + self.chunk, n - 1)
            x = torch.tensor([ids[pos:end]], device=self.dev)
            o = self.model(input_ids=x, past_key_values=pkv, use_cache=True)
            pkv = o.past_key_values
            first_tgt = max(n_p - 1 - pos, 0)
            if first_tgt < end - pos:
                lg = o.logits[0, first_tgt:].float()
                lp = torch.log_softmax(lg, dim=-1)
                tgt = torch.tensor(ids[pos + 1 + first_tgt : end + 1], device=self.dev)
                sel = lp.gather(1, tgt[:, None])[:, 0]
                a = pos + first_tgt + 1 - n_p
                out[a : a + sel.shape[0]] = sel.cpu().numpy()
                for k, mid in mask_ids.items():
                    extra[k][a : a + sel.shape[0]] = torch.logsumexp(lp[:, mid], dim=-1).cpu().numpy()
                if want_rank1:
                    r1[a : a + sel.shape[0]] = (lg.argmax(-1) == tgt).cpu().numpy()
                del lg, lp
            del o
            pos = end
        del pkv
        torch.cuda.empty_cache()
        return Scored(out, np.array(offs, dtype=np.int64).reshape(-1, 2), n_p, time.time() - t0, r1, extra or None)

    # -- generation -----------------------------------------------------------
    @torch.inference_mode()
    def generate(self, ids: list[int], max_tokens: int, temp: float = 0.0, stop_fn=None) -> dict:
        """Generate from token ids. temp=0 -> greedy; temp=1 -> plain ancestral sampling."""
        t0 = time.time()
        pkv, logits = None, None
        for i in range(0, len(ids), 2048):
            o = self.model(input_ids=torch.tensor([ids[i : i + 2048]], device=self.dev), past_key_values=pkv, use_cache=True)
            pkv, logits = o.past_key_values, o.logits[0, -1]
        t1 = time.time()
        toks: list[int] = []
        for _ in range(max_tokens):
            if temp > 0:
                nxt = int(torch.multinomial(torch.softmax(logits.float() / temp, -1), 1))
            else:
                nxt = int(logits.argmax())
            if nxt in self.eos:
                break
            toks.append(nxt)
            if stop_fn is not None and stop_fn(toks):
                break
            o = self.model(input_ids=torch.tensor([[nxt]], device=self.dev), past_key_values=pkv, use_cache=True)
            pkv, logits = o.past_key_values, o.logits[0, -1]
        t2 = time.time()
        del pkv
        torch.cuda.empty_cache()
        return {"text": self.hf.decode(toks, skip_special_tokens=True), "tokens": toks, "secs": t2 - t0,
                "prompt_tokens": len(ids), "gen_tokens": len(toks),
                "prompt_tps": len(ids) / max(t1 - t0, 1e-9), "gen_tps": len(toks) / max(t2 - t1, 1e-9)}
