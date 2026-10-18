"""all-MiniLM-L6-v2 sentence embeddings in plain numpy.

Why this exists: the machine has the model in the Hugging Face cache but no Python
environment with both sentence-transformers and a clean path to it from the system
python3. This file reads the cached safetensors file by hand (a JSON header followed by
raw float32 bytes), tokenizes with the `tokenizers` package, and runs the 6-layer BERT
forward pass, mean pooling and L2 normalisation that sentence-transformers applies.
`python3 validation/minilm_np.py --check REF.npy` compares against a reference.

Falls back to None (callers then use term overlap) when the cache or `tokenizers` is
missing; callers must say so in their report.
"""
import glob
import json
import os
import struct
import sys

import numpy as np

HUB = os.path.expanduser("~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots")
MAX_LEN = 256  # sentence_bert_config.json
N_HEADS = 12
EPS = 1e-12


def _snapshot():
    for d in sorted(glob.glob(os.path.join(HUB, "*"))):
        if os.path.exists(os.path.join(d, "model.safetensors")) and os.path.exists(os.path.join(d, "tokenizer.json")):
            return d
    return None


def _read_safetensors(path):
    with open(path, "rb") as f:
        (n,) = struct.unpack("<Q", f.read(8))
        header = json.loads(f.read(n))
        base = 8 + n
        out = {}
        for name, meta in header.items():
            if name == "__metadata__" or meta["dtype"] != "F32":
                continue
            a, b = meta["data_offsets"]
            f.seek(base + a)
            out[name] = np.frombuffer(f.read(b - a), dtype="<f4").reshape(meta["shape"])
        return out


def _gelu(x):
    # exact erf form, as in BERT; scipy if present, else a vectorised math.erf
    try:
        from scipy.special import erf
    except ImportError:
        import math

        erf = np.vectorize(math.erf, otypes=[np.float64])
    return 0.5 * x * (1.0 + erf(x / np.sqrt(2.0)))


def _layer_norm(x, w, b):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return (x - mu) / np.sqrt(var + EPS) * w + b


class MiniLM:
    def __init__(self):
        snap = _snapshot()
        if snap is None:
            raise RuntimeError("all-MiniLM-L6-v2 not found in the Hugging Face cache")
        from tokenizers import Tokenizer

        self.tok = Tokenizer.from_file(os.path.join(snap, "tokenizer.json"))
        self.tok.enable_truncation(MAX_LEN)
        self.tok.no_padding()
        self.w = {k: v.astype(np.float64) for k, v in _read_safetensors(os.path.join(snap, "model.safetensors")).items()}
        self.snapshot = snap

    def _encode_one(self, text):
        w = self.w
        ids = np.array(self.tok.encode(text).ids)
        x = w["embeddings.word_embeddings.weight"][ids] + w["embeddings.position_embeddings.weight"][: len(ids)] + w["embeddings.token_type_embeddings.weight"][0]
        x = _layer_norm(x, w["embeddings.LayerNorm.weight"], w["embeddings.LayerNorm.bias"])
        d = x.shape[1]
        hd = d // N_HEADS
        for i in range(6):
            p = f"encoder.layer.{i}."
            q = x @ w[p + "attention.self.query.weight"].T + w[p + "attention.self.query.bias"]
            k = x @ w[p + "attention.self.key.weight"].T + w[p + "attention.self.key.bias"]
            v = x @ w[p + "attention.self.value.weight"].T + w[p + "attention.self.value.bias"]
            sh = lambda a: a.reshape(len(ids), N_HEADS, hd).transpose(1, 0, 2)
            s = sh(q) @ sh(k).transpose(0, 2, 1) / np.sqrt(hd)
            s = np.exp(s - s.max(-1, keepdims=True))
            s /= s.sum(-1, keepdims=True)
            ctx = (s @ sh(v)).transpose(1, 0, 2).reshape(len(ids), d)
            a = ctx @ w[p + "attention.output.dense.weight"].T + w[p + "attention.output.dense.bias"]
            x = _layer_norm(x + a, w[p + "attention.output.LayerNorm.weight"], w[p + "attention.output.LayerNorm.bias"])
            h = _gelu(x @ w[p + "intermediate.dense.weight"].T + w[p + "intermediate.dense.bias"])
            o = h @ w[p + "output.dense.weight"].T + w[p + "output.dense.bias"]
            x = _layer_norm(x + o, w[p + "output.LayerNorm.weight"], w[p + "output.LayerNorm.bias"])
        e = x.mean(0)
        return e / np.linalg.norm(e)

    def encode(self, texts):
        return np.stack([self._encode_one(t) for t in texts])


def load_or_none():
    try:
        return MiniLM()
    except Exception as exc:  # noqa: BLE001 - any failure means "fall back and say so"
        sys.stderr.write(f"minilm_np: unavailable ({type(exc).__name__}: {exc})\n")
        return None


if __name__ == "__main__":
    m = MiniLM()
    texts = ["The cat sits on the mat.", "A trained table equals a random table.", "Champernowne completes late.", "ω-complete de Bruijn word"]
    e = m.encode(texts)
    if len(sys.argv) == 3 and sys.argv[1] == "--check":
        ref = np.load(sys.argv[2])
        print("max abs diff vs reference:", float(np.abs(ref - e).max()))
    else:
        np.save(sys.argv[1] if len(sys.argv) > 1 else "/dev/stdout", e)
