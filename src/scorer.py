"""Teacher-forced token scoring with a local Gemma 4 model.

Two interchangeable backends with the same interface:
  * scorer_mlx.py   - Apple silicon, MLX, 4-bit checkpoints (laptop runs)
  * scorer_torch.py - CUDA, PyTorch/transformers, full-precision bf16 checkpoints (DGX runs)
Select with SCORER_BACKEND=mlx|torch (default: mlx if importable, else torch).
"""
import os

from scorer_common import Scored, line_scores  # noqa: F401

_b = os.environ.get("SCORER_BACKEND")
if _b is None:
    try:
        import mlx.core  # noqa: F401

        _b = "mlx"
    except Exception:
        _b = "torch"
if _b == "mlx":
    from scorer_mlx import Scorer  # noqa: F401
else:
    from scorer_torch import Scorer  # noqa: F401
BACKEND = _b
