"""Small ctypes boundary: Python wakes once per sensory cycle, not per neural step."""
import ctypes as c
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Circuit:
    def __init__(self, path=None):
        self.model = json.loads(Path(path or ROOT / "models/escape.json").read_text())
        self.neurons = self.model["neurons"]
        self.n = len(self.neurons)
        ids = {n["id"]: i for i, n in enumerate(self.neurons)}
        incoming = [[] for _ in self.neurons]
        for edge in self.model["edges"]:
            pre, post = ids[edge["pre"]], ids[edge["post"]]
            nt = self.neurons[pre]["nt"]
            sign = {"ACH": 1, "GABA": -1, "GLUT": -1, "": 0}[nt]
            incoming[post].append((pre, sign * edge["count"] * self.model["dynamics"]["gain"]))
        offsets, sources, weights = [0], [], []
        for row in incoming:
            for pre, weight in row:
                sources.append(pre); weights.append(weight)
            offsets.append(len(sources))
        self.offsets = (c.c_int * len(offsets))(*offsets)
        self.sources = (c.c_int * len(sources))(*sources)
        self.weights = (c.c_float * len(weights))(*weights)
        self.input = (c.c_float * self.n)()
        self.output = (c.c_float * self.n)()
        self.lib = c.CDLL(str(ROOT / "build/libfruitfly.so"))
        self.lib.ff_create.restype = c.c_void_p
        self.lib.ff_create.argtypes = [c.c_int, c.c_int, c.POINTER(c.c_int),
                                       c.POINTER(c.c_int), c.POINTER(c.c_float)]
        self.lib.ff_step.argtypes = [c.c_void_p, c.POINTER(c.c_float), c.c_int, c.POINTER(c.c_float)]
        self.lib.ff_destroy.argtypes = [c.c_void_p]
        self.lib.ff_reset.argtypes = [c.c_void_p]
        self.ptr = self.lib.ff_create(self.n,len(sources),self.offsets,self.sources,self.weights)
        if not self.ptr:
            raise ValueError("Invalid circuit")
        self.elapsed_ms = 0

    def step(self, currents, steps=20):
        if not self.ptr or not isinstance(steps,int) or not 1 <= steps <= 1000 or len(currents) != self.n:
            raise ValueError("Invalid step batch or input size")
        for i, value in enumerate(currents):
            if not math.isfinite(value):raise ValueError("Non-finite neural input")
            self.input[i] = value
        self.lib.ff_step(self.ptr,self.input,steps,self.output)
        self.elapsed_ms += steps
        return list(self.output)

    def reset(self):
        self.lib.ff_reset(self.ptr)
        self.elapsed_ms = 0

    def close(self):
        if self.ptr:
            self.lib.ff_destroy(self.ptr)
            self.ptr = None

    def __enter__(self): return self
    def __exit__(self, *_): self.close()
