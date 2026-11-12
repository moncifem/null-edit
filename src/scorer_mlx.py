"""Teacher-forced token scoring with a local Gemma 4 model (MLX).

`Scorer.score(prefix, target)` returns the log-probability (nats) of every token of
`target` given `prefix` + preceding target tokens, with character offsets so scores can
be mapped back to source lines. No text is generated.
"""
from __future__ import annotations

import os
import time
import mlx.core as mx
import numpy as np
from mlx_lm import load
from mlx_lm.models.cache import make_prompt_cache


from scorer_common import Scored, line_scores  # noqa: F401


class Scorer:
    def __init__(self, model_path: str, chunk: int = 512):
        mx.set_cache_limit(1 * 1024**3)  # MLX otherwise keeps tens of GB of freed buffers
        self.model, self.tok = load(model_path)
        self.hf = self.tok._tokenizer  # underlying HF fast tokenizer
        self.chunk = chunk
        self.model_path = model_path
        # Duty-cycle throttle: after each chunk sleep THROTTLE x (compute time). 1.5 -> GPU busy ~40% of the time.
        self.throttle = float(os.environ.get("THROTTLE", "0"))

    # -- prompt helpers -------------------------------------------------------
    def chat_prefix(self, user: str, assistant_start: str = "") -> str:
        msgs = [{"role": "user", "content": user}]
        s = self.tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        return s + assistant_start

    def encode(self, text: str, offsets: bool = False):
        enc = self.hf(text, add_special_tokens=False, return_offsets_mapping=offsets)
        if offsets:
            return enc["input_ids"], enc["offset_mapping"]
        return enc["input_ids"]

    # -- scoring --------------------------------------------------------------
    def vocab_ids_startswith(self, chars: str) -> list[int]:
        """Token ids whose surface string starts with one of `chars` (no leading-space marker)."""
        toks = self.hf.convert_ids_to_tokens(list(range(len(self.hf))))
        return [i for i, t in enumerate(toks) if t and t[0] in chars]

    def score(self, prefix: str, target: str, want_rank1: bool = False, masks: dict | None = None) -> Scored:
        t0 = time.time()
        p_ids = self.encode(prefix)
        if not p_ids or p_ids[0] != self.hf.bos_token_id:
            if self.hf.bos_token_id is not None and not prefix.startswith(self.hf.bos_token or "\0"):
                p_ids = [self.hf.bos_token_id] + p_ids
        t_ids, offs = self.encode(target, offsets=True)
        ids = p_ids + t_ids
        n_p, n = len(p_ids), len(ids)
        cache = make_prompt_cache(self.model)
        out = np.empty(len(t_ids), dtype=np.float32)
        r1 = np.empty(len(t_ids), dtype=bool) if want_rank1 else None
        extra = {k: np.empty(len(t_ids), dtype=np.float32) for k in (masks or {})}
        mask_ids = {k: mx.array(v) for k, v in (masks or {}).items()}
        pos = 0
        body = getattr(getattr(self.model, "language_model", None), "model", None)
        slept = 0.0
        t_chunk = time.time()
        while pos < n - 1:
            if self.throttle and pos > 0:
                dt = (time.time() - t_chunk) * self.throttle
                time.sleep(dt)
                slept += dt
            t_chunk = time.time()
            end = min(pos + self.chunk, n - 1)
            if body is not None and end <= n_p - 1:
                # chunk lies entirely in the prompt: no output distribution needed, skip the vocab head
                end = min(pos + 2 * self.chunk, n_p - 1)
                h = body(mx.array(ids[pos:end])[None], cache=cache)
                mx.eval(h[0, -1, :1])
                del h
                pos = end
                continue
            x = mx.array(ids[pos:end])[None]
            logits = self.model(x, cache=cache)[0]  # (L, V) predicts ids[pos+1:end+1]
            # only positions predicting target tokens are needed
            first_tgt = max(n_p - 1 - pos, 0)
            if first_tgt < end - pos:
                lg = logits[first_tgt:].astype(mx.float32)
                tgt = mx.array(ids[pos + 1 + first_tgt : end + 1])
                lp = lg - mx.logsumexp(lg, axis=-1, keepdims=True)
                sel = mx.take_along_axis(lp, tgt[:, None], axis=-1)[:, 0]
                a = pos + first_tgt + 1 - n_p
                for k, mid in mask_ids.items():
                    em = mx.logsumexp(lp[:, mid], axis=-1)
                    mx.eval(em)
                    extra[k][a : a + em.shape[0]] = np.array(em)
                if want_rank1:
                    am = mx.argmax(lg, axis=-1)
                    mx.eval(sel, am)
                    r1[a : a + sel.shape[0]] = np.array(am) == np.array(tgt)
                else:
                    mx.eval(sel)
                out[a : a + sel.shape[0]] = np.array(sel)
            else:
                mx.eval(logits[-1, :1])
            pos = end
            del logits
        del cache
        mx.clear_cache()
        return Scored(out, np.array(offs, dtype=np.int64).reshape(-1, 2), n_p, time.time() - t0 - slept, r1, extra or None)

    # -- generation -----------------------------------------------------------
    def generate(self, ids: list[int], max_tokens: int, temp: float = 0.0, stop_fn=None) -> dict:
        """Generate from token ids. temp=0 -> greedy; temp=1 -> plain ancestral sampling."""
        from mlx_lm import stream_generate
        from mlx_lm.sample_utils import make_sampler

        sampler = make_sampler(temp=temp, top_p=1.0, top_k=0) if temp > 0 else make_sampler(temp=0.0)
        t0 = time.time()
        text, toks, last = "", [], None
        for r in stream_generate(self.model, self.tok, ids, max_tokens=max_tokens, sampler=sampler):
            text += r.text
            toks.append(r.token)
            last = r
            if stop_fn is not None and stop_fn(toks):
                break
        mx.clear_cache()
        return {"text": text, "tokens": toks, "secs": time.time() - t0, "prompt_tokens": len(ids),
                "gen_tokens": len(toks), "prompt_tps": last.prompt_tps if last else None,
                "gen_tps": last.generation_tps if last else None}
