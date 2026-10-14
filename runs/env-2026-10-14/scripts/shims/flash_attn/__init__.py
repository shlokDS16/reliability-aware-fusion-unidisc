"""Minimal pure-PyTorch stand-in for the parts of flash-attn used by MDLM/UniDisc (no wheel exists for Windows).
Only equal-length, non-causal/causal, no-dropout calls are supported. NOT the real flash-attn."""
from . import flash_attn_interface  # noqa: F401
from . import layers  # noqa: F401
__version__ = "0.0.0+shim"
